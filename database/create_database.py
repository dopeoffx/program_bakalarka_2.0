import sqlite3
from tables import create_MQR_table
from tables import create_PIPELINE_table
from tables import create_SINGLE_table
from tables import create_ALIGNBNX_table


def create_database(db_name="bionano.db"):
   
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    create_MQR_table(cursor)
    create_ALIGNBNX_table(cursor)
    create_PIPELINE_table(cursor)
    create_SINGLE_table(cursor)
    
    
    tables = ["VARIANT", "COMPARISON", "SCAFFOLD"]

    
    for table in tables:
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table} (
            id INTEGER PRIMARY KEY,
             success BOOLEAN CHECK (success IN (0, 1) OR success IS NULL)
        );
        ''')
        
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

    print(f"Databáze '{db_name}' byla úspěšně vytvořena se všemi tabulkami.\n")
    
if __name__ == "__main__":
    create_database()