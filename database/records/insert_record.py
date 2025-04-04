import sqlite3

def insert_record(table_name, id, success=None, db_name="bionano.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(f'''
    INSERT INTO {table_name} (id, success)
    VALUES (?, ?)
    ''', (id, success))

    conn.commit()
    conn.close()
    print(f"Záznam byl vložen do tabulky '{table_name}'.\n")