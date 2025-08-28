import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import pandas as pd
import datetime
import json
import os
import requests
from typing import Dict, List, Optional, Union

class AutomationAgent:
    def get_templates(self) -> List[Dict]:
        """
        Fetch all existing email templates from Brevo.
        Returns:
            List[Dict]: List of email templates with id and name.
        """
        try:
            response = requests.get(
                "https://api.brevo.com/v3/smtp/templates",
                headers={
                    "Accept": "application/json",
                    "api-key": self.api_key
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                templates = []
                for template in data.get('templates', []):
                    templates.append({
                        "id": template.get('id'),
                        "name": template.get('name')
                    })
                print(f"Successfully fetched {len(templates)} templates")
                return templates
            else:
                print(f"Failed to fetch templates. Status code: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error fetching templates: {e}")
            return []
    def __init__(self, api_key: str):
        """Initialize the Automation Agent with Brevo API credentials."""
        self.api_key = api_key
        self.api_client = None
        self.contacts_api = None
        self.campaigns_api = None
        self.configure_api()
        
    def configure_api(self):
        """Configure the Brevo API client."""
        try:
            # Initialize configuration
            self.configuration = sib_api_v3_sdk.Configuration()
            self.configuration.api_key['api-key'] = self.api_key
            
            # Initialize API client
            self.api_client = sib_api_v3_sdk.ApiClient(self.configuration)
            
            # Initialize API instances with configured client
            self.contacts_api = sib_api_v3_sdk.ContactsApi(self.api_client)
            self.campaigns_api = sib_api_v3_sdk.EmailCampaignsApi(self.api_client)
            
            # Test API connection with a simple call
            result = self.contacts_api.get_contacts(limit=1)
            if result is None:
                raise Exception("Could not connect to Brevo API")
                
            print("API configured successfully")
            
        except ApiException as e:
            error_msg = e.body if hasattr(e, 'body') else str(e)
            self._handle_error(f"API configuration failed - API Error: {error_msg}", e)
            raise
        except Exception as e:
            self._handle_error(f"API configuration failed - Error: {str(e)}", e)
            raise

    def import_contacts(self, csv_path: str, list_name: str, folder_id: int = 1) -> Dict:
        """
        Import contacts from a CSV file into Brevo.
        
        Args:
            csv_path (str): Path to the CSV file containing contacts
            list_name (str): Name for the new list to be created
            folder_id (int): ID of the folder to create the list in (default: 1)
            
        Returns:
            Dict: Response containing status and list ID
        """
        try:
            # First create a list
            create_list = {
                "name": list_name,
                "folderId": folder_id
            }
            
            list_response = self.contacts_api.create_list(create_list)
            list_id = list_response.id
            
            # Read the CSV file
            with open(csv_path, 'rb') as file:
                file_content = file.read()
            
            # Import contacts to the list
            import_data = {
                "listIds": [list_id],
                "fileBody": file_content.decode('utf-8'),
                "updateExistingContacts": True
            }
            
            import_response = self.contacts_api.import_contacts(import_data)
            
            return {
                "status": "success",
                "message": f"Created list '{list_name}' and imported contacts",
                "list_id": list_id
            }
            
        except Exception as e:
            return self._handle_error("Contact import failed", e)

    def validate_template_id(self, template_id: int) -> bool:
        """
        Validate if the provided Template ID exists in Brevo.
        Args:
            template_id (int): The Template ID to validate.
        Returns:
            bool: True if the Template ID exists, False otherwise.
        """
        try:
            response = requests.get(
                f"https://api.brevo.com/v3/smtp/templates/{template_id}",
                headers={
                    "Accept": "application/json",
                    "api-key": self.api_key
                }
            )
            return response.status_code == 200
        except Exception as e:
            self._handle_error("Failed to fetch campaign templates", e)
            return False

    def activate_template(self, template_id: int) -> Dict:
        """
        Activate a template in Brevo.
        Args:
            template_id (int): The Template ID to activate.
        Returns:
            Dict: Response containing the status of the activation.
        """
        try:
            response = requests.put(
                f"https://api.brevo.com/v3/smtp/templates/{template_id}",
                headers={"Accept": "application/json", "api-key": self.api_key},
                json={"status": "active"}
            )
            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to activate template: {response.text}")
            return {
                "status": "success",
                "message": f"Template ID {template_id} activated successfully."
            }
        except Exception as e:
            return self._handle_error(f"Failed to activate template ID {template_id}", e)

    def schedule_campaign(self, 
                         campaign_name: str, 
                         template_id: int, 
                         list_id: int, 
                         send_date: datetime.datetime,
                         sender_name: str,
                         sender_email: str) -> Dict:
        """
        Schedule an email campaign.
        
        Args:
            campaign_name (str): Name of the campaign
            template_id (int): ID of the email template to use
            list_id (int): ID of the contact list
            send_date (datetime): When to send the campaign
            sender_name (str): Name of the sender
            sender_email (str): Email of the sender
            
        Returns:
            Dict: Response containing campaign status and ID
        """
        try:
            # Log the template ID being used for debugging
            print(f"Scheduling campaign with Template ID: {template_id}")

            # Validate Template ID
            if not self.validate_template_id(template_id):
                return {
                    "status": "error",
                    "message": f"Template ID {template_id} does not exist."
                }

            # Ensure date is in future
            if send_date <= datetime.datetime.now():
                return {
                    "status": "error",
                    "message": "Scheduled date must be in the future."
                }

            # Create campaign data
            campaign_data = {
                "name": campaign_name,
                "templateId": template_id,
                "subject": campaign_name,
                "sender": {
                    "name": sender_name,
                    "email": sender_email
                },
                "recipients": {
                    "listIds": [list_id]
                },
                "scheduledAt": send_date.isoformat() + "Z"
            }

            # Create the campaign using direct API call
            response = requests.post(
                f"https://api.brevo.com/v3/emailCampaigns",
                headers={"Accept": "application/json", "api-key": self.api_key},
                json=campaign_data
            )

            if response.status_code != 201:
                raise Exception(f"Failed to create campaign: {response.text}")

            campaign_id = response.json().get("id")
            if not campaign_id:
                raise ValueError("No campaign ID in response")

            return {
                "status": "success",
                "campaign_id": campaign_id,
                "scheduled_time": send_date.isoformat(),
                "message": f"Campaign '{campaign_name}' scheduled successfully"
            }
        except Exception as e:
            return self._handle_error(f"Failed to schedule campaign '{campaign_name}'", e)

    def execute_workflow(self, 
                        csv_path: str,
                        list_name: str,
                        selected_templates: Dict[str, int],
                        sender_info: Dict[str, str],
                        event_end_date: datetime.datetime) -> Dict:
        """
        Execute the complete email campaign workflow.
        
        Args:
            csv_path (str): Path to contacts CSV
            list_name (str): Name for the contact list
            selected_templates (Dict[str, int]): Dict of template IDs for different emails (selected by user)
            sender_info (Dict[str, str]): Sender name and email
            event_end_date (datetime.datetime): When the event ends
            
        Returns:
            Dict: Complete workflow execution results
        """
        results = {
            "task_understanding": "Execute complete email campaign workflow",
            "steps": [],
            "actions_taken": [],
            "result": {}
        }
        
        try:
            # Step 1: Import Contacts
            import_result = self.import_contacts(csv_path, list_name)
            results["steps"].append("Import contacts")
            results["actions_taken"].append(import_result["message"])
            list_id = import_result["list_id"]
            
            # Calculate campaign dates
            today = datetime.datetime.now()
            
            # Tuesday campaign
            days_until_tuesday = (1 - today.weekday() + 7) % 7
            next_tuesday = today + datetime.timedelta(days=days_until_tuesday)
            next_tuesday = next_tuesday.replace(hour=9, minute=0)
            
            # Friday campaign
            days_until_friday = (4 - today.weekday() + 7) % 7
            next_friday = today + datetime.timedelta(days=days_until_friday)
            next_friday = next_friday.replace(hour=9, minute=0)
            
            # Post-event campaign
            post_event_saturday = event_end_date + datetime.timedelta(days=2)
            post_event_saturday = post_event_saturday.replace(hour=10, minute=0)
            
            # Schedule campaigns using user-selected templates
            campaign_schedules = [
                ("Tuesday Invitation", selected_templates["tuesday"], next_tuesday),
                ("Friday Reminder", selected_templates["friday"], next_friday),
                ("Post-Event Survey", selected_templates["post_event"], post_event_saturday)
            ]
            
            # Ensure templates are active before scheduling campaigns
            for campaign_name, template_id, _ in campaign_schedules:
                if not self.validate_template_id(template_id):
                    activation_result = self.activate_template(template_id)
                    if activation_result["status"] != "success":
                        raise Exception(f"Failed to activate template for {campaign_name}: {activation_result['message']}")
            
            for campaign_name, template_id, send_date in campaign_schedules:
                results["steps"].append(f"Schedule {campaign_name}")
                campaign_result = self.schedule_campaign(
                    campaign_name=campaign_name,
                    template_id=template_id,
                    list_id=list_id,
                    send_date=send_date,
                    sender_name=sender_info["name"],
                    sender_email=sender_info["email"]
                )
                results["actions_taken"].append(campaign_result["message"])
            
            results["result"] = "Complete workflow executed successfully"
            return results
            
        except Exception as e:
            results["result"] = f"Workflow failed: {str(e)}"
            return results

    def _handle_error(self, message: str, error: Exception) -> Dict:
        """Handle and format error responses."""
        error_response = {
            "status": "error",
            "message": message,
            "error_details": str(error)
        }
        print(json.dumps(error_response, indent=2))
        return error_response

# Example usage:
if __name__ == "__main__":
    try:
        import requests
        from config import (
            API_KEY,
            CSV_PATH,
            LIST_NAME,
            TEMPLATES,
            SENDER_INFO
        )

        # Base URL for Brevo API v3
        API_URL = "https://api.brevo.com/v3"
        
        # Headers for all API requests
        HEADERS = {
            "Accept": "application/json",
            "api-key": API_KEY
        }
        
        # Step 1: Create a new list
        create_list_response = requests.post(
            f"{API_URL}/contacts/lists",
            headers=HEADERS,
            json={"name": LIST_NAME, "folderId": 1}
        )
        
        if not create_list_response.ok:
            raise Exception(f"Failed to create list: {create_list_response.text}")
            
        list_id = create_list_response.json()['id']
        print(f"Created list with ID: {list_id}")
        
        # Step 2: Import contacts
        with open(CSV_PATH, 'rb') as file:
            file_content = file.read()
            
            # Prepare the import request
            import_data = {
                'fileBody': file_content.decode('utf-8'),
                'listIds': [list_id],
                'updateExistingContacts': True,
                'emailBlacklist': False
            }
            
            import_response = requests.post(
                f"{API_URL}/contacts/import",
                headers=HEADERS,
                json=import_data
            )
            
            if not import_response.ok:
                raise Exception(f"Failed to import contacts: {import_response.text}")
                
            print("Contact import initiated successfully")
            
            # Step 3: Create campaigns
            # Calculate dates
            today = datetime.datetime.now()
            
            # Tuesday campaign
            days_until_tuesday = (1 - today.weekday() + 7) % 7
            next_tuesday = today + datetime.timedelta(days=days_until_tuesday)
            next_tuesday = next_tuesday.replace(hour=9, minute=0)
            
            # Friday campaign
            days_until_friday = (4 - today.weekday() + 7) % 7
            next_friday = today + datetime.timedelta(days=days_until_friday)
            next_friday = next_friday.replace(hour=9, minute=0)
            
            # Post-event campaign (2 weeks from now)
            event_end_date = datetime.datetime.now() + datetime.timedelta(weeks=2)
            post_event_saturday = event_end_date + datetime.timedelta(days=2)
            post_event_saturday = post_event_saturday.replace(hour=10, minute=0)
            
            # Campaign schedules
            campaigns = [
                {
                    "name": "Tuesday Invitation",
                    "templateId": TEMPLATES["tuesday"],
                    "scheduledAt": next_tuesday.isoformat() + "Z",
                },
                {
                    "name": "Friday Reminder",
                    "templateId": TEMPLATES["friday"],
                    "scheduledAt": next_friday.isoformat() + "Z",
                },
                {
                    "name": "Post-Event Survey",
                    "templateId": TEMPLATES["post_event"],
                    "scheduledAt": post_event_saturday.isoformat() + "Z",
                }
            ]
            
            # Create each campaign
            for campaign in campaigns:
                campaign_data = {
                    "name": campaign["name"],
                    "templateId": campaign["templateId"],
                    "scheduledAt": campaign["scheduledAt"],
                    "subject": campaign["name"],
                    "sender": SENDER_INFO,
                    "recipients": {"listIds": [list_id]}
                }
                
                campaign_response = requests.post(
                    f"{API_URL}/emailCampaigns",
                    headers=HEADERS,
                    json=campaign_data
                )
                
                if not campaign_response.ok:
                    raise Exception(f"Failed to create campaign {campaign['name']}: {campaign_response.text}")
                    
                print(f"Created campaign: {campaign['name']}")
                
            print("\nAll operations completed successfully!")
            
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {str(e)}")
    except ImportError as e:
        print(f"Import Error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
