# Weekend Ticket Report

This repo is designed to retrieve only the tickets that were submitted during weekends. This is useful to get an idea whether your organization needs to hire support engineers during weekend hours - especially if you're legally obligated to weekend coverage because of your SLA contracts.

## Usage
1. Export ticket `.csv` from Zendesk
2. Upload `.csv` file onto this repos root directory and name it `reports.csv`
3. Run `docker-compose up` on the command line in the root directory
4. Import `output.csv` as a separate sheet on your Google Spreadsheet
5. View data