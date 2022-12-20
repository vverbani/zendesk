import os, requests, csv, time
from dotenv import load_dotenv

# Create Organization class for storing org data
class Org:
    def __init__(self, name, sla, region, environment):
        self.name = name
        self.sla = sla
        self.region= region
        self.environment= environment

def get_all(url, header):
    response_list= []
    print('Starting organization retrieval.... ... ... .. . . .')

    # If API still has more data - keep requesting
    while url:
        org_response= requests.get(url, headers={'Authorization': header})
        time.sleep(0.25)

        # Keep calling API unless a non-successful response occurs
        if(org_response.status_code != 200):
            return "Something went wrong in your the Zendesk API call. Please check your auth token and/or Zendesk URL"

        # Append new data to full data list to not override older data
        org_list= org_response.json()
        response_list.extend(org_list['organizations'])

        # Determine whether there's more data to call the API or not
        if org_list['meta']['has_more']:
            url= org_list['links']['next']
        else:
            url= None

    return response_list

def main():
    list= []
    entries= 0
    headers= ['Name', 'SLA', 'Region', 'Environment']

    # Load .env file
    load_dotenv()

    # API url and headers
    zendesk_url= os.getenv('zendesk_url')
    auth_header_bearer=os.getenv('auth_header_bearer')

    org_list= get_all(zendesk_url, auth_header_bearer)

    for org in org_list:
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

        entries += 1

        # Add org objects to our list of orgs
        org_object = Org(name, sla,region, environment)
        list.append(org_object)

    # Create `output.csv` and dump our list of organizations in there
    with open('./src/output.csv', 'w') as file:
        # creating a csv writer object
        writer = csv.writer(file, delimiter=',')

        # Insert our headers
        writer.writerow(headers)

        # Insert actual organization data
        for x in range(len(list) - 1):
            temp_row=[list[x].name, list[x].region, list[x].sla, list[x].environment]
            writer.writerow(temp_row)

        print('Purged a total of ' + str(entries) + ' entries into the csv file!')
        print("Everything has been exported, please look at 'output.csv' in the output folder")

if __name__ == "__main__":
    main()