import csv
from datetime import datetime
from datetime import timedelta

date_format= '%Y-%m-%d'

# Starting and ending date - fill these out
start_date= datetime.strptime('2023-02-06', date_format)
end_date= datetime.strptime('2023-02-12', date_format)

# Bringing total list of tickets - filtering to the tickets inside the date only
def csv_to_list():
    ticket_list= []

    # Create `output.csv` and dump our list of organizations in there
    with open('../reports.csv', 'r') as file:
        # creating a csv writer object
        reader = csv.reader(file)

        for line in reader:

            # Skip header
            if line[16] == 'Created at':
                continue

            if datetime.strptime(str(line[16][:10]), date_format) >= start_date and datetime.strptime(str(line[16][:10]), date_format) <= end_date:
                # TO-DO: ADD ONLY THE COLUMNS THAT WE NEED
                ticket_list.append(line)

    return ticket_list

# Retrieve the total number of tickets that are SLA only
def total_sla_tickets(ticket_list):
    total= 0

    for ticket in ticket_list:
        # Check to see if tags have silver or gold. Means tickets come from SLA orgs
        if 'silver' in ticket[11] or 'gold' in ticket[11]:
            total += 1

    return total

# Retrieve how many of the tickets that came in are bugs
def total_bug_tickets(ticket_list):
    total_bugs, total_bugs_percent= 0,0

    for ticket in ticket_list:
        if ticket[12] == 'Hold':
            total_bugs += 1

    total_bugs_percent= (total_bugs / len(ticket_list)) * 100
    return round(total_bugs_percent, 2)

# Convert minutes to hours, minutes and seconds
def convert_time(minutes):
    sec= minutes * 60
    time= timedelta(seconds=sec)
    return time

# Retrieve the first response average for all tickets
def first_response_average(ticket_list):
    # [Non-SLA, Gold SLA 1, Gold SLA 2, Gold SLA 3, Silver SLA 1, Silver SLA 2, Silver SLA 3]
    first_response_average= []

    # Use this go get the average first response time per SLA priority
    gold_p1, gold_p2, gold_p3, gold_p1_count, gold_p2_count, gold_p3_count= 0, 0, 0, 0, 0, 0
    silver_p1, silver_p2, silver_p3, silver_p1_count, silver_p2_count, silver_p3_count= 0, 0, 0, 0, 0, 0
    no_sla, no_sla_count = 0, 0

    # Get the total ticket priority for each SLA/Non-SLA and the sum of it
    for ticket in ticket_list:
        # Some tickets don't have a first response time
        if ticket[29] == '':
            continue

        # TO-DO: Clean up - this is essentially a repeat, can take this out into it's own function
        if 'gold' in ticket[11]:
            if ticket[13] == 'Urgent':
                gold_p1 += int(ticket[29])
                gold_p1_count += 1
            elif ticket[13] == 'High':
                gold_p2 += int(ticket[29])
                gold_p2_count += 1
            else:
                gold_p3 += int(ticket[29])
                gold_p3_count += 1
        elif 'silver' in ticket[11]:
            if ticket[13] == 'Urgent':
                silver_p1 += int(ticket[29])
                silver_p1_count += 1
            elif ticket[13] == 'High':
                silver_p2 += int(ticket[29])
                silver_p2_count += 1
            else:
                silver_p3 += int(ticket[29])
                silver_p3_count += 1
        else:
            no_sla += int(ticket[29])
            no_sla_count += 1

    # TO-DO: Clean up? Use extend instead of append
    first_response_average.append(convert_time(no_sla / no_sla_count))

    first_response_average.append(convert_time(gold_p1 / gold_p1_count))
    first_response_average.append(convert_time(gold_p2 / gold_p2_count))
    first_response_average.append(convert_time(gold_p3 / gold_p3_count))

    first_response_average.append(convert_time(silver_p1 / silver_p1_count))
    first_response_average.append(convert_time(silver_p2 / silver_p2_count))
    first_response_average.append(convert_time(silver_p3 / silver_p3_count))

    return first_response_average

# Retrieve the total severity count of all tickets
def severity_count(ticket_list):
    severities=[]
    high, medium, low= 0, 0, 0
    for severity in ticket_list:
        if severity[13] == 'Urgent':
            high += 1
        elif severity[13] == 'High':
            medium += 1
        else:
            low += 1

    severities.extend([high, medium, low])

    return severities

# Retrieve how the satisfaction scores were given and rated
def csat_scores(ticket_list):
    scores=[]
    offered, not_offered, good, bad= 0, 0, 0, 0

    for ticket in ticket_list:
        if ticket[24] == 'Offered':
            offered += 1
        elif ticket[24] == 'Not Offered':
            not_offered += 1
        elif ticket[24] == 'Good':
            good += 1
        else:
            bad += 1

    replies= good + bad
    reply_percentage= round((replies / offered) * 100,2)
    scores.extend([replies, offered, reply_percentage])

    return scores

# Export the full list into a .csv file for exporting
def export_report(ticket_list):
    # Create `output.csv` and dump our list of organizations in there
    with open('../output.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        for ticket in ticket_list:
            if isinstance(ticket, list):
                for row in ticket:
                    file.write(str(row)+ '\n')
            else:
                file.write(str(ticket) +'\n')

def main():

    # Where all the report values will be held
    full_report=[]

    # The date of the report
    report_date= str(start_date) + ' - ' + str(end_date)

    # Swift through the csv file full of tickets and put them into a iterable list
    ticket_list= csv_to_list()

    # The total ticket count for the weekly report
    ticket_count= len(ticket_list)

    # The total number of tickets that were SLA tickets
    ticket_sla_count= total_sla_tickets(ticket_list)

    # The total number of tickets that were on-hold tickets, i.e Jira/internal tickets
    bug_tickets= total_bug_tickets(ticket_list)

    # This is a list of all the response averages for each SLA
    response_averages= first_response_average(ticket_list)

    # List of total severities, i.e p1 (high), p2 (medium) and p3 (low)
    ticket_severity= severity_count(ticket_list)

    # List of the CSAT scores, i.e offers, replies, percentage of how many replied
    satisfaction_score= csat_scores(ticket_list)

    # Convert to all answers into one list so it's easier to filter/export to file afterwards
    full_report.extend([report_date, ' ', ticket_count, ticket_sla_count, bug_tickets, ' ', response_averages, ' ', ' ',' ', ticket_severity, ' ', satisfaction_score])

    export_report(full_report)

if __name__ == "__main__":
    main()