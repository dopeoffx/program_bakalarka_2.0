import json
import stat
import paramiko
import os

import database.create_database as create_database
import database.records.json_separator as json_separator
import database.records.insert_record as insert_record
import database.create_record as create_record

import database.delete_database as delete_database

from database.default_projects import insert_projects

from dotenv import load_dotenv


def connect_ssh(HOST, PORT, USERNAME, PASSWORD):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD)
    return client

def find_files_containing_string(sftp):
    load_dotenv("config.env")
    #REMOTE_DIR = os.getenv("REMOTE_DIR")
    #SUMMARY_DIR = os.getenv("SUMMARY_DIR")
    SUMMARY_DIR = os.getenv("REMOTE_DIR")
    REMOTE_DIR = os.getenv("SUMMARY_DIR")
    SEARCH_STRING = os.getenv("SEARCH_STRING") 
    #sftp = ssh_client.open_sftp()
    sftp.chdir(REMOTE_DIR)
    
    local_file = open("JSONS.txt", "w")
    
    for folder in sftp.listdir():
        folder_path = os.path.join(REMOTE_DIR, folder)
        
        
        
        if not is_directory(sftp, folder_path):
            continue 

        try:
            check = False
            for filename in sftp.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                print(f'Filepath je {file_path}, filename je {filename}, search string je {SEARCH_STRING}\n')
                if not is_file(sftp, file_path) or not filename.endswith(".json"):
                    continue 
                
                if SEARCH_STRING in filename:
                    check=True
                    print("Search string")
                        
                    with sftp.open(file_path, 'r') as file:
                            try:
                                json_content = json.load(file)
                                local_file.write(f"Obsah souboru {folder}:")
                                local_file.write(json.dumps(json_content, indent=4, ensure_ascii=False))
                                summary_path = os.path.join(SUMMARY_DIR, folder)
                                create_record.create_record(json_content, summary_path, sftp)
                            except json.JSONDecodeError:
                                local_file.write(f"Chyba při čtení JSON souboru: {folder}")
                            finally:
                                file.close() 
            if check == False:
                local_file.write(f"Comparison: {folder}\n")
                insert_record.insert_record("Comparison", folder)
                   
        except IOError:
            continue  # bez přístupu

    insert_projects(sftp.listdir())
    
   

    sftp.close()

def is_directory(sftp, path):
    try:
        return stat.S_ISDIR(sftp.stat(path).st_mode)
    except IOError:
        return False

def is_file(sftp, path):
    try:
        return stat.S_ISREG(sftp.stat(path).st_mode)
    except IOError:
        return False

def run(sftp_wrapper):
    delete_database.delete_database("bionano.db")
    create_database.create_database()
    find_files_containing_string(sftp_wrapper.get_sftp())
    


