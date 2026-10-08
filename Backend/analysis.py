# ============================================================
# CALL & SIGNAL FORENSIC TRACKER
# Analysis Module
# ============================================================

import pandas as pd


# ============================================================
# CALL ANALYSIS
# ============================================================

def analyse_calls(data):

    print("\n" + "=" * 60)
    print("                 CALL ANALYSIS")
    print("=" * 60)

    if data is None or data.empty:
        print("[!] No data available.")
        return None

    total_calls = len(data)

    incoming = 0
    outgoing = 0
    missed = 0

    if "call_type" in data.columns:

        incoming = (
            data["call_type"]
            .astype(str)
            .str.upper()
            .eq("INCOMING")
            .sum()
        )

        outgoing = (
            data["call_type"]
            .astype(str)
            .str.upper()
            .eq("OUTGOING")
            .sum()
        )

        missed = (
            data["call_type"]
            .astype(str)
            .str.upper()
            .eq("MISSED")
            .sum()
        )

    total_duration = 0

    if "duration_seconds" in data.columns:

        total_duration = pd.to_numeric(
            data["duration_seconds"],
            errors="coerce"
        ).fillna(0).sum()

    print(f"\nTotal records     : {total_calls}")
    print(f"Incoming calls    : {incoming}")
    print(f"Outgoing calls    : {outgoing}")
    print(f"Missed calls      : {missed}")
    print(f"Total duration    : {total_duration} seconds")

    return {
        "total_records": int(total_calls),
        "incoming": int(incoming),
        "outgoing": int(outgoing),
        "missed": int(missed),
        "total_duration": float(total_duration)
    }


# ============================================================
# SIGNAL ANALYSIS
# ============================================================

def analyse_signal(data):

    print("\n" + "=" * 60)
    print("                SIGNAL ANALYSIS")
    print("=" * 60)

    if data is None or data.empty:
        print("[!] No data available.")
        return None

    if "rsrp" not in data.columns:
        print("[!] Signal strength data unavailable.")
        return None

    signal = pd.to_numeric(
        data["rsrp"],
        errors="coerce"
    ).dropna()

    if signal.empty:
        print("[!] No valid signal values found.")
        return None

    average_signal = signal.mean()
    strongest_signal = signal.max()
    weakest_signal = signal.min()

    print(f"\nAverage RSRP     : {average_signal:.2f} dBm")
    print(f"Strongest signal : {strongest_signal} dBm")
    print(f"Weakest signal   : {weakest_signal} dBm")

    return {
        "average_rsrp": float(average_signal),
        "strongest_rsrp": float(strongest_signal),
        "weakest_rsrp": float(weakest_signal)
    }


# ============================================================
# NETWORK ANALYSIS
# ============================================================

def analyse_network(data):

    print("\n" + "=" * 60)
    print("                NETWORK ANALYSIS")
    print("=" * 60)

    if data is None or data.empty:
        print("[!] No data available.")
        return None

    result = {}

    if "radio_type" in data.columns:

        network_counts = (
            data["radio_type"]
            .astype(str)
            .value_counts()
        )

        print("\nNetwork types:")

        for network, count in network_counts.items():
            print(f"  {network}: {count}")

        result["network_types"] = network_counts.to_dict()

    if "cell_id" in data.columns:

        cell_counts = (
            data["cell_id"]
            .astype(str)
            .value_counts()
        )

        print("\nCell usage:")

        for cell, count in cell_counts.items():
            print(f"  {cell}: {count}")

        result["cell_usage"] = cell_counts.to_dict()

    return result


# ============================================================
# COMPLETE ANALYSIS
# ============================================================

def run_analysis(data):

    print("\n" + "=" * 60)
    print("              FORENSIC DATA ANALYSIS")
    print("=" * 60)

    call_results = analyse_calls(data)

    signal_results = analyse_signal(data)

    network_results = analyse_network(data)

    analysis_results = {
        "calls": call_results,
        "signal": signal_results,
        "network": network_results
    }

    print("\n[✓] Analysis completed successfully.")

    return analysis_results