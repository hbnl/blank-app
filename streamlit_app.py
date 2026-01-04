import streamlit as st
import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="ISP Helpdesk Diagnostic Tool",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Helper Functions ---
def calculate_bandwidth_capacity(standard, rssi):
    capacity_map = {
        'be': 100, 'ax': 40, 'ac': 15, 'n': 2, 
        'g': 0.5, 'a': 0.5, 'b': 0.1, 'legacy': 0.05
    }
    base = capacity_map.get(standard, 0)
    if rssi <= -60:
        base = base * 0.5
    elif rssi <= -50:
        base = base * 0.8
    return round(base, 2)

def reset_workflows():
    # Clear all session state keys to ensure a fresh start for all workflows
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # Re-initialize basic steps
    st.session_state.tlos_step = 1
    st.session_state.slow_step = 1

# --- Session State Initialization ---
if 'tlos_step' not in st.session_state:
    st.session_state.tlos_step = 1
if 'slow_step' not in st.session_state:
    st.session_state.slow_step = 1
if 'notes' not in st.session_state:
    st.session_state.notes = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "sync_status": "Unknown",
        "reboot_done": "No",
        "scope": "Unknown",
        "rssi": "N/A",
        "rssi_val": -50,
        "band": "Unknown",
        "placement": "Optimal",
        "same_room": "N/A",
        "los": "N/A",
        "standard": "Unknown",
        "standard_name": "Unknown",
        "ping": "N/A",
        "background_data": "None detected",
        "household_load": "Light",
        "recommendation": "General WiFi Optimization"
    }

# --- Sidebar UI ---
with st.sidebar:
    st.title("🛠️ Workflow Selection")
    workflow = st.selectbox(
        "Choose a Diagnostic Path:",
        ["Home", "FTTP TLOS Broadband Troubleshooter", "Slow Speeds Troubleshooter"],
        on_change=reset_workflows
    )

    st.divider()
    st.subheader("📚 Training & Knowledge Base")
    with st.expander("FTTP Architecture Overview"):
        st.write("""
        - **ONT**: Optical Network Terminal (Demarcation point)
        - **SDG**: Smart Digital Gateway (The Router)
        - **Mosaic**: Primary line testing tool
        """)
    with st.expander("WiFi Standards Guide"):
        st.write("""
        - **802.11ax (WiFi 6)**: High capacity
        - **802.11ac (WiFi 5)**: Standard modern speed
        - **802.11n (WiFi 4)**: Legacy, speed bottleneck
        """)
    with st.expander("Red Light Interpretations"):
        st.write("""
        - **LOS Red**: No light received from Exchange
        - **PON Red**: Authentication failure
        - **Power Red**: Internal hardware failure
        """)

# --- Main Application Logic ---

