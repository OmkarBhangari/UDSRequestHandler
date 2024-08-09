import json
import os

class Jason_Handle:
    def __init__(self):
        self.config_file='uds_config.json'
        self.load_file()
    

    def load_file(self):
        if os.path.exists(self.config_file):
            with open(self.config_file,'r') as f:
                config=json.load(f)
    
    def auto_load_file(self):
        if os.path.exists(self.config_file):
            with open(self.config_file,'r') as f:
                config=json.load(f)
        else self.get_user_input():
         self.save_config(config)



    def get_user_input(self):
        request_id = 0x743
        response_id =  0x763
        return {'request_id':request_id,'response_id':response_id}
    
    
    def save_config(self):
        config = {
            'request_id': self.request_combo.get(),
            'response_id': self.response_combo.get()
        }
        self.uds_wrapper.save_config(config)
        print("Configuration saved to", self.uds_wrapper.config_file)
