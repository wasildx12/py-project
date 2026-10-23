import os, sqlite3, hashlib, secrets
from datetime import datetime, timezone
from config import WASTE_RATES, REJECTED_TYPES

DB_PATH = os.environ.get("ECOCOIN_DB_PATH", "ecocoin.db")

def connect():
    con=sqlite3.connect(DB_PATH, timeout=20)
    con.row_factory=sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def hash_password(password, salt=None):
    salt=salt or secrets.token_hex(16)
    digest=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),200000).hex()
    return salt,digest

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, username TEXT NOT NULL UNIQUE,
          salt TEXT NOT NULL, password_hash TEXT NOT NULL, is_admin INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS submissions(
          id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id),
          material TEXT NOT NULL, weight_kg REAL NOT NULL, notes TEXT, estimated_coins REAL NOT NULL,
          status TEXT NOT NULL DEFAULT 'Pending', created_at TEXT NOT NULL,
          reviewed_at TEXT, reviewed_by INTEGER REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS transactions(
          id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id),
          submission_id INTEGER REFERENCES submissions(id), amount REAL NOT NULL,
          description TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_submissions_user ON submissions(user_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
        """)
        # Admin is provisioned only when no admin exists. Change these demo credentials before deployment.
        admins=c.execute("SELECT COUNT(*) AS n FROM users WHERE is_admin=1").fetchone()["n"]
        if admins==0:
            salt,digest=hash_password("ChangeMe_EcoCoin_2026!")
            c.execute("INSERT OR IGNORE INTO users(name,username,salt,password_hash,is_admin,created_at) VALUES(?,?,?,?,1,?)",
                      ("EcoCoin Administrator","admin",salt,digest,datetime.now(timezone.utc).isoformat()))

def create_user(name, username, password):
    salt,digest=hash_password(password)
    try:
        with connect() as c:
            c.execute("INSERT INTO users(name,username,salt,password_hash,created_at) VALUES(?,?,?,?,?)",
                      (name,username,salt,digest,datetime.now(timezone.utc).isoformat()))
        return True,"Account created"
    except sqlite3.IntegrityError:
        return False,"That username is already taken."

def authenticate(username,password):
    with connect() as c:
        row=c.execute("SELECT * FROM users WHERE username=?",(username,)).fetchone()
    if not row: return None
    _,digest=hash_password(password,row["salt"])
    if secrets.compare_digest(digest,row["password_hash"]):
        return dict(row)
    return None

def get_user(user_id):
    with connect() as c:
        r=c.execute("SELECT * FROM users WHERE id=?",(user_id,)).fetchone()
    return dict(r) if r else None

def submit_waste(user_id,material,weight,notes,estimate):
    if material in REJECTED_TYPES: raise ValueError("This material is not accepted")
    if weight<=0 or weight>1000: raise ValueError("Weight out of range")
    with connect() as c:
        c.execute("INSERT INTO submissions(user_id,material,weight_kg,notes,estimated_coins,status,created_at) VALUES(?,?,?,?,?,'Pending',?)",
                  (user_id,material,weight,notes,estimate,datetime.now(timezone.utc).isoformat()))

def get_user_submissions(user_id):
    with connect() as c:
        rows=c.execute("SELECT material AS Material,weight_kg AS 'Weight (kg)',estimated_coins AS 'Estimated EcoCoins',status AS Status,created_at AS Submitted FROM submissions WHERE user_id=? ORDER BY id DESC",(user_id,)).fetchall()
    return [dict(r) for r in rows]

def get_wallet(user_id):
    with connect() as c:
        earned=c.execute("SELECT COALESCE(SUM(amount),0) n FROM transactions WHERE user_id=? AND amount>0",(user_id,)).fetchone()["n"]
        balance=c.execute("SELECT COALESCE(SUM(amount),0) n FROM transactions WHERE user_id=?",(user_id,)).fetchone()["n"]
        pending=c.execute("SELECT COALESCE(SUM(estimated_coins),0) n FROM submissions WHERE user_id=? AND status='Pending'",(user_id,)).fetchone()["n"]
    return {"balance":float(balance),"earned":float(earned),"pending":float(pending)}

def get_transactions(user_id,limit=None):
    sql="SELECT description AS Description,amount AS 'EcoCoins',created_at AS Date FROM transactions WHERE user_id=? ORDER BY id DESC"
    params=[user_id]
    if limit:
        sql+=" LIMIT ?";params.append(limit)
    with connect() as c: rows=c.execute(sql,params).fetchall()
    return [dict(r) for r in rows]

def get_stats(user_id):
    with connect() as c:
        total=c.execute("SELECT COUNT(*) n FROM submissions WHERE user_id=?",(user_id,)).fetchone()["n"]
        approved=c.execute("SELECT COUNT(*) n FROM submissions WHERE user_id=? AND status='Approved'",(user_id,)).fetchone()["n"]
        pending=c.execute("SELECT COUNT(*) n FROM submissions WHERE user_id=? AND status='Pending'",(user_id,)).fetchone()["n"]
    return {"total":total,"approved":approved,"pending":pending}

def get_pending_submissions():
    with connect() as c:
        rows=c.execute("""SELECT s.*,u.name,u.username FROM submissions s JOIN users u ON u.id=s.user_id
                          WHERE s.status='Pending' ORDER BY s.id""").fetchall()
    return [dict(r) for r in rows]

def review_submission(submission_id,admin_id,approve):
    with connect() as c:
        c.execute("BEGIN IMMEDIATE")
        row=c.execute("SELECT * FROM submissions WHERE id=?",(submission_id,)).fetchone()
        if not row or row["status"]!="Pending": return False
        status="Approved" if approve else "Rejected"
        now=datetime.now(timezone.utc).isoformat()
        c.execute("UPDATE submissions SET status=?,reviewed_at=?,reviewed_by=? WHERE id=? AND status='Pending'",(status,now,admin_id,submission_id))
        if approve:
            amount=float(row["estimated_coins"])
            c.execute("INSERT INTO transactions(user_id,submission_id,amount,description,created_at) VALUES(?,?,?,?,?)",
                      (row["user_id"],submission_id,amount,f"Approved {row['material']} recycling ({row['weight_kg']} kg)",now))
        return True

def get_all_users():
    with connect() as c:
        rows=c.execute("""SELECT username AS Username,name AS Name,created_at AS 'Joined' FROM users ORDER BY id""").fetchall()
    return [dict(r) for r in rows]
