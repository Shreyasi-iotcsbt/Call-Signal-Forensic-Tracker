import os
import shutil
from datetime import datetime


RAW_DIR = os.path.join("data", "raw")


def acquire_data(requisition):

    print("\n" + "=" * 60)
    print("              DATA ACQUISITION")
    print("=" * 60)

    # Check whether anything was authorised
    if not requisition.get("call_records") and not requisition.get("signal_data"):
        print("[!] No data types were authorised.")
        return None

    print("\nAuthorised data:")
    
    if requisition.get("call_records"):
        print("[✓] Call records")

    if requisition.get("signal_data"):
        print("[✓] Signal/network data")

    print("\nThis prototype accepts an authorised CSV or JSON export.")

    file_path = input(
        "\nEnter path to authorised device export: "
    ).strip().strip('"')

    # Check file exists
    if not os.path.isfile(file_path):
        print("[!] File not found.")
        return None

    # Check supported format
    extension = os.path.splitext(file_path)[1].lower()

    if extension not in [".csv", ".json"]:
        print("[!] Only CSV and JSON files are supported.")
        return None

    # Create raw evidence directory
    os.makedirs(RAW_DIR, exist_ok=True)

    filename = os.path.basename(file_path)

    destination = os.path.join(
        RAW_DIR,
        filename
    )

    # Prevent source and destination being the same file
    source_abs = os.path.abspath(file_path)
    destination_abs = os.path.abspath(destination)

    if source_abs == destination_abs:
    print("[!] Source file is already inside the raw evidence folder.")
    return {
        "status": "ACQUIRED",
        "source": source_abs,
        "evidence_path": destination,
        "filename": filename,
        "extension": extension,
        "acquisition_time": datetime.now().isoformat(),
        "size_bytes": os.path.getsize(destination)
    }
    try:

        shutil.copy2(
            file_path,
            destination
        )

    except Exception as e:

        print("[!] Acquisition failed:", e)
        return None

    acquisition = {
        "status": "ACQUIRED",
        "source": source_abs,
        "evidence_path": destination,
        "filename": filename,
        "extension": extension,
        "acquisition_time": datetime.now().isoformat(),
        "size_bytes": os.path.getsize(destination)
    }

    print("\n[+] Evidence acquired successfully.")
    print(f"[+] Evidence file : {filename}")
    print(f"[+] Stored at     : {destination}")
    print(f"[+] Size          : {acquisition['size_bytes']} bytes")
    print(f"[+] Acquired at   : {acquisition['acquisition_time']}")

    return acquisition
