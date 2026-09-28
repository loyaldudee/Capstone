"""
Database Configuration & Seeding Engine
----------------------------------------
Manages database connection, engine lifecycle, session injection,
and automatic table creation/seeding from processed data files.
"""

import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Customer, Claim, InvestigationRecord, AdjusterDecision

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SQLITE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'insurance.db')}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)

# Configure engine
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initializes tables and seeds initial clean records if empty."""
    Base.metadata.create_all(bind=engine)
    # Safe migration for new columns
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE investigation_records ADD COLUMN advisor_guidance TEXT"))
            conn.commit()
    except Exception:
        pass
    db = SessionLocal()

    try:
        claim_count = db.query(Claim).count()
        if claim_count == 0:
            print("[Database] Empty database detected. Auto-seeding from processed_data...")
            customers_path = os.path.join(BASE_DIR, "task1_data_preparation", "processed_data", "customers_clean.csv")
            claims_path = os.path.join(BASE_DIR, "task1_data_preparation", "processed_data", "claims_knowledge_base.csv")

            if os.path.exists(customers_path) and os.path.exists(claims_path):
                # Seed Customers
                df_cust = pd.read_csv(customers_path)
                customers_to_add = []
                for _, r in df_cust.iterrows():
                    customers_to_add.append(
                        Customer(
                            customer_id=str(r["customer_id"]),
                            customer_subtype=str(r.get("customer_subtype_desc", "")),
                            customer_main_type=str(r.get("customer_main_type_desc", "")),
                            age_group=str(r.get("age_group_desc", "")),
                            purchasing_power_class=int(r.get("MKOOPKLA", 5)),
                            total_policies_count=int(r.get("total_policies_count", 0)),
                            active_product_lines_count=int(r.get("active_product_lines_count", 0)),
                            has_car_policy=bool(r.get("has_car_policy", False)),
                            has_fire_policy=bool(r.get("has_fire_policy", False)),
                            has_boat_policy=bool(r.get("has_boat_policy", False)),
                            has_life_policy=bool(r.get("has_life_policy", False)),
                            has_accident_policy=bool(r.get("has_accident_policy", False))
                        )
                    )
                db.bulk_save_objects(customers_to_add)
                db.commit()
                print(f"[Database] Seeded {len(customers_to_add):,} customers.")

                # Seed Claims
                df_claims = pd.read_csv(claims_path)
                claims_to_add = []
                for _, r in df_claims.iterrows():
                    claims_to_add.append(
                        Claim(
                            claim_id=str(r["claim_id"]),
                            customer_id=str(r["customer_id"]),
                            policy_type=str(r["policy_type"]),
                            policy_count=int(r["policy_count"]),
                            policy_contribution_tier=int(r["policy_contribution_tier"]),
                            purchasing_power_class=int(r["purchasing_power_class"]),
                            claim_amount=float(r["claim_amount"]),
                            incident_type=str(r["incident_type"]),
                            incident_severity=str(r["incident_severity"]),
                            incident_date=str(r["incident_date"]),
                            claim_date=str(r["claim_date"]),
                            reporting_delay_days=int(r["reporting_delay_days"]),
                            police_report_filed=str(r["police_report_filed"]),
                            witness_present=str(r["witness_present"]),
                            prior_claims_count=int(r["prior_claims_count"]),
                            incident_description=str(r["incident_description"]),
                            claim_status="Pending Review"
                        )
                    )
                db.bulk_save_objects(claims_to_add)
                db.commit()
                print(f"[Database] Seeded {len(claims_to_add):,} claims.")
        else:
            print(f"[Database] Database already initialized ({claim_count:,} claims on record).")

    except Exception as e:
        db.rollback()
        print(f"[Database] Seeding error: {e}")
    finally:
        db.close()


def get_db():
    """Dependency helper for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
