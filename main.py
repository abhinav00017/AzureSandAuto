from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import TagsPatchResource
from azure.communication.email import EmailClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
 
 
from datetime import datetime, timedelta 
 

from dotenv import load_dotenv

load_dotenv()
 
DEFAULT_EXPIRATION_DAYS = 10
MAX_EXPIRATION_DAYS = 60
 
class Settings:
    AZURE_SUBSCRIPTION_ID="XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    EMAIL_CONNECTION_STRING = "endpoint==https://azurexxxxxxxxx.xxxxxxxxx.communication.azure.com/;accesskey=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    SENDER_EMAIL = "xxxxxxx@XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX.azurecomm.net"
 
Settings=Settings()
 
class Emails():
    def __init__(self, Settings):
        self.email_client = EmailClient.from_connection_string(Settings.EMAIL_CONNECTION_STRING)
        self.sender_email = Settings.SENDER_EMAIL
        pass

    def email_creation(self, email, resource_name, creation_date_str, age,expiry_date):
        message = {
            "content": {
                "subject": "Azure Sandbox Resource Group is Created!",
                "plainText": f'Hello @{email.split("@")[0]},\n\nYou have created a Resource Group "{resource_name}" in Azure Sandbox subscription on {creation_date_str.split()[0]}. It will be valid for {MAX_EXPIRATION_DAYS} days.\n\nThanks,\nAzure LZ Team.',
            },
            "recipients": {
                "to": [
                    {
                        "address": email
                    }
                ]
            },
            "senderAddress": self.sender_email
        }
 
        self.email_client.begin_send(message)
        print(f"Email Sent to {email}")
 
    def email_notifier(self, email, resource_name, creation_date_str, age,expiry_date,details_list):
        mail_data=''
        if details_list!=None:
            mail_data=f'Hello @{email.split("@")[0]},\n\nYou have created a Resource Group "{resource_name}" in Azure Sandbox Subscription on {creation_date_str.split()[0]} , and it has been {age} days. Do you still need it?\n\nIf you want to continue using this Resource Group please update the expiry date within {expiry_date}. If not, the resource group and the resources under it will be automatically deleted.\n\nThe Resource Group "{resource_name}" has following resources (Format Name-Creationdate-Type):'
            for i in range(len(details_list[0])):
                mail_data=mail_data+"\n\t"+str(details_list[0][i])+" --- "+str(details_list[1][i]+" --- " +str(details_list[2][i]))
            mail_data=mail_data+f'\n\nFollow the Steps to update Expiry date:\n\t1. Log in to Azure portal https://portal.azure.com\n\t2. Select the resource group "{resource_name}"\n\t3. Go to tags\n\t4. Edit "ExpirationDate" (Date should not exceed 60 days and format should be YYYY-MM-DD)\n\nThanks,\nAzure LZ Team.'  
        else:
            mail_data=f'Hello @{email.split("@")[0]},\n\nYou have created a Resource Group "{resource_name}" in Azure Sandbox Subscription on {creation_date_str.split()[0]} , and it has been {age} days. Do you still need it?\n\nIf you want to continue using this Resource Group please update the expiry date within {expiry_date}. If not, the resource group and the resources under it will be automatically deleted.\n\nThe Resource Group "{resource_name}" has no resources under it. \n\nFollow the Steps to update Expiry date:\n\t1. Log in to Azure portal https://portal.azure.com\n\t2. Select the resource group "{resource_name}"\n\t3. Go to tags\n\t4. Edit "ExpirationDate" (Date should not exceed 60 days and format should be YYYY-MM-DD)\n\nThanks,\nAzure LZ Team.'
        message = {
            "content": {
                "subject": "Azure Sandbox Resource Group will get Expired Soon!",
                "plainText":mail_data,
            },
            "recipients": {
                "to": [
                    {
                        "address": email
                    }
                ]
            },
            "senderAddress": self.sender_email
        }
 
        self.email_client.begin_send(message)
        print(f"Email Sent to {email}")
 
    def email_after_deletion(self, email, resource_name, creation_date_str, age,expiry_date):
        print(email, resource_name,creation_date_str.split()[0],age, expiry_date)
 
        message = {
            "content": {
                "subject": "Azure Sandbox Resource Group deleted",
                "plainText": f'Hello @{email.split("@")[0]},\n\nThis "{resource_name}" Resource Group in Azure created on {creation_date_str} in Sandbox Subscription, and it surpassed {expiry_date}. \n\n Since no Action is taken from your side, it is Deleted. \n\nThanks,\nAzure LZ Team.', 
            },
            "recipients": {
                "to": [
                    {
                        "address": email
                    }
                ]
            },
            "senderAddress": self.sender_email
        }
 
        self.email_client.begin_send(message)
        print("Deletion Email sent!")
 
    def email_wrongformat(self,resource_name,email,expiry_date):
        message = {
            "content": {
                "subject": "Azure Sandbox Resource Group Expiry Date Wrong Format",
                "plainText": f'Hello @{email.split("@")[0]},\n\nThis resource "{resource_name}" in Azure created in Sandbox Subscription, Recently you have modified date and given {expiry_date}, which is in the wrong format, it should be in "YYYY-MM-DD" \n\nThanks,\nAzure LZ Team.', 
            },
            "recipients": {
                "to": [
                    {
                        "address": email
                    }
                ]
            },
            "senderAddress": self.sender_email
        }
 
        self.email_client.begin_send(message)
        print("Wrong Format Email sent!")
 
    def change_date_email(self,resource_name,email,expiry_date,new_expiry_date):
        message = {
            "content": {
                "subject": "Azure Sandbox Resource Expiry Date Changed",
                "plainText": f'Hello @{email.split("@")[0]},\n\nThis resource "{resource_name}" in Azure, created in Sandbox Subscription. Recently you Have modified date and given {expiry_date}, which was more then {MAX_EXPIRATION_DAYS} days from now, it should be within 60 days. Now its changed to {new_expiry_date}. If you want to contiue, you can again extend after 60 days.  \n\nThanks,\nAzure LZ Team.', 
            },
            "recipients": {
                "to": [
                    {
                        "address": email
                    }
                ]
            },
            "senderAddress": self.sender_email
        }
 
        self.email_client.begin_send(message)
        print("Date Change Email sent!")
 
emails = Emails(Settings)


 
def get_resource_management_client():
    credential = DefaultAzureCredential()
    subscription_id = Settings.AZURE_SUBSCRIPTION_ID
    return [ResourceManagementClient(credential, subscription_id),NetworkManagementClient(credential,subscription_id),ComputeManagementClient(credential,subscription_id)]
 
def get_resourcegroups_list(l):
    return l[0].resource_groups.list()
    
def add_resource_expiry_tag(l,resource_group_id,day):
    expiration_date = datetime.utcnow() + timedelta(days=day)
    tags = {
    "ExpirationDate": str(expiration_date).split('T')[0].split()[0],
    "CreationDate": str(datetime.utcnow()).split('T')[0].split()[0]
    }
    tag_patch_resource = TagsPatchResource(
    operation="Merge",
    properties={'tags': tags}
    )
    l[0].tags.begin_update_at_scope(resource_group_id, tag_patch_resource)
    print(tag_patch_resource.properties.tags)
    return expiration_date.strftime("%Y-%m-%dT%H:%M:%SZ")
 
def expiry_date_maximum(l,expiry_date):
    new_expirydate=datetime.utcnow() + timedelta(days=MAX_EXPIRATION_DAYS)
    if new_expirydate<expiry_date:
        return new_expirydate
    return True

def date_format_validation(user_date):
    try:
        datetime.strptime(user_date,'%Y-%m-%d')
        return True
    except ValueError:
        return False
     
def delete_resource(rg,l):
    l[0].resource_groups.begin_delete(rg.name)
    return True

def process_resource_group(l,rg):
    if rg.tags!=None:
        if "CreatorEmail" in rg.tags:
            if "ExpirationDate" not in rg.tags:
                expiry_date=add_resource_expiry_tag(l,rg.id,MAX_EXPIRATION_DAYS)
                emails.email_creation(rg.tags['CreatorEmail'],rg.name,str(datetime.utcnow()).split('T')[0].split()[0],str(0),str(expiry_date).split('T')[0])
                print("Expiry Date Set!")
            else:
                expiry_date=rg.tags["ExpirationDate"].split('T')[0]
                if date_format_validation(expiry_date) == False:
                    emails.email_wrongformat(rg.name,rg.tags['CreatorEmail'],str(expiry_date).split()[0])
                    print("validated-> WrongFormat Found!")
                    return
                expiry_date=datetime.strptime(expiry_date, "%Y-%m-%d")
                if expiry_date_maximum(l,expiry_date)!=True:
                    new_expiry_date=expiry_date_maximum(l,expiry_date)
                    add_resource_expiry_tag(l,rg.id,MAX_EXPIRATION_DAYS)
                    emails.change_date_email(rg.name,rg.tags['CreatorEmail'],str(expiry_date).split()[0],str(new_expiry_date).split()[0])
                    return
                current_date=datetime.now()
                age=current_date-datetime.strptime(rg.tags["CreationDate"], "%Y-%m-%d")
                if expiry_date < current_date:
                    l[0].resource_groups.begin_delete(rg.name)
                    if delete_resource(rg,l)==True:
                        emails.email_after_deletion(rg.tags['CreatorEmail'],rg.name,rg.tags['CreationDate'],str(age.days),str(expiry_date).split()[0])
                        print('Its Deleted....')
                    else:
                        print("Not deleted")
                    print('Its Deleted....')
                else:
                    current_age=expiry_date-current_date
                    if current_age.days in [9,2,0]:
                        resources_names_list=[]
                        resources_creation_date_list=[]
                        resource_type=[]
                        details_list=[]
                        resources=l[0].resources.list_by_resource_group(rg.name,expand = "createdTime,changedTime")
                        for resource in resources:
                            resources_names_list.append(resource.name)
                            resources_creation_date_list.append(str(resource.created_time).split()[0])
                            resource_type.append(resource.type)
                        if len(resources_names_list)==0:
                            details_list=None
                        else:
                            details_list=[resources_names_list,resources_creation_date_list,resource_type]
                        emails.email_notifier(rg.tags['CreatorEmail'],rg.name,rg.tags['CreationDate'],str(age.days),str(expiry_date).split()[0],details_list)
                    
    return

def main():
    l = get_resource_management_client()
    # resource_client=l[0]
    # network_client=l[1]
    # compute_client=l[2]
    resource_groups = get_resourcegroups_list(l)
    for rg in resource_groups:
        process_resource_group(l,rg)
 
if __name__=="__main__":
    main()
 