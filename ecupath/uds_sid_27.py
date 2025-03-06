import queue
import time

from .frame import Frame

class Ox27:
    def __init__(self, uds_instance):
        self._buffer = queue.Queue()
        self.uds = uds_instance
        self.frame = Frame()
        self.seed = []

    def buffer_frame(self, frame):
        self._buffer.put(frame)
        self.main()

    def main(self):
        if not self._buffer.empty():
            data = self._buffer.get()
            sub_function = int(data[1], 16)
            if sub_function % 2 == 1:  # Seed request
                self.handle_seed_request(data)
            else:  # Key response
                self.handle_key_response(data)

    def handle_seed_request(self, data):
        print(data[0])
        if data[0] == '0x67':  # Positive response for seed request
            self.seed = data[2:18]  # Extract the 16-byte seed from the response
            key = self.calculate_key(self.seed)
            key_sub_function = hex(int(data[1], 16) + 1)  # Increment sub-function for key
            key_request = (0x27, int(key_sub_function, 16)) + key
            self.uds.send_immediate_request(key_request)
            self.uds.process_immediate_request()

    def handle_key_response(self, data):
        if data[0] == 0x67:  # Positive response
            print("Security access granted.")
        else:
            print("Security access denied.")

    def calculate_key(self, seed):
        # Custom algorithm based on XOR and bitwise operations
        key = []
        for i in range(len(seed)):
            key_byte = int(seed[i], 16) ^ 0xAA
            key.append(key_byte)
        return tuple(key)