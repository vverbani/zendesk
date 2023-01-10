import os, requests, csv, time
from dotenv import load_dotenv

# Create Organization class for storing org data
class Org:
    def __init__(self, name, sla, region, environment):
        self.name = name
        self.sla = sla
        self.region= region
        self.environment= environment

# Recursively call Zendesk API to get all Organizations
def get_all():
    response_list, filtered_list= [],[]

    # API url and headers
    zendesk_url= os.getenv('zendesk_url')
    auth_header_bearer=os.getenv('auth_header_bearer')

    print('Started organization retrieval.... ... ... .. . . .')

    # If API still has more data - keep requesting
    while zendesk_url:
        org_response= requests.get(zendesk_url, headers={'Authorization': auth_header_bearer})
        time.sleep(0.25)

        # Keep calling API unless a non-successful response occurs
        if(org_response.status_code != 200):
            return "Something went wrong in your the Zendesk API call. Please check your auth token and/or Zendesk URL"

        # Append new data to full data list to not override older data
        org_list= org_response.json()
        response_list.extend(org_list['organizations'])

        # Determine whether there's more data to call the API or not
        if org_list['meta']['has_more']:
            zendesk_url= org_list['links']['next']
        else:
            zendesk_url= None

    filtered_list= filter_list(response_list)

    return filtered_list

def filter_list(unfiltered_org_list):
    filtered_org_list=[]

    for org in unfiltered_org_list:
        # Add default values of '-' if value doesn't exist making easier to read dead space
        name, sla, region, environment= '-','-','-','-'

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
        filtered_org_list.append((name,sla,region,environment))

    return filtered_org_list

def upload_to_csv(org_list):
    headers= ['Name', 'SLA', 'Region', 'Environment']

    # Create `output.csv` and dump our list of organizations in there
    with open('./src/output.csv', 'w') as file:
        # creating a csv writer object
        writer = csv.writer(file, delimiter=',')

        # Insert our headers
        writer.writerow(headers)

        # Insert actual organization data
        for x in range(len(org_list)):
            temp_row=[org_list[x][0], org_list[x][1], org_list[x][2], org_list[x][3]]
            writer.writerow(temp_row)

def main():
    org_list= []

    # Load .env file
    load_dotenv()

    # Get all of the Organizations in an unfiltered list
    org_list= get_all()

    # Put Organization list in csv
    upload_to_csv(org_list)

    print("Everything has been exported, please look at the 'output.csv' file in the output folder")

if __name__ == "__main__":
    main()