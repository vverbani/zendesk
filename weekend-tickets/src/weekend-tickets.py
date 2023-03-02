import csv
import pandas as pd

date_format= '%Y-%m-%d'
SATURDAY= 5
SUNDAY= 6

# Bringing total list of tickets - filtering to the tickets inside the date only
def csv_to_list():
    ticket_list= []

    # Create `output.csv` and dump our list of organizations in there
    with open('./reports.csv', 'r') as file:
        # creating a csv writer object
        reader = csv.reader(file)

        for line in reader:

            # Skip header
            if line[16] == 'Created at':
                continue

            # Get the day in week - Monday == 0, Sunday == 6
            day= pd.Timestamp(str(line[16][:10]))

            if day.dayofweek == SATURDAY or day.dayofweek == SUNDAY:
                # print(day.dayofweek, day.day_name())
                ticket_list.append(line)

    return ticket_list

# Retrieve the SLA depending on the tags of the ticket
def get_sla(tags):
    sla=''

    if 'gold' in tags:
        sla= 'Gold'
    elif 'silver' in tags:
        sla= 'Silver'
    elif 'standard' in tags:
        sla= 'Standard'
    else:
        sla= '--'

    return sla

# Export the list of weekend tickets only
def export_tickets_only(ticket_list):
    spreadsheet_headers= ['Ticket Id', 'Created Date', 'Requester Domain', 'Ticket Title', 'SLA', 'Priority', 'First Resolution' ]
    # Create `output.csv` and dump our list of organizations in there
    with open('./output.csv', 'w', newline='') as file:

        writer = csv.writer(file, delimiter=',')
        writer.writerow(spreadsheet_headers)

        for ticket in ticket_list:
            sla = get_sla(ticket[11])
            temp_row=[ticket[1], str(ticket[16][:10]), ticket[6], ticket[10], sla, ticket[13], ticket[29]]
            writer.writerow(temp_row)

def main():

    weekend_tickets= csv_to_list()
    export_tickets_only(weekend_tickets)

if __name__ == "__main__":
    main()