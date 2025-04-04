def find_file(sftp, start_path, target_filename):
    try:
        for entry in sftp.listdir_attr(start_path):
            full_path = f"{start_path}/{entry.filename}"

            if entry.st_mode & 0o170000 == 0o100000:  
                if target_filename in entry.filename:
                    return full_path

            elif entry.st_mode & 0o170000 == 0o040000:  # adresář
                result = find_file(sftp, full_path, target_filename)
                if result:
                    return result

    except Exception as e:
        print(f"Chyba při prohledávání {start_path}: {e}\n")

    return None  
