""" from ecupath import PCAN
from ecupath import CAN
from ecupath import CAN_TP """
from ecupath import UDS
from ecupath import EventManager
import threading
import time

class App:
    def __init__(self, tx_id, rx_id, channel, baud_rate, message_type):
        self.event_manager = EventManager()

        # Initialize CAN
        #self.can = CAN(can_id, can_tp_id, pcan_device, baud_rate, message_type, self.event_manager)

        # Initialize CAN-TP
        #self.can_tp = CAN_TP(self.can, self.event_manager)

        # Initialize UDS
        self.uds = UDS(tx_id, rx_id, channel, baud_rate, message_type, self.event_manager)

        self.monitoring = False

    def start_monitoring(self):
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor)
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join()

    def monitor(self):
        while self.monitoring:
            self.uds.process_request_queue()
            self.uds.can_tp.cantp_monitor()
            self.uds.can_tp.can.can_monitor()
            # Sleep briefly to prevent high CPU usage
            time.sleep(0.1)

    def get_uds(self):
        return self.uds
