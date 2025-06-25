import hashlib, datetime
from database import init_db
from utils import generate_otp, send_otp_via_email

conn = init_db()
c = conn.cursor()
otp_store = {}  # temp: username → otp

def make_hash(p): return hashlib.sha256(p.encode()).hexdigest()

def add_user(u, p, e, contact, is_admin=False):
    c.execute('SELECT * FROM users WHERE username=?', (u,))
    if c.fetchone(): raise ValueError("Username exists")
    role = 'admin' if is_admin else 'user'
    c.execute('INSERT INTO users VALUES (?,?,?,?,?,?)',
      (u, make_hash(p), e, contact, role, 0))
    conn.commit()
    otp = generate_otp(); otp_store[u] = otp
    send_otp_via_email(e, otp)

def verify_otp(u, otp):
    if otp_store.get(u) == otp:
        c.execute('UPDATE users SET is_verified=1 WHERE username=?', (u,))
        conn.commit()
        return True
    return False

def login(u, p):
    c.execute('SELECT password,is_verified FROM users WHERE username=?', (u,))
    res = c.fetchone()
    return res and res[0]==make_hash(p) and res[1]==1

def get_role(u):
    c.execute('SELECT role FROM users WHERE username=?', (u,))
    return c.fetchone()[0]

def save_file(u, fname):
    c.execute('INSERT INTO files(username,filename,uploaded_at) VALUES (?,?,?)',
              (u, fname, datetime.datetime.now().isoformat()))
    conn.commit()

def list_user_files(u):
    c.execute('SELECT filename, uploaded_at FROM files WHERE username=?', (u,))
    return c.fetchall()

def list_all_users(): return [row[0] for row in c.execute('SELECT username FROM users')]
