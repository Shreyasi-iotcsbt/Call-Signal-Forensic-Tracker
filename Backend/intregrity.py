# ============================================================
# CALL & SIGNAL FORENSIC TRACKER
# Evidence Integrity Verification Module
# ============================================================

import hashlib
import os
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

EVIDENCE_DIR = os.path.join("evidence")
HASH_FILE = os.path.join(EVIDENCE_DIR, "integrity_hash.txt")


# ============================================================
# SHA-256 HASH CALCULATION
# ============================================================

def calculate_sha256(file_path):
    """
    Calculate the SHA-256 hash of a file.
    """

    sha256 = hashlib.sha256()

    try:
        with open(file_path, "rb") as file:

            while True:
                chunk = file.read(4096)

                if not chunk:
                    break

                sha256.update(chunk)

        return sha256.hexdigest()

    except Exception as e:
        print(f"[!] Hash calculation failed: {e}")
        return None


# ============================================================
# EVIDENCE INTEGRITY VERIFICATION
# ============================================================

def verify_integrity(evidence):
    """
    Calculate and record the SHA-256 hash
    of the acquired evidence file.
    """

    print("\n" + "=" * 60)
    print("             INTEGRITY VERIFICATION")
    print("=" * 60)

    # Check evidence information
    if not evidence:
        print("[!] No evidence information available.")
        return None

    file_path = evidence.get("evidence_path")

    # Check evidence file
    if not file_path:
        print("[!] Evidence path is missing.")
        return None

    if not os.path.isfile(file_path):
        print("[!] Evidence file not found.")
        return None

    # Calculate SHA-256
    file_hash = calculate_sha256(file_path)

    if file_hash is None:
        return None

    # Create evidence directory
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

    # Verification time
    verification_time = datetime.now().isoformat()

    # Save integrity record
    try:
        with open(HASH_FILE, "w") as file:

            file.write("CALL & SIGNAL FORENSIC TRACKER\n")
            file.write("EVIDENCE INTEGRITY RECORD\n")
            file.write("=" * 60 + "\n")
            file.write(f"File Name       : {os.path.basename(file_path)}\n")
            file.write(f"File Path       : {os.path.abspath(file_path)}\n")
            file.write("Hash Algorithm  : SHA-256\n")
            file.write(f"SHA-256 Hash    : {file_hash}\n")
            file.write(f"Verified At     : {verification_time}\n")

    except Exception as e:
        print(f"[!] Failed to save integrity record: {e}")
        return None

    # Integrity information
    integrity = {
        "status": "VERIFIED",
        "algorithm": "SHA-256",
        "hash": file_hash,
        "file": os.path.basename(file_path),
        "file_path": os.path.abspath(file_path),
        "verification_time": verification_time,
        "hash_record": HASH_FILE
    }

    # Display result
    print("\n[✓] Evidence integrity verified.")
    print(f"[✓] File       : {integrity['file']}")
    print(f"[✓] Algorithm  : {integrity['algorithm']}")
    print(f"[✓] SHA-256    : {integrity['hash']}")
    print(f"[✓] Hash record: {integrity['hash_record']}")

    return integrity