import re
import sqlite3
import os
import filtering_functions.find_file as find_file
import database.records.insert_record as insert_record

def MQR_record(id, folder_path, sftp, succes, db_name):
    
    if succes== False:
        insert_record.insert_record("MQR", id, succes, db_name)
        return
    
    file_path = find_file.find_file(sftp, folder_path, "Molecules_summary.txt")
    
    if file_path==None:
        return
    

    
    
    with sftp.open(file_path, 'r') as file:       
        try:          
            content = file.read().decode('utf-8')
            
            data = parse_mqr_content(content)

            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            values = list(data.values())

            query = f"INSERT INTO MQR (id, success, {columns}) VALUES (?, ?, {placeholders})"
            cursor.execute(query, [id] + [succes] + values)

            conn.commit()
            conn.close()

            print(f"Záznam s ID {id} byl úspěšně vložen do tabulky MQR.\n")
        except Exception as e:
            print(f"Chyba MQR: {e}\n")
        finally:
            file.close() 
            
            

def parse_mqr_content(content):
    data = {}

    patterns = {
        "input_bnx_file": r"Input BNX file:\s*(.*)",
        "input_reference_file": r"Input reference file for channel 1:\s*(.*)",
        "output_folder": r"Output folder:\s*(.*)",
        "min_nicks_channel1": r"Minimum nicks in each channel of the molecule:\s*(\d+)",
        "min_length_kb": r"Minimum length of the molecule in kb:\s*(\d+)",
        "snr_cutoff_channel1": r"SNR cutoff for channel 1:\s*([\d.]+)",

        "instrument_sn": r"Instrument SN:\s*(.*)",
        "chip_sn": r"Chip SN:\s*(.*)",
        "run_id": r"Run ID:\s*(.*)",
        "sample": r"Sample:\s*(.*)",
        "flowcell": r"Flowcell:\s*(\d+)",
        "total_scan_count": r"Total Scan Count:\s*(.*)",
        "job_id": r"Job ID:\s*(\d+)",
        "job_created_on": r"Job created on:\s*(.*)",
        "total_molecules_input_bnx": r"Total molecules in the input BNX:\s*(\d+)",

        "refaligner_path": r"RefAligner absolute path:\s*(.*)",

        "num_molecules_filtered": r"Number of molecules \(filtered\):\s*(\d+)",
        "total_molecule_length_bp": r"Total molecule length \(bp\):\s*([\d.]+)",
        "avg_molecule_length_bp": r"Average molecule length \(bp\):\s*([\d.]+)",
        "molecule_length_n50_bp": r"Molecule length N50 \(bp\):\s*([\d.]+)",
        "total_dna_20kb": r"Total DNA \(>= 20 kbp\):\s*([\d.]+)",
        "n50_20kb": r"N50 \(>= 20 kbp\):\s*([\d.]+)",
        "total_dna_150kb_min9": r"Total DNA \(>= 150 kbp & minSites >= 9\):\s*([\d.]+)",
        "n50_150kb_min9": r"N50 \(>=150 kbp & minSites >= 9\):\s*([\d.]+)",
        "num_molecules_20kb": r"N Molecules \(>= 20 kbp\):\s*(\d+)",
        "num_molecules_150kb": r"N Molecules \(>= 150 kbp\):\s*(\d+)",
        "num_molecules_150kb_min9": r"N Molecules \(>= 150 kbp & minSite >= 9\):\s*(\d+)",

        "avg_label_density": r"Average label density for channel 1 \(/100kb\):\s*([\d.]+)",
        "avg_label_snr": r"Average label SNR for channel 1:\s*([\d.]+)",
        "avg_molecule_snr": r"Average molecule SNR for channel 1:\s*([\d.]+)",
        "avg_label_intensity": r"Average label intensity for channel 1:\s*([\d.]+)",
        "avg_molecule_intensity": r"Average molecule intensity for channel 1:\s*([\d.]+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            value = match.group(1)

            if value.isdigit():
                data[key] = int(value)
            else:
                try:
                    data[key] = float(value)
                except ValueError:
                    data[key] = value.strip()  #bez bílých znaků

    return data