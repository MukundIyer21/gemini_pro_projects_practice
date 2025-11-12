import sqlite3

conn = sqlite3.connect("company.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    department TEXT,
    salary INTEGER
)
""")

employees = [
    ("Alice", "Engineering", 85000),
    ("Bob", "HR", 60000),
    ("Charlie", "Marketing", 75000),
    ("Diana", "Engineering", 95000),
    ("Evan", "Finance", 72000),
    ("Fiona", "Marketing", 68000)
]

cursor.executemany("INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)", employees)
conn.commit()

print("Database created and records inserted successfully!")
conn.close()