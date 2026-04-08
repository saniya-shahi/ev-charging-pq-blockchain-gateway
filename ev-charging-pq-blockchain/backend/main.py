from fastapi import FastAPI
from blockchain.blockchain import Blockchain
from crypto.sha3_hash import generate_id
from utils.helpers import generate_vmid
import hashlib
import time

app = FastAPI()
blockchain = Blockchain()

users = {}
franchises = {}

# REGISTER USER
@app.post("/register_user")
def register_user(name: str, password: str, mobile: str):
    uid = generate_id(name, password)
    vmid = generate_vmid(uid, mobile)

    users[uid] = {
        "name": name,
        "password": password,
        "vmid": vmid,
        "balance": 1000
    }

    print(f"[GRID] User Registered: {uid}")

    return {"UID": uid, "VMID": vmid}

# REGISTER FRANCHISE
@app.post("/register_franchise")
def register_franchise(name: str, password: str):
    fid = generate_id(name, password)

    franchises[fid] = {
        "name": name,
        "password": password,
        "balance": 0
    }

    print(f"[GRID] Franchise Registered: {fid}")

    return {"FID": fid}

# PROCESS TRANSACTION
@app.post("/process_transaction")
def process_transaction(vmid: str, pin: str, amount: int, fid: str):

    print("\n[GRID] Processing Transaction...")

    # Find user
    user = None
    for u in users.values():
        if u["vmid"] == vmid:
            user = u
            break

    if not user:
        print("[GRID] User not found")
        return {"status": "User not found"}

    if user["password"] != pin:
        print("[GRID] Invalid PIN")
        return {"status": "Invalid PIN"}

    if user["balance"] < amount:
        print("[GRID] Insufficient balance")
        return {"status": "Insufficient balance"}

    if fid not in franchises:
        print("[GRID] Invalid Franchise")
        return {"status": "Invalid Franchise"}

    print("[GRID] Validation successful")

    # Deduct + credit
    user["balance"] -= amount
    franchises[fid]["balance"] += amount

    print("[GRID] Balance updated")

    # 🔥 ADD TRANSACTION ID (IMPORTANT)
    tx_string = vmid + fid + str(amount) + str(time.time())
    tx_id = hashlib.sha3_256(tx_string.encode()).hexdigest()

    transaction_data = {
        "tx_id": tx_id,
        "vmid": vmid,
        "fid": fid,
        "amount": amount,
        "timestamp": time.time(),
        "status": "success"
    }

    blockchain.add_block(transaction_data)

    print("[BLOCKCHAIN] Block added")

    # OPTIONAL: simulate failure → refund
    failure = False

    if failure:
        print("[SYSTEM] Charging failed → refunding")

        user["balance"] += amount
        franchises[fid]["balance"] -= amount

        blockchain.add_block({
            "tx_id": tx_id + "_refund",
            "vmid": vmid,
            "fid": fid,
            "amount": -amount,
            "timestamp": time.time(),
            "status": "refund"
        })

        return {"status": "Charging Failed - Refunded"}

    return {"status": "Transaction Successful"}

# GET BLOCKCHAIN
@app.get("/get_blockchain")
def get_blockchain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "data": block.data,
            "prev_hash": block.prev_hash,
            "hash": block.hash
        })
    return chain_data