import os, requests, csv, time
from dotenv import load_dotenv

# Recursively call Zendesk API to get all relevant data
def get_all(zendesk_url):

    response_list= []
    auth_header_bearer=os.getenv('auth_header_bearer')

    print('Started Zendesk data retrieval.... ... ... .. . . .')

    # If API still has more data - keep requesting
    while zendesk_url:
        response= requests.get(zendesk_url, headers={'Authorization': auth_header_bearer})
        time.sleep(0.25)

        # Keep calling API unless a non-successful response occurs
        if(response.status_code != 200):
            return "Something went wrong in your the Zendesk API call. Please check your auth token and/or Zendesk URL"

        # Append new data to full data list to not override older data
        list= response.json()

        # Add list type to it's own list, i.e org to org list, user to user list
        if 'organizations' in zendesk_url:
            response_list.extend(list['organizations'])
        else:
            response_list.extend(list['users'])

        # Determine whether there's more data to call the API or not
        if list['meta']['has_more']:
            zendesk_url= list['links']['next']
        else:
            zendesk_url= None

    return response_list

# Filter all organizations with only the data we need
def filter_org_list(unfiltered_org_list):
    filtered_org_list=[]

    for org in unfiltered_org_list:
        # Add default values of '-' if value doesn't exist making easier to read dead space
        name, sla, region, environment= '-','-','-','-'

        id= org['id']

        if org['name'] != '':
            name= org['name']

        for tag in org['tags']:
            # Find Region
            if(tag.lower() =='emea' or tag.lower() == 'apac'):
                region= tag.capitalize()
            if(tag.lower() == 'amer' or tag.lower() == 'us'):
                region= 'Amer'

            # Find SLA
            if(tag.lower() == 'standard' or tag.lower() == 'silver' or tag.lower() == 'gold'):
                sla= tag.capitalize()

            # Environment - Hybrid
            if(tag.lower() == 'hybrid'):
                environment= tag.capitalize()
            if(tag.lower() == 'mdcb'):
                environment= 'On-prem w/ MDCB'
            if(tag.lower() == 'saas' or tag.lower() == 'cloud_native' or tag.lower() == 'ara' or tag.lower() == 'tyk_launch'):
                environment= 'Cloud'
            if(tag.lower() == 'on-prem'):
                environment= 'On-prem w/o MDCB'

        # Add org objects to our list of orgs
        filtered_org_list.append({"id": id, "name": name, "sla": sla, "region": region, "environment": environment, "user": ""})

    return filtered_org_list

def minimum_6_users(org_list):
    org_user_list_greater= []

    for org in org_list:
        if org['user'].count('@') > 6:
            org_user_list_greater.append(org)

    return org_user_list_greater

# Add users to organizations
def users_and_orgs_list(orgs, users):

    org_user_list= []

    for count, org in enumerate(orgs):
        for user in users:
            if user['organization_id'] == org['id']:
                name= user['name'] + ' ' + user['email'] + ' '
                org['user']= org['user'] + name
        org_user_list.append(org)

    return org_user_list

# Upload our organization list with users in spreadsheet format
def upload_to_csv(list):
    headers= ['Id', 'Name', 'SLA', 'Region', 'Environment', 'Users']

    # Create `output.csv` and dump our list of organizations in there
    with open('./src/output.csv', 'w') as file:
        # creating a csv writer object
        writer = csv.writer(file, delimiter=',')

        # Insert our headers and Organization with user data
        writer.writerow(headers)

        for row in list:
            temp_row=[row['id'], row['name'], row['sla'], row['region'], row['environment'], row['user']]
            writer.writerow(temp_row)

def main():

    # Load .env file
    load_dotenv()

    # API URLS for orgs and users
    zendesk_org_url= os.getenv('zendesk_org_url')
    zendesk_user_url= os.getenv('zendesk_user_url')

    # Get all of the organizations and users in unfiltered lists
    unfiltered_org_list= get_all(zendesk_org_url)
    user_list= get_all(zendesk_user_url)

    # Filter both lists
    filtered_org_list= filter_org_list(unfiltered_org_list)

    full_list= users_and_orgs_list(filtered_org_list, user_list)

    # Put Organization list in csv
    upload_to_csv(full_list)

    print("Everything has been exported, please look at the 'output.csv' file in the output folder")

if __name__ == "__main__":
    main()