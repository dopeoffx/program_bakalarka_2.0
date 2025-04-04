import database.records.insert_record as insert_record
import json
import database.records.Report_simple_record as Report_simple_record
import database.records.MQR_record as MQR_record

def create_record(data, path, sftp, db_name="bionano.db"):
    table_name = data["subject"].replace("start", "").upper()
    
    output = data["output"]
    
    output_str = json.dumps(output).lower()

    
    contains_error = "error" in output_str
    
    if  table_name=="SCAFFOLD":
        id = data["input"]["outobject"]["jobpk"]
        insert_record.insert_record(table_name, id, not contains_error, db_name)
    elif table_name=="VARIANT":
        id = data["input"]["outobject"]["jobpk"]
        insert_record.insert_record(table_name, id, not contains_error, db_name)
    elif table_name=="MQR":
        id = data["input"]["jobpk"]
        MQR_record.MQR_record(id, path, sftp, not contains_error, db_name)
    else:
        id = data["input"]["outobject"]["jobpk"]
        Report_simple_record.Report_simple_record(table_name, id, path, sftp, not contains_error, db_name)