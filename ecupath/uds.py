from .can_tp import CAN_TP
from .event_manager import EventManager
from .UDSException import UDSException
from .frame import Frame
from .uds_sid_19 import Ox19
from .uds_sid_22 import Ox22
from .uds_sid_2E import Ox2E
from .uds_sid_27 import Ox27
import queue
import threading
import time

class UDS:
    START_SESSION = (0x10, 0x60)  # Updated to match your testing

    def __init__(self, tx_id, rx_id, channel, baud_rate, message_type, event_manager: EventManager):
        self.event_manager = event_manager
        self.can_tp = CAN_TP(tx_id, channel, baud_rate, message_type, self.event_manager)
        self.event_manager.publish('rx_id', rx_id)
        self.event_manager.subscribe('data_to_uds', self.process_response)
        self.event_manager.subscribe('send_security_key', self.handle_security_key_request)
        self._buffer_to_cantp = queue.Queue()
        self._sid_output_display = queue.Queue()
        self._output_terminal = queue.Queue()
        self.frame = Frame()

        self.handlers = {
            0x19: Ox19(self),
            0x22: Ox22(self),
            0x2E: Ox2E(self),
            0x27: Ox27(self)
        }
        self.security_access_granted = False

        self.p2_timer = 0.05
        self.p2_star_timer = 5
        self.waiting_for_response = False
        self.response_pending = False
        self.current_request = None
        self.session_started = False
        self.request_lock = threading.Lock()
        self._immediate_request_queue = queue.Queue()

    def handle_security_key_request(self, request_data):
        thread_id = threading.current_thread().ident
        print(f"Thread {thread_id}: Received security key request via event: {[hex(x) for x in request_data]}")
        try:
            self.send_request(request_data, immediate=True)
        except Exception as e:
            print(f"Thread {thread_id}: Error in handle_security_key_request: {e}")

    def send_request(self, data, immediate=False):
        thread_id = threading.current_thread().ident
        print(f"Thread {thread_id}: Entering send_request for: {[hex(x) for x in data]}")
        try:
            self.received_data = data
            self._output_terminal.put(self.received_data)
            print(f"Thread {thread_id}: Attempting to acquire lock in send_request for: {[hex(x) for x in data]}")
            acquired = self.request_lock.acquire(timeout=2)  # 2-second timeout
            if acquired:
                try:
                    print(f"Thread {thread_id}: Lock acquired in send_request for: {[hex(x) for x in data]}")
                    if immediate:
                        self._immediate_request_queue.put(self.received_data)
                        self.process_immediate_request()
                    elif not self.session_started and self.received_data != self.START_SESSION:
                        print(f"Thread {thread_id}: Queueing request due to session not started")
                        self._buffer_to_cantp.put(self.received_data)
                    elif self.waiting_for_response:
                        print(f"Thread {thread_id}: Waiting for response, queueing new request")
                        self._buffer_to_cantp.put(self.received_data)
                    else:
                        self.prepare_and_send_request(self.received_data)
                finally:
                    self.request_lock.release()
                    print(f"Thread {thread_id}: Lock released in send_request for: {[hex(x) for x in data]}")
            else:
                print(f"Thread {thread_id}: Failed to acquire lock in send_request for: {[hex(x) for x in data]} after 2s timeout")
        except Exception as e:
            print(f"Thread {thread_id}: Exception in send_request: {e}")

    def process_immediate_request(self):
        while not self._immediate_request_queue.empty():
            data = self._immediate_request_queue.get()
            print(f"Sending immediate request: {data}")
            self.can_tp.receive_data_from_uds(data)

    def prepare_and_send_request(self, data):
        self.current_request = data
        self.waiting_for_response = True
        self.response_pending = False
        print(f"Sending request: {data}")
        self.can_tp.receive_data_from_uds(data)
        threading.Thread(target=self.response_timeout_handler).start()

    def process_request_queue(self):
        thread_id = threading.current_thread().ident
        print(f"Thread {thread_id}: Starting process_request_queue")
        self.process_immediate_request()  # Immediate requests outside lock
        if not self.waiting_for_response and not self._buffer_to_cantp.empty():
            with self.request_lock:
                print(f"Thread {thread_id}: Lock acquired in process_request_queue for dequeue")
                request = self._buffer_to_cantp.get()
                print(f"Thread {thread_id}: Request dequeued: {[hex(x) for x in request]}")
            print(f"Thread {thread_id}: Lock released in process_request_queue")
            self.prepare_and_send_request(request)
        print(f"Thread {thread_id}: Finished process_request_queue")

    def process_response(self, response):
        self.received_response = response
        self._output_terminal.put(self.received_response)
        try:
            print("process_response", self.received_response)
            if self.received_response[0] == '0x7F':
                if self.received_response[2] == '0x78':
                    print("Received ResponsePending (0x78)")
                    self.response_pending = True
                    threading.Thread(target=self.wait_for_response).start()
                else:
                    self.handle_response(self.received_response)
            else:
                self.handle_response(self.received_response)
        except Exception as e:
            print(f"Unexpected Error: {e}")

    def handle_response(self, response):
        thread_id = threading.current_thread().ident
        print(f"Thread {thread_id}: Attempting to acquire lock in handle_response for: {response}")
        with self.request_lock:
            print(f"Thread {thread_id}: Lock acquired in handle_response for: {response}")
            self.waiting_for_response = False
            self.response_pending = False
            if response[0] == '0x50':
                print("received session positive response")
                self.update_timers(response)
                print("Diagnostic session started successfully")
                self.session_started = True
            elif response[0] == '0x67':
                if response[1] in ['0x32', '0x34', '0x62']:
                    self.security_access_granted = True
                    print("Security access Granted")
        print(f"Thread {thread_id}: Lock released in handle_response for: {response}")
        if response[0] == '0x50':
            self.process_queued_requests()
        elif response[0] in ['0x67', '0x7F']:
            self.direct_to_sid(response)
        else:
            self.direct_to_sid(response)

    def start_session(self):
        if not self.session_started:
            print("Starting diagnostic session")
            self.send_request(self.START_SESSION, immediate=True)
            self.session_started = True

    def update_timers(self, response):
        print("UPDATE TIMERS")
        if len(response) >= 4:
            self.p2_timer = (int(response[2], 16) << 8 | int(response[3], 16)) / 1000
        if len(response) >= 6:
            self.p2_star_timer = (int(response[4], 16) << 8 | int(response[5], 16)) / 1000
        print(f"Updated timers - P2: {self.p2_timer}s, P2*: {self.p2_star_timer}s")

    def wait_for_response(self):
        timeout = self.p2_star_timer
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.response_pending:
                return
            time.sleep(0.01)
        print(f"Timeout occurred while waiting for response after 0x78")
        self.waiting_for_response = False
        self.response_pending = False
        self.process_request_queue()

    def response_timeout_handler(self):
        timeout = self.p2_timer if self.current_request != self.START_SESSION else self.p2_star_timer
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.waiting_for_response or self.response_pending:
                return
            time.sleep(0.01)
        if self.waiting_for_response and not self.response_pending:
            print(f"Timeout occurred while waiting for response to {self.current_request}")
            self.waiting_for_response = False
            if self.current_request == self.START_SESSION:
                self.session_started = False

    def sid_display(self):
        if not self._sid_output_display.empty():
            return self._sid_output_display.get()
        return None

    def terminal_display(self):
        if not self._output_terminal.empty():
            return self._output_terminal.get()
        return None

    def direct_to_sid(self, response):
        self.Frame_response = response
        print("direct_to_sid", self.Frame_response)
        self.sid = self.frame.get_sid(self.Frame_response)
        print("sid received: ", self.sid)
        handler = self.handlers.get(self.sid)
        if handler:
            handler.buffer_frame(self.Frame_response)
        else:
            print(f"No handler for SID {self.sid}")

    def process_next_request(self):
        if not self.waiting_for_response and not self._buffer_to_cantp.empty():
            request = self._buffer_to_cantp.get()
            print(f"Sending request: {request}")
            self.can_tp.receive_data_from_uds(request)
            self.waiting_for_response = True
            self.response_pending = False
            threading.Thread(target=self.response_timeout_handler).start()

    def added_from_sid(self, data):
        self.event_manager.publish('response_received', data)
        self._sid_output_display.put(data)

    def process_queued_requests(self):
        print("A")
        while not self._buffer_to_cantp.empty():
            with self.request_lock:
                print("6")
                if not self.waiting_for_response:
                    request = self._buffer_to_cantp.get()
                    self.prepare_and_send_request(request)
                else:
                    break
            while self.waiting_for_response:
                time.sleep(0.01)