import importlib
import sqlite3
import sys
from database.default_projects import get_projects
from dotenv import load_dotenv

class EnvironmentCommands():
    #Přesun 
    def reload_projects_cmd(self, _):
        self.variables["projects"] = get_projects()
        print("Projekty načteny")
    #Přesun 
    def reload_config_cmd(self, _):
        print("Načítám znovu .env soubor...")
        try:
            load_dotenv("config.env", override=True)
            print("config.env úspěšně načten")

            if hasattr(self, "sftp_wrapper"):
                try:
                    self.sftp_wrapper.reconnect()
                    if self.sftp_wrapper.sftp is None:
                        raise ConnectionError("Připojení k SFTP se nezdařilo.")
                    print("SFTP připojení obnoveno.")
                except Exception as e:
                    print(f"Obnovení připojení selhalo: {e}")

        except Exception as e:
            print(f"Chyba při načítání config.env: {e}")

    #Přesun     
    def reload_database_cmd(self, items):
        if items and items[0]:
            db_name = self._get_val(items[0])[1:-1]
        else:
            db_name = "bionano.db"
        self.reload_database(db_name)
    #Přesun     
    def reload_database(self, db_path="bionano.db"):
        try:
            if self.conn:
                self.conn.close()
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            print(f"Databáze znovu načtena: {db_path}")
        except Exception as e:
            print(f"Chyba při načítání databáze: {e}")
    

    #Přesun         
    def load_functions_cmd(self, _):
        try:
            if "user_functions" in sys.modules:
                importlib.reload(sys.modules["user_functions"])
                module = sys.modules["user_functions"]
            else:
                import user_functions
                module = user_functions

            functions = {
                name: getattr(module, name)
                for name in dir(module)
                if not name.startswith("_") and callable(getattr(module, name))
            }
            self.functions.update(functions)
            print("Uživatelské funkce byly načteny.")
        except Exception as e:
            print(f"Chyba při načítání uživatelských funkcí: {e}")
    #Přesun 
    def load_types_cmd(self, _):
        self.load_user_types()
    #Přesun 
    def load_user_types(self):
        try:
            if "user_types" in sys.modules:
                importlib.reload(sys.modules["user_types"])
                module = sys.modules["user_types"]
            else:
                import user_types
                module = user_types

            self.custom_types = {} 

            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and hasattr(obj, "EXTENSIONS"):
                    for ext in obj.EXTENSIONS:
                        self.custom_types[ext] = obj
            print("Uživatelské typy byly načteny:", self.custom_types)
        except Exception as e:
            print(f"Chyba při načítání uživatelských typů: {e}")