import cmd
import sqlite3
import sys
import database.fill_database as fill_database
from interpreter import parser, Interpreter
import pickle
import os
from dotenv import load_dotenv 
from SFPT_connection.SFPTConnectionWrapper import SFTPConnectionWrapper


class StdoutRedirector:
    def __init__(self, shell):
        self.shell = shell
    def write(self, message):
        if message.strip():
            self.shell.stdout.write(message)
            self.shell.stdout.flush()
    def flush(self):
        pass

class MyShell(cmd.Cmd):
    intro = "Vítejte v mém shellu. Napište 'help' pro seznam příkazů."
    prompt = "> "
    SAVE_FILE = "variables.pkl"

    def __init__(self):
        super().__init__()
        self.busy = False
        load_dotenv("config.env")
        
        self.wrapper = SFTPConnectionWrapper()
        
        if not os.path.exists(os.getenv("DATABASE_NAME")):
            print("Databáze neexistuje, vytvářím...")
            fill_database.run(self.wrapper)
        else:
            print("Databáze existuje.")        
       
        self.interpreter = Interpreter(self.wrapper)
        
    def do_save(self, arg):
        try:
            with open(self.SAVE_FILE, "wb") as f:
                pickle.dump(self.interpreter.variables, f)
            print("Proměnné byly úspěšně uloženy.")
        except Exception as e:
            print(f"Chyba při ukládání proměnných: {e}")
            

    def do_load(self, arg):
        if not os.path.exists(self.SAVE_FILE):
            print("Soubor s proměnnými neexistuje. Načítání přeskočeno.")
            return

        try:
            with open(self.SAVE_FILE, "rb") as f:
                self.interpreter.variables = pickle.load(f)
            print("Proměnné byly úspěšně načteny.")
        except Exception as e:
            print(f"Chyba při načítání proměnných: {e}")    
        

    def do_exit(self, arg):
        if self.busy:
            print("Nelze ukončit shell během běhu příkazu.")
            return
        print("Ukončuji shell...")
        return True

    def default(self, line):
        try:
            print(f"DEBUG: Vstupní řetězec -> {line}")
            
            tree = parser.parse(line)

            print(f"DEBUG: Vygenerovaný parse tree:\n{tree.pretty()}")

            
            if not tree or not tree.children:  
                raise ValueError("Chyba: `tree` je prázdný nebo nevalidní.")

            self.interpreter.execute(tree)
        
        except Exception as e:
            print(f"Chyba při zpracování příkazu `{line}`: {e}")


    def precmd(self, line):
        if self.busy:
            print("Příkaz stále běží. Počkejte na dokončení.")
            return ""
        return line

    def do_update(self, arg):
        self.busy = True
        self.prompt = "(běží...) > "
        original_stdout = sys.stdout
        sys.stdout = StdoutRedirector(self)
        
        try:
            fill_database.run(self.wrapper)
        finally:
            sys.stdout = original_stdout
            self.busy = False
            self.prompt = "> "
                      
            
    def do_print_database(self, arg):
        conn = sqlite3.connect("bionano.db")
        cursor = conn.cursor()

        tables= ["SINGLE", "VARIANT", "PIPELINE", "ALIGNBNX", "COMPARISON", "SCAFFOLD", "MQR"]

        for table_name in tables:
            print(f"\nTabulka: {table_name}")
            try:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                print("Sloupce:", ", ".join(columns))

                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()

                for row in rows:
                    print(row)

            except Exception as e:
                print(f"Chyba při čtení tabulky {table_name}: {e}")

        conn.close()


            
    def do_run_script(self, filename):
        if not filename:
            print("Chyba: Musíš zadat název souboru se skriptem.")
            return

        try:
            with open(filename, "r") as file:
                lines = file.readlines()

            print(f"🔹 Spouštím skript: {filename}")

            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                print(f"> {line}")
                self.onecmd(line)

            print(f"Skript `{filename}` úspěšně dokončen.")

        except FileNotFoundError:
            print(f"Chyba: Soubor `{filename}` neexistuje.")
        except Exception as e:
            print(f"Chyba při vykonávání skriptu `{filename}`: {e}")

if __name__ == "__main__":
    MyShell().cmdloop()
