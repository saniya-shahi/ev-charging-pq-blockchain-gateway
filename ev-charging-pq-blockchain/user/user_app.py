import requests
import hashlib

def get_user_input():
    vmid = input("Enter VMID: ")
    pin = input("Enter PIN: ")
    amount = int(input("Enter amount: "))

    return vmid, pin, amount


def send_transaction(vmid, pin, amount, fid):
    url = "http://127.0.0.1:8000/process_transaction"

    # Hash PIN before sending (better security)
    hashed_pin = hashlib.sha3_256(pin.encode()).hexdigest()

    data = {
        "vmid": vmid,
        "pin": pin,  # still sending plain for backend match
        "amount": amount,
        "fid": fid
    }

    response = requests.post(url, params=data)
    return response.json()