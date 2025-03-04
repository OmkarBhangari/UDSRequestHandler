import queue
from . import Colors
from rich.table import Table
from rich.console import Console
from io import StringIO
from .frame import Frame

class Ox31:

    def __init__(self, uds_instance):
        self._buffer = queue.Queue()
        self.uds = uds_instance
        self.frame = Frame()
        self.subfunction_handlers = {
            0x01: self.handle_start_routine,
            0x02: self.handle_stop_routine,
            0x03: self.handle_request_routine_results
        }

    def buffer_frame(self, frame):
        self._buffer.put(frame)
        self.main()

    def main(self):
        if not self._buffer.empty():
            self.data = self._buffer.get()
            subfunction = self.data[1]
            handler = self.subfunction_handlers.get(subfunction)
            if handler:
                handler(self.data[2:])
            else:
                print(f"Unsupported subfunction: {hex(subfunction)}")

    def handle_start_routine(self, data):
        routine_id = (data[0] << 8) + data[1]
        print(f"Handling start routine (0x01) for routine ID: {hex(routine_id)}")
        self.report_start_routine(routine_id)

    def handle_stop_routine(self, data):
        routine_id = (data[0] << 8) + data[1]
        print(f"Handling stop routine (0x02) for routine ID: {hex(routine_id)}")
        self.report_stop_routine(routine_id)

    def handle_request_routine_results(self, data):
        routine_id = (data[0] << 8) + data[1]
        routine_status = data[2:] if len(data) > 2 else []
        print(f"Handling request routine results (0x03) for routine ID: {hex(routine_id)}")
        self.report_routine_results(routine_id, routine_status)

    def start_routine(self, routine_id, option_bytes=None):
        request = [0x31, 0x01, (routine_id >> 8) & 0xFF, routine_id & 0xFF]
        if option_bytes:
            request.extend(option_bytes)
        print(f"Starting routine {hex(routine_id)} (hex): {[hex(x) for x in request]}")
        self.uds.send_request(tuple(request))

    def stop_routine(self, routine_id, option_bytes=None):
        request = [0x31, 0x02, (routine_id >> 8) & 0xFF, routine_id & 0xFF]
        if option_bytes:
            request.extend(option_bytes)
        print(f"Stopping routine {hex(routine_id)} (hex): {[hex(x) for x in request]}")
        self.uds.send_request(tuple(request))

    def request_routine_results(self, routine_id):
        request = [0x31, 0x03, (routine_id >> 8) & 0xFF, routine_id & 0xFF]
        print(f"Requesting results for routine {hex(routine_id)} (hex): {[hex(x) for x in request]}")
        self.uds.send_request(tuple(request))

    def report_start_routine(self, routine_id):
        table = Table(title=f"Routine Control (0x31) - Start Routine")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Routine ID", f"0x{routine_id:04X}")
        table.add_row("Status", "Routine Started")
        with StringIO() as buffer:
            console = Console(file=buffer)
            console.print(table)
            result = buffer.getvalue()
        print(result)
        self.uds.added_from_sid(result)

    def report_stop_routine(self, routine_id):
        table = Table(title=f"Routine Control (0x31) - Stop Routine")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Routine ID", f"0x{routine_id:04X}")
        table.add_row("Status", "Routine Stopped")
        with StringIO() as buffer:
            console = Console(file=buffer)
            console.print(table)
            result = buffer.getvalue()
        print(result)
        self.uds.added_from_sid(result)

    def report_routine_results(self, routine_id, routine_status):
        table = Table(title=f"Routine Control (0x31) - Request Routine Results")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Routine ID", f"0x{routine_id:04X}")
        table.add_row("Status", " ".join(f"0x{b:02X}" for b in routine_status) if routine_status else "No additional data")
        with StringIO() as buffer:
            console = Console(file=buffer)
            console.print(table)
            result = buffer.getvalue()
        print(result)
        self.uds.added_from_sid(result)

    def report_error(self, error_message):
        table = Table(title="Routine Control (0x31) Result")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Status", "Failed")
        table.add_row("Error", error_message)
        with StringIO() as buffer:
            console = Console(file=buffer)
            console.print(table)
            result = buffer.getvalue()
        print(result)
        self.uds.added_from_sid(result)