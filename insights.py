import sqlite3

conn = sqlite3.connect('sales_insights.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM Insights")
insights = cursor.fetchall()

for insight in insights:
    print(insight)
conn.close()
