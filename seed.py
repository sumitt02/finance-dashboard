"""
seed.py — Populates the database with demo users and sample financial records.
Run with: python seed.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
import random
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.record import FinancialRecord
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)

DEMO_USERS = [
    {"name": "Alice Admin",   "email": "admin@demo.com",   "password": "admin123",   "role": "admin"},
    {"name": "Anna Analyst",  "email": "analyst@demo.com", "password": "analyst123", "role": "analyst"},
    {"name": "Victor Viewer", "email": "viewer@demo.com",  "password": "viewer123",  "role": "viewer"},
]

CATEGORIES = {
    "income":  ["Salary", "Freelance", "Investment", "Bonus", "Rental Income"],
    "expense": ["Rent", "Groceries", "Utilities", "Travel", "Entertainment", "Healthcare", "Subscriptions"],
}

NOTES = [
    "Monthly payment", "One-time expense", "Recurring cost",
    "Q1 settlement", "Reimbursed later", None, None
]

def random_date_in_last_6_months() -> date:
    today = date.today()
    days_ago = random.randint(0, 180)
    return today - timedelta(days=days_ago)

def seed():
    db = SessionLocal()

    try:
        # ── Clear existing data ──────────────────────────────────────────
        db.query(FinancialRecord).delete()
        db.query(User).delete()
        db.commit()

        # ── Seed users ───────────────────────────────────────────────────
        created_users = []
        for u in DEMO_USERS:
            user = User(
                name=u["name"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
                is_active=True
            )
            db.add(user)
            db.flush()   # get the id before commit
            created_users.append(user)

        db.commit()

        admin_user = created_users[0]

        # ── Seed financial records ────────────────────────────────────────
        records = []
        for _ in range(25):
            rec_type = random.choice(["income", "expense"])
            category = random.choice(CATEGORIES[rec_type])
            amount   = round(random.uniform(100, 5000), 2)
            records.append(FinancialRecord(
                amount=amount,
                type=rec_type,
                category=category,
                date=random_date_in_last_6_months(),
                notes=random.choice(NOTES),
                created_by=admin_user.id
            ))

        db.add_all(records)
        db.commit()

        # ── Print credentials ─────────────────────────────────────────────
        print("\n✅ Seeding complete!\n")
        print("=" * 48)
        print(f"{'Role':<10} {'Email':<25} {'Password'}")
        print("-" * 48)
        for u in DEMO_USERS:
            print(f"{u['role']:<10} {u['email']:<25} {u['password']}")
        print("=" * 48)
        print(f"\n📊 {len(records)} financial records inserted.")
        print("🚀 Start the server: uvicorn main:app --reload")
        print("📖 Swagger docs:     http://127.0.0.1:8000/docs\n")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
