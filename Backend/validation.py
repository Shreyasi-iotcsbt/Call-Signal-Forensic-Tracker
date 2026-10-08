# ============================================================
# CALL & SIGNAL FORENSIC TRACKER
# Data Validation Module
# ============================================================

import os
import pandas as pd


# ============================================================
# VALIDATE ACQUIRED DATA
# ============================================================

def validate_data(evidence, requisition):

    print("\n" + "=" * 60)
    print("                DATA VALIDATION")
    print("=" * 60)

    # Check evidence
    if not evidence:
        print("[!] No evidence available.")
        return None

    file_path = evidence.get("evidence_path")

    if not file_path or not os.path.isfile(file_path):
        print("[!] Evidence file not found.")
        return None

    # Load file
    try:

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".csv":
            data = pd.read_csv(file_path)

        elif extension == ".json":
            data = pd.read_json(file_path)

        else:
            print("[!] Unsupported file format.")
            return None

    except Exception as e:

        print(f"[!] Failed to read evidence: {e}")
        return None

    # Check empty file
    if data.empty:
        print("[!] Evidence file contains no records.")
        return None

    print(f"\n[✓] File loaded successfully.")
    print(f"[✓] Records found: {len(data)}")

    # Standardise column names
    data.columns = (
        data.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Required columns
    required_columns = [
        "timestamp",
        "phone_number"
    ]

    # Call data validation
    if requisition.get("call_records"):

        required_columns.extend([
            "call_type",
            "duration_seconds"
        ])

    # Signal data validation
    if requisition.get("signal_data"):

        required_columns.extend([
            "cell_id",
            "radio_type"
        ])

        # Accept either rsrp or signal_strength
        if "rsrp" not in data.columns and "signal_strength" not in data.columns:
            print("[!] Missing signal strength column.")
            return None

    # Find missing columns
    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:

        print("\n[!] Validation failed.")
        print("[!] Missing columns:")

        for column in missing_columns:
            print(f"    - {column}")

        return None

    # Convert timestamp
    try:

        data["timestamp"] = pd.to_datetime(
            data["timestamp"],
            errors="coerce"
        )

    except Exception:

        print("[!] Invalid timestamp data.")
        return None

    # Check invalid timestamps
    invalid_timestamps = data["timestamp"].isna().sum()

    if invalid_timestamps > 0:

        print(
            f"[!] Invalid timestamps found: "
            f"{invalid_timestamps}"
        )

        return None

    # Check phone numbers
    data["phone_number"] = (
        data["phone_number"]
        .astype(str)
        .str.strip()
    )

    invalid_numbers = (
        data["phone_number"]
        .isin(["", "nan", "None"])
        .sum()
    )

    if invalid_numbers > 0:

        print(
            f"[!] Invalid phone numbers found: "
            f"{invalid_numbers}"
        )

        return None

    # Convert signal strength
    if "signal_strength" in data.columns and "rsrp" not in data.columns:

        data["rsrp"] = pd.to_numeric(
            data["signal_strength"],
            errors="coerce"
        )

    elif "rsrp" in data.columns:

        data["rsrp"] = pd.to_numeric(
            data["rsrp"],
            errors="coerce"
        )

    # Convert call duration
    if "duration_seconds" in data.columns:

        data["duration_seconds"] = pd.to_numeric(
            data["duration_seconds"],
            errors="coerce"
        )

    # Check duplicate records
    duplicate_count = data.duplicated().sum()

    # Validation result
    validation = {
        "status": "VALID",
        "records": len(data),
        "columns": list(data.columns),
        "duplicates": int(duplicate_count),
        "invalid_timestamps": int(invalid_timestamps),
        "data": data
    }

    # Display results
    print("\n" + "-" * 60)
    print("              VALIDATION RESULTS")
    print("-" * 60)

    print("[✓] Required columns present")
    print("[✓] Timestamp format valid")
    print("[✓] Phone number data valid")
    print("[✓] Signal/call data validated")
    print(f"[✓] Records validated: {len(data)}")
    print(f"[i] Duplicate records: {duplicate_count}")

    print("\n[✓] DATA VALIDATION PASSED.")

    return validation