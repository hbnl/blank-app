import streamlit as st
import datetime

# --- SETTINGS & STYLING ---
st.set_page_config(page_title="FTTP Slow Speed Workflow", page_icon="🌐", layout="centered")

def display_final_result(notes, script):
    """Formats the final output in a clean, copy-pasteable UI."""
    st.divider()
    st.subheader("🚀 SUGGESTED SCRIPT FOR CUSTOMER")
    st.info(f"**Agent says:** \"{script}\"")
    
    st.subheader("📋 COPY-PASTE CASE NOTES")
    case_notes = (
        f"DIAGNOSTIC DATE: {notes['timestamp']}\n"
        f"SYNC STATUS:    {notes['sync_status']}\n"
        f"DEVICE RSSI:    {notes['rssi']}\n"
        f"WIFI BAND:      {notes['band']}\n"
        f"WIFI STANDARD:  {notes['standard'].upper()}\n"
        f"OUTCOME:        {notes['recommendation']}"
    )
    st.code(case_notes, language="text")
    if st.button("Start New Diagnosis"):
        st.rerun()

def wifi_diagnostic_tool(sync_already_verified):
    """Phase 2: Mosaic WiFi & End User Device Diagnosis."""
    st.header("PHASE 2: Mosaic WiFi & Device Diagnosis")
    
    notes = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "sync_status": "STABLE/IN-RANGE" if sync_already_verified else "Unknown",
        "rssi": "N/A",
        "band": "Unknown",
        "standard": "Unknown",
        "recommendation": ""
    }

    # --- Gateway Sync Logic ---
    if not sync_already_verified:
        sync_ok = st.radio("Is the FTTP Sync Speed in Mosaic within range?", ["Select...", "Yes", "No"], key="sync_ok")
        if sync_ok == "No":
            notes["sync_status"] = "BELOW GUARANTEE"
            notes["recommendation"] = "RAISE LINE FAULT"
            display_final_result(notes, "I've detected the speed reaching your home is below our guarantee. I am raising a line fault.")
            return
        elif sync_ok == "Select...": return
        notes["sync_status"] = "STABLE/IN-RANGE"

    # --- Phase 2: Signal Strength (RSSI) ---
    st.subheader("Signal Strength Check")
    
    rssi_val = st.number_input("Enter device Signal Strength (RSSI) from Mosaic (e.g., -40 to -90):", value=0, step=1)
    
    if rssi_val < 0: 
        notes["rssi"] = f"{rssi_val} dBm"
        
        if rssi_val <= -67: 
            in_room = st.radio("Is the customer in the same room as the router?", ["Select...", "Yes", "No"], key="in_room")
            if in_room == "Yes":
                notes["recommendation"] = "REPOSITION ROUTER / CHECK INTERFERENCE"
                display_final_result(notes, "Signal weak despite proximity. Advised repositioning away from obstacles.")
            elif in_room == "No":
                notes["recommendation"] = "MESH EXTENDER REQUIRED"
                display_final_result(notes, "Poor coverage due to distance. Advised on Mesh system.")
            return

        # --- NEW Phase 3: Band Validation ---
        st.divider()
        st.subheader("Band Validation")
        on_5ghz = st.radio("Is the device connected to the 5GHz band?", ["Select...", "Yes", "No"], key="on_5ghz")
        
        if on_5ghz == "No":
            supports_5g = st.radio("Does the device hardware support 5GHz/WiFi 5 or 6?", ["Select...", "Yes", "No"], key="supports_5g")
            if supports_5g == "Yes":
                notes["band"] = "2.4GHz (STUCK)"
                notes["recommendation"] = "SPLIT WIRELESS BANDS"
                display_final_result(notes, "Your device is stuck on the slower 2.4GHz frequency. I recommend splitting the wireless bands to force a 5GHz connection.")
                return
            elif supports_5g == "No":
                notes["band"] = "2.4GHz (LEGACY)"
                notes["recommendation"] = "DEVICE LIMITATION"
                display_final_result(notes, "This device only supports 2.4GHz. It is physically incapable of reaching the higher speeds of your FTTP package.")
                return
            return
        elif on_5ghz == "Yes":
            notes["band"] = "5GHz"

        # --- Phase 4: Device Capacity ---
        st.divider()
        st.subheader("Network Load")
        device_count = st.number_input("How many devices are currently connected in Mosaic?", min_value=0, step=1)
        if device_count > 20:
            notes["recommendation"] = "HIGH CONGESTION - ADVISE ETHERNET"
            display_final_result(notes, "High device density detected. Advised Ethernet for stationary devices to free up airtime.")
            return

        # --- Phase 5: WiFi Standard ---
        st.divider()
        st.subheader("WLAN Adapter Check")
        standard = st.selectbox("What is the WiFi Standard in Mosaic?", ["Select...", "ax", "ac", "n", "g"], index=0)
        if standard != "Select...":
            notes["standard"] = standard
            if standard in ['n', 'g']:
                notes["recommendation"] = f"LEGACY DEVICE LIMITATION ({standard.upper()})"
                display_final_result(notes, f"Device using legacy standard ({standard.upper()}). Hardware bottleneck detected.")
            elif standard == 'ac':
                notes["recommendation"] = "WIFI 5 (OPTIMAL FOR 1440P)"
                display_final_result(notes, "Telemetry shows WiFi 5 (802.11ac). Advise on wireless speed ceilings.")
            elif standard == 'ax':
                notes["recommendation"] = "WIFI 6 (ULTIMATE)"
                display_final_result(notes, "Top-tier connection. Check for device-side software issues (VPN/Updates).")

def main():
    st.title("🌐 FTTP Slow Speed Troubleshooter")
    
    # GDPR Sidebar
    gdpr_ok = st.sidebar.radio("Step 1: GDPR Checks OK?", ["No", "Yes"])
    if gdpr_ok == "No":
        st.warning("⚠️ Please complete GDPR authentication to proceed.")
        return

    # Triage
    st.header("Step 2 & 3: Initial Triage")
    router_issue = st.radio("Is the slow speed isolated to the router/SDG?", ["Select...", "Yes", "No"])

    if router_issue == "No":
        wifi_diagnostic_tool(sync_already_verified=False)
        return
    elif router_issue == "Select...":
        return

    # Physicals & Line Tests
    st.header("Line Diagnostics")
    ont_ok = st.radio("Step 4: ONT OK (No red lights)?", ["Select...", "Yes", "No"])
    if ont_ok == "No":
        st.error("Physical fault detected. Raise repair ticket.")
        return
    
    if ont_ok == "Yes":
        m1_rag = st.radio("Step 7: Are 'Circuit' and 'Router' GREEN in M1?", ["Select...", "Yes", "No"])
        if m1_rag == "No":
            st.error("Circuit/Router fault detected. Raise repair ticket.")
            return
        
        if m1_rag == "Yes":
            speed_test_ok = st.radio("Step 8: Is Speed Test GREEN (within 15% of package)?", ["Select...", "Yes", "No"])
            if speed_test_ok == "Yes":
                st.success("Speeds to router are optimal. Moving to WiFi diagnosis...")
                wifi_diagnostic_tool(sync_already_verified=True)
            elif speed_test_ok == "No":
                st.info("Investigate provisioning (Step 9) or speed trends (Step 10) in M1.")

if __name__ == "__main__":
    main()