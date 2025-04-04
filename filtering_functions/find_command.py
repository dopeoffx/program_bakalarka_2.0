from lark import Tree

ALLOWED_TABLES = {"SINGLE", "VARIANT", "PIPELINE", "ALIGNBNX", "COMPARISON", "SCAFFOLD", "MQR"}

class FindCommand():
    
     #Přesun     
    def find_cmd(self, items):
        table_tree = items[0]  
        
        
        if isinstance(table_tree, Tree):
            table_token = table_tree.children[0]  
        else:
            table_token = table_tree  

        table = self._get_val(table_token).upper()  
        
        print(f"DEBUG: Tabulka = {table}")

        if table not in ALLOWED_TABLES:
            raise ValueError(f"Neplatná tabulka: {table}")

        
        conditions = []
        if len(items) > 1:
            for condition_tree in items[1:]:  
                if isinstance(condition_tree, Tree) and condition_tree.data == "condition":
                    field = self._get_val(condition_tree.children[0])
                    operator = self._get_val(condition_tree.children[1])
                    value = self._get_val(condition_tree.children[2])
                    conditions.append((field, operator, value))
        print(f"Conditons {conditions}")
        query, values = self.build_query(table, conditions)
        print(query)
        print(values)
        self.cursor.execute(query, values)
        results = [row[0] for row in self.cursor.fetchall()]
        print(results)
        return results
    
    #Přesun
    def conditions(self, items):
        print("Zapínám conditions")
        result = []
        print(f'Items jsou {items}')
        if items is None:
            print("items je None")
            return None
        print(f'Items children jsou {items.children[0]}')
        current_condition = self.condition(items.children[0])  
        print("První")
        result.append(current_condition)

        for i in range(1, len(items.children), 2):
            if str(self._get_val(items.children[i])) in ("AND", "OR"):
                logical_op = str(self._get_val(items.children[i]))  
                next_condition = self.condition(items.children[i + 1])
                
                result.append((logical_op, next_condition)) 
            else:
                next_condition = self.condition(items.children[i])
                result.append( next_condition)
            
        print(f'Result: {result}')
        return result 
    
    #Přesun
    def condition(self, items):
        print("Zapínám condision")
        
        field = str(self._get_val(items.children[0])) 
        operator = str(self._get_val(items.children[1]))
        value_item = items.children[2] 
        
        if isinstance(value_item, Tree) and value_item.data == "string":
            value = self._get_val(value_item.children[0])[1:-1] 
        else:
            raw_value = self._get_val(value_item.children[0]) 

            try:
                if "." in raw_value or "e" in raw_value or "E" in raw_value:  
                    value = float(raw_value) 
                else:
                    value = int(raw_value) 
            except ValueError:
                value = str(raw_value)     

        print(f'Value: {value}')
        return (field, operator, value)


    #Přesun
    def build_query(self, table, conditions):
        query = f"SELECT id FROM {table}"
        values = []
        if conditions:
            filters = [f"{field} {operator} ?" for field, operator, value in conditions]
            values = [value for _, _, value in conditions]
            query += " WHERE " + " AND ".join(filters)
        return query, values
    