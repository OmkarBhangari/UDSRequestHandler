import json
import os

class Jason_Handle:
    def __init__(self):
        self.config_file = 'uds_config.json'
        self.load_config()
    

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)


    def auto_load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        else:
            config = self.get_user_input()
            self.save_config(config)

        self.request_id = int(config['request_id'], 16)
        self.response_id = int(config['response_id'], 16)

    def get_user_input(self):
        request_id = 0x743
        response_id =  0x763
        return {'request_id': request_id, 'response_id': response_id}

    def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
class UdsConfigGUI:
    def save_config(self):
        config = {
            'request_id': self.request_combo.get(),
            'response_id': self.response_combo.get()
        }
        self.uds_wrapper.save_config(config)
        print("Configuration saved to", self.uds_wrapper.config_file)
