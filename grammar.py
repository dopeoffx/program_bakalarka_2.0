grammar = r"""
    start: statement+

    statement: assign
             | find_cmd
             | print_cmd
             | print_list_cmd
             | for_cmd
             | loadfile_cmd
             | del_cmd
             | save_output_cmd
             | expr
             | load_functions_cmd
             | reload_database_cmd
             | load_types_cmd
             | reload_config_cmd
             | reload_projects_cmd
    
    load_types_cmd: "load_types" "(" ")" -> load_types_cmd
         

    reload_database_cmd: "reload_database" "("[ESCAPED_STRING]")" -> reload_database_cmd

    assign: attr_access "=" expr        -> assign_attr_expr
          |NAME "=" (find_cmd | expr | loadfile_cmd | for_cmd )        -> assign
          | NAME "+=" (find_cmd | loadfile_cmd | expr)                     -> append_assign

    reload_projects_cmd: "reload_projects" "(" ")" -> reload_projects_cmd
    reload_config_cmd: "reload_config" "(" ")" -> reload_config_cmd
    find_cmd: "find" "("table ("," expr)*")"       -> find_cmd
    print_cmd: "print" "("expr")"            -> print_cmd
    print_list_cmd: "print_list" "("expr")"  -> print_list_cmd
    for_cmd: "for" for_vars "in" expr ":" for_block
    loadfile_cmd: "loadfile""(" ESCAPED_STRING ["," expr]")" -> loadfile_cmd
    load_functions_cmd: "load_functions" "(" ")"-> load_functions_cmd
    del_cmd: "del" "("attr_access")"                      -> del_cmd
    save_output_cmd: "save_output" "("ESCAPED_STRING "," attr_access ")"-> save_output_cmd
    
    for_vars: NAME ("," NAME)?          -> for_vars
    for_block: statement (";" statement)*   -> for_block

    attr_access: NAME attr_tail*

    attr_tail: "." NAME
            | "[" slice_or_index "]"

    slice_or_index: [signed_number] ":" [signed_number] [":" signed_number]   -> slice
                | signed_number                        -> index
                | ESCAPED_STRING                       -> string_key
                | NAME                                -> index_var

    signed_number: MINUS? NUMBER
    MINUS: "-"

    table: NAME                               -> table
    
    // Podpora funkcí + kombinace operací
    expr: term_expr            -> term_expr
        | expr "+" term_expr   -> addition
        | expr "-" term_expr   -> subtraction
        | expr "*" term_expr   -> multiplication
        | expr "/" term_expr   -> division
        | expr OPERATOR expr   -> condition
        | expr LOGICAL_OP expr -> logical_condition
        | function_call        -> function_call_value

    // Možnost volání více funkcí v jednom výrazu
    term_expr: attr_access  -> var
             | signed_number       -> number
             | ESCAPED_STRING ->string
             | list_expr 
             | raw_expr_block -> raw_eval
             
    list_expr: "[" [list_element ("," list_element)*] "]" ->list

    list_element: value
                | raw_expr_block
                
    raw_expr_block: LBRACE RAW_EXPR RBRACE


    SIZE: /[0-9]+(\.[0-9]+)?(?:[kMG])?/

    size_value: NUMBER UNIT?
    value: SIZE           -> size_value 
         | ESCAPED_STRING -> string
         | NAME           -> var
         | function_call  -> function_call_value
     
    // Oprava function_call, aby podporovalo `filter()` i `map()`
    function_call: NAME "("function_call")" -> function_call
                 | NAME "(" lambda_expr "," function_call ")" -> function_call  // Podpora pro vnořené volání
                 | NAME "(" lambda_expr "," expr ")" -> function_call
                 | NAME "(" [term_expr ("," term_expr)*] ")" -> function_call          
               
    lambda_expr: "lambda" NAME ":" LBRACE RAW_EXPR RBRACE

    RAW_EXPR: /[^}]+/

    LBRACE: "{"
    RBRACE: "}"      
               
    UNIT: /(k|M|G)/  

    OPERATOR: "=" | ">" | "<" | "=="
    LOGICAL_OP: "and" | "or"
    NAME: /(?!or\b|and\b)[a-zA-Z_][a-zA-Z0-9_]*/

    %import common.NUMBER
    %import common.ESCAPED_STRING
    %import common.WS
    %ignore WS
"""