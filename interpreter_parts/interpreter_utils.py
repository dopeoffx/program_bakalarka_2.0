from lark import Tree, Token

class InterpreterUtils:
    def _extract_key_from_attr(self, attr):
        key_tree = attr.children[0]
        if isinstance(key_tree, Tree) and key_tree.data == "index":
            return self._get_val_signed_number(key_tree.children[0])
        elif key_tree.data == "index_var":
            var_name = self._get_val(key_tree.children[0])
            return self.variables.get(var_name)
        elif isinstance(key_tree, Tree) and key_tree.data == "string_key":
            return self._get_val(key_tree.children[0])[1:-1]
        elif key_tree.data == "slice":
            parts = [self._get_val_signed_number(c) if c else None for c in key_tree.children]
            return slice(*parts)
        else:
            return self._get_val(attr)

    def term_expr(self, items):
        if isinstance(items[0], Tree):
            return self.execute(items[0]) 

        value = self._get_val(items[0])  
        return value
  
    def _get_val(self, item):
        if isinstance(item, Tree):  
            return self._get_val(item.children[0])
        elif isinstance(item, Token): 
            return item.value
        return item  

    def _get_val_index(self, item):
        if isinstance(item, Tree):  
            return self._get_val_index(item.children[0])
        elif isinstance(item, Token): 
            return self.variables[item]
        return self.variables[item]  

    def _get_val_signed_number(self, item):
        if item is None:
            return item
        children = item.children
        if len(children) == 2:
            sign_token, number_token = children
            sign = -1 if sign_token.type == "MINUS" else 1
            num = int(number_token.value)
            return sign * num

        elif len(children) == 1:
            number_token = children[0]
            return int(number_token.value)

        raise ValueError("Neplatná struktura signed_number")

    def extract_token(self, value_item):
        if isinstance(value_item, Tree) and value_item.data == "string":
            value = self.variables[f"{self._get_val(value_item.children[0].children[0])[1:-1]}"] 
        else:
            value = self.variables[f"{self._get_val(value_item.children[0].children[0])}"] 
        return value  

    def resolve_attr_access(self, base_value, attr_access_tree):
        current = base_value
        for attr in attr_access_tree.children[1:]: 
            key_tree = attr.children[0] if isinstance(attr, Tree) and attr.children else None

            if isinstance(key_tree, Tree) and key_tree.data == "slice":
                parts = [self._get_val_signed_number(c) if c else None for c in key_tree.children]
                current = current[slice(*parts)]
            elif isinstance(key_tree, Tree) and key_tree.data == "index":
                key = self._get_val_signed_number(key_tree.children[0])
                current = current[key]
            elif isinstance(key_tree, Tree) and key_tree.data == "string_key":
                key = self._get_val(key_tree.children[0])[1:-1]
                current = current[key]
            elif isinstance(key_tree, Tree) and key_tree.data == "index_var":
                key = self._get_val_index(key_tree.children[0])
                current = current[key]
            else:
                key = self._get_val(attr)
                if isinstance(current, list):
                    current = current[int(key)]
                elif isinstance(current, dict):
                    current = current[key]
                elif hasattr(current, key):
                    current = getattr(current, key)
                else:
                    raise ValueError(f"Chyba: `{current}` neobsahuje klíč/index `{key}`.")
        return current  
            
    def wrap(self, item):
        if isinstance(item, Tree) and item.data ==  "attr_access":
            wrapped_tree = Tree('var', [item])
            value = self.execute(wrapped_tree)
        else:
            value = self.execute(item)
            
        return value
     
    def table(self, items):
        table_name = self._get_val(items[0])  
        return table_name.upper()  

    def _extract_attr_tail_key(self, attr_tail_tree):
        inner = attr_tail_tree.children[0]

        if isinstance(inner, Tree) and inner.data == "index":
            return self._get_val_signed_number(inner.children[0])
        elif isinstance(inner, Tree) and inner.data == "string_key":
            return self._get_val(inner.children[0])[1:-1]  # bez uvozovek
        elif isinstance(inner, Tree) and inner.data == "slice":
            parts = [self._get_val_signed_number(c) if c is not None else None for c in inner.children]
            return slice(*parts)
        elif isinstance(inner, Tree) and inner.data == "index_var":
            key_name = self._get_val(inner.children[0])
            return self.variables.get(key_name)
        elif isinstance(inner, Token):  # např. atribut .data
            return inner.value
        else:
            raise ValueError(f"Nepodporovaný přístup: {inner}")
           
    def number(self, n):
        print(f'N je {n}')
        if len(n[0].children)>1:
            val = str(self._get_val_signed_number(n[0]))
        else:
            val = self._get_val(n[0])
        print(f'VAL je {val}')
        try:
            return int(val) if "." not in val and "e" not in val.lower() else float(val)
        except ValueError:
            raise ValueError(f"Nelze převést '{val}' na číslo.")

    def string(self, s):
        return self._get_val(s[0])[1:-1]

    def var(self, name):
        var_name = self._get_val(name[0])
        return self.variables.get(var_name, None)

    def list(self, items):
        result = []
        print(f'Items jsou {items}')
        if items ==[None]: 
            return []
        for item in items:
            if isinstance(item, Tree) and item.data == "raw_expr_block":
                raw_code = item.children[1].value.strip()
                print(f'Raw code jsou {raw_code}')
                try:
                    result.append(self.my_exec(raw_code))
                except Exception as e:
                    raise ValueError(f"Chyba při vyhodnocení výrazu: {raw_code} → {e}")
            else:
                result.append(self.execute(item) if isinstance(item, Tree) else self._get_val(item))
        return result

    def list_element(self, items):
        return self.execute(items[0])

    def statement(self, children):
        return self.execute(children[0])

    def size_value(self, items):
        number = self._get_val(items[0]) 
        unit = self._get_val(items[1]) if len(items) > 1 else "" 

        if unit:  
            return f"{number}{unit}" 
        
        return int(number) if number.isdigit() else float(number)

    def raw_eval(self, items):
        print(f"Items jsou: {items}")
        raw_code = items[0].children[1].value.strip()
        print(f'Raw code je {raw_code}')
        try:
            return self.my_exec(raw_code)
        except Exception as e:
            raise ValueError(f"Chyba při vyhodnocení výrazu: {raw_code}\n{e}")