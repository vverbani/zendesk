# Retrieve Org Information

Zendesk doesn't provide an easy or a free way to retrieve organization information outside of the API. This script is intended to be used to pull information from the API
for gathering the following data from every organization:

1. Name
2. Region
3. SLA

## Start

1. cp .env.example > .env
2. Get Zendesk url and copy into your `.env` file
3. Get Zendesk token and copy into your `.env` file
4. Call the below (copy and paste onto your terminal)
```bash

docker-compose up

```
5. Import `output.csv` into spreadsheet for viewing