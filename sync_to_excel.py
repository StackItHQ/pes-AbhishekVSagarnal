import os
import time
import hashlib
import json
import mysql.connector
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

# Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Abhishek')
DB_NAME = os.getenv('DB_NAME', 'mydb')
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', './credentials.json')
SPREADSHEET_ID = os.getenv('SHEET_ID', '1eop0KMrdMD1dBxnwLdCx0irWGk0HfSMfZ-mI8ZP6lRM')
RANGE_NAME = 'Sheet1!A1:E'  # Adjust the range to your needs

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = service_account.Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# Set up MySQL connection
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

# CRUD Operations for MySQL
def create_row(data):
    cursor = db.cursor()
    query = """INSERT INTO EmployeeData (employee_name, role, email, salary, last_updated) 
               VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(query, data)
    db.commit()

def read_rows():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM EmployeeData")
    return cursor.fetchall()

def get_row_by_employee_name(employee_name):
    cursor = db.cursor()
    query = "SELECT * FROM EmployeeData WHERE employee_name = %s"
    cursor.execute(query, (employee_name,))
    return cursor.fetchone()

def update_row(data, employee_name):
    cursor = db.cursor()
    query = """UPDATE EmployeeData 
               SET role=%s, email=%s, salary=%s, last_updated=%s 
               WHERE employee_name=%s"""
    cursor.execute(query, data + (employee_name,))
    db.commit()

def delete_row(employee_name):
    cursor = db.cursor()
    query = "DELETE FROM EmployeeData WHERE employee_name=%s"
    cursor.execute(query, (employee_name,))
    db.commit()

# CRUD Operations for Google Sheets
def fetch_sheet_data():
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    return result.get('values', [])

def update_sheet_row(row_index, data):
    range_name = f'Sheet1!A{row_index + 1}:E{row_index + 1}'
    body = {
        'values': [data]
    }
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()

def delete_sheet_row(row_index):
    range_name = f'Sheet1!A{row_index + 1}:E{row_index + 1}'
    sheet.values().clear(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()

def append_sheet_row(data):
    range_name = 'Sheet1!A2'
    body = {
        'values': [data]
    }
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()

# Sync Logic
def get_row_hash(row):
    return hashlib.sha256(json.dumps(row, sort_keys=True).encode('utf-8')).hexdigest()

def sync_sheet_to_db():
    logging.info("Syncing data from Google Sheets to MySQL...")
    rows = fetch_sheet_data()
    
    if not rows or len(rows) <= 1:
        logging.warning("No data found in Google Sheets to sync.")
        return

    for index, row in enumerate(rows[1:]):  # Skip the header
        if len(row) < 4:  # Ensure the row has enough data
            logging.warning(f"Skipping row with insufficient data: {row}")
            continue
        
        employee_name, role, email, salary = row[0], row[1], row[2], row[3]
        current_row = (employee_name, role, email, salary, datetime.utcnow().isoformat())
        current_hash = get_row_hash(current_row)
        
        existing_row = get_row_by_employee_name(employee_name)
        
        if existing_row:
            existing_data = (existing_row[1], existing_row[2], existing_row[3], existing_row[4])
            existing_hash = get_row_hash(existing_data)
            if current_hash != existing_hash:
                logging.info(f"Updating row for employee: {employee_name}")
                update_row((role, email, salary, datetime.utcnow().isoformat()), employee_name)
        else:
            logging.info(f"Inserting new row for employee: {employee_name}")
            create_row((employee_name, role, email, salary, datetime.utcnow().isoformat()))

def sync_db_to_sheet():
    logging.info("Syncing data from MySQL to Google Sheets...")
    mysql_rows = read_rows()
    
    if not mysql_rows:
        logging.warning("No data found in MySQL to sync.")
        return
    
    body = []
    for row in mysql_rows:
        employee_name, role, email, salary, last_updated = row
        body.append([employee_name, role, email, salary, last_updated])

    sheet.values().clear(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A2:E").execute()
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1!A2",
        valueInputOption="RAW",
        body={'values': body}
    ).execute()
    
    logging.info(f"{result.get('updatedCells')} cells updated in Google Sheets")

# Main Function
def continuous_sync(interval=30):
    while True:
        try:
            # Sync Google Sheets to MySQL
            sync_sheet_to_db()

            # Sync MySQL to Google Sheets
            sync_db_to_sheet()

        except Exception as e:
            logging.error(f"An error occurred during synchronization: {e}")
        
        time.sleep(interval)  # Wait for the next sync cycle

if __name__ == "__main__":
    logging.info("Starting the continuous synchronization process...")
    continuous_sync(interval=30)
