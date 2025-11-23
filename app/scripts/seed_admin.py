from database import SessionLocal
from models import User
import auth_utils

def seed_admin(username: str = "admin", password: str = "Admin@123", email: str = "admin@example.com", phone_number: str = "0000000000"):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print("Admin user already exists.")
            return
        hashed = auth_utils.hash_password(password)
        admin = User(username=username, email=email, phone_number=phone_number, hashed_password=hashed, role="admin")
        db.add(admin)
        db.commit()
        print(f"Created admin user '{username}'.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
