import hashlib
import time

def generate_id(name, password):
    timestamp = str(time.time())
    raw_data = name + password + timestamp
    hash_object = hashlib.sha3_256(raw_data.encode())
    return hash_object.hexdigest()[:16]