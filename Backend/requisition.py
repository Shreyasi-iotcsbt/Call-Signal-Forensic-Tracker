def create_requisition():

    print("\n========== DATA REQUISITION ==========")

    call_data = input(
        "Call records? (Y/N): "
    ).strip().upper() == "Y"

    signal_data = input(
        "Signal/network data? (Y/N): "
    ).strip().upper() == "Y"

    requisition = {
        "call_records": call_data,
        "signal_data": signal_data
    }

    print("\n[+] Requisition created.")

    return requisition
