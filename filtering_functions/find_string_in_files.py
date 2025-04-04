import paramiko
from dotenv import load_dotenv
import os



def find_string_in_files(directory, search_string):
    
    load_dotenv("config.env")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        hostname=os.getenv("HOST"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD")
    )
    
    
    try:
        command = f'grep -rl "{search_string}" "{directory}"'
        stdin, stdout, stderr = ssh.exec_command(command)

        result = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if error:
            print(f"Chyba při hledání řetězce: {error}")
            return False
        
        if result:
            print(f"Řetězec nalezen v souborech:\n{result}")
            return True
        
        print("Řetězec nebyl nalezen v žádném souboru.")
        return False
    except Exception as e:
        print(f"Chyba při spouštění příkazu: {e}")
        return False
    finally:
        ssh.close()
   