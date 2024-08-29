from .can_tp import CAN_TP
from .event_manager import EventManager
from .UDSException import UDSException
from .frame import Frame
from .uds_sid_19 import Ox19
from .uds_sid_22 import Ox22
from .uds_sid_2E import Ox2E
import queue
import threading
import time

class UDS:
    START_SESSION = (0x10, 0x03)  # StartDiagnosticSession frame

    def __init__(self, tx_id, rx_id, channel, baud_rate, message_type, event_manager: EventManager):
        self.event_manager = event_manager
        self.can_tp = CAN_TP(tx_id, channel, baud_rate, message_type, self.event_manager)
        self.event_manager.publish('rx_id', rx_id)
        self.event_manager.subscribe('data_to_uds', self.process_response)
        self._buffer_to_cantp = queue.Queue() # queue to put items to send to can_tp.py
        self._sid_output_display = queue.Queue() # queue to display data of SID's
        self._output_terminal = queue.Queue() # queue to display in the terminal
        self.frame = Frame()

        self.handlers = {
            0x19: Ox19(self),
            0x22: Ox22(self),
            0x2E: Ox2E(self)
        }

        self.p2_timer = 0.05  # Default P2 timer value in seconds
        self.p2_star_timer = 5  # Default P2* timer value in seconds
        self.waiting_for_response = False
        self.response_pending = False
        self.current_request = None
        self.session_started = False
        self.request_lock = threading.Lock()
        self._immediate_request_queue = queue.Queue()

    # called from app.py and sends session control frame
    def start_session(self):
        if not self.session_started:
            print("Starting diagnostic session")
            self.send_request(self.START_SESSION, immediate=True)
            self.session_started = True

    # called from gui to add the requests in _buffer_to_cantp
    def send_request(self, data, immediate=False):
        self.received_data = data
        self._output_terminal.put(self.received_data)
        with self.request_lock:
            if immediate:
                self._immediate_request_queue.put(self.received_data)
                self.process_immediate_request()
            elif not self.session_started and self.received_data != self.START_SESSION:
                print("Queueing request.")
                self._buffer_to_cantp.put(self.received_data)
            elif self.waiting_for_response:
                print("Waiting for response, queueing new request")
                self._buffer_to_cantp.put(self.received_data)
            else:
                self.prepare_and_send_request(self.received_data)

    def process_immediate_request(self):
        while not self._immediate_request_queue.empty():
            data = self._immediate_request_queue.get()
            print(f"Sending immediate request: {data}")
            self.can_tp.receive_data_from_uds(data)
            """ if data == self.START_SESSION:
                self.session_started = True """

    def prepare_and_send_request(self, data):
        self.current_request = data
        self.waiting_for_response = True
        self.response_pending = False
        print(f"Sending request: {data}")
        self.can_tp.receive_data_from_uds(data)
        threading.Thread(target=self.response_timeout_handler).start()

    # called from app for continuous monitoring
    def process_request_queue(self):
        with self.request_lock:
            self.process_immediate_request()
            if not self.waiting_for_response and not self._buffer_to_cantp.empty():
                request = self._buffer_to_cantp.get()
                self.prepare_and_send_request(request)

    # called via pubsub method whenever we get data from can_tp
    def process_response(self, response):
        self.received_response = response
        self._output_terminal.put(self.received_response)
        try:
            print("process_response", self.received_response)
            if self.received_response[0] == '0x7F':  # Negative response
                if self.received_response[2] == '0x78':  # ResponsePending
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
        with self.request_lock:
            print("handle response")
            self.waiting_for_response = False
            self.response_pending = False

            if response[0] == '0x50':  # Positive response to StartDiagnosticSession
                print("received session positive response")
                self.update_timers(response)
                print("Diagnostic session started successfully")
                self.session_started = True
                self.process_queued_requests()
            elif response[0] == '0x7F':  # Negative response
                print("Negative Response Detected:", response)
                nrc = response[2]
                print("NRC:", nrc)
                if self.current_request == self.START_SESSION:
                    self.session_started = False
                print(UDSException.create_exception(nrc))
            else:
                self.direct_to_sid(response)
        
        self.process_request_queue()  # Try to process the next request, if any


    def update_timers(self, response):
        print("UPDATE TIMERS")
        if len(response) >= 4:
            self.p2_timer = (int(response[2], 16) << 8 | int(response[3], 16)) / 1000  # Convert ms to s
        if len(response) >= 6:
            self.p2_star_timer = (int(response[4], 16) << 8 | int(response[5], 16)) / 1000  # Convert ms to s
        print(f"Updated timers - P2: {self.p2_timer}s, P2*: {self.p2_star_timer}s")

    def wait_for_response(self):
        timeout = self.p2_star_timer
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.response_pending:
                return  # Response received, exit wait
            time.sleep(0.01)
        print(f"Timeout occurred while waiting for response after 0x78")
        self.waiting_for_response = False
        self.response_pending = False
        # Process the next request if available
        #self.process_next_request()
        self.process_request_queue()

    def response_timeout_handler(self):
        timeout = self.p2_timer if self.current_request != self.START_SESSION else self.p2_star_timer
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.waiting_for_response or self.response_pending:
                return  # Response received or pending, exit timeout handler
            time.sleep(0.01)
        if self.waiting_for_response and not self.response_pending:
            print(f"Timeout occurred while waiting for response to {self.current_request}")
            self.waiting_for_response = False
            if self.current_request == self.START_SESSION:
                self.session_started = False

    # called from final_gui.py to display the sid data
    def sid_display(self):
        if not self._sid_output_display.empty():
            return self._sid_output_display.get()
        return None
    
    # called from final_gui.py to display the data into the output terminal
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
        while not self._buffer_to_cantp.empty():
            with self.request_lock:
                if not self.waiting_for_response:
                    request = self._buffer_to_cantp.get()
                    self.prepare_and_send_request(request)
                else:
                    break  # Stop processing if waiting for a response
            while self.waiting_for_response:
                time.sleep(0.01)