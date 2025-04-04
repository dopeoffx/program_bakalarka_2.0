import sqlite3

def show_table_content(db_name, table_name):
    # Připojení k databázi
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        # Výběr všech dat z tabulky
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Získání názvů sloupců
        columns = [description[0] for description in cursor.description]

        # Zobrazení dat
        print(f"\n📊 Obsah tabulky '{table_name}':\n")
        print(" | ".join(columns))
        print("-" * (len(columns) * 15))

        for row in rows:
            print(" | ".join(str(item) if item is not None else '' for item in row))

    except sqlite3.Error as e:
        print(f"❗ Chyba: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    show_table_content("bionano.db", "ALIGNBNX")