class Frame:
    def __init__(self) :
        self.service_id_map={
            'Read DTC Information': 0x19,
            'Read Data By Identifier': 0x22,
            'Write Data By Identifier': 0x2E
        }
        self.Sub_function_map={
            "ReportNumberOfDTCByStatusMask ": 0x01,
            "ReportDTCByStatusMask":0x02,
            "ReportDTCSnapshotIdentification":0x03,
            "ReportDTCSnapshotRecordByDTCNumber":0x04
        }
    def construct_frame(self,service_id_text , sub_function_text):
       service_id=self.service_id_map.get(service_id_text,0x00)
       Sub_function=self.Sub_function_map.get(sub_function_text,0x00)
       return (0x30,service_id, Sub_function, 0x00, 0x00, 0x00, 0x00, 0x00)
    


# Example usage
frame = Frame()
result = frame.construct_frame('Read DTC Information', 'ReportDTCByStatusMask')
print(result)  # Output: (0x30, 0x19, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00)
