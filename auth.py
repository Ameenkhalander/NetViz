"""Small local authentication helpers for NetViz. Use HTTPS and a managed auth provider for production."""
import hashlib, hmac, os, uuid
from sqlalchemy import func
from database import SessionLocal
from models import User

ITERATIONS=600_000

def hash_password(password: str) -> str:
    salt=os.urandom(16)
    digest=hashlib.pbkdf2_hmac("sha256",password.encode("utf-8"),salt,ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest.hex()}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm,iterations,salt_hex,digest_hex=encoded.split("$")
        if algorithm!="pbkdf2_sha256": return False
        candidate=hashlib.pbkdf2_hmac("sha256",password.encode("utf-8"),bytes.fromhex(salt_hex),int(iterations)).hex()
        return hmac.compare_digest(candidate,digest_hex)
    except (ValueError,TypeError):
        return False

def register_user(username: str,email: str,password: str):
    username=username.strip(); email=email.strip().lower()
    if len(username)<3 or len(username)>40: return None,"Username must be 3–40 characters."
    if not email or "@" not in email or len(email)>254: return None,"Enter a valid email address."
    if len(password)<10: return None,"Use a password with at least 10 characters."
    with SessionLocal() as db:
        if db.query(User).filter(func.lower(User.username)==username.lower()).first(): return None,"That username is already taken."
        if db.query(User).filter(func.lower(User.email)==email).first(): return None,"An account already uses that email."
        user=User(id=str(uuid.uuid4()),username=username,email=email,password_hash=hash_password(password),is_guest=False)
        db.add(user); db.commit(); return user,"Account created. You are signed in."

def authenticate(email: str,password: str):
    with SessionLocal() as db:
        user=db.query(User).filter(func.lower(User.email)==email.strip().lower(),User.is_guest.is_(False)).first()
        if user and verify_password(password,user.password_hash): return user
    return None
