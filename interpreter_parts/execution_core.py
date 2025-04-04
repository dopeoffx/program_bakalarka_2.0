from lark import Tree

class ExecutionCore():
    
    def execute(self, tree):
        print("DEBUG: Executing tree:", tree)
        if isinstance(tree, Tree) and tree.data == "start":
            print("START")
            results = []
            for child in tree.children:
                result = self.execute(child)
                if result is not None:
                    results.append(result)
            return results if results else None

        if isinstance(tree, Tree) and (tree.data == "function_call_value" or tree.data == "statement"):
            return self.execute(tree.children[0]) 
           
        if isinstance(tree, Tree) and tree.data == "var":
            print("DEBUG: Processing var:", tree)

            var_name = self._get_val(tree.children[0])
            value = self.variables.get(var_name, None)

            if value is None:
                raise ValueError(f"Chyba: Proměnná `{var_name}` neexistuje.")

            if len(tree.children[0].children) > 1 and tree.children[0].data == "attr_access":
                value = self.resolve_attr_access(value, tree.children[0])
    
            return value

        if isinstance(tree, Tree):
            print("OSTATNI")
            method_name = tree.data
            print(f"Method_name je: {method_name}")
            method = getattr(self, method_name, None)
            print(f"Method je: {method}")
            if method:
                return method(tree.children)
        else:
            return tree

        print("Zadny execute")
    
    def for_cmd(self, items):
        vars_tree = items[0]
        if len(vars_tree.children) == 2:
            index_var = self._get_val(vars_tree.children[0])
            value_var = self._get_val(vars_tree.children[1])
        else:
            index_var = None
            value_var = self._get_val(vars_tree.children[0])

        iterable = self.execute(items[1]) 
        if not isinstance(iterable, list):
            iterable = [iterable]

        commands = items[2].children 

        for index, value in enumerate(iterable):
            if index_var:
                self.variables[index_var] = index                     
                self.variables["index"] = index
            self.variables[value_var] = value
            self.variables["current"] = value
            print(f"Iterace {index}: {index_var}={index}, {value_var}={value}")

            for cmd in commands:
                self.execute(cmd)
    
        
    def assign(self, items):
        print("Zapinám assign")
        name_token = items[0]
        name = self._get_val(name_token)
        value_item = items[1]

        value = self.execute(value_item) if isinstance(value_item, Tree) else self._get_val(value_item)
        print(f'Value v assign je {value}')
        self.variables[name] = value
        

    
    def append_assign(self, items):
        print("Zapinám increment_assign")
        name_token = items[0]  
        name = self._get_val(name_token)
        value_item = items[1]  

        
        value = self.execute(value_item) if isinstance(value_item, Tree) else self._get_val(value_item)

        if name in self.variables:
            existing_value = self.variables[name]
            if isinstance(existing_value, list):
                existing_value.append(value)
            else:
                self.variables[name] = [existing_value, value]
        else:
            self.variables[name] = [value]  
    
    def assign_attr_expr(self, items):
        target_tree = items[0]
        expr_tree = items[1]

        value = self.execute(expr_tree)

        var_name = self._get_val(target_tree.children[0])
        container = self.variables.get(var_name)

        if container is None:
            raise ValueError(f"⚠️ Proměnná `{var_name}` neexistuje.")

        path = target_tree.children[1:]
        current = container

        for part in path[:-1]:
            key = self._extract_key_from_attr(part)
            current = current[key] if isinstance(current, (list, dict)) else getattr(current, key)

        last_part = path[-1]
        if isinstance(last_part.children[0], Tree) and last_part.children[0].data == "slice":
            slice_parts = [self._get_val_signed_number(c) if c else None for c in last_part.children[0].children]
            current[slice(*slice_parts)] = value
        else:
            key = self._extract_key_from_attr(last_part)
            if isinstance(current, dict):
                current[key] = value
            elif isinstance(current, list):
                current[int(key)] = value
            else:
                setattr(current, key, value)

        print(f"Přiřazeno: {var_name} → {value}")
        return value
    
    def del_cmd(self, items):
        attr_access_tree = items[0]

        var_name = self._get_val(attr_access_tree.children[0])
        value = self.variables.get(var_name)

        if value is None:
            print(f"Proměnná `{var_name}` neexistuje.")
            return

        if len(attr_access_tree.children) == 1:
            del self.variables[var_name]
            print(f"Smazána proměnná `{var_name}`")
            return

        try:
            for attr_tail in attr_access_tree.children[1:-1]:
                key = self._extract_attr_tail_key(attr_tail)
                value = value[key]

            final_key = self._extract_attr_tail_key(attr_access_tree.children[-1])
            print(f"Value je {value} a final key je {final_key}")
            if isinstance(final_key, slice):
                del value[final_key]
                print(f"Smazán rozsah {final_key} z `{var_name}`")
            else:
                del value[final_key]
                print(f"Smazán prvek `{final_key}` z `{var_name}`")

        except Exception as e:
            print(f"Chyba při mazání z `{var_name}`: {e}")
            
    def addition(self, items):
        left = self.execute(items[0]) if isinstance(items[0], Tree) else self._get_val(items[0])
        right = self.execute(items[1]) if isinstance(items[1], Tree) else self._get_val(items[1])

        if isinstance(left, list) and isinstance(right, list):
            return left + right
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left + right

        raise ValueError(f"Nepodporované sčítání: {type(left)} + {type(right)}")