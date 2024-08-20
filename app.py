
from ecupath import UDS
from ecupath import EventManager
import threading
import time

class App:
    TESTER_PRESENT = (0x3E, 0x00)

    def __init__(self, tx_id, rx_id, channel, baud_rate, message_type):
        self.event_manager = EventManager()
        self.uds = UDS(tx_id, rx_id, channel, baud_rate, message_type, self.event_manager)
        self.monitoring = False
        self.sending_tester_present = False
        self.tester_present_lock = threading.Lock()

    def start_monitoring(self):
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor)
        self.monitor_thread.start()
        self.tester_present_thread = threading.Thread(target=self.send_tester_present)
        self.tester_present_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join()
        if self.tester_present_thread.is_alive():
            self.tester_present_thread.join()

    def monitor(self):
        while self.monitoring:
            with self.tester_present_lock:
                if not self.sending_tester_present:
                    self.uds.process_request_queue()
                    self.uds.can_tp.cantp_monitor()
                    self.uds.can_tp.can.can_monitor()
            time.sleep(0.1)

    def send_tester_present(self):
        while self.monitoring:
            with self.tester_present_lock:
                self.sending_tester_present = True
                self.uds.send_request(App.TESTER_PRESENT)  # Sending Tester Frame
                self.sending_tester_present = False
            time.sleep(4)

    def get_uds(self):
        return self.uds