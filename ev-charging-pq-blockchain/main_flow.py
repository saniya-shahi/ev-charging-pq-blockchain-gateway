import requests
from kiosk.kiosk import create_qr, process_scan
from user.user_app import get_user_input, send_transaction
from crypto.qiskit_shor import simulate_shor_attack

print("\n--- EV Charging System Simulation ---\n")

# STEP 1: Register User
user_res = requests.post(
    "http://127.0.0.1:8000/register_user",
    params={
        "name": "Saniya",
        "password": "1234",
        "mobile": "9876543210"
    }
)

user_data = user_res.json()
vmid = user_data["VMID"]

print("User Registered:", user_data)

# STEP 2: Register Franchise
fr_res = requests.post(
    "http://127.0.0.1:8000/register_franchise",
    params={
        "name": "TataPower",
        "password": "abcd"
    }
)

fr_data = fr_res.json()
fid = fr_data["FID"]

print("Franchise Registered:", fr_data)

# STEP 3: Generate QR (Kiosk)
encrypted_qr_data = create_qr(fid)
print("QR Generated (Encrypted VFID):", encrypted_qr_data)

# STEP 4: User Input
vmid_input, pin, amount = get_user_input()

# STEP 5: Decode QR
decoded_fid = process_scan(encrypted_qr_data)

if not decoded_fid:
    print("Invalid QR Code")
    exit()

print("Decoded FID:", decoded_fid)

# STEP 6: Process Transaction
result = send_transaction(vmid_input, pin, amount, decoded_fid)

print("\nTransaction Result:", result)

# STEP 7: Show Blockchain
bc = requests.get("http://127.0.0.1:8000/get_blockchain")

print("\n--- BLOCKCHAIN ---")

for block in bc.json():
    print("\n==============================")
    print(f"Block Index   : {block['index']}")
    print(f"Timestamp     : {block['timestamp']}")
    
    if block['index'] == 0:
        print(f"Data          : {block['data']}")
    else:
        data = block['data']
        print(f"Transaction ID: {data['tx_id']}")
        print(f"VMID          : {data['vmid']}")
        print(f"FID           : {data['fid']}")
        print(f"Amount        : {data['amount']}")
        print(f"Status        : {data['status']}")
        print(f"Tx Timestamp  : {data['timestamp']}")

    print(f"Previous Hash : {block['prev_hash']}")
    print(f"Current Hash  : {block['hash']}")
    print("==============================")

# STEP 8: Quantum Demo
print("\n--- QUANTUM ATTACK DEMO ---")
print(simulate_shor_attack())