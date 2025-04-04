import paramiko
import os
from dotenv import load_dotenv

def find_files(project_id, where_clauses, variables):
    load_dotenv("config.env")
    current_folder = os.path.join(os.getenv("REMOTE_DIR"), str(project_id))
    return filter_files(current_folder, where_clauses)


def build_find_command(directory, conditions):
    find_parts = [f'find "{directory}" -type f'] 
    grep_part = "" 

    for condition in conditions:
        key, value = condition  

        if key == "contain_file":
            find_parts.append(f'-name "{value}"')  

        elif key == "size_gt":
            find_parts.append(f'-size +{convert_size(value)}')

        elif key == "size_lt":
            find_parts.append(f'-size -{convert_size(value)}')

        elif key == "size":
            find_parts.append(f'-size {convert_size(value)}')

        elif key == "contain_string":
            grep_part = f'xargs grep -l --with-filename "{value}"'  

    find_cmd = " ".join(find_parts)
    if grep_part:
        find_cmd += f" | {grep_part}"

    return find_cmd


def convert_size(size_str):
    units = {"K": "k", "M": "M", "G": "G"}
    if size_str[-1] in units:
        return f"{size_str[:-1]}{units[size_str[-1]]}"
    return size_str 


def filter_files(directory, conditions):
    load_dotenv("config.env")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        hostname=os.getenv("HOST"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD")
    )

    find_cmd = build_find_command(directory, conditions)

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
        for file in files:
            print(file)

        return files

    except Exception as e:
        print(f"Chyba při spouštění příkazu: {e}")
        return []
    finally:
        ssh.close()
