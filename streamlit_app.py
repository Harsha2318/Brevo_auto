import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from brevo_automation import AutomationAgent
from config import API_KEY
import requests

st.set_page_config(
    page_title="Brevo Automation Dashboard",
    page_icon="✉️",
    layout="wide"
)

# Initialize the automation agent
@st.cache_resource
def init_agent():
    return AutomationAgent(API_KEY)

agent = init_agent()

@st.cache_data
def get_folders():
    """Fetch folders dynamically from Brevo API."""
    try:
        response = requests.get(
            f"https://api.brevo.com/v3/contacts/folders",
            headers={"Accept": "application/json", "api-key": API_KEY}
        )
        if response.status_code == 200:
            folders = response.json().get("folders", [])
            return {folder["name"]: folder["id"] for folder in folders}
        else:
            return {"Default": 1}
    except:
        return {"Default": 1}

@st.cache_data
def get_verified_senders():
    """Fetch verified senders dynamically from Brevo API."""
    try:
        response = requests.get(
            f"https://api.brevo.com/v3/senders",
            headers={"Accept": "application/json", "api-key": API_KEY}
        )
        if response.status_code == 200:
            senders = response.json().get("senders", [])
            return {s["name"]: s["email"] for s in senders if s.get("active")}
        else:
            return {}
    except:
        return {}

@st.cache_data
def get_templates():
    """Fetch available campaign templates dynamically using AutomationAgent."""
    templates = agent.get_templates()
    return {template["name"]: template["id"] for template in templates}

# Sidebar
st.sidebar.title("✉️ Brevo Automation")
menu = st.sidebar.selectbox(
    "Select Operation",
    ["Home", "Import Contacts", "Schedule Campaigns", "Execute Workflow"]
)

# Main area header
st.title("Brevo Email Automation Dashboard")

# Ensure global initialization of senders and templates
senders = get_verified_senders()
templates = get_templates()

if menu == "Home":
    st.markdown("""
    ## Welcome to Brevo Email Automation!
    
    This dashboard helps you manage your email campaigns efficiently:
    
    - **Import Contacts**: Upload your CSV file and create contact lists
    - **Schedule Campaigns**: Set up email campaigns with custom templates
    - **Execute Workflow**: Run complete email campaign workflows
    
    ### Getting Started
    1. Select an operation from the sidebar
    2. Follow the instructions to configure your campaign
    3. Review and submit your settings
    
    Need help? Check out the documentation below.
    """)
    
    st.info("Make sure you have your CSV file ready before starting!")

elif menu == "Import Contacts":
    st.header("Import Contacts")
    
    # Add folder selection
    folders = get_folders()
    selected_folder = st.selectbox(
        "Select Folder",
        options=list(folders.keys()),
        index=0
    )
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    list_name = st.text_input("List Name", "My Contact List")
    
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with open("temp_contacts.csv", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Show preview of the data
        df = pd.read_csv("temp_contacts.csv")
        st.write("Preview of uploaded data:")
        st.dataframe(df.head())
        
        if st.button("Import Contacts"):
            with st.spinner("Importing contacts..."):
                result = agent.import_contacts(
                    "temp_contacts.csv", 
                    list_name,
                    folder_id=folders[selected_folder]
                )
                
                if result["status"] == "success":
                    st.success(result["message"])
                    # Store the list ID for campaign scheduling
                    st.session_state['last_list_id'] = result["list_id"]
                else:
                    st.error(f"Import failed: {result['message']}")

elif menu == "Schedule Campaigns":
    st.header("Schedule Campaign")

    campaign_name = st.text_input("Campaign Name", "My Campaign")
    template_name = st.selectbox("Select Template", options=list(templates.keys()))
    template_id = templates.get(template_name, 0)

    # Use last created list ID if available
    default_list_id = st.session_state.get('last_list_id', 1)
    list_id = st.number_input("List ID", min_value=1, value=default_list_id)

    col1, col2 = st.columns(2)

    with col1:
        send_date = st.date_input("Send Date")
        send_time = st.time_input("Send Time")

    with col2:
        if senders:
            sender_name = st.selectbox("Select Sender", options=list(senders.keys()))
            sender_email = senders[sender_name]
        else:
            st.error("No verified senders found. Please verify a sender in Brevo first.")
            sender_name = ""
            sender_email = ""

    # Validate Template ID and Send Date before scheduling
    if not agent.validate_template_id(template_id):
        st.error(f"Template ID {template_id} does not exist. Please select a valid template.")
    else:
        send_datetime = datetime.combine(send_date, send_time)
        current_time = datetime.now()
        
        # Add a 15-minute buffer to allow for processing time
        min_schedule_time = current_time + timedelta(minutes=15)
        
        if send_datetime < min_schedule_time:
            st.warning(f"Please schedule the campaign at least 15 minutes in the future. Current time: {current_time.strftime('%Y-%m-%d %H:%M')})")
        
        if st.button("Schedule Campaign"):
                if not sender_name or not sender_email:
                    st.error("Sender name and email must be provided.")
                else:
                    with st.spinner("Scheduling campaign..."):
                        result = agent.schedule_campaign(
                            campaign_name=campaign_name,
                            template_id=template_id,
                            list_id=list_id,
                            send_date=send_datetime,
                            sender_name=sender_name,
                            sender_email=sender_email
                        )

                        if result["status"] == "success":
                            st.success(result["message"])
                        else:
                            st.error(f"Scheduling failed: {result['message']}")

elif menu == "Execute Workflow":
    st.header("Execute Complete Workflow")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    list_name = st.text_input("List Name", "Event Participants List")

    # Template IDs
    template_names = list(templates.keys())
    col1, col2, col3 = st.columns(3)
    with col1:
        tuesday_template_name = st.selectbox("Tuesday Template", options=template_names)
        tuesday_template = templates.get(tuesday_template_name, 0)
    with col2:
        friday_template_name = st.selectbox("Friday Template", options=template_names)
        friday_template = templates.get(friday_template_name, 0)
    with col3:
        post_event_template_name = st.selectbox("Post-Event Template", options=template_names)
        post_event_template = templates.get(post_event_template_name, 0)

    # Event date
    event_end_date = st.date_input("Event End Date")

    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with open("temp_workflow.csv", "wb") as f:
            f.write(uploaded_file.getvalue())

        if st.button("Execute Workflow"):
            with st.spinner("Executing workflow..."):
                selected_templates = {
                    "tuesday": tuesday_template,
                    "friday": friday_template,
                    "post_event": post_event_template
                }

                result = agent.execute_workflow(
                    csv_path="temp_workflow.csv",
                    list_name=list_name,
                    selected_templates=selected_templates,
                    sender_info={"name": "", "email": ""},
                    event_end_date=datetime.combine(event_end_date, datetime.min.time())
                )

                st.subheader("Workflow Results")
                st.write("Steps Executed:")
                for step in result["steps"]:
                    st.write(f"✓ {step}")

                st.write("Actions Taken:")
                for action in result["actions_taken"]:
                    st.info(action)

                if result["result"] == "Complete workflow executed successfully":
                    st.success(result["result"])
                else:
                    st.error(result["result"])

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Made by hidevs")
