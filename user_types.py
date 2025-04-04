# user_types.py

class TXTFile:
    EXTENSIONS = [".txt"]
    def __init__(self, content):
        self.raw_lines = content.splitlines()
        self.data = self._parse_lines()

    def _parse_lines(self):
        parsed = []
        for line in self.raw_lines:
            line = line.strip()
            parsed.append(line)
        return parsed
    

class SMAPFile:
    EXTENSIONS = [".smap"]

    def __init__(self, content):
        self.data = self._parse_data(content)

    def _parse_data(self, content):
        lines = content.strip().splitlines()
        data = []
        headers = []

        for line in lines:
            if line.startswith("#"):
                if line.startswith("#h"):
                    headers = line[2:].strip().split("\t")
                continue

            row = line.strip().split("\t")
            if headers and len(row) == len(headers):
                data.append(self._cast_row(dict(zip(headers, row))))
        
        return data

    def _cast_row(self, row):
        for key, val in row.items():
            if val.replace('.', '', 1).replace('-', '', 1).isdigit():
                try:
                    row[key] = float(val) if '.' in val else int(val)
                except ValueError:
                    pass
        return row
