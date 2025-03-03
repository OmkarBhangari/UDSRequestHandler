from ecupath import UDS
from ecupath import EventManager
import threading
import time

class App:
    TESTER_PRESENT = (0x3E, 0x00)
    STOP_MONITORING = False

    def __init__(self, tx_id, rx_id, channel, baud_rate, message_type, event_manager: EventManager):
        self.event_manager = event_manager
        self.uds = UDS(tx_id, rx_id, channel, baud_rate, message_type, self.event_manager)
        self.monitoring = False
        self.sending_tester_present = False
        self.tester_present_lock = threading.Lock()

    def start_monitoring(self):
        self.monitoring = True
        self.STOP_MONITORING = False
        self.uds.start_session()  # Start the diagnostic session immediately
        time.sleep(0.01)  # Small delay to allow the start session request to be processed
        self.monitor_thread = threading.Thread(target=self.monitor)
        self.monitor_thread.start()
        self.tester_present_thread = threading.Thread(target=self.send_tester_present)
        self.tester_present_thread.start()

    def stop_monitoring(self):
        self.STOP_MONITORING = True
        self.monitoring = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join()
        if self.tester_present_thread.is_alive():
            self.tester_present_thread.join()

    def monitor(self):
        while self.monitoring and not self.STOP_MONITORING:
            with self.tester_present_lock:
                if not self.sending_tester_present:
                    self.uds.process_request_queue()
                    self.uds.can_tp.cantp_monitor()
                    self.uds.can_tp.can.can_monitor()
            #time.sleep(0.01)
            time.sleep(0.001)

    def send_tester_present(self):
        while self.monitoring and not self.STOP_MONITORING:

            with self.tester_present_lock:
                self.sending_tester_present = True

                self.uds.send_request(App.TESTER_PRESENT, immediate=True)  # Sending Tester Frame
                self.sending_tester_present = False
            #time.sleep(4)
            time.sleep(4)

    def get_uds(self):
        return self.uds