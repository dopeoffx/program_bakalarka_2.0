import os

def delete_database(db_name):
    if os.path.exists(db_name):
        os.remove(db_name)
        print(f"Databáze '{db_name}' byla úspěšně smazána.\n")
    else:
        print(f"Databáze '{db_name}' neexistuje.\n")