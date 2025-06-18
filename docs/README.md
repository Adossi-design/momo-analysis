# MTN MoMo Transaction Analysis System

## Overview
This system processes and analyzes MTN Mobile Money transaction data from SMS messages in XML format.

## Features
- Transaction categorization (incoming, payments, transfers, etc.)
- Interactive dashboard with visualizations
- Search and filtering capabilities
- Monthly transaction summaries
- Detailed transaction views

## Installation

### Prerequisites
- Python 3.7+
- SQLite

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/momo-analysis.git
   cd momo-analysis
   ```

## Install dependencies:
```bash
pip install -r backend/requirements.txt
```

## Set up the database
```bash
python scripts/setup_database.py
```

## Process your transaction data:
```bash
python scripts/process_data.py data/modified_sms_v2.xml
```

## Usage
### Running the Application
Start the development server:

```bash
python momo_analysis.py --debug
```

Or start the production server:

```bash
python momo_analysis.py
```

Access the dashboard
