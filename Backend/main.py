# ============================================================
# CALL & SIGNAL FORENSIC TRACKER
# Main Application / Pipeline Orchestrator
# ============================================================

if __package__:
    from .acquisition import acquire_data
    from .analysis import run_analysis
    from .consent import obtain_consent
    from .integrity import verify_integrity
    from .requisition import create_requisition
    from .report import generate_report
    from .validation import validate_data
else:
    from acquisition import acquire_data
    from analysis import run_analysis
    from consent import obtain_consent
    from integrity import verify_integrity
    from requisition import create_requisition
    from report import generate_report
    from validation import validate_data


# ============================================================
# APPLICATION INFORMATION
# ============================================================

APP_NAME = "Call & Signal Forensic Tracker"
APP_VERSION = "1.0"


# ============================================================
# MAIN WORKFLOW
# ============================================================

def main():

    print("=" * 60)
    print(f"        {APP_NAME} v{APP_VERSION}")
    print("=" * 60)

    # --------------------------------------------------------
    # STEP 1: USER CONSENT
    # --------------------------------------------------------

    print("\n[1] USER CONSENT")

    consent = obtain_consent()

    if not consent:
        print("\n[!] Consent was not granted.")
        print("[!] Forensic workflow stopped.")
        return

    # --------------------------------------------------------
    # STEP 2: DATA REQUISITION
    # --------------------------------------------------------

    print("\n[2] DATA REQUISITION")

    requisition = create_requisition()

    if not requisition.get("call_records") and not requisition.get("signal_data"):
        print("\n[!] No data type was authorised.")
        print("[!] Forensic workflow stopped.")
        return

    # --------------------------------------------------------
    # STEP 3: DATA ACQUISITION
    # --------------------------------------------------------

    print("\n[3] DATA ACQUISITION")

    evidence = acquire_data(requisition)

    if evidence is None:
        print("\n[!] Evidence acquisition failed.")
        print("[!] Forensic workflow stopped.")
        return

    # --------------------------------------------------------
    # STEP 4: DATA VALIDATION
    # --------------------------------------------------------

    print("\n[4] DATA VALIDATION")

    validation = validate_data(
        evidence,
        requisition
    )

    if validation is None:
        print("\n[!] Data validation failed.")
        print("[!] Forensic workflow stopped.")
        return

    # --------------------------------------------------------
    # STEP 5: INTEGRITY VERIFICATION
    # --------------------------------------------------------

    print("\n[5] INTEGRITY VERIFICATION")

    integrity = verify_integrity(evidence)

    if integrity is None:
        print("\n[!] Integrity verification failed.")
        print("[!] Forensic workflow stopped.")
        return

    # --------------------------------------------------------
    # STEP 6: FORENSIC ANALYSIS
    # --------------------------------------------------------

    print("\n[6] FORENSIC ANALYSIS")

    analysis_results = run_analysis(
        validation["data"],
        requisition
    )

    if analysis_results is None:
        print("\n[!] Analysis failed.")
        print("[!] Forensic workflow stopped.")
        return

    # --------------------------------------------------------
    # STEP 7: REPORT GENERATION
    # --------------------------------------------------------

    print("\n[7] REPORT GENERATION")

    report = generate_report(
        consent,
        requisition,
        evidence,
        validation,
        integrity,
        analysis_results
    )

    if report is None:
        print("\n[!] Report generation failed.")
        print("[!] Forensic workflow stopped.")
        return

    # --------------------------------------------------------
    # PIPELINE STATUS
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("              PIPELINE STATUS")
    print("=" * 60)

    print("[✓] Consent granted")
    print("[✓] Data requisition created")
    print("[✓] Evidence acquired")
    print("[✓] Data validation passed")
    print("[✓] SHA-256 integrity verified")
    print("[✓] Forensic analysis completed")
    print("[✓] Report generated")

    # --------------------------------------------------------
    # EVIDENCE INFORMATION
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("             EVIDENCE INFORMATION")
    print("=" * 60)

    print(f"Filename         : {evidence['filename']}")
    print(f"Evidence path    : {evidence['evidence_path']}")
    print(f"File size        : {evidence['size_bytes']} bytes")
    print(f"Records          : {validation['records']}")
    print(f"SHA-256          : {integrity['hash']}")
    print(f"Report           : {report['report_path']}")

    # --------------------------------------------------------
    # ANALYSIS SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("              ANALYSIS SUMMARY")
    print("=" * 60)

    calls = analysis_results.get("calls")

    if calls:
        print(f"Total records     : {calls['total_records']}")
        print(f"Incoming calls    : {calls['incoming']}")
        print(f"Outgoing calls    : {calls['outgoing']}")
        print(f"Missed calls      : {calls['missed']}")
        print(f"Total duration    : {calls['total_duration']} seconds")

    signal = analysis_results.get("signal")

    if signal:
        print(f"Average RSRP      : {signal['average_rsrp']:.2f} dBm")
        print(f"Strongest signal  : {signal['strongest_rsrp']} dBm")
        print(f"Weakest signal    : {signal['weakest_rsrp']} dBm")

    network = analysis_results.get("network")

    if network:

        network_types = network.get("network_types")

        if network_types:
            print("\nNetwork types:")

            for network_type, count in network_types.items():
                print(f"  {network_type}: {count}")

        cell_usage = network.get("cell_usage")

        if cell_usage:
            print("\nCell usage:")

            for cell, count in cell_usage.items():
                print(f"  {cell}: {count}")

    # --------------------------------------------------------
    # HOUR 4 COMPLETION
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("              HOUR 4 COMPLETE")
    print("=" * 60)

    print("\nCompleted outputs:")
    print("  -> Forensic report")
    print("  -> Evidence summary")
    print("  -> Investigation review")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
