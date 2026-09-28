"""
Data Sanitizer & Cleaning Module
--------------------------------
Ingestion sanitation pipeline that standardizes, cleans, and coerces messy incoming
raw claim data before inserting into SQLAlchemy RDBMS and ChromaDB Vector Store.
"""

import re
import random
from datetime import datetime
from typing import Dict, Any, Tuple, Optional


# Standard Policy Lines supported by Aegis actuarial models
VALID_POLICY_TYPES = ["Auto", "Fire_Property", "Boat_Marine", "Life_Health", "Accident_Liability"]
POLICY_TYPE_MAP = {
    "auto": "Auto",
    "car": "Auto",
    "vehicle": "Auto",
    "automobile": "Auto",
    "motor": "Auto",
    "fire": "Fire_Property",
    "property": "Fire_Property",
    "home": "Fire_Property",
    "house": "Fire_Property",
    "fire_property": "Fire_Property",
    "boat": "Boat_Marine",
    "marine": "Boat_Marine",
    "yacht": "Boat_Marine",
    "boat_marine": "Boat_Marine",
    "life": "Life_Health",
    "health": "Life_Health",
    "medical": "Life_Health",
    "life_health": "Life_Health",
    "accident": "Accident_Liability",
    "liability": "Accident_Liability",
    "casualty": "Accident_Liability",
    "accident_liability": "Accident_Liability"
}

VALID_INCIDENT_TYPES = ["Collision", "Theft", "Water Damage", "Fire", "Vandalism", "Medical Emergency", "Other"]
VALID_SEVERITIES = ["Minor", "Moderate", "Severe", "Catastrophic"]


class DataSanitizer:
    @staticmethod
    def clean_claim_payload(raw_data: Dict[str, Any], next_claim_num: Optional[int] = None) -> Dict[str, Any]:
        """
        Sanitizes a raw claim payload into a clean, model-ready dictionary.
        Coerces numeric fields, maps messy categories, imputes missing defaults,
        and ensures standard formatting.
        """
        cleaned = {}

        # 1. Claim ID
        cid = str(raw_data.get("claim_id", "")).strip().upper()
        if not cid or cid == "NONE" or cid == "NULL":
            num = next_claim_num or random.randint(10000, 99999)
            cid = f"CLM-INGEST-{num:05d}"
        cleaned["claim_id"] = cid

        # 2. Customer ID
        cust_id = str(raw_data.get("customer_id", "")).strip().upper()
        if not cust_id or cust_id == "NONE" or cust_id == "NULL":
            cust_id = f"CUST_{random.randint(1000, 9999):05d}"
        cleaned["customer_id"] = cust_id

        # 3. Policy Type Mapping
        raw_policy = str(raw_data.get("policy_type", "Auto")).strip().lower()
        cleaned["policy_type"] = POLICY_TYPE_MAP.get(raw_policy, "Auto")

        # 4. Numeric Coercions
        cleaned["claim_amount"] = DataSanitizer._coerce_float(raw_data.get("claim_amount"), default=3500.0)
        cleaned["policy_count"] = DataSanitizer._coerce_int(raw_data.get("policy_count"), default=1)
        cleaned["policy_contribution_tier"] = DataSanitizer._coerce_int(raw_data.get("policy_contribution_tier"), default=3)
        cleaned["purchasing_power_class"] = DataSanitizer._coerce_int(raw_data.get("purchasing_power_class"), default=5)
        cleaned["reporting_delay_days"] = max(0, DataSanitizer._coerce_int(raw_data.get("reporting_delay_days"), default=0))
        cleaned["prior_claims_count"] = max(0, DataSanitizer._coerce_int(raw_data.get("prior_claims_count"), default=0))

        # 5. Incident Attributes
        raw_inc_type = str(raw_data.get("incident_type", "Collision")).strip().title()
        cleaned["incident_type"] = raw_inc_type if raw_inc_type in VALID_INCIDENT_TYPES else "Collision"

        raw_sev = str(raw_data.get("incident_severity", "Moderate")).strip().title()
        cleaned["incident_severity"] = raw_sev if raw_sev in VALID_SEVERITIES else "Moderate"

        # 6. Binary Flags ("Yes" / "No")
        cleaned["police_report_filed"] = DataSanitizer._coerce_yes_no(raw_data.get("police_report_filed"), default="No")
        cleaned["witness_present"] = DataSanitizer._coerce_yes_no(raw_data.get("witness_present"), default="No")

        # 7. Dates
        today_str = datetime.now().strftime("%Y-%m-%d")
        cleaned["incident_date"] = DataSanitizer._coerce_date(raw_data.get("incident_date"), default=today_str)
        cleaned["claim_date"] = DataSanitizer._coerce_date(raw_data.get("claim_date"), default=today_str)

        # 8. Text Narrative
        desc = str(raw_data.get("incident_description", "")).strip()
        if not desc or len(desc) < 5:
            desc = f"{cleaned['incident_severity']} {cleaned['incident_type']} incident reported for policy line {cleaned['policy_type']}."
        cleaned["incident_description"] = desc

        cleaned["claim_status"] = "Pending Review"
        return cleaned

    @staticmethod
    def _coerce_float(val: Any, default: float = 0.0) -> float:
        if val is None:
            return default
        try:
            # Strip currency symbols and commas
            cleaned_str = re.sub(r"[^\d.-]", "", str(val))
            return round(float(cleaned_str), 2)
        except Exception:
            return default

    @staticmethod
    def _coerce_int(val: Any, default: int = 0) -> int:
        if val is None:
            return default
        try:
            cleaned_str = re.sub(r"[^\d-]", "", str(val))
            return int(float(cleaned_str))
        except Exception:
            return default

    @staticmethod
    def _coerce_yes_no(val: Any, default: str = "No") -> str:
        if val is None:
            return default
        s = str(val).strip().lower()
        if s in ["yes", "true", "y", "1"]:
            return "Yes"
        if s in ["no", "false", "n", "0"]:
            return "No"
        return default

    @staticmethod
    def _coerce_date(val: Any, default: str) -> str:
        if not val:
            return default
        s = str(val).strip()
        # Check standard format YYYY-MM-DD
        if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
            return s
        try:
            parsed = datetime.strptime(s[:10], "%Y-%m-%d")
            return parsed.strftime("%Y-%m-%d")
        except Exception:
            return default
