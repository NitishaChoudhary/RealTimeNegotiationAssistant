# import gspread

# def log_to_google_sheets(sheet_name, row_data):
#     """Log data to Google Sheets."""
#     gc = gspread.service_account(filename="credentials.json")
#     sheet = gc.open(sheet_name).sheet1
#     sheet.append_row(row_data)
import sqlite3
def initialize_db():
    conn = sqlite3.connect('sales_insights.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        sentiment TEXT,
        sentiment_score REAL,
        intent TEXT,
        intent_score REAL
    )
    ''')

    conn.commit()
    conn.close()
def log_to_sqlite(text, sentiment, sentiment_score, intent, intent_score):
    conn = sqlite3.connect('sales_insights.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Insights (text, sentiment, sentiment_score, intent, intent_score)
    VALUES (?, ?, ?, ?, ?)
    ''', (text, sentiment, sentiment_score, intent, intent_score))

    conn.commit()
    conn.close()
def get_all_insights():
    conn = sqlite3.connect('sales_insights.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Insights')
    all_insights = cursor.fetchall()

    conn.close()
    return all_insights
initialize_db()