if workflow == "Home":
    st.title("ISP Technical Support Portal")
    st.info("Please select a diagnostic workflow from the sidebar to begin helping the customer.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="System Status", value="All Clear")
    with col2:
        st.metric(label="Wait Time", value="< 2 Mins")

# --- WORKFLOW 1: FTTP TLOS ---
elif workflow == "FTTP TLOS Broadband Troubleshooter":
    st.title("🔴 FTTP TLOS Broadband Troubleshooter")
    st.write("Current Step: ", st.session_state.tlos_step)

    if st.session_state.tlos_step == 1:
        st.subheader("Step 1: Initial Power Check")
        st.info("Agent: 'Can I just check that power is going to the ONT? Are you able to check that the plug is correctly inserted?'")
        if st.button("Power is OK"):
            st.session_state.tlos_step = 2
            st.rerun()
        if st.button("Power is NOT OK"):
            st.error("Outcome: Ensure power is connected. If resolved, end call.")
            if st.button("Reset Workflow"): reset_workflows(); st.rerun()

    elif st.session_state.tlos_step == 2:
        st.subheader("Step 2: Device Connectivity Check")
        st.info("Agent: 'Can you confirm that you are experiencing a loss of service across multiple devices (phone, laptop, TV)?'")
        if st.button("Yes - All devices affected"):
            st.session_state.tlos_step = 3
            st.rerun()
        if st.button("No - Single device only"):
            st.warning("Outcome: Refer to 'Device Connectivity' KB article.")
            if st.button("Back"): st.session_state.tlos_step = 1; st.rerun()

    elif st.session_state.tlos_step == 3:
        st.subheader("Step 3: Mosaic One Care & Physical Check")
        st.warning("Action: Navigate to Mosaic One Care and run line test.")
        st.info("Agent: 'Please check the cables. Green head on the far left of the ONT, and Ethernet next to it connected to the Router WAN port.'")
        
        cables = st.radio("Cabling confirmed correct?", ["Pending", "Yes", "No"])
        ont_red = st.radio("Is the ONT Optical light RED?", ["Pending", "Yes", "No"])

        if cables == "Yes" and ont_red == "No":
            if st.button("Proceed to RAG Status"):
                st.session_state.tlos_step = 4
                st.rerun()
        elif ont_red == "Yes":
            st.error("Outcome: RED Light detected. Check green fibre cable. If persists, follow Service Visit escalation.")
            if st.button("Reset"): reset_workflows(); st.rerun()

    elif st.session_state.tlos_step == 4:
        st.subheader("Step 4: Mosaic RAG Status")
        circuit = st.radio("Is 'Circuit' Status GREEN?", ["Pending", "Yes", "No"])
        router = st.radio("Is 'Router' Status GREEN?", ["Pending", "Yes", "No"])

        if circuit == "Yes" and router == "Yes":
            st.success("Outcome: Connection appears working. Refer to 'Device Connectivity' KB.")
            if st.button("Reset"): reset_workflows(); st.rerun()
        elif circuit == "No" or router == "No":
            if st.button("Proceed to Reboot Step"):
                st.session_state.tlos_step = 5
                st.rerun()

    elif st.session_state.tlos_step == 5:
        st.subheader("Step 5: Reboot Equipment")
        st.info("Agent: 'Please power off both the ONT and the router. Wait 15 seconds, then turn them back on.'")
        if st.button("Reboot Completed"):
            st.session_state.tlos_step = 6
            st.rerun()

    elif st.session_state.tlos_step == 6:
        st.subheader("Step 6: Final Online Check")
        final = st.radio("After 2 minutes, is the circuit now ONLINE?", ["Pending", "Yes", "No"])
        if final == "Yes":
            st.success("Outcome: Service restored by reboot.")
        elif final == "No":
            st.error("Outcome: Still offline. Follow 'Service Visit' escalation process.")
        if st.button("Finish"): reset_workflows(); st.rerun()

# --- WORKFLOW 2: NEW SLOW SPEEDS (UPDATED) ---
elif workflow == "Slow Speeds Troubleshooter":
    st.title("🚀 FTTP & WiFi Diagnostic Tool")
    st.markdown("---")

    # PHASE 1: Validation
    if st.session_state.slow_step == 1:
        st.header("Phase 1: Validation & Initial Remediation")
        gdpr = st.radio("Step 1: Are GDPR checks OK?", ["No", "Yes"], index=0)
        
        if gdpr == "Yes":
            st.info("Step 1.5: Hardware Power Cycle")
            reboot = st.radio("Has the Router AND ONT been power cycled recently?", ["No", "Yes"])
            
            col1, col2 = st.columns(2)
            with col1:
                all_devices = st.selectbox("Step 1.6: Scope of Impact", ["one", "all"])
            with col2:
                router_iso = st.radio("Step 3: Slow speed isolated to router (SDG)?", ["Yes", "No"])

            if st.button("Next Step ➡️"):
                st.session_state.notes["reboot_done"] = reboot
                st.session_state.notes["scope"] = "Whole LAN" if all_devices == "all" else "Single Device"
                
                if reboot == "No":
                    st.warning("ACTION: Ask customer to power cycle BOTH ONT and Router now.")
                
                if router_iso == "No":
                    st.session_state.slow_step = 3  # Skip to WiFi
                else:
                    st.session_state.slow_step = 2  # Continue FTTP flow
                st.rerun()

    # PHASE 2: FTTP Physical & Circuit
    elif st.session_state.slow_step == 2:
        st.header("Phase 2: FTTP Physical & Circuit")
        ont_light = st.radio("Step 4: Is ONT Light Status OK (No RED)?", ["Yes", "No"])
        cables_phys = st.radio("Step 5: Are cables undamaged?", ["Yes", "No"])
        cables_plug = st.radio("Step 6: Are all cables securely plugged in?", ["Yes", "No"])
        m1_rag = st.radio("Step 7: Are 'Circuit' and 'Router' GREEN in M1?", ["Yes", "No"])
        speed_test = st.radio("Step 8: Is Speed Test Result GREEN?", ["Yes", "No"])

        if st.button("Analyze Circuit"):
            if ont_light == "No" or cables_phys == "No":
                st.error("RESULT: Physical Fault. Raise Repair Ticket.")
                st.session_state.notes["recommendation"] = "PHYSICAL FAULT - REPAIR REQ"
                st.session_state.slow_step = 4
            elif m1_rag == "No":
                st.error("RESULT: Non-Green M1. Raise Repair Ticket.")
                st.session_state.notes["recommendation"] = "M1 CIRCUIT ERROR"
                st.session_state.slow_step = 4
            elif speed_test == "No":
                st.session_state.slow_step = 2.5
            else:
                st.success("Line is Green. Moving to WiFi diagnosis...")
                st.session_state.notes["sync_status"] = "STABLE/IN-RANGE"
                st.session_state.slow_step = 3
            st.rerun()

    # PHASE 2.5: Advanced Circuit Analysis
    elif st.session_state.slow_step == 2.5:
        st.header("Phase 2.5: Advanced Circuit Analysis")
        plan_match = st.radio("Step 9: Do 'Plan' and 'Speed Profile' match in M1?", ["Yes", "No"])
        trend = st.radio("Step 10: Is the 'Speed Tests' graph consistent?", ["Yes", "No"])
        
        if st.button("Finalize Circuit Check"):
            if plan_match == "No":
                st.session_state.notes["recommendation"] = "PROVISIONING MISMATCH"
                st.session_state.slow_step = 4
            elif trend == "No":
                st.session_state.notes["recommendation"] = "MAINTENANCE TREND DETECTED"
                st.session_state.slow_step = 4
            else:
                st.session_state.notes["sync_status"] = "STABLE/IN-RANGE"
                st.session_state.slow_step = 3
            st.rerun()

    # PHASE 3: WiFi & Device Diagnosis
    elif st.session_state.slow_step == 3:
        st.header("Phase 3: WiFi & Device Telemetry")
        col1, col2 = st.columns(2)
        with col1:
            rssi_val = st.number_input("Device Signal (RSSI) from Mosaic", value=-50, max_value=0, min_value=-100)
            on_5g = st.radio("Is device on 5GHz band?", ["Yes", "No"])
            enclosed = st.radio("Is router in a cupboard/behind TV/on floor?", ["No", "Yes"])
        
        with col2:
            std = st.selectbox("WiFi Standard", ['be', 'ax', 'ac', 'n', 'g', 'a', 'b', 'legacy'])
            gaming = st.radio("Reporting gaming lag?", ["No", "Yes"])
            load = st.radio("Other high-load users active?", ["No", "Yes"])

        st.subheader("Physical Environment Check")
        if on_5g == "Yes":
            st.warning("5GHz is high-speed but easily blocked by obstacles.")
            same_rm = st.radio("Is the customer in the same room as the router?", ["Yes", "No"])
            clear_los = st.radio("Is there a clear line of sight (no walls/mirrors)?", ["Yes", "No"])
        else:
            same_rm = "N/A"
            clear_los = "N/A"

        if st.button("Generate Final Report"):
            st.session_state.notes.update({
                "rssi_val": rssi_val,
                "rssi": f"{rssi_val} dBm",
                "standard": std,
                "band": "5GHz" if on_5g == "Yes" else "2.4GHz",
                "same_room": same_rm,
                "los": clear_los
            })
            
            if rssi_val <= -67:
                st.session_state.notes["recommendation"] = "MESH EXTENDER REQUIRED"
            elif enclosed == "Yes":
                st.session_state.notes["recommendation"] = "ROUTER PLACEMENT ISSUE"
            elif on_5g == "Yes" and (same_rm == "No" or clear_los == "No"):
                st.session_state.notes["recommendation"] = "PHYSICAL OBSTRUCTION - 5GHz"
            elif load == "Yes":
                st.session_state.notes["recommendation"] = "CONCURRENT USAGE LIMIT"
            else:
                st.session_state.notes["recommendation"] = "GENERAL WIFI OPTIMIZATION"
                
            st.session_state.slow_step = 4
            st.rerun()

    # PHASE 4: Results
    elif st.session_state.slow_step == 4:
        st.header("📋 Diagnostic Results")
        notes = st.session_state.notes
        streams = calculate_bandwidth_capacity(notes['standard'], notes['rssi_val'])
        
        st.success(f"**Final Outcome:** {notes['recommendation']}")
        
        st.subheader("🚀 Suggested Script for Customer")
        st.code(f"Your line tests are healthy. However, your speed is being impacted by {notes['recommendation'].lower()}. We recommend repositioning for better line-of-sight to the router.")

        st.subheader("📋 Copy-Paste Case Notes")
        case_summary = f"""
DIAGNOSTIC DATE: {notes['timestamp']}
IMPACT SCOPE:    {notes['scope']}
SYNC STATUS:     {notes['sync_status']}
HW REBOOTED:     {notes['reboot_done']}
DEVICE RSSI:     {notes['rssi']}
WLAN BAND:       {notes['band']}
PLACEMENT:       {notes['placement']}
SAME ROOM (5G):  {notes['same_room']}
LINE OF SIGHT:   {notes['los']}
WIFI STANDARD:   {notes['standard'].upper()}
EST. CAPACITY:   ~{streams} simultaneous 4K streams
FINAL OUTCOME:   {notes['recommendation']}
        """
        st.code(case_summary)

        if st.button("Start New Troubleshooting"):
            reset_workflows()
            st.rerun()