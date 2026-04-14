"""
main_flow.py — Full EV Charging Payment Gateway Simulation (FINAL)
==================================================================
Features:
  • Multiple users across different providers/zones
  • Optional VMID manual input
  • Proper failure handling (stops on invalid transactions)
"""

import requests
from kiosk.kiosk import create_qr, process_scan
from user.user_app import send_transaction
from crypto.qiskit_shor import simulate_shor_attack

GRID_URL = "http://127.0.0.1:8000"

print("\n" + "="*60)
print("   EV Charging Payment Gateway — Full Simulation (Multi-User)")
print("="*60)

#STEP 0: Show available grid zones
grid_info = requests.get(f"{GRID_URL}/grid_info").json()
print("\n[GRID] Available providers and zones:")
for provider, data in grid_info.items():
    print(f"  {provider}: {data['zones']}")

#STEP 1: Register Multiple Users
print("\n[STEP 1] Registering Multiple Users:")

user_inputs = [
    {"name": "Saniya", "pin": "1234", "zone": "TP-NORTH", "mobile": "9876543210"},
    {"name": "Rahul",  "pin": "5678", "zone": "AD-SOUTH", "mobile": "9123456780"},
    {"name": "Ananya", "pin": "9999", "zone": "CP-EAST",  "mobile": "9988776655"},
]

users_data = []

for u in user_inputs:
    res = requests.post(
        f"{GRID_URL}/register_user",
        params={
            "name":      u["name"],
            "password":  "pass",
            "mobile":    u["mobile"],
            "pin":       u["pin"],
            "zone_code": u["zone"],
        }
    )
    data = res.json()
    data["pin"] = u["pin"]
    users_data.append(data)

    print(f"  {u['name']} → VMID: {data['VMID']} | PIN: {u['pin']} | Zone: {u['zone']}")

#STEP 2: Register Franchise
fr_res = requests.post(
    f"{GRID_URL}/register_franchise",
    params={
        "name":            "Universal_Station",
        "password":        "frpass",
        "zone_code":       "TP-NORTH",
        "initial_balance": 500.0,
    }
)
fr_data = fr_res.json()
fid     = fr_data["FID"]

print(f"\n[STEP 2] Franchise Registered:")
print(f"  FID       : {fid}")
print(f"  Zone      : {fr_data['zone_code']}")

#STEP 3: Generate QR
print("\n[STEP 3] Kiosk generating ASCON-encrypted QR code...")
encrypted_qr_data = create_qr(fid)
print(f"  Encrypted QR data: {encrypted_qr_data[:60]}...")

#STEP 4: Select User
print("\n[STEP 4] Select User for Transaction:")
for i, u in enumerate(user_inputs):
    print(f"  {i+1}. {u['name']} ({u['zone']})")

choice = int(input("Enter choice: ")) - 1
selected_user = users_data[choice]

print(f"\nSelected User: {user_inputs[choice]['name']}")

#STEP 5: VMID Handling
print(f"System fetched VMID: {selected_user['VMID']}")
confirm = input("Use this VMID? (y/n): ")

if confirm.lower() == 'y':
    vmid_input = selected_user["VMID"]
else:
    vmid_input = input("Enter VMID manually: ")

pin    = input("Enter PIN: ")
amount = float(input("Enter amount: "))

#STEP 6: Decode QR
decoded_fid = process_scan(encrypted_qr_data)
if not decoded_fid:
    print("\n[ERROR] QR decode failed — aborting.")
    exit(1)

print(f"\n[STEP 6] Kiosk decoded FID: {decoded_fid}")

#STEP 7: Send Transaction
print("\n[STEP 7] Sending transaction with RSA-encrypted credentials...")
result = send_transaction(vmid_input, pin, amount, decoded_fid)

print(f"\n  Transaction Result: {result['status']}")

#STOP if failed
if result["status"] != "Transaction Successful":
    print("\n[INFO] Transaction failed — stopping further processing.")
    print("\n" + "="*60)
    print("   Simulation complete.")
    print("="*60)
    exit()

#STEP 8: Blockchain
bc_res = requests.get(f"{GRID_URL}/get_blockchain").json()

print("\n[STEP 8] Blockchain Ledger:")
for block in bc_res:
    print("\n  " + "─"*54)
    print(f"  Block Index   : {block['index']}")
    print(f"  Timestamp     : {block['timestamp']}")

    if block["index"] == 0:
        print(f"  Data          : {block['data']}")
    else:
        d = block["data"]
        print(f"  Transaction ID: {d['tx_id']}")
        print(f"  UID           : {d['uid']}")
        print(f"  VMID          : {d['vmid']}")
        print(f"  FID           : {d['fid']}")
        print(f"  Amount        : {d['amount']}")
        print(f"  Status        : {d['status']}")
        print(f"  Dispute Flag  : {d['dispute_flag']}")

    print(f"  Previous Hash : {block['prev_hash']}")
    print(f"  Current Hash  : {block['hash']}")

#STEP 9: Balances
balances = requests.get(f"{GRID_URL}/get_balances").json()

print("\n[STEP 9] Updated Balances:")
for uid, u in balances["users"].items():
    print(f"  User {u['name']}     : ₹{u['balance']}")
for fid_, f in balances["franchises"].items():
    print(f"  Franchise {f['name']}: ₹{f['balance']}")

#STEP 10: Quantum Demo
print("\n[STEP 10] Running Shor's Algorithm — Quantum Attack Demo...")
simulate_shor_attack(use_qiskit=True)

print("\n" + "="*60)
print("   Simulation complete.")
print("="*60)