import json
import os
from concurrent.futures import ThreadPoolExecutor

import requests

from crypto.rsa_keys import PUBLIC_KEY
from crypto.rsa_sim import encrypt as rsa_encrypt

BASE_URL = os.getenv("GRID_URL", "http://127.0.0.1:8010")


def post(path: str, **params):
    return requests.post(f"{BASE_URL}{path}", params=params, timeout=10).json()


def get(path: str):
    return requests.get(f"{BASE_URL}{path}", timeout=10).json()


def send_tx(vmid: str, pin: str, amount: float, fid: str):
    encrypted_credential = rsa_encrypt(PUBLIC_KEY, json.dumps({"vmid": vmid, "pin": pin}))
    return post(
        "/process_transaction",
        encrypted_credential=encrypted_credential,
        amount=amount,
        fid=fid,
    )


results = []


def check(name: str, condition: bool, detail: str = ""):
    results.append((name, condition, detail))


def run():
    post("/admin/reset_state", confirm=True)
    post("/hardware_failure_mode", enabled=False)

    u1 = post("/register_user", name="Saniya", password="pass", mobile="9876543210", pin="1234", zone_code="TP-NORTH")
    check("register_user_valid", "UID" in u1 and "VMID" in u1, str(u1))

    u1_dup = post("/register_user", name="Saniya", password="pass", mobile="9876543210", pin="1234", zone_code="TP-NORTH")
    check("register_user_duplicate_idempotent", u1_dup.get("UID") == u1.get("UID"), str(u1_dup))

    u_mobile_dup = post("/register_user", name="Saniya2", password="pass2", mobile="9876543210", pin="0000", zone_code="TP-NORTH")
    check("register_user_duplicate_mobile_blocked", u_mobile_dup.get("UID") == u1.get("UID"), str(u_mobile_dup))

    u_bad_zone = post("/register_user", name="BadZone", password="pass", mobile="9000000000", pin="1234", zone_code="BAD")
    check("register_user_invalid_zone", "error" in u_bad_zone, str(u_bad_zone))

    fr1 = post("/register_franchise", name="Universal_Station", password="frpass", zone_code="TP-NORTH", initial_balance=100.0)
    check("register_franchise_valid", "FID" in fr1, str(fr1))

    fr1_dup = post("/register_franchise", name="Universal_Station", password="frpass", zone_code="TP-NORTH", initial_balance=100.0)
    check("register_franchise_duplicate_idempotent", fr1_dup.get("FID") == fr1.get("FID"), str(fr1_dup))

    fr_name_zone_dup = post("/register_franchise", name="universal_station", password="other", zone_code="TP-NORTH", initial_balance=0.0)
    check("register_franchise_duplicate_name_zone_blocked", fr_name_zone_dup.get("FID") == fr1.get("FID"), str(fr_name_zone_dup))

    fr_neg = post("/register_franchise", name="BadFr", password="x", zone_code="TP-NORTH", initial_balance=-1)
    check("register_franchise_negative_balance_rejected", "error" in fr_neg, str(fr_neg))

    invalid_amount = send_tx(u1["VMID"], "1234", 0, fr1["FID"])
    check("transaction_invalid_amount_rejected", invalid_amount.get("status") == "Invalid amount", str(invalid_amount))

    bad_pin = send_tx(u1["VMID"], "9999", 10, fr1["FID"])
    check("transaction_invalid_pin_rejected", bad_pin.get("status") == "Invalid PIN", str(bad_pin))

    bad_fid = send_tx(u1["VMID"], "1234", 10, "NOPE")
    check("transaction_invalid_fid_rejected", bad_fid.get("status") == "Invalid Franchise", str(bad_fid))

    insuff = send_tx(u1["VMID"], "1234", 5000, fr1["FID"])
    check("transaction_insufficient_balance_rejected", insuff.get("status") == "Insufficient balance", str(insuff))

    post("/admin/reset_state", confirm=True)
    post("/hardware_failure_mode", enabled=False)
    uc = post("/register_user", name="ConcU", password="pass", mobile="9000000001", pin="1111", zone_code="TP-NORTH")
    fc = post("/register_franchise", name="ConcF", password="fr", zone_code="TP-NORTH", initial_balance=0.0)
    start_bal = get("/get_balances")
    start_chain_len = len(get("/get_blockchain"))

    def tx_call():
        return send_tx(uc["VMID"], "1111", 100.0, fc["FID"]).get("status")

    with ThreadPoolExecutor(max_workers=20) as ex:
        statuses = list(ex.map(lambda _: tx_call(), range(20)))

    success_count = statuses.count("Transaction Successful")
    insuff_count = statuses.count("Insufficient balance")
    end_bal = get("/get_balances")
    end_chain_len = len(get("/get_blockchain"))
    user_end_balance = end_bal["users"][uc["UID"]]["balance"]
    fr_end_balance = end_bal["franchises"][fc["FID"]]["balance"]
    chain_delta = end_chain_len - start_chain_len
    check("concurrency_success_count", success_count == 10, f"success={success_count}, statuses={statuses}")
    check("concurrency_insufficient_count", insuff_count == 10, f"insufficient={insuff_count}, statuses={statuses}")
    check("concurrency_user_balance_consistent", user_end_balance == 0.0, f"user_balance={user_end_balance}")
    check("concurrency_franchise_balance_consistent", fr_end_balance == 1000.0, f"fr_balance={fr_end_balance}")
    check("concurrency_blockchain_append_count", chain_delta == 10, f"chain_delta={chain_delta}")

    post("/admin/reset_state", confirm=True)
    hu = post("/register_user", name="HwU", password="pass", mobile="9000000002", pin="2222", zone_code="TP-NORTH")
    hf = post("/register_franchise", name="HwF", password="fr", zone_code="TP-NORTH", initial_balance=0.0)
    post("/hardware_failure_mode", enabled=True)
    b_before = get("/get_balances")
    user_before = b_before["users"][hu["UID"]]["balance"]
    fr_before = b_before["franchises"][hf["FID"]]["balance"]
    c_before = len(get("/get_blockchain"))

    hw_res = send_tx(hu["VMID"], "2222", 50.0, hf["FID"])
    b_after = get("/get_balances")
    c_after = len(get("/get_blockchain"))
    user_after = b_after["users"][hu["UID"]]["balance"]
    fr_after = b_after["franchises"][hf["FID"]]["balance"]
    mode_state = get("/hardware_failure_mode").get("enabled")
    check("hardware_failure_mode_enabled", mode_state is True, f"enabled={mode_state}")
    check("hardware_failure_refund_status", hw_res.get("status") == "Charging Failed — Refunded", str(hw_res))
    check("hardware_failure_user_balance_rolled_back", user_before == user_after, f"{user_before} -> {user_after}")
    check("hardware_failure_fr_balance_rolled_back", fr_before == fr_after, f"{fr_before} -> {fr_after}")
    check("hardware_failure_chain_has_two_blocks", (c_after - c_before) == 2, f"chain_delta={c_after-c_before}")
    post("/hardware_failure_mode", enabled=False)

    passed = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]
    print(f"BASE_URL={BASE_URL}")
    print(f"PASSED={len(passed)} FAILED={len(failed)} TOTAL={len(results)}")
    for name, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        print(f"{status}: {name} :: {detail}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
