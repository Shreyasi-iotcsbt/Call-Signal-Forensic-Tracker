from datetime import datetime


def obtain_consent():

    print("=" * 60)
    print("             USER CONSENT REQUIRED")
    print("=" * 60)

    print("""
This application processes data from an
authorised device/export for forensic analysis.

Only data explicitly authorised by the
device owner/user should be supplied.

Purpose:
Forensic call and signal analysis
""")

    choice = input("Do you give consent? (YES/NO): ").strip().upper()

    if choice != "YES":
        return None

    consent = {
        "status": "GRANTED",
        "timestamp": datetime.now().isoformat(),
        "purpose": "Forensic call and signal analysis"
    }

    print("\n[+] Consent granted.")

    return consent