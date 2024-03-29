import csv
from datetime import datetime

# Date format
date_format= '%Y-%m-%d'

# Starting and ending date - fill these out
start_date= datetime.strptime('2023-04-03', date_format)
end_date= datetime.strptime('2023-04-09', date_format)

# Global SLA times per SLA
GOLD_P1_SLA= 1 * 60 # 1 hour
GOLD_P2_SLA= 2 * 60 # 2 hours
GOLD_P3_SLA= 24 * 60 # 24 hours
SILVER_P1_SLA= 4 * 60 # 4 hours
SILVER_P2_SLA= 12 * 60 # 12 hours
SILVER_P3_SLA= 24 * 60 # 24 hours

# Bringing total list of tickets - filtering to the tickets inside the date only
def csv_to_list():
    ticket_list= []

    # Create `output.csv` and dump our list of organizations in there
    with open('../reports.csv', 'r') as file:
        # creating a csv writer object
        reader= csv.reader(file)

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
def convert_time(minutes_given):
    minutes, seconds= divmod(minutes_given * 60, 60)
    hours, minutes= divmod(minutes, 60)

    return '%02d:%02d:%02d' % (hours, minutes, seconds) # return format 01:34:50 (hh:mm:ss)

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
    first_response_average.append(convert_time(no_sla / no_sla_count)) if no_sla_count > 0 else first_response_average.append("n/a")

    first_response_average.append(convert_time(gold_p1 / gold_p1_count)) if gold_p1_count > 0 else first_response_average.append("n/a")
    first_response_average.append(convert_time(gold_p2 / gold_p2_count)) if gold_p2_count > 0 else first_response_average.append("n/a")
    first_response_average.append(convert_time(gold_p3 / gold_p3_count)) if gold_p3_count > 0 else first_response_average.append("n/a")

    first_response_average.append(convert_time(silver_p1 / silver_p1_count)) if silver_p1_count > 0 else first_response_average.append("n/a")
    first_response_average.append(convert_time(silver_p2 / silver_p2_count)) if silver_p2_count > 0 else first_response_average.append("n/a")
    first_response_average.append(convert_time(silver_p3 / silver_p3_count)) if silver_p3_count > 0 else first_response_average.append("n/a")

    return first_response_average

# Retrieve the breach percentage of all the ticket(s) that were a breach of SLA
def sla_breaches(ticket_list, ticket_count):
    breach, breach_percentage= 0,0
    # Ticket[29] == first response

    for ticket in ticket_list:
        # First Response isn't documented
        if ticket[29] == '':
            continue

        if 'gold' in ticket[11]:
            # Gold SLA P1 (Urgent): 1 hour
            if ticket[13] == 'Urgent' and int(ticket[29]) > GOLD_P1_SLA:
                print(f'Zendesk Id that was breached: https://tyksupport.zendesk.com/agent/tickets/{ticket[1]}')
                breach += 1
            # Gold SLA P2 (High): 2 hour
            if ticket[13] == 'High' and int(ticket[29]) > GOLD_P2_SLA:
                print(f'Zendesk Id that was breached: https://tyksupport.zendesk.com/agent/tickets/{ticket[1]}')
                breach += 1
            # Gold SLA P3 (Normal/ low): 24 hour
            if ticket[13] == 'Normal' or ticket[13] == 'Low':
                if int(ticket[29]) >  GOLD_P3_SLA:
                    print(f'Zendesk Id that was breached: https://tyksupport.zendesk.com/agent/tickets/{ticket[1]}')
                    breach += 1

        if 'silver' in ticket[11]:
            # Silver SLA P1 (Urgent): 4 hour
            if ticket[13] == 'Urgent' and int(ticket[29]) > SILVER_P1_SLA:
                print(f'Zendesk Id that was breached: https://tyksupport.zendesk.com/agent/tickets/{ticket[1]}')
                breach += 1
            # Silver SLA P2 (High): 12 hour
            if ticket[13] == 'High' and int(ticket[29]) > SILVER_P2_SLA:
                print(f'Zendesk Id that was breached: https://tyksupport.zendesk.com/agent/tickets/{ticket[1]}')
                breach += 1
            # Silver SLA P3 (Normal/ low): 24 hour
            if ticket[13] == 'Normal' or ticket[13] == 'Low':
                if int(ticket[29]) >  SILVER_P3_SLA:
                    print(f'Zendesk Id that was breached: https://tyksupport.zendesk.com/agent/tickets/{ticket[1]}')
                    breach += 1

    # Calculate breach percentage
    if breach == 0:
        breach_percentage= 100
    else:
        breach_percentage= 100 - round((breach/ ticket_count) * 100,2)

    return breach_percentage

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
    offered, not_offered, good, bad, customer_satisfication, reply_percentage= 0, 0, 0, 0, 0, 0

    for ticket in ticket_list:
        if ticket[24] == 'Offered':
            offered += 1
        elif ticket[24] == 'Not Offered':
            not_offered += 1
        elif ticket[24] == 'Good':
            good += 1
        else:
            print(f'Bad Rating: https://tyksupport.zendesk.com/agent/tickets/{ticket[1]}')
            bad += 1

    replies= good + bad
    if replies > 0: 
        customer_satisfication= round((good/ replies) * 100,2)
        reply_percentage= round((replies / offered) * 100,2)

    scores.extend([customer_satisfication,replies, offered, reply_percentage])

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
    report_date= str(start_date)[:10] + ' - ' + str(end_date)[:10]

    # Swift through the csv file full of tickets and put them into a iterable list
    ticket_list= csv_to_list()

    # The total ticket count for the weekly report
    ticket_count= len(ticket_list)
    # print(f'Total ticket count: {ticket_count}')

    # The total number of tickets that were SLA tickets
    ticket_sla_count= total_sla_tickets(ticket_list)
    # print(f'Total SLA Ticket count: {ticket_sla_count}')

    # The total number of tickets that were on-hold tickets, i.e Jira/internal tickets
    bug_tickets= total_bug_tickets(ticket_list)
    # print(f'Total tickets that were bugs: {bug_tickets}')

    # This is a list of all the response averages for each SLA
    response_averages= first_response_average(ticket_list)
    # print(f'Here are the response averages: {response_averages}')

    # List of total severities, i.e p1 (high), p2 (medium) and p3 (low)
    ticket_severity= severity_count(ticket_list)
    # print(f'Here are the ticket severity counts: {ticket_severity}')

    # List of the CSAT scores, i.e offers, replies, percentage of how many replied
    satisfaction_score= csat_scores(ticket_list)

    # Total amount of breaches we've had
    breaches_percentage= sla_breaches(ticket_list, int(ticket_count))

    # Convert to all answers into one list so it's easier to filter/export to file afterwards
    full_report.extend([report_date, ' ', ticket_count, ticket_sla_count, ' ',' ', bug_tickets, ' ', response_averages, ' ', breaches_percentage ,' ', ' ',' ', ticket_severity, ' ', satisfaction_score])

    export_report(full_report)

if __name__ == "__main__":
    main()