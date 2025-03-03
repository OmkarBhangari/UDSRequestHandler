import queue
from . import Colors
from .frame import Frame
from Crypto.Cipher import AES


class Ox27:
    def __init__(self, uds_instance):
        self.buffer = queue.Queue()
        self.uds = uds_instance
        self.frame = Frame()
        self.seed = None
        self.subfunction = None
        self.full_message = []

        self.keys = {
            0x31: bytes(
                [0x1D, 0x3A, 0x92, 0x94, 0x2A, 0xC8, 0x16, 0xC4, 0x8B, 0xDD, 0xC0, 0x5C, 0x4C, 0xC9, 0x2C, 0x06]),
            0x33: bytes(
                [0x22, 0x2A, 0x46, 0x3F, 0xF2, 0x71, 0xE2, 0x55, 0x69, 0x80, 0xAC, 0x16, 0xA9, 0x17, 0xC2, 0x9B]),
            0x61: bytes(
                [0xE0, 0x02, 0x02, 0x68, 0xC6, 0x67, 0x55, 0x08, 0xB7, 0x56, 0x15, 0xC8, 0xC8, 0xC8, 0xB8, 0x7E])
        }
        self.ivs = {
            0x31: bytes(
                [0x9D, 0x4E, 0x8F, 0x83, 0xA9, 0xE0, 0xD6, 0x3E, 0x1B, 0xFB, 0xE7, 0x73, 0x20, 0xDA, 0x5C, 0x65]),
            0x33: bytes(
                [0xFD, 0x31, 0x15, 0x0A, 0xC4, 0x6A, 0x31, 0xD9, 0xD0, 0x1F, 0x0D, 0xFA, 0x34, 0xF0, 0x0A, 0x54]),
            0x61: bytes(
                [0x93, 0x2D, 0xAD, 0xA4, 0x3C, 0x89, 0x61, 0x43, 0xD1, 0xD5, 0xD0, 0xF0, 0x99, 0x32, 0xEC, 0x74])
        }

    def buffer_frame(self, frame):
        frame = [int(x, 16) if isinstance(x, str) else x for x in frame]
        print(f"Buffering frame: {[hex(x) for x in frame]}")

        if frame[0] == 0x67:
            self.buffer.put(frame)
        elif frame[0] & 0xF0 == 0x10:
            length = ((frame[0] & 0x0F) << 8) + frame[1]
            self.full_message = frame[2:8]
            print(f"FF, expecting {length} bytes: {[hex(x) for x in self.full_message]}")
        elif frame[0] & 0xF0 == 0x20:
            self.full_message.extend(frame[1:8])
            print(f"CF added: {[hex(x) for x in self.full_message]}")
            if len(self.full_message) >= 18:
                self.buffer.put(self.full_message)
                self.full_message = []
        self.main()

    def main(self):
        if not self.buffer.empty():
            print("I'm in Ox27")
            frame = self.buffer.get()
            self.process_response(frame)

    def process_response(self, frame):
        print(f"Processing frame: {[hex(x) for x in frame]}")

        if len(frame) < 2:
            self.report_error("Invalid response length")
            return

        sid = frame[0]
        subfunction = frame[1]

        if sid == 0x67:
            if subfunction in [0x31, 0x33, 0x61]:
                if len(frame) >= 18:
                    self.subfunction = subfunction
                    self.seed = bytes(frame[2:18])
                    self.send_key()
                else:
                    self.report_error("Invalid seed length")
            elif subfunction in [0x62, 0x34, 0x32]:
                self.report_unlock_success(subfunction - 1)
            else:
                self.report_error(f"Unsupported subfunction: {hex(subfunction)}")
        elif sid == 0x7F and frame[1] == 0x27:
            nrc = frame[2]
            self.report_error(f"Security access failed with NRC: {hex(nrc)}")
        else:
            self.report_error(f"Unexpected response: {self.frame.hex(frame)}")

    def compute_key(self):
        if self.subfunction not in self.keys:
            raise ValueError(f"Unsupported subfunction: {hex(self.subfunction)}")
        key = self.keys[self.subfunction]
        iv = self.ivs[self.subfunction]
        seed_work = bytes(a ^ b for a, b in zip(self.seed, iv))
        cipher = AES.new(key, AES.MODE_ECB)
        return cipher.encrypt(seed_work)

    def send_key(self):
        key = self.compute_key()
        request = [0x27, self.subfunction + 1] + list(key)
        print(f"Sending key request (hex): {[hex(x) for x in request]}")
        self.uds.can_tp.receive_data_from_uds(tuple(request))
        print("Key sent directly to CAN bus via CAN_TP!")

    def report_unlock_success(self, subfunction):
        print(f"Security Access (0x27) - Send Key (0x{subfunction + 1:02X})")
        print(f"Subfunction: Send Key (0x{subfunction + 1:02X})")
        print("Status: Security Access Granted")
        self.uds.added_from_sid(f"Security Access Granted for Send Key (0x{subfunction + 1:02X})")

    def report_error(self, error_message):
        print("Security Access (0x27) Result")
        print("Status: Failed")
        print(f"Error: {error_message}")
        self.uds.added_from_sid(f"Security Access Failed: {error_message}")