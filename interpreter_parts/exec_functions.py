from lark import Tree

class ExecFunctions():
    def function_call(self, items):
        func_name = self._get_val(items[0])

        if func_name in ("map", "filter"):
            lambda_expr = items[1]
            lambda_var = self._get_val(lambda_expr.children[0])

            lambda_body_token = lambda_expr.children[2]
            if hasattr(lambda_body_token, "value"):
                lambda_body_str = lambda_body_token.value.strip()
            else:
                lambda_body_str = self.rebuild_expr(lambda_body_token)

            iterable_expr = items[2]
            iterable = self.execute(iterable_expr) if isinstance(iterable_expr, Tree) else self._get_val(iterable_expr)
            if not isinstance(iterable, list):
                iterable = [iterable]

            
            print("lambda_body_str:", repr(lambda_body_str))
            
                
            def run_lambda(x):
                context = {**self.variables}
                local_vars = {}
                exec(f"def _lambda({lambda_var}):\n    return {lambda_body_str}", context, local_vars)
                return local_vars["_lambda"](x)


            return [run_lambda(x) for x in iterable] if func_name == "map" else [x for x in iterable if run_lambda(x)]

        # Ostatní funkce 
        args = [self.execute(arg) if isinstance(arg, Tree) else self._get_val(arg) for arg in items[1:]]

        if func_name in self.functions and callable(self.functions[func_name]):
            return self.functions[func_name](*args)

        raise ValueError(f"Nepodporovaná funkce: {func_name}")


    def my_exec(self, raw_code):
        context = {**self.variables}
        local_vars = {}
        exec(f"def _temp():\n    return {raw_code}", context, local_vars)
        return local_vars["_temp"]()