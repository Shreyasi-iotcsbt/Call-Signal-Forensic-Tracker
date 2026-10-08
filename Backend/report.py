from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_ROOT / "reports"


def generate_report(consent, requisition, evidence, validation, integrity, analysis):
    if not all((consent, requisition, evidence, validation, integrity, analysis)):
        print("[!] Required workflow information is missing.")
        return None

    generated_at = datetime.now().astimezone().isoformat()
    report_path = REPORT_DIR / f"forensic_report_{datetime.now():%Y%m%dT%H%M%S%f}.txt"
    lines = [
        "CALL & SIGNAL FORENSIC TRACKER",
        "FORENSIC ANALYSIS REPORT",
        "=" * 60,
        f"Generated At       : {generated_at}",
        f"Consent Status     : {consent['status']}",
        f"Consent Timestamp  : {consent['timestamp']}",
        f"Call Records       : {bool(requisition.get('call_records'))}",
        f"Signal Data        : {bool(requisition.get('signal_data'))}",
        f"Evidence File      : {evidence['filename']}",
        f"Evidence Path      : {Path(evidence['evidence_path']).resolve()}",
        f"Evidence Size      : {evidence['size_bytes']} bytes",
        f"Validated Records  : {validation['records']}",
        f"Duplicate Records  : {validation['duplicates']}",
        f"Acquisition SHA-256: {evidence['sha256']}",
        f"Hash Algorithm     : {integrity['algorithm']}",
        f"SHA-256            : {integrity['hash']}",
        "",
        "ANALYSIS SUMMARY",
        "=" * 60,
    ]

    calls = analysis.get("calls")
    if calls:
        lines.extend([
            f"Total call records : {calls['total_records']}",
            f"Incoming calls     : {calls['incoming']}",
            f"Outgoing calls     : {calls['outgoing']}",
            f"Missed calls       : {calls['missed']}",
            f"Total duration     : {calls['total_duration']} seconds",
        ])

    signal = analysis.get("signal")
    if signal:
        lines.extend([
            f"Average RSRP       : {signal['average_rsrp']:.2f} dBm",
            f"Strongest RSRP     : {signal['strongest_rsrp']} dBm",
            f"Weakest RSRP       : {signal['weakest_rsrp']} dBm",
        ])

    network = analysis.get("network") or {}
    for title, key in (("Network Types", "network_types"), ("Cell Usage", "cell_usage")):
        values = network.get(key)
        if values:
            lines.extend(["", title + ":"])
            lines.extend(f"  {name}: {count}" for name, count in values.items())

    try:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as error:
        print(f"[!] Failed to write report: {error}")
        return None

    print(f"[+] Report generated: {report_path}")
    return {"status": "GENERATED", "report_path": str(report_path)}