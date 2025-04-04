import re

class XMAPFile:
    def __init__(self, content):
        self.metadata = {}
        self.columns = []
        self.column_types = []
        self.data = [] 

        self._parse(content)

    def _parse(self, content):
        lines = content.strip().split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                if line.startswith("#h"):
                    self.columns = [col.strip() for col in line.lstrip("#h").split("\t")]
                elif line.startswith("#f"):
                    self.column_types = [typ.strip() for typ in line.lstrip("#f").split("\t")]
                else:
                    key_value = re.match(r"#\s*(.+?)\s*:\s*(.*)", line)
                    if key_value:
                        key, value = key_value.groups()
                        self.metadata[key.strip()] = value.strip()
            else:
                values = line.strip().split("\t")
                record = dict(zip(self.columns, self._cast_row(values)))
                self.data.append(record)

    def _cast_row(self, row):
        type_map = {"int": int, "float": float, "str": str}
        casted = []

        for col_name, val, dtype in zip(self.columns, row, self.column_types):
            val = val.strip()
            if col_name == "Alignment":
                casted.append(self.parse_alignment(val))
            else:
                try:
                    casted.append(type_map.get(dtype, str)(val))
                except:
                    casted.append(val)
        return casted

    def parse_alignment(self, value):
        matches = re.findall(r"\((\d+),(\d+)\)", value)
        return [(int(a), int(b)) for a, b in matches]