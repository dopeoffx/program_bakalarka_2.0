import re


class BNXFile:
    def __init__(self, content):
        self.metadata = {}
        self.columns = []
        self.column_types = []
        self.quality_headers = []

        self.data = [] 

        self._parse(content)

    def _parse(self, content):
        lines = content.strip().split("\n")
        current_record = None

        for line in lines:
            line = line.strip() 
            if line.startswith("#"):
                if line.startswith("#0h"):
                    self.columns = [col.strip() for col in line.lstrip("#0h").split("\t")]
                    #self.columns = line.lstrip("#0h").split("\t")
                elif line.startswith("#0f"):
                    self.column_types = [col.strip() for col in line.lstrip("#0f").split("\t")]
                    #self.column_types = line.lstrip("#0f").split("\t")
                elif line.startswith("#Qh"):
                    self.quality_headers = line.lstrip("#Qh").split("\t")[1:]
                else:
                    key_value = re.match(r"#\s*(.+?)\s*:\s*(.*)", line)
                    if key_value:
                        key, value = key_value.groups()
                        self.metadata[key] = value

            elif line.startswith("0"):
                values = line.split("\t")
                record = dict(zip(self.columns, self._cast_row(values)))
                current_record = record
                self.data.append(record)

            elif line.startswith("1") and current_record:
                current_record["LabelPositions"] = [float(x) for x in line.split("\t")[1:]]

            elif line.startswith("2") and current_record:
                current_record["Fragments"] = [float(x) for x in line.split("\t")[1:]]

            elif line.startswith("QX") and current_record:
                parts = line.split("\t")
                score_id = parts[0]
                scores = [float(x) for x in parts[1:]]
                current_record[score_id] = scores

    def _cast_row(self, row):
        type_map = {"int": int, "float": float, "str": str}
        casted = []
        for val, dtype in zip(row, self.column_types):    
            try:
                casted.append(type_map.get(dtype, str)(val))
            except:
                casted.append(val)
        return casted
