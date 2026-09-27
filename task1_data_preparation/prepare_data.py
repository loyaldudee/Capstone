"""
Data Pipeline and Cleaning Script for AI-Powered Insurance Claims Intelligence Assistant
----------------------------------------------------------------------------------------
This script implements strict separation between:
1. Observable Input Features (available to models and agents at inference time)
2. Held-out Ground Truth Evaluation Labels (used ONLY in Task 4 evaluation benchmarks)

Outputs in 'processed_data/':
- customers_clean.csv: 9,822 customer demographic & policy records with decoded features.
- claims_knowledge_base.csv: 1,800 operational claims containing ONLY observable features (no leakage).
- claims_ground_truth.csv: Held-out ground truth evaluation targets and synthetic reference reasons.
- data_dictionary.json: Schema and metadata documentation.
"""

import os
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set random seeds for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "insurance+company+benchmark+coil+2000")
OUTPUT_DIR = os.path.join(BASE_DIR, "processed_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------------------
# 1. ATTRIBUTE DEFINITIONS & CATEGORICAL DICTIONARIES (COIL 2000)
# -------------------------------------------------------------------------

COLUMN_NAMES = [
    "MOSTYPE", "MAANTHUI", "MGEMOMV", "MGEMLEEF", "MOSHOOFD", "MGODRK", "MGODPR", "MGODOV", "MGODGE",
    "MRELGE", "MRELSA", "MRELOV", "MFALLEEN", "MFGEKIND", "MFWEKIND", "MOPLHOOG", "MOPLMIDD", "MOPLLAAG",
    "MBERHOOG", "MBERZELF", "MBERBOER", "MBERMIDD", "MBERARBG", "MBERARBO", "MSKA", "MSKB1", "MSKB2",
    "MSKC", "MSKD", "MHHUUR", "MHKOOP", "MAUT1", "MAUT2", "MAUT0", "MZFONDS", "MZPART", "MINKM30",
    "MINK3045", "MINK4575", "MINK7512", "MINK123M", "MINKGEM", "MKOOPKLA", "PWAPART", "PWABEDR", "PWALAND",
    "PPERSAUT", "PBESAUT", "PMOTSCO", "PVRAAUT", "PAANHANG", "PTRACTOR", "PWERKT", "PBROM", "PLEVEN",
    "PPERSONG", "PGEZONG", "PWAOREG", "PBRAND", "PZEILPL", "PPLEZIER", "PFIETS", "PINBOED", "PBYSTAND",
    "AWAPART", "AWABEDR", "AWALAND", "APERSAUT", "ABESAUT", "AMOTSCO", "AVRAAUT", "AAANHANG", "ATRACTOR",
    "AWERKT", "ABROM", "ALEVEN", "APERSONG", "AGEZONG", "AWAOREG", "ABRAND", "AZEILPL", "APLEZIER",
    "AFIETS", "AINBOED", "ABYSTAND", "CARAVAN"
]

L0_CUSTOMER_SUBTYPES = {
    1: "High Income, expensive child",
    2: "Very Important Provincials",
    3: "High status seniors",
    4: "Affluent senior apartments",
    5: "Mixed seniors",
    6: "Career and childcare",
    7: "Dinki's (double income no kids)",
    8: "Middle class families",
    9: "Modern, complete families",
    10: "Stable family",
    11: "Family starters",
    12: "Affluent young families",
    13: "Young all american family",
    14: "Junior cosmopolitan",
    15: "Senior cosmopolitans",
    16: "Students in apartments",
    17: "Fresh masters in the city",
    18: "Single youth",
    19: "Suburban youth",
    20: "Ethnically diverse",
    21: "Young urban have-nots",
    22: "Mixed apartment dwellers",
    23: "Young and rising",
    24: "Young, low educated",
    25: "Young seniors in the city",
    26: "Own home elderly",
    27: "Seniors in apartments",
    28: "Residential elderly",
    29: "Porchless seniors: no front yard",
    30: "Religious elderly singles",
    31: "Low income catholics",
    32: "Mixed seniors",
    33: "Lower class large families",
    34: "Large family, employed child",
    35: "Village families",
    36: "Couples with teens 'Married with children'",
    37: "Mixed small town dwellers",
    38: "Traditional families",
    39: "Large religious families",
    40: "Large family farms",
    41: "Mixed rurals"
}

L1_AGE_GROUPS = {
    1: "20-30 years",
    2: "30-40 years",
    3: "40-50 years",
    4: "50-60 years",
    5: "60-70 years",
    6: "70-80 years"
}

L2_MAIN_TYPES = {
    1: "Successful hedonists",
    2: "Driven Growers",
    3: "Average Family",
    4: "Career Loners",
    5: "Living well",
    6: "Cruising Seniors",
    7: "Retired and Religious",
    8: "Family with grown ups",
    9: "Conservative families",
    10: "Farmers"
}

L4_CONTRIBUTION_TIERS = {
    0: "f 0",
    1: "f 1 - 49",
    2: "f 50 - 99",
    3: "f 100 - 199",
    4: "f 200 - 499",
    5: "f 500 - 999",
    6: "f 1,000 - 4,999",
    7: "f 5,000 - 9,999",
    8: "f 10,000 - 19,999",
    9: "f 20,000+"
}

POLICY_COLUMNS = {
    "Auto": {"contrib": "PPERSAUT", "count": "APERSAUT"},
    "Fire_Property": {"contrib": "PBRAND", "count": "ABRAND"},
    "Boat_Marine": {"contrib": "PPLEZIER", "count": "APLEZIER"},
    "Private_Accident": {"contrib": "PPERSONG", "count": "APERSONG"},
    "Third_Party_Private": {"contrib": "PWAPART", "count": "AWAPART"},
    "Motorcycle": {"contrib": "PMOTSCO", "count": "AMOTSCO"},
    "Life": {"contrib": "PLEVEN", "count": "ALEVEN"},
    "Disability": {"contrib": "PWAOREG", "count": "AWAOREG"}
}


# -------------------------------------------------------------------------
# 2. LOAD AND CLEAN CUSTOMER REGISTRY
# -------------------------------------------------------------------------

def load_and_clean_customers():
    print("[1/4] Ingesting and decoding raw COIL 2000 customer data...")

    train_path = os.path.join(RAW_DATA_DIR, "ticdata2000.txt")
    eval_path = os.path.join(RAW_DATA_DIR, "ticeval2000.txt")
    tgts_path = os.path.join(RAW_DATA_DIR, "tictgts2000.txt")

    # Load train set
    df_train = pd.read_csv(train_path, sep="\t", header=None, names=COLUMN_NAMES)
    df_train["dataset_split"] = "train"

    # Load eval set and targets
    df_eval = pd.read_csv(eval_path, sep="\t", header=None, names=COLUMN_NAMES[:-1])
    eval_targets = pd.read_csv(tgts_path, header=None, names=["CARAVAN"])
    df_eval["CARAVAN"] = eval_targets["CARAVAN"].values
    df_eval["dataset_split"] = "eval"

    # Combine all 9,822 customers
    df_customers = pd.concat([df_train, df_eval], ignore_index=True)
    df_customers["customer_id"] = [f"CUST_{i+1:05d}" for i in range(len(df_customers))]

    # Decoded descriptive features
    df_customers["customer_subtype_desc"] = df_customers["MOSTYPE"].map(L0_CUSTOMER_SUBTYPES).fillna("Unknown Subtype")
    df_customers["customer_main_type_desc"] = df_customers["MOSHOOFD"].map(L2_MAIN_TYPES).fillna("Unknown Main Type")
    df_customers["age_group_desc"] = df_customers["MGEMLEEF"].map(L1_AGE_GROUPS).fillna("Unknown Age Group")

    # Calculate policy portfolio aggregates
    count_cols = [c for c in COLUMN_NAMES if c.startswith("A") and c != "AAANHANG"]
    contrib_cols = [c for c in COLUMN_NAMES if c.startswith("P")]
    
    df_customers["total_policies_count"] = df_customers[count_cols].sum(axis=1)
    df_customers["active_product_lines_count"] = (df_customers[count_cols] > 0).sum(axis=1)
    df_customers["total_contribution_score"] = df_customers[contrib_cols].sum(axis=1)

    # Boolean flags for key policies
    df_customers["has_car_policy"] = df_customers["APERSAUT"] > 0
    df_customers["has_fire_policy"] = df_customers["ABRAND"] > 0
    df_customers["has_boat_policy"] = df_customers["APLEZIER"] > 0
    df_customers["has_life_policy"] = df_customers["ALEVEN"] > 0
    df_customers["has_accident_policy"] = df_customers["APERSONG"] > 0

    print(f"      Total customer records loaded: {len(df_customers):,} (Train: {len(df_train):,}, Eval: {len(df_eval):,})")
    return df_customers


# -------------------------------------------------------------------------
# 3. FEATURE ENGINEER CLAIMS & SEPARATE OBSERVABLES FROM GROUND TRUTH
# -------------------------------------------------------------------------

INCIDENT_TEMPLATES = {
    "Auto": [
        ("Front-end collision at intersection during heavy rain; significant bumper, radiator and bonnet deformation. Third-party admitted fault.", "Collision", "Moderate", 3200, 1200),
        ("Rear-ended while stationary at red signal; tailgate, rear lights, and chassis panel crushed. Other driver present and exchanged insurance.", "Rear-End", "Moderate", 4100, 1500),
        ("Parked vehicle side-swiped overnight along suburban roadway; left driver doors and mirror torn off. Perpetrator fled scene.", "Hit and Run", "Minor", 1950, 600),
        ("Single-vehicle rollover on icy highway curve after vehicle skidded on black ice; frame compromised, curtain airbags deployed.", "Rollover", "Severe", 18500, 6000),
        ("Hail storm caused extensive bodywork dimpling and shattered panoramic sunroof during sudden convective storm.", "Weather/Hail", "Moderate", 4800, 1400),
        ("High-speed collision with utility pole following brake failure attempt; total front structural destruction. Airbags deployed.", "Single-Vehicle Crash", "Catastrophic", 28000, 7500),
        ("Vehicle stolen from private driveway overnight; recovery team found vehicle stripped of wheels, exhaust, and infotainment unit.", "Theft & Stripping", "Severe", 14500, 4200),
    ],
    "Fire_Property": [
        ("Kitchen grease fire ignited on stovetop, spreading quickly to cabinetry and extractor hood before local brigade extinguished blaze.", "Kitchen Fire", "Moderate", 12500, 4500),
        ("Faulty electrical wiring in attic sparked smoldering insulation fire, resulting in heavy ceiling collapse and structural timber charring.", "Electrical Fire", "Severe", 38000, 11000),
        ("Lightning strike ignited secondary residential garage roof, destroying stored tools, lawn equipment, and structural roofing rafters.", "Lightning/Structure Fire", "Severe", 24000, 8000),
        ("Minor chimney soot flare caused interior smoke staining across living room walls, upholstery, and drapes; no structural flames.", "Smoke Ingress", "Minor", 3200, 950),
        ("Water pipe ruptured in second-floor bathroom during deep freeze, causing cascading water damage through ceiling onto hardwood floors.", "Water Leak/Flooding", "Moderate", 8900, 2800),
    ],
    "Boat_Marine": [
        ("Vessel hull impacted submerged rock shoal near harbor approach, fracturing fiberglass keel and causing rapid bilge flooding.", "Grounding/Hull Damage", "Severe", 16500, 5200),
        ("Moored pleasure craft broke stern line during gale-force harbor squall and collided repeatedly with marina pier pilings.", "Marina Collision", "Moderate", 7800, 2400),
        ("Inboard marine engine overheated and suffered catastrophic crankcase seizure following cooling intake plastic debris blockage.", "Engine Failure", "Severe", 11200, 3600),
        ("Outboard motor stolen from boat transom while docked at secure marine club slipway overnight.", "Marine Theft", "Minor", 4200, 1100),
    ],
    "Private_Accident": [
        ("Insured slipped on wet marble staircase at regional train concourse, sustaining fractured right clavicle and severe wrist sprain.", "Slip and Fall", "Moderate", 4500, 1600),
        ("Injured during amateur weekend cycling sportive when struck by crossing dog; sustained fractured collarbone and severe road abrasions.", "Bicycle Accident", "Minor", 2800, 900),
        ("Fall from ladder while trimming domestic hedgerow; compounded compound ankle fracture requiring surgical pinning and 6-week immobilization.", "Domestic Fall", "Severe", 14200, 4100),
    ],
    "Third_Party_Private": [
        ("Insured's domestic dog bolted from garden gate and caused a passing cyclist to crash, damaging bicycle frame and causing minor injuries.", "Third-Party Liability", "Minor", 2100, 700),
        ("Accidental spill of caustic chemical solvent onto neighbor's imported hardwood patio decking while conducting fence restoration work.", "Property Damage Liability", "Minor", 3400, 1100)
    ]
}

def generate_claims_and_ground_truth(df_customers, total_claims=1800):
    print(f"[2/4] Generating observable claims and separate ground-truth labels ({total_claims} claims)...")

    observable_claims = []
    ground_truth_records = []
    base_date = datetime(2024, 1, 1)

    # Eligible customer candidates by policy type
    auto_customers = df_customers[df_customers["has_car_policy"]]["customer_id"].tolist()
    fire_customers = df_customers[df_customers["has_fire_policy"]]["customer_id"].tolist()
    boat_customers = df_customers[df_customers["has_boat_policy"]]["customer_id"].tolist()
    accident_customers = df_customers[df_customers["has_accident_policy"]]["customer_id"].tolist()
    all_customer_ids = df_customers["customer_id"].tolist()

    # Pre-index customers for fast lookups
    customer_lookup = df_customers.set_index("customer_id").to_dict(orient="index")

    # Policy distribution weights
    policy_weights = [("Auto", 0.52, auto_customers),
                      ("Fire_Property", 0.28, fire_customers),
                      ("Boat_Marine", 0.08, boat_customers),
                      ("Private_Accident", 0.08, accident_customers),
                      ("Third_Party_Private", 0.04, all_customer_ids)]

    claim_counter = 1

    for policy_type, weight, candidate_pool in policy_weights:
        num_policy_claims = int(total_claims * weight)
        templates = INCIDENT_TEMPLATES[policy_type]

        for _ in range(num_policy_claims):
            claim_id = f"CLM-{claim_counter:05d}"
            claim_counter += 1

            # Decide if this claim has an injected anomaly (12% base anomaly rate)
            is_anomaly = (random.random() < 0.12)
            anomaly_types = []
            anomaly_category = "Standard"

            # 1. Coverage Mismatch Anomaly (~35% of anomalies): Customer files claim on policy they do NOT own
            if is_anomaly and random.random() < 0.35:
                zero_policy_col = POLICY_COLUMNS.get(policy_type, {}).get("count")
                if zero_policy_col:
                    non_holders = df_customers[df_customers[zero_policy_col] == 0]["customer_id"].tolist()
                    cust_id = random.choice(non_holders) if non_holders else random.choice(candidate_pool)
                else:
                    cust_id = random.choice(candidate_pool)
                anomaly_category = "Coverage Mismatch"
                anomaly_types.append("Zero active policies on record for claimed insurance line")
            else:
                cust_id = random.choice(candidate_pool)

            cust = customer_lookup[cust_id]
            policy_count = cust.get(POLICY_COLUMNS.get(policy_type, {}).get("count", "APERSAUT"), 0)
            policy_contrib = cust.get(POLICY_COLUMNS.get(policy_type, {}).get("contrib", "PPERSAUT"), 0)
            purchasing_power = cust.get("MKOOPKLA", 5)

            # Pick incident template
            template_text, inc_type, severity, base_mean, base_std = random.choice(templates)

            # 2. Amount Discrepancy Anomaly
            if is_anomaly and random.random() < 0.40:
                claim_amount = round(base_mean * random.uniform(3.5, 6.5) + abs(np.random.normal(0, base_std)), 2)
                anomaly_category = "Amount Outlier"
                anomaly_types.append(f"Claim amount (€{claim_amount:,.2f}) significantly exceeds typical policy band and purchasing power class ({purchasing_power}/8)")
            else:
                scale_factor = 0.8 + (policy_contrib / 10.0) * 0.4
                raw_amt = np.random.normal(base_mean * scale_factor, base_std)
                claim_amount = round(max(350.0, raw_amt), 2)

            # Dates & Delay
            incident_days_offset = random.randint(1, 350)
            incident_date = base_date + timedelta(days=incident_days_offset)

            # 3. Reporting Delay Anomaly
            if is_anomaly and random.random() < 0.30:
                reporting_delay = random.randint(35, 75)
                anomaly_category = "Delayed Reporting"
                anomaly_types.append(f"Incident reported {reporting_delay} days post-occurrence without valid explanation")
            else:
                reporting_delay = random.randint(0, 7)

            claim_date = incident_date + timedelta(days=reporting_delay)

            # Documentation flags
            police_report = "Yes" if severity in ["Severe", "Catastrophic"] or policy_type == "Auto" else random.choice(["Yes", "No"])
            witness_present = random.choice(["Yes", "No"])

            # 4. Lack of Police Report on Major Loss
            if is_anomaly and severity in ["Severe", "Catastrophic"] and random.random() < 0.35:
                police_report = "No"
                witness_present = "No"
                anomaly_category = "Unverified Major Loss"
                anomaly_types.append("Major catastrophic damage reported with neither police report nor independent witnesses")

            # Enrich incident narrative with factual customer context
            demographic_snippet = f"Insured ({cust['age_group_desc']}, {cust['customer_subtype_desc']})"
            full_narrative = (
                f"{template_text} "
                f"{demographic_snippet}. "
                f"Incident occurred on {incident_date.strftime('%B %d, %Y')} under standard operational conditions. "
                f"Police report filed: {police_report}. Independent witness present: {witness_present}. "
                f"Total estimated repair and indemnity loss assessed at €{claim_amount:,.2f}."
            )

            # -----------------------------------------------------------------
            # TIER 1: PURE OBSERVABLE INPUT FEATURES (Zero target/leakage features)
            # -----------------------------------------------------------------
            observable_claims.append({
                "claim_id": claim_id,
                "customer_id": cust_id,
                "policy_type": policy_type,
                "policy_count": int(policy_count),
                "policy_contribution_tier": int(policy_contrib),
                "purchasing_power_class": int(purchasing_power),
                "claim_amount": claim_amount,
                "incident_type": inc_type,
                "incident_severity": severity,
                "incident_date": incident_date.strftime("%Y-%m-%d"),
                "claim_date": claim_date.strftime("%Y-%m-%d"),
                "reporting_delay_days": reporting_delay,
                "police_report_filed": police_report,
                "witness_present": witness_present,
                "incident_description": full_narrative
            })

            # -----------------------------------------------------------------
            # TIER 2: HELD-OUT GROUND TRUTH LABELS (Used ONLY in Task 4 evaluation)
            # -----------------------------------------------------------------
            ground_truth_records.append({
                "claim_id": claim_id,
                "ground_truth_is_anomaly": 1 if is_anomaly else 0,
                "ground_truth_anomaly_type": anomaly_category if is_anomaly else "Standard",
                "ground_truth_anomaly_reason": " | ".join(anomaly_types) if anomaly_types else "Legitimate claim; consistent with coverage and demographics",
                "reference_risk_tier": "High" if is_anomaly else "Low"
            })

    df_claims = pd.DataFrame(observable_claims)
    df_ground_truth = pd.DataFrame(ground_truth_records)

    # Calculate genuine historical prior claims count chronologically (Zero temporal leakage)
    df_claims["incident_date_dt"] = pd.to_datetime(df_claims["incident_date"])
    df_claims = df_claims.sort_values(["customer_id", "incident_date_dt", "claim_id"])
    df_claims["prior_claims_count"] = df_claims.groupby("customer_id").cumcount()
    df_claims = df_claims.drop(columns=["incident_date_dt"]).sort_values("claim_id").reset_index(drop=True)

    print(f"      Total observable claims: {len(df_claims):,}")
    print(f"      Ground truth anomalies: {df_ground_truth['ground_truth_is_anomaly'].sum():,} ({df_ground_truth['ground_truth_is_anomaly'].mean():.2%})")
    print(f"      Observable features count: {len(df_claims.columns)} (Zero leakage columns present)")
    return df_claims, df_ground_truth


# -------------------------------------------------------------------------
# 4. SAVE OUTPUTS AND STRICT DATA DICTIONARY
# -------------------------------------------------------------------------

def save_processed_data(df_customers, df_claims, df_ground_truth):
    print("[3/4] Exporting strictly separated datasets to 'processed_data/' directory...")

    customers_csv_path = os.path.join(OUTPUT_DIR, "customers_clean.csv")
    claims_csv_path = os.path.join(OUTPUT_DIR, "claims_knowledge_base.csv")
    ground_truth_csv_path = os.path.join(OUTPUT_DIR, "claims_ground_truth.csv")
    dict_json_path = os.path.join(OUTPUT_DIR, "data_dictionary.json")

    # Save CSVs
    df_customers.to_csv(customers_csv_path, index=False)
    df_claims.to_csv(claims_csv_path, index=False)
    df_ground_truth.to_csv(ground_truth_csv_path, index=False)

    # Build schema and metadata dictionary
    dictionary_meta = {
        "dataset_name": "AI-Powered Insurance Claims Intelligence Knowledge Base",
        "generated_timestamp": datetime.now().isoformat(),
        "design_architecture": "Strict separation between Observable Input Features and Held-out Evaluation Ground Truth to prevent data leakage.",
        "customer_records_count": len(df_customers),
        "claims_records_count": len(df_claims),
        "raw_source": "COIL 2000 / TIC 2000 (Sentient Machine Research)",
        "datasets": {
            "customers_clean.csv": {
                "description": "Cleaned customer demographic and policy registry with 86 COIL attributes decoded.",
                "primary_key": "customer_id",
                "rows": len(df_customers),
                "columns_count": len(df_customers.columns)
            },
            "claims_knowledge_base.csv": {
                "description": "Operational claims table containing ONLY observable features available at inference time (Zero leakage).",
                "primary_key": "claim_id",
                "foreign_key": "customer_id -> customers_clean.csv",
                "rows": len(df_claims),
                "columns_count": len(df_claims.columns),
                "columns": list(df_claims.columns),
                "observable_fields": {
                    "claim_id": "Unique claim identifier (CLM-XXXXX)",
                    "customer_id": "Foreign key pointing to COIL 2000 customer record",
                    "policy_type": "Insurance product line (Auto, Fire_Property, Boat_Marine, Private_Accident, Third_Party_Private)",
                    "policy_count": "Number of active policies customer holds in this product line",
                    "policy_contribution_tier": "Customer's contribution tier (0-9) for this policy line",
                    "purchasing_power_class": "Customer's socio-economic purchasing power bracket (1-8)",
                    "claim_amount": "Total claimed damage amount in Euros (€)",
                    "incident_type": "Specific loss event (e.g. Collision, Electrical Fire, Rollover)",
                    "incident_severity": "Severity classification (Minor, Moderate, Severe, Catastrophic)",
                    "incident_date": "Date incident occurred (YYYY-MM-DD)",
                    "claim_date": "Date claim was officially filed (YYYY-MM-DD)",
                    "reporting_delay_days": "Days elapsed between incident and claim notification",
                    "police_report_filed": "Official police verification indicator (Yes/No)",
                    "witness_present": "Independent witness availability (Yes/No)",
                    "prior_claims_count": "Historical prior claims count on record for this customer",
                    "incident_description": "Unstructured text narrative for vector embedding and semantic retrieval"
                }
            },
            "claims_ground_truth.csv": {
                "description": "Held-out ground truth benchmark labels used STRICTLY for Task 4 evaluation metrics (Precision, Recall, ROC-AUC). Never exposed to models/agents during inference.",
                "primary_key": "claim_id",
                "rows": len(df_ground_truth),
                "columns_count": len(df_ground_truth.columns),
                "fields": {
                    "claim_id": "Claim identifier matching claims_knowledge_base.csv",
                    "ground_truth_is_anomaly": "Binary ground-truth target (1 = High-risk anomaly, 0 = Normal claim)",
                    "ground_truth_anomaly_type": "Categorical anomaly archetype (Coverage Mismatch, Amount Outlier, Delayed Reporting, Frequency Anomaly, Unverified Major Loss, Standard)",
                    "ground_truth_anomaly_reason": "Verifiable reference explanation for evaluation grounding checks",
                    "reference_risk_tier": "Baseline risk tier classification (Low, High)"
                }
            }
        },
        "l0_subtypes_mapping": L0_CUSTOMER_SUBTYPES,
        "l1_age_groups_mapping": L1_AGE_GROUPS,
        "l2_main_types_mapping": L2_MAIN_TYPES,
        "l4_contribution_tiers_mapping": L4_CONTRIBUTION_TIERS
    }

    with open(dict_json_path, "w", encoding="utf-8") as f:
        json.dump(dictionary_meta, f, indent=2)

    print(f"      Saved: {customers_csv_path} ({os.path.getsize(customers_csv_path):,} bytes)")
    print(f"      Saved: {claims_csv_path} ({os.path.getsize(claims_csv_path):,} bytes)")
    print(f"      Saved: {ground_truth_csv_path} ({os.path.getsize(ground_truth_csv_path):,} bytes)")
    print(f"      Saved: {dict_json_path} ({os.path.getsize(dict_json_path):,} bytes)")


# -------------------------------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print(" INSURANCE CLAIMS INTELLIGENCE: ZERO-LEAKAGE DATA RE-PIPELINE")
    print("=" * 70)

    # Step 1: Clean and decode customers
    customers_df = load_and_clean_customers()

    # Step 2: Generate observable claims and separate ground-truth labels
    claims_df, ground_truth_df = generate_claims_and_ground_truth(customers_df, total_claims=1800)

    # Step 3: Save strictly separated clean artifacts
    save_processed_data(customers_df, claims_df, ground_truth_df)

    print("[4/4] Zero-leakage data preparation completed successfully!")
    print("=" * 70)
