import hashlib
import shutil
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def acquire_data(requisition, file_path=None):

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

    entered_path = file_path
    if entered_path is None:
        entered_path = input(
            "\nEnter path to authorised device export: "
        ).strip().strip('"')
    source = Path(entered_path).expanduser()
    if not source.is_absolute() and not source.is_file():
        source = PROJECT_ROOT / source
    source = source.resolve()

    # Check file exists
    if not source.is_file():
        print("[!] File not found.")
        return None

    # Check supported format
    extension = source.suffix.lower()

    if extension not in [".csv", ".json"]:
        print("[!] Only CSV and JSON files are supported.")
        return None

    # Create raw evidence directory
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    filename = source.name

    destination = RAW_DIR / filename

    # Prevent source and destination being the same file
    source_abs = str(source)
    if source == destination.resolve():
        destination = source
    elif destination.exists():
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        destination = destination.with_name(
            f"{destination.stem}_{timestamp}{destination.suffix}"
        )

    try:
        if source != destination:
            shutil.copy2(source, destination)
        with destination.open("rb") as evidence_file:
            acquisition_hash = hashlib.file_digest(evidence_file, "sha256").hexdigest()
    except OSError as e:

        print("[!] Acquisition failed:", e)
        return None

    acquisition = {
        "status": "ACQUIRED",
        "source": source_abs,
        "evidence_path": str(destination),
        "filename": destination.name,
        "extension": extension,
        "acquisition_time": datetime.now().isoformat(),
        "size_bytes": destination.stat().st_size,
        "sha256": acquisition_hash
    }

    print("\n[+] Evidence acquired successfully.")
    print(f"[+] Evidence file : {destination.name}")
    print(f"[+] Stored at     : {destination}")
    print(f"[+] Size          : {acquisition['size_bytes']} bytes")
    print(f"[+] SHA-256       : {acquisition['sha256']}")
    print(f"[+] Acquired at   : {acquisition['acquisition_time']}")

    return acquisition
