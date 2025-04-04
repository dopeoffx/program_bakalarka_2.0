import sqlite3


def insert_projects(projects, db_name="bionano.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.executemany("INSERT OR IGNORE INTO projects (name) VALUES (?)", [(p,) for p in projects])

    conn.commit()
    conn.close()
    
    
def get_projects(db_name="bionano.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM projects")
        projects = [int(row[0]) for row in cursor.fetchall()]
    except sqlite3.OperationalError as e:
        if "no such table" in str(e).lower():
            print("Tabulka 'projects' neexistuje.")
            projects = [] 
        else:
            raise 

    conn.close()
    return projects