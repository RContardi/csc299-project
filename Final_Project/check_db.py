import sqlite3

conn = sqlite3.connect('tasks.db')
cur = conn.cursor()
cur.execute('SELECT id, title, completed FROM tasks ORDER BY id')
tasks = cur.fetchall()
print(f'Total tasks: {len(tasks)}')
for t in tasks:
    status = "✓" if t[2] else "○"
    print(f'{t[0]}. {status} {t[1]}')
conn.close()
