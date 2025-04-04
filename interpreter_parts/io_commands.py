import csv
import gzip
import io
import os
import filtering_functions.find_file as find_file
from dotenv import load_dotenv
from filtering_functions.files import find_files
from SFPT_connection.SFTP_download_large_files import download_file_content
from MY_DATA_TYPES import BNX, CMAP, XMAP

class IOCommands: 
    def print_cmd(self, items):
        print("Zapinám print")
        
        value = self.wrap(items[0])

        print(value)  
     
    def print_list_cmd(self, items):
        print("Zapinám print_list")
        
        value = self.wrap(items[0])

        for record in value:
            print(record)
            print()
              
    def save_output_cmd(self, items):
        print("Zapínám save_output")

        filename = self._get_val(items[0])[1:-1] 
        value = self.wrap(items[1])

        print(f"Cílový soubor: {filename}")

        is_csv = filename.lower().endswith(".csv")

        if is_csv:
            print("CSV výstup detekován")
            if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                try:
                    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=value[0].keys())
                        writer.writeheader()
                        writer.writerows(value)
                    print(f"Data uložena do CSV souboru: {filename}")
                except Exception as e:
                    print(f"Chyba při ukládání do CSV: {e}")
            else:
                print("Data nejsou ve formátu list[dict] – nelze uložit jako CSV.")

        else:
            
            try:
                with open(filename, "w", encoding="utf-8") as file:
                    file.write(str(value))
                print(f"Výstup uložen do souboru: {filename}")
            except Exception as e:
                print(f"Chyba při ukládání souboru `{filename}`: {e}")

    def loadfile_cmd(self, items):
        print("Zapinam loadfile")
        sftp = self.sftp_wrapper.get_sftp()

        if len(items) == 2 and items[1] is None:
            file_path = self._get_val(items[0])[1:-1]  
            file_name = os.path.basename(file_path)
            print("Přímá cesta:", file_path)
        elif len(items) == 2:
            file_name = self._get_val(items[0])[1:-1]
            folder = self.variables[self._get_val(items[1])]
            print(f"Hledám soubor `{file_name}` ve složce `{folder}`")

            load_dotenv("config.env")
            current_folder = os.path.join(os.getenv("REMOTE_DIR"), str(folder))
            file_path = find_file.find_file(sftp, current_folder, file_name)
        else:
            raise ValueError("loadfile 1 nebo 2 parametry.")    
        
        print(f"Cesta je {file_path}")
        if file_path==None:
            print(f"Soubor `{file_name}` nebyl nalezen.")
            return
        
        try:
            print("Testuji připojení k SFTP...")
            sftp.listdir(".")  
            print("SFTP připojení funguje!")
        except Exception as e:
            print(f"Chyba: Nelze přistoupit k SFTP: {e}")
            return

        try:
            print("Načítám obsah") 
            content = download_file_content(sftp, file_path)

            if file_name.endswith(".gz"):
                print("Detekován komprimovaný soubor .gz – dekomprimuji...")
                with gzip.GzipFile(fileobj=io.BytesIO(content.encode())) as f:
                    content = f.read().decode("utf-8")

                file_name = file_name[:-3]
            
            if file_name.endswith(".xmap"):
                print("Vracím xmap") 
                return XMAP.XMAPFile(content)
            elif file_name.endswith(".cmap"):
                print("Vracím cmap") 
                return CMAP.CMAPFile(content)
            elif file_name.endswith(".bnx"):
                print("Vracím bnx")
                return BNX.BNXFile(content)
            else:
                ext = os.path.splitext(file_name)[-1].lower()
                if ext in self.custom_types:
                    print(f"Vracím uživatelský typ pro {ext}")
                    return self.custom_types[ext](content)
                else:
                    raise ValueError(f"Chyba: Nepodporovaný typ souboru '{file_name}'")        
        except Exception as e:
            print(f"Chyba typu {type(e).__name__}: {e}")