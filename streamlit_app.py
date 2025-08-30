import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import os
try:
    from brevo_automation import AutomationAgent
    from config import API_KEY
except ModuleNotFoundError:
    # Fallback for Streamlit Cloud: use environment variable directly
    from brevo_automation import AutomationAgent
    API_KEY = os.environ.get("BREVO_API_KEY", "")
import os

# Add import for ApiException
try:
    from sib_api_v3_sdk.rest import ApiException
except ImportError:
    ApiException = Exception  # fallback if SDK not available

st.set_page_config(
    page_title="Brevo Automation Dashboard",
    page_icon="✉️",
    layout="wide"
)

# Initialize the automation agent with error handling
@st.cache_resource
def init_agent():
    try:
        return AutomationAgent(API_KEY if API_KEY is not None else "")
    except ApiException as e:
        st.error("Failed to initialize Brevo AutomationAgent. Please check your API key and network connectivity.")
        st.stop()
    except Exception as e:
        st.error(f"Unexpected error initializing AutomationAgent: {e}")
        st.stop()

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


    # Option to choose data source
    data_source = st.radio("Select Data Source", ["Upload CSV", "Fetch from API"], horizontal=True)
    list_name = st.text_input("List Name", "My Contact List")

    # Available categories for API fetch
    category_options = [
        "users_with_unsubmitted_projects",
        "users_with_incomplete_courses",
        "users_close_to_completing_courses",
        "users_with_unstarted_roadmaps",
        "users_with_incomplete_roadmaps",
        "users_without_interviews",
        "users_without_resumes",
        "users_for_new_features",
        "users_without_prompt_engineering",
        "users_with_high_scores",
        "users_in_talent_pool",
        "users_with_low_talent_scores",
        "users_with_incomplete_profiles",
        "users_without_mock_interviews",
        "users_close_to_leaderboard_top",
        "users_with_stalled_projects",
        "users_without_project_applications",
        "inactive_users",
        "users_for_new_problems",
        "top_leaderboard_users",
        "users_inactive_mentorship"
    ]
    USER_RETENTION_API_URL = os.getenv("USER_RETENTION_API_URL", "http://localhost:5000/api/user-retention/emails")

    df = None
    if data_source == "Upload CSV":
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            # Save the uploaded file temporarily
            with open("temp_contacts.csv", "wb") as f:
                f.write(uploaded_file.getvalue())
            # Show preview of the data
            df = pd.read_csv("temp_contacts.csv")
            st.write("Preview of uploaded data:")
            st.dataframe(df.head())
            st.session_state['import_df'] = df
    else:
        selected_category = st.selectbox("Select Category", options=category_options, index=0)
        api_url = f"{USER_RETENTION_API_URL}/{selected_category}"
        if st.button("Fetch Emails"):
            try:
                response = requests.get(api_url)
                if response.status_code == 200:
                    data = response.json()
                    emails = data.get("emails", [])
                    if isinstance(emails, list):
                        df = pd.DataFrame({"email": list(set(emails))})
                        st.write(f"Preview of fetched emails for {selected_category}:")
                        st.dataframe(df.head())
                        st.session_state['import_df'] = df
                    else:
                        st.error("API did not return a list of emails.")
                else:
                    st.error(f"API request failed: {response.status_code}")
            except Exception as e:
                st.error(f"Error fetching from API: {e}")

    import_df = st.session_state.get('import_df', None)
    if import_df is not None:
        if st.button("Import Contacts"):
            with st.spinner("Importing contacts..."):
                temp_path = "temp_contacts.csv"
                import_df.to_csv(temp_path, index=False)
                result = agent.import_contacts(
                    temp_path,
                    list_name,
                    folder_id=folders[selected_folder]
                )
                if result["status"] == "success":
                    st.success(result["message"])
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

    # Option to choose data source
    data_source = st.radio("Select Data Source", ["Upload CSV", "Fetch from API"], horizontal=True)
    list_name = st.text_input("List Name", "Event Participants List")

    # Available categories for API fetch
    category_options = [
        "users_with_unsubmitted_projects",
        "users_with_incomplete_courses",
        "users_close_to_completing_courses",
        "users_with_unstarted_roadmaps",
        "users_with_incomplete_roadmaps",
        "users_without_interviews",
        "users_without_resumes",
        "users_for_new_features",
        "users_without_prompt_engineering",
        "users_with_high_scores",
        "users_in_talent_pool",
        "users_with_low_talent_scores",
        "users_with_incomplete_profiles",
        "users_without_mock_interviews",
        "users_close_to_leaderboard_top",
        "users_with_stalled_projects",
        "users_without_project_applications",
        "inactive_users",
        "users_for_new_problems",
        "top_leaderboard_users",
        "users_inactive_mentorship"
    ]
    USER_RETENTION_API_URL = os.getenv("USER_RETENTION_API_URL", "http://localhost:5000/api/user-retention/emails")

    df = None
    if data_source == "Upload CSV":
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            with open("temp_workflow.csv", "wb") as f:
                f.write(uploaded_file.getvalue())
            df = pd.read_csv("temp_workflow.csv")
            st.write("Preview of uploaded data:")
            st.dataframe(df.head())
            st.session_state['workflow_df'] = df
    else:
        selected_category = st.selectbox("Select Category", options=category_options, index=0)
        api_url = f"{USER_RETENTION_API_URL}/{selected_category}"
        if st.button("Fetch Emails"):
            try:
                response = requests.get(api_url)
                if response.status_code == 200:
                    data = response.json()
                    emails = data.get("emails", [])
                    if isinstance(emails, list):
                        df = pd.DataFrame({"email": list(set(emails))})
                        st.write(f"Preview of fetched emails for {selected_category}:")
                        st.dataframe(df.head())
                        st.session_state['workflow_df'] = df
                    else:
                        st.error("API did not return a list of emails.")
                else:
                    st.error(f"API request failed: {response.status_code}")
            except Exception as e:
                st.error(f"Error fetching from API: {e}")

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

    workflow_df = st.session_state.get('workflow_df', None)
    if workflow_df is not None:
        if st.button("Execute Workflow"):
            with st.spinner("Executing workflow..."):
                temp_path = "temp_workflow.csv"
                workflow_df.to_csv(temp_path, index=False)
                selected_templates = {
                    "tuesday": tuesday_template,
                    "friday": friday_template,
                    "post_event": post_event_template
                }

                result = agent.execute_workflow(
                    csv_path=temp_path,
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
