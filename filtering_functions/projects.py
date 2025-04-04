import paramiko
import os
from dotenv import load_dotenv

def filter_projects(project_id, where_clauses, variables):
    load_dotenv("config.env")
    
    if not where_clauses:
        return True

    current_folder = os.path.join(os.getenv("REMOTE_DIR"), str(project_id))
    
    find_conditions, grep_conditions = generate_find_conditions(where_clauses)

    matching_projects = execute_find_ssh(current_folder, find_conditions, grep_conditions)

    if matching_projects:
        return True

    return False


def generate_find_conditions(where_clauses):
    find_conditions = []
    grep_conditions = []

    for condition in where_clauses:
        field, value = condition

        if field == "contain_file":
            find_conditions.append(f'-name "{value}"')
        elif field == "size_gt":
            find_conditions.append(f'-size +{value}')
        elif field == "size_lt":
            find_conditions.append(f'-size -{value}')
        elif field == "size":
            find_conditions.append(f'-size {value}')

        elif field == "contain_string":
            grep_conditions.append(f'grep -l "{value}"')

    return " ".join(find_conditions), " | ".join(grep_conditions)


def execute_find_ssh(directory, find_conditions, grep_conditions):
    load_dotenv("config.env")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        hostname=os.getenv("HOST"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD")
    )

    find_cmd = f'find "{directory}" -type f {find_conditions}'
    if grep_conditions:
        find_cmd += f' | xargs {grep_conditions}'

    print(f"Spouštím příkaz: {find_cmd}")

    try:
        stdin, stdout, stderr = ssh.exec_command(find_cmd)
        files = stdout.read().decode().strip().split("\n")
        error = stderr.read().decode().strip()

        if error:
            print(f"Chyba při hledání souborů: {error}")
            return []

        if files == [""]:
            print("Žádné soubory neodpovídají kritériím.")
            return []

        print(f"Nalezeno {len(files)} souborů:")


        return files

    except Exception as e:
        print(f"Chyba při spouštění příkazu: {e}")
        return []
    finally:
        ssh.close()

