# DPDzero Data Ops Assignment

## Overview
This project implements a data pipeline for processing loan collection call data. It ingests, validates, and processes call logs, agent roster, and disposition summary data to generate performance metrics for call center agents.

## Features
- Data ingestion from CSV files
- Comprehensive data validation
- Join logic to merge datasets
- Feature engineering to calculate performance metrics
- Report generation with basic statistics
- Slack-style summary messages

## Project Structure
```
dpdzero-data-pipeline/
├── data/                    ← Raw CSV files directory
├── src/
│   ├── ingestion.py         ← Data ingestion functions
│   ├── validation.py        ← Data validation functions
│   ├── processing.py        ← Data processing and feature engineering
│   ├── reporting.py         ← Report generation
│   └── main.py              ← Main entry point
├── logs/                    ← Log files
├── requirements.txt         ← Python dependencies
└── README.md                ← Project documentation
```

## Requirements
- Python 3.8 or higher
- pandas 2.1.0
- numpy 1.25.2

## Installation
1. Clone the repository:
```bash
git clone <repository-url>
cd dpdzero-data-pipeline
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
### Basic Usage
```bash
python -m src.main
```

### Specifying File Paths
```bash
python -m src.main --call-logs=data/call_logs.csv --agent-roster=data/agent_roster.csv --disposition-summary=data/disposition_summary.csv --output=agent_performance_summary.csv
```

### Generate Report for Specific Date
```bash
python -m src.main --date=2025-04-28
```

### Generate Detailed Report
```bash
python -m src.main --detailed
```

## Input Files

### call_logs.csv
Contains information about individual calls:
- `call_id`: Unique identifier for each call
- `agent_id`: ID of the agent who made the call
- `org_id`: Organization ID
- `installment_id`: ID of the loan installment
- `status`: Call status (completed, connected, failed, etc.)
- `duration`: Call duration in seconds
- `created_ts`: Timestamp when the call was created
- `call_date`: Date of the call

### agent_roster.csv
Contains information about agents:
- `agent_id`: Unique identifier for each agent
- `users_first_name`: Agent's first name
- `users_last_name`: Agent's last name
- `users_office_location`: Agent's office location
- `org_id`: Organization ID

### disposition_summary.csv
Contains information about agent logins:
- `agent_id`: Agent ID
- `org_id`: Organization ID
- `call_date`: Date
- `login_time`: Time when the agent logged in

## Output
- `agent_performance_summary.csv`: CSV file with agent performance metrics
- Slack-style summary message displayed in the console
- Detailed report (optional)

## Metrics Calculated
- **Total Calls Made**: Number of calls made by each agent on each date
- **Unique Loans Contacted**: Number of unique installment IDs contacted
- **Connect Rate**: Completed calls / Total calls
- **Avg Call Duration**: Average call duration in minutes
- **Presence**: 1 if login_time exists for the agent on that date, 0 otherwise

## Logging
Logs are stored in the `logs/` directory with timestamps. They include:
- Information about the data ingestion process
- Validation warnings and errors
- Processing statistics
- Report generation details

## Author
Saksham Tapadia