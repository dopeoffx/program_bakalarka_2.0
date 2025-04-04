import database.records.insert_record as insert_record
import json

def json_separator(data):
    type = data["subject"].replace("start", "").upper()
    
    if type=="MQR": 
        id = data["input"]["jobpk"]
    else:
        id = data["input"]["outobject"]["jobpk"]
    output = data["output"]
    
    output_str = json.dumps(output).lower()

    contains_error = "error" in output_str
    
    if contains_error:
        insert_record.insert_record(type, id, 1)
    else:
        insert_record.insert_record(type, id, 0)