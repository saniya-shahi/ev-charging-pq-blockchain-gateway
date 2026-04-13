"""
main_flow.py — Full EV Charging Payment Gateway Simulation
===========================================================
Runs the complete end-to-end flow:
  1. Register a user and a franchise under grid zones
  2. Kiosk generates ASCON-encrypted QR code
  3. User encrypts credentials with RSA and sends transaction
  4. Grid validates, records on blockchain
  5. Shor's algorithm demonstrates RSA vulnerability
  6. Blockchain integrity is verified
"""

import requests
from kiosk.kiosk import create_qr, process_scan
from user.user_app import get_user_input, send_transaction
from crypto.qiskit_shor import simulate_shor_attack

GRID_URL = "http://127.0.0.1:8000"

print("\n" + "="*60)
print("   EV Charging Payment Gateway — Full Simulation")
print("="*60)

#STEP 0: Show available grid zones
grid_info = requests.get(f"{GRID_URL}/grid_info").json()
print("\n[GRID] Available providers and zones:")
for provider, data in grid_info.items():
    print(f"  {provider}: {data['zones']}")

#STEP 1: Register User
user_res = requests.post(
    f"{GRID_URL}/register_user",
    params={
        "name":      "Saniya",
        "password":  "securepass",   # registration password
        "mobile":    "9876543210",
        "pin":       "1234",          # separate PIN for authorizing charges
        "zone_code": "TP-NORTH",
    }
)
user_data = user_res.json()
vmid      = user_data["VMID"]
print(f"\n[STEP 1] User Registered:")
print(f"  UID       : {user_data['UID']}")
print(f"  VMID      : {vmid}")
print(f"  Zone      : {user_data['zone_code']}")

#STEP 2: Register Franchise
fr_res = requests.post(
    f"{GRID_URL}/register_franchise",
    params={
        "name":            "TataPower_Station_01",
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

#STEP 3: Kiosk generates ASCON-encrypted QR code
print("\n[STEP 3] Kiosk generating ASCON-encrypted QR code...")
encrypted_qr_data = create_qr(fid)
print(f"  Encrypted QR data: {encrypted_qr_data[:60]}...")

#STEP 4: User scans QR and enters payment details
print("\n[STEP 4] User scanning QR and entering payment details...")
vmid_input, pin, amount = get_user_input()

#STEP 5: Kiosk decodes QR to recover FID
decoded_fid = process_scan(encrypted_qr_data)
if not decoded_fid:
    print("\n[ERROR] QR decode failed — aborting.")
    exit(1)
print(f"\n[STEP 5] Kiosk decoded FID: {decoded_fid}")

#STEP 6: Send transaction (with RSA-encrypted credentials)
print("\n[STEP 6] Sending transaction with RSA-encrypted credentials...")
result = send_transaction(vmid_input, pin, amount, decoded_fid)
print(f"\n  Transaction Result: {result['status']}")

#STEP 7: Display blockchain
bc_res = requests.get(f"{GRID_URL}/get_blockchain").json()
print("\n[STEP 7] Blockchain Ledger:")
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

#STEP 8: Check blockchain integrity
integrity = requests.get(f"{GRID_URL}/get_blockchain").json()
print(f"\n[STEP 8] Blockchain integrity: chain has {len(integrity)} block(s) — validated via prev_hash chain.")

#STEP 9: Show balances
balances = requests.get(f"{GRID_URL}/get_balances").json()
print("\n[STEP 9] Updated Balances:")
for uid, u in balances["users"].items():
    print(f"  User {u['name']}     : ₹{u['balance']}")
for fid_, f in balances["franchises"].items():
    print(f"  Franchise {f['name']}: ₹{f['balance']}")

#STEP 10: Quantum attack demo
print("\n[STEP 10] Running Shor's Algorithm — Quantum Attack Demo...")
simulate_shor_attack(use_qiskit=True)

print("\n" + "="*60)
print("   Simulation complete.")
print("="*60)