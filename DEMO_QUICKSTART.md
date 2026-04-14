# Multi-User Demo Quickstart

## Server machine (host IP: `172.16.46.192`)

1. Open PowerShell in project folder.
2. Run:
   - `.\run_server.ps1`
3. Keep this terminal open.
4. Make sure Windows firewall allows inbound TCP `8000` on private network.

## Client machine(s)

1. Copy this project folder to client machine (or open shared copy).
2. Open PowerShell in project folder.
3. Run:
   - `.\run_client.ps1 -ServerIp 172.16.46.192`
4. Alternative (double-click): `run_client.bat`

## Notes

- `run_client.ps1` auto-creates virtual environment (if missing), installs requirements, sets `GRID_URL`, and starts `main_flow.py`.
- `run_server.ps1` starts the backend with `--workers 1` to keep consistent in-memory state for this demo.
- All clients will share the same backend balances and blockchain while server is running.
