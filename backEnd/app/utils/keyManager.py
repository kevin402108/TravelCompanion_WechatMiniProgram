import os

class KeyManager:
    def __init__(self, env_var_name="SEC_KEY", rotation_days=30):
        self.env_var_name = env_var_name
        self.rotation_days = rotation_days
        self.master_seed = os.urandom(32)
        
        