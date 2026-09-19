import sqlite3

conn = sqlite3.connect('data/edumesh.db')
tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
print("Tables found:", tables)
print("Total:", len(tables))