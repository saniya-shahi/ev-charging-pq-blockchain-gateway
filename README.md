# Secure Centralized EV Charging Payment Gateway
## BITS F463 Cryptography — Term Project 2025-26

---

## 1. Team Members

- **Saniya Shahi** — 2022A8PS0810H
- **Kumar Shivansh Sinha** — 2022B1AA1227H
- **Surbhit Jain** — 2022B3A70868H
- **Rickpoul Ghosh** — 2022AAPS1549H
- **Gaurvi Khurana** — 2023A7PS0035H

---

## 2. Abstract

This project implements a secure, centralized EV charging payment gateway simulation that combines modern cryptographic primitives with a blockchain-backed audit trail. The system supports multi-user concurrent transactions across multiple client machines connected to a single grid authority server. It demonstrates:

- lightweight cryptography for kiosk QR payloads,
- public-key encryption for credential transmission,
- blockchain immutability for transaction logging,
- and a quantum-risk demonstration for RSA via Shor's algorithm simulation.

---

## 3. Objectives

- Build an end-to-end EV charging payment flow with clear system roles.
- Integrate cryptographic mechanisms from the course syllabus in one practical workflow.
- Provide tamper-evident transaction recording.
- Simulate realistic operational and failure edge cases.
- Support LAN-based multi-user demonstration.

---

## 4. System Roles and Scope

| Role | Responsibility |
|---|---|
| Grid Authority (Backend) | Registers entities, validates credentials, processes payments, updates balances, appends blockchain blocks |
| EV Owner (User) | Initiates payment using VMID + PIN + amount |
| Charging Kiosk | Generates and scans encrypted QR payload containing franchise identity |
| Franchise | Receives payment for charging services |

**Scope note:** This is a controlled academic simulation; account deletion and production-grade persistence are intentionally out of scope.

---

## 5. Cryptographic Design

### 5.1 ASCON-128 (Lightweight Cryptography)
- Used for encrypting franchise data in QR flow.
- Nonce-based encryption with nonce bundled for decryption.

### 5.2 RSA (Credential Protection)
- User VMID and PIN are encrypted before network transfer.
- Backend decrypts and validates credentials.

### 5.3 SHA3-256 (Identity + Blockchain)
- Used for deterministic identity and transaction hashing.
- Blockchain block hash and transaction identifiers rely on SHA3-256.

### 5.4 Quantum Security Demonstration
- Shor's algorithm simulation illustrates RSA vulnerability under quantum computing assumptions.

---

## 6. Blockchain Design

- Genesis block created at startup.
- Each successful payment appends a new block.
- Block linkage via `prev_hash`.
- Block hash computed on canonicalized data representation.
- Refund/reversal transactions are recorded as explicit blocks with `dispute_flag=True`.

---

## 7. Multi-User Reliability Improvements (Implemented)

The following improvements were added to make the project demo-safe for simultaneous users:

- Thread-safe lock over shared in-memory state (`users`, `franchises`, blockchain append).
- Atomic transaction critical section (validate + debit/credit + block append).
- Duplicate user protection by mobile number.
- Duplicate franchise protection by normalized `(name, zone)` identity.
- Input validation:
  - invalid amount (`<= 0`) rejected,
  - negative initial franchise balance rejected,
  - invalid zone rejected.
- Consistent snapshot reads via protected balance/blockchain endpoints.
- Graceful `Ctrl+C` exit in kiosk loop.

---

## 8. Hardware Failure Simulation (Implemented)

A runtime toggle is available to simulate charging hardware failure after payment:

- UI option: `9) Toggle hardware failure simulation`
- Backend endpoints:
  - `GET /hardware_failure_mode`
  - `POST /hardware_failure_mode?enabled=true|false`

When enabled, the backend:
1. Processes transaction,
2. Applies reversal,
3. Appends refund block (`dispute_flag=True`),
4. Returns `Charging Failed — Refunded`.

---

## 9. Repository Structure

```text
ev-charging-gateway/
├── backend/
│   └── main.py
├── blockchain/
│   ├── block.py
│   └── blockchain.py
├── crypto/
│   ├── ascon.py
│   ├── rsa_sim.py
│   ├── qiskit_shor.py
│   └── sha3_hash.py
├── kiosk/
│   └── kiosk.py
├── user/
│   └── user_app.py
├── utils/
│   ├── helpers.py
│   └── qr.py
├── main_flow.py
├── edge_case_tests.py
├── run_server.ps1
├── run_client.ps1
├── run_client.bat
└── requirements.txt
```

---

## 10. Environment and Dependency Setup (From Scratch)

### 10.1 Prerequisites
- Windows + PowerShell
- Python `3.10+`
- LAN connectivity between server and clients

Check Python:

```powershell
python --version
```

### 10.2 Create Virtual Environment

From project root:

```powershell
python -m venv evcrypto_env
```

### 10.3 Activate Virtual Environment

```powershell
.\evcrypto_env\Scripts\Activate.ps1
```

If execution policy blocks scripts:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\evcrypto_env\Scripts\Activate.ps1
```

### 10.4 Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 11. How To Run the System

## 11.1 Recommended Script-Based Run

### Server machine (host)

```powershell
.\run_server.ps1
```

### Client machine(s)

```powershell
.\run_client.ps1 -ServerIp 172.16.46.192
```

Alternative for clients:
- double-click `run_client.bat`

## 11.2 Manual Run

### Server

```powershell
.\evcrypto_env\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1
```

### Clients

```powershell
.\evcrypto_env\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GRID_URL="http://172.16.46.192:8000"
python main_flow.py
```

---

## 12. Network Configuration for Demo

- Ensure all machines are on the same LAN.
- On the server machine, allow inbound TCP `8000`.
- Verify reachability from client browser:
  - `http://172.16.46.192:8000/grid_info`

---

## 13. Demo Procedure for Evaluation

1. Start server on host machine.
2. Start `main_flow.py` on 2+ client systems.
3. In one client:
   - register default users (`1`),
   - register default franchise (`2`).
4. Perform transactions from different client systems (`4`).
5. Display shared balances (`6`) and blockchain ledger (`5`) from any client.
6. Enable hardware failure simulation (`9`) and run one transaction to show automated refund logic.

This sequence demonstrates consistency, concurrency handling, and fault-path recovery.

---

## 14. Test and Validation

Automated edge-case suite:

```powershell
python edge_case_tests.py
```

Validated scenarios include:
- duplicate registration and idempotency,
- invalid input rejection,
- invalid PIN/FID handling,
- insufficient balance,
- concurrent transaction correctness,
- hardware-failure rollback and refund block generation.

Observed result in current build: **22/22 tests passed**.

---

## 15. API Endpoints (Core)

### Operational
- `GET /grid_info`
- `POST /register_user`
- `POST /register_franchise`
- `POST /process_transaction`
- `GET /get_balances`
- `GET /get_blockchain`

### Simulation/Testing
- `GET /hardware_failure_mode`
- `POST /hardware_failure_mode?enabled=true|false`
- `POST /admin/reset_state?confirm=true`

---

## 16. Design Assumptions

- Backend state is maintained in memory for classroom demo simplicity.
- Single backend worker (`--workers 1`) is used to preserve in-memory consistency.
- Password is used for UID derivation; transaction authorization uses PIN.
- VMID format: UID prefix + full mobile number.

---

## 17. Limitations and Future Enhancements

Current limitations:
- No persistent database; state resets when server restarts.
- No role-based authentication layer for admin endpoints.
- No account deletion/closure workflow.

Potential enhancements:
- migrate to SQLite/PostgreSQL persistence,
- add JWT/session authentication,
- add audit dashboard and structured logging,
- introduce rate limiting and stronger API validation.

---

## 18. Troubleshooting

- **Client cannot connect**
  - confirm server is running,
  - confirm firewall rule on port `8000`,
  - confirm correct `ServerIp` in client command.
- **Changes not reflected**
  - restart backend server.
- **Dependency/module errors**
  - reactivate venv and run `pip install -r requirements.txt`.

---

## 19. Windows Path-Length Issue (WinError 206)

On some Windows laptops, client startup may fail with:

- `WinError 206: The filename or extension is too long`

This is typically triggered when loading native `pycryptodome` binaries from a very deep project path (especially inside cloud-sync folders like OneDrive).

### 19.1 Reliable Demo Fix (Recommended)

Run the client from a short path such as `C:\evdemo`.

```powershell
New-Item -ItemType Directory -Force C:\evdemo | Out-Null
robocopy "C:\Users\shiva\OneDrive\Documents\projects\ev-charging-pq-blockchain-gateway-pr-kiosk-clean (2)\ev-charging-pq-blockchain-gateway-pr-kiosk-clean\ev-charging-pq-blockchain-gateway-pr-kiosk-clean" "C:\evdemo" /E
cd C:\evdemo
.\run_client.bat -ServerIp 172.16.46.192
```

### 19.2 Faster Alternative (No Full Copy)

Map a short drive letter to the long project path:

```powershell
subst X: "C:\Users\shiva\OneDrive\Documents\projects\ev-charging-pq-blockchain-gateway-pr-kiosk-clean (2)\ev-charging-pq-blockchain-gateway-pr-kiosk-clean\ev-charging-pq-blockchain-gateway-pr-kiosk-clean"
cd X:\
.\run_client.bat -ServerIp 172.16.46.192
```

If the error persists, recreate virtual environment from short path:

```powershell
Remove-Item -Recurse -Force .\evcrypto_env
.\run_client.bat -ServerIp 172.16.46.192
```

### 19.3 Live Demo Checklist with This Issue

1. Host machine keeps `.\run_server.ps1` running.
2. Host firewall allows inbound TCP `8000` (private network).
3. Client machine runs from short path (`C:\evdemo` or `X:\`).
4. Run app flow: `1 -> 2 -> 4 (multi-clients) -> 6 -> 5 -> 9 + 4`.
