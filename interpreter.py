from lark import Lark
import sqlite3
from database.default_projects import get_projects
from filtering_functions.projects import filter_projects
from filtering_functions.files import find_files

from interpreter_parts.interpreter_utils import InterpreterUtils
from grammar import grammar
from interpreter_parts.io_commands import IOCommands
from filtering_functions.find_command import FindCommand
from interpreter_parts.environment_commands import EnvironmentCommands
from interpreter_parts.execution_core import ExecutionCore
from interpreter_parts.exec_functions import ExecFunctions

class Interpreter(InterpreterUtils, IOCommands, FindCommand, EnvironmentCommands, ExecutionCore,ExecFunctions):
    def __init__(self, sftp_wrapper, db_name="bionano.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.variables = {}
        self.functions = {}
        self.custom_types = {}
        self.sftp_wrapper = sftp_wrapper
        self.current_iteration= 0
        
        self.variables["projects"] = get_projects()
        
        self.functions.update({
            "sum": sum,
            "min": min,
            "max": max,
            "len": len,
            "count": lambda x: len(x),
            "avg": lambda lst: sum(lst) / len(lst) if lst else 0,
            "filter_projects": lambda x, conds=None: filter_projects(x, conds, self.variables),
            "find_files": lambda x, conds=None: find_files(x, conds, self.variables)
        })
        self.load_functions_cmd(None)
        self.load_types_cmd(None)
 
parser = Lark(grammar, parser="lalr")