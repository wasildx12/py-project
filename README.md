# EcoCoin — Liquid Acrylic Edition

A Streamlit demo for recycling submissions, individual user wallets, rewards, and administrator review.

## Features
- Glassmorphism / acrylic UI with animated floating particles and responsive layout.
- User registration and login; passwords hashed with PBKDF2.
- Separate balances, submissions, and transaction histories by user ID.
- Waste submission and admin approval flow.
- Accepted materials: Plastic, Polythene, Rubber, Wood.
- Automobile and construction waste are rejected.

## Run on Windows
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m unittest discover -s tests -v
streamlit run app.py
```
Open http://localhost:8501.

## Default demo administrator
Username: `admin`
Password: `ChangeMe_EcoCoin_2026!`

**Change/remove demo administrator credentials before public deployment.** This is a prototype; do not use the default credentials on an exposed production app.

## Deploy
Upload project files to a GitHub repository, then deploy `app.py` with Streamlit Community Cloud. Add `requirements.txt` at the repository root.

## Production notes
This demo uses local SQLite. Hosted local files may be ephemeral and are not suitable as the sole database for a reliable public multi-user service. Use a managed persistent database (e.g. PostgreSQL), secure admin provisioning, rate limits, backups, and stronger session/security controls before real-world use. Collection-point management and real-world waste verification are not implemented in this starter.
