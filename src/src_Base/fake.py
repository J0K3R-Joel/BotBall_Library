import os, sys
from types import ModuleType

sys.path.append("/usr/lib")

from logger import *  # selfmade

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-07-28

try:
    import subprocess
    import ast
    import re
    import inspect
    import importlib.util
    from typing import List, Optional
    from threading import Thread, Event
    from RoboComm import RobotCommunicator  # selfmade
    from fileR import FileR  # selfmade
    from stop_manager import stop_manager  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}',  important=True, in_exception=True)


class FakeR():
    def __init__(self, thread_instance: Event = None, comm_instance: RobotCommunicator = None):
        '''
        Not for the basic user! Class for high or new main priority (RoboComm - RobotCommunicator - Communication).

        Args (work in progress):
            thread_instance (Event, optional): Instance of a pause event
            comm_instance (RobotCommunicator, optional): Instance of the communicator
        '''
        self.file_Manager = FileR()

        try:
            result = subprocess.run(["pwd"], capture_output=True, text=True, check=True)
            current_dir = result.stdout.strip()
            self.working_dir = os.path.dirname(current_dir)
        except Exception as e:
            log(f"Error while fetching for directory: {e}", important=True, in_exception=True)
            self.working_dir = os.getcwd()

        self.target_dir = '/home/kipr/FakeR_created'
        self.inserted_method = ".wait()"
        self.replacer_method = '.set()' 
        self.inserted_line = ''
        self.communicator_instance_name = ''
        self.another_main_function_names = list()
        self.another_main_file_names = list()
        self.thread_instance = thread_instance
        self.comm_instance = comm_instance
        self.comm_wanted = True
        self.fake_main = None
        self.kipr_module_name = ''
        self.setup()


    # ======================== SET INSTANCES ========================

    def set_instance_thread(self, Instance_thread: Event) -> None:
        '''
        Create or overwrite the existence of the thread instance

        Args:
            Instance_thread (Event): the instance of the thread

       Returns:
            None
        '''
        self.thread_instance = Instance_thread

    def set_instance_comm(self, communication_instance: RobotCommunicator) -> None:
        '''
        Create or overwrite the existence of the Communicator instance

        Args:
            communication_instance (RobotCommunicator): the instance of the Communicator

       Returns:
            None
        '''
        self.comm_instance = communication_instance


    # ======================== CHECK INSTANCES ========================

    def check_instance_thread(self) -> bool:
        '''
        Inspect the existence of the thread instance

        Args:
            None

       Returns:
            if there is an instance of the thread sensor in existence
        '''
        if not isinstance(self.thread_instance, Event):
            log('The thread instance is not initialized!', in_exception=True)
            raise TypeError('The thread instance is not initialized!')
        return True

    def check_instance_comm(self) -> bool:
        '''
        Inspect the existence of the communication instance

        Args:
            None

        Returns:
            if there is an instance of the thread sensor in existence (True) or not (False)
        '''
        if not isinstance(self.comm_instance, RobotCommunicator):
            log('The Communicator instance is not initialized!', in_exception=True)
            raise TypeError('The Communicator instance is not initialized!')
        return True


    # ======================== PRIVATE METHODS ========================

    def _late_import(self, original:bool = True) -> None:
        '''
        All the imports that have to be done after initializing of the class

        Args:
            original (bool, optional): If it should focus on the original file (True) or the new "fake" file (False)

        Returns:
            None
       '''
        if original:
            wanted_dir = self.working_dir
        else:
            wanted_dir = self.target_dir + '/src'

        sys.path.append(f"{wanted_dir}")
        try:
            print(wanted_dir + '/main.py', flush=True)
            main_module = self._import_main_from_path(wanted_dir + '/main.py')
            self.fake_main = main_module.main
        except Exception as e:
            log(str(e), important=True, in_exception=True)
            self.fake_main = None

    def _extract_on_new_main_functions(self, code: str) -> list:
        '''
        Extracts function names from all '.on_new_main(...)' calls in the given code.

        Args:
            code (str): The entire source code to be analyzed.

        Returns:
            List[str]: A list of unique function names passed as first argument to `.on_new_main()`.
        '''
        pattern = r'\.on_new_main\(\s*([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(pattern, code)

        seen = set()
        for m in matches:
            seen.add(m)

        return list(seen)

    def _insert_valid_markers_in_file(self, file_path: str) -> None:
        '''
        Inserts important markers inside the code

        Args:
            file_path (str): The file to modify.

        Returns:
            None
        '''
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            lines = code.splitlines()
            tree = ast.parse(code)

            target_functions = ['main'] + getattr(self, 'another_main_function_names', [])

            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name in target_functions:
                    param_names = [arg.arg for arg in node.args.args]
                    if self.inserted_line.replace(self.inserted_method, '') not in param_names:
                        log(f"[SKIP] '{node.name}' has no parameter '{self.inserted_line.replace(self.inserted_method, '')}'. No marker will be added.", important=True)
                        continue

                    first_stmt = node.body[0] if node.body else None
                    if isinstance(first_stmt, ast.Try):
                        inserts = []

                        def collect_statements_in_try(try_node):
                            result = []

                            def visit(n):
                                if isinstance(n, ast.stmt) and hasattr(n, 'lineno'):
                                    end_lineno = getattr(n, 'end_lineno', n.lineno)
                                    result.append(end_lineno)
                                for child in ast.iter_child_nodes(n):
                                    visit(child)

                            for stmt in try_node.body:
                                visit(stmt)
                            return result

                        inserts = collect_statements_in_try(first_stmt)
                        for lineno in sorted(inserts, reverse=True):
                            code_line = lines[lineno - 1]
                            indent = code_line[:len(code_line) - len(code_line.lstrip())]
                            blank_line_count = 0
                            next_line_index = lineno
                            while next_line_index < len(lines) and lines[next_line_index].strip() == '':
                                blank_line_count += 1
                                next_line_index += 1
                            insert_at = lineno + blank_line_count
                            lines.insert(insert_at, indent + 'if stop_manager.check_stopped():')
                            lines.insert(insert_at + 1, indent + '    ' + f'{self.communicator_instance_name}.execute_last_main()')
                            lines.insert(insert_at + 2, indent + self.inserted_line)
                    else:
                        log(f"try/except was not found as the first statement in function '{node.name}'. Writing marker in the first line instead. ADD a try/except block at the very beginning of the function!",
                            important=True)
                        func_start = node.lineno
                        indent = lines[func_start][:len(lines[func_start]) - len(lines[func_start].lstrip())]
                        print(func_start, flush=True)
                        lines.insert(func_start, indent + 'if stop_manager.check_stopped():')
                        lines.insert(func_start + 1, indent + '    ' + f'{self.communicator_instance_name}.execute_last_main()')
                        lines.insert(func_start + 2, indent + self.inserted_line)
                        print(f"'{node.name}': Marker inserted in the first line, since there is no try/except as the first statement", flush=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def _merge_functions_back_into_text(self, entire_text: str) -> str:
        '''
        Reads each function file saved in self.another_main_file_names and replaces the original function definition in entire_text with the (possibly modified) function code from the file.

        Args:
            entire_text (str): the text that should be overwritten

        Returns:
            str: The updated entire_text with functions replaced by their updated versions.
        '''
        # split lines once for easier slicing
        lines = entire_text.splitlines()

        # build a list of (start_idx, end_idx, replacement_text) for each target function
        replacements = []

        try:
            tree = ast.parse(entire_text)
        except Exception as e:
            log(f"Could not parse entire_text for merging functions: {e}", important=True)
            return entire_text

        func_positions = {}
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in self.another_main_function_names:
                start_line = node.lineno - 1  # 0-based index for lines list
                end_line = getattr(node, 'end_lineno', node.lineno) - 1
                func_positions[node.name] = (start_line, end_line)

        for file_path in self.another_main_file_names:
            try:
                base = os.path.basename(file_path)
                if base.startswith("function_") and base.endswith(".py"):
                    func_name = base[len("function_"):-len(".py")]
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        fcode = f.read()
                    ftree = ast.parse(fcode)
                    fname = None
                    for n in ftree.body:
                        if isinstance(n, ast.FunctionDef):
                            fname = n.name
                            break
                    if fname is None:
                        continue
                    func_name = fname

                if func_name not in func_positions:
                    continue

                with open(file_path, 'r', encoding='utf-8') as f:
                    updated_code = f.read().rstrip('\n')

                start_line, end_line = func_positions[func_name]
                replacements.append((start_line, end_line, updated_code))
            except Exception as e:
                log(f"Error while preparing merge for {file_path}: {e}", important=True, in_exception=True)
                continue

        replacements.sort(key=lambda x: x[0], reverse=True)

        for start_line, end_line, updated_code in replacements:
            before = lines[:start_line]
            after = lines[end_line + 1:]
            updated_lines = updated_code.splitlines()
            lines = before + updated_lines + after

        return '\n'.join(lines)

    def _insert_beginning_in_code(self, code_str: str, is_new_main: bool = False) -> str:
        '''
        Insert pre-defined code at the beginning of a code snippet.

        Args:
            code_str (str): The code that has to be changed.
            is_new_main (bool): Whether this is a new main function or the original main.

        Returns:
            str: The changed code with the new pre-defined lines.
        '''
        lines = code_str.splitlines()
        tree = ast.parse(code_str)

        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == 'main' or is_new_main:
                try_block = None
                for child in node.body:
                    if isinstance(child, ast.Try):
                        try_block = child
                        break
                if try_block is None:
                    log(f"No 'try:'-block found in {'new main' if is_new_main else 'main'}().", important=True)
                    return code_str

                if not try_block.body:
                    log("Try-block is empty.", important=True)
                    return code_str

                first_statement_line = try_block.body[0].lineno
                first_line = lines[first_statement_line - 1]
                indent = first_line[:len(first_line) - len(first_line.lstrip())]

                insert_lines = []
                new_main_params = []
                if is_new_main:
                    new_main_params = self._get_param_names_from_text(code_str)

                if is_new_main:
                    insert_lines.append(indent + 'stop_manager.change_stopped(False)')


                if is_new_main and new_main_params and self.inserted_line.replace(self.inserted_method, '') in new_main_params:
                    insert_lines.append(
                        indent + f'{self.inserted_line.replace(self.inserted_method, self.replacer_method)}')

                if not is_new_main and self.kipr_module_name != '':
                    insert_lines.append(indent + f'{self.kipr_module_name}.console_clear()')

                lines = lines[:first_statement_line - 1] + insert_lines + lines[first_statement_line - 1:]
                return '\n'.join(lines)

        return code_str

    def _import_main_from_path(self, path_to_main_py : str) -> ModuleType:
        '''
        Lets you import a main from another python file in another directory

        Args:
            path_to_main_py (str): the directory of the python file that has to be imported

        Returns:
           The module that needs to be imported
        '''
        try:
            module_name = "fake_main"
            spec = importlib.util.spec_from_file_location(module_name, path_to_main_py)
            if spec is None:
                log(f"No spec could be created on {path_to_main_py}.", in_exception=True)
                raise ImportError(f"No spec could be created on {path_to_main_py}.")
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def _extract_params_and_assign(self, method) -> list:
        '''
        Lets you see all the params of a method from another file

        Args:
            method: the function from which you want to see the params

        Returns:
           List of parameter names
        '''
        sig = inspect.signature(method)
        param_names = [name for name in sig.parameters if name != 'self']

        for name in param_names:
            setattr(self, name, None)

        return param_names

    def _get_param_names_from_text(self, code_str: str) -> list:
        '''
        Lets you get all parameter names of a text (preferably one function only)

        Args:
            code_str (str): the function you want to get the params from

        Returns:
            List[str]: The parameters of the functions
        '''
        tree = ast.parse(code_str)
        func_def = tree.body[0]
        params = [arg.arg for arg in func_def.args.args]
        return params

    def _replace_first_valid_event_assignment(self, code: str) -> str:
        '''
        Replaces a pre-defined line with another pre-defined line

        Args:
            code (str): the code that has to be looked at

        Returns:
           the new code on which the replacement took place
        '''
        pattern = r'^(\s*)(\w*pause\w*|\w*event\w*)\s*=\s*threading\.Event\(\)(?:\.set\(\))?'
        matches = list(re.finditer(pattern, code, flags=re.MULTILINE))

        if matches:
            first_match = matches[0]
            indent = first_match.group(1)
            variable_name = first_match.group(2)

            start, end = first_match.span()
            new_code = code[:start] + f"{indent}{variable_name} = None" + code[end:]
            return new_code
        else:
            log("[INFO] No threading.Event() assignment found with a variable name containing 'pause' or 'event'.", important=True)
            return code

    def _save_functions_to_files(self, code: str, target_dir: str) -> None:
        '''
        Saves each function from self.another_main_function_names as a separate file.

        Args:
            code (str): The entire source code to extract functions from.
            target_dir (str): Directory where the function files will be saved.

        Returns:
            None
        '''
        tree = ast.parse(code)
        functions_found = {}
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in self.another_main_function_names:
                start_line = node.lineno - 1  # ast lines are 1-based
                end_line = getattr(node, 'end_lineno', node.lineno)  # 'end_lineno' available in Python 3.8+
                function_lines = code.splitlines()[start_line:end_line]
                functions_found[node.name] = '\n'.join(function_lines)

        os.makedirs(target_dir, exist_ok=True)

        # Save each function to a separate file
        for func_name, func_code in functions_found.items():
            file_path = os.path.join(target_dir, f"function_{func_name}.py")
            self.another_main_file_names.append(file_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(func_code)

    def _resolve_import_alias(self, module_name: str, class_name: str, code: str) -> List[Optional[str]]:
        '''
        Returns the alias of an import or the exact import path

        Return:
            [0, alias]                      -> with 'as'
            [1, 'modulename.classname']     -> Class without alias
            [2, 'modulename']               -> Module without alias
            [3, None]                       -> Module nor class found
        '''
        if class_name:
            pattern_with_as = rf'from\s+{re.escape(module_name)}\s+import\s+{re.escape(class_name)}\s+as\s+(\w+)'
            match = re.search(pattern_with_as, code)
            if match:
                return [0, match.group(1)]

            pattern_without_as = rf'from\s+{re.escape(module_name)}\s+import\s+{re.escape(class_name)}(\s|$)'
            if re.search(pattern_without_as, code):
                return [1, f"{module_name}.{class_name}"]

        else:
            pattern_with_as = rf'import\s+{re.escape(module_name)}\s+as\s+(\w+)'
            match = re.search(pattern_with_as, code)
            if match:
                return [0, match.group(1)]

            pattern_without_as = rf'import\s+{re.escape(module_name)}(\s|$)'
            if re.search(pattern_without_as, code):
                return [2, module_name]

        log(f"[Warning] The module '{module_name}' and class '{class_name}' could not be found in the provided code.", important=True)
        return [3, None]


    # ======================== PUBLIC METHODS ========================

    def replace_exact_word(self, text: str, target: str, replacement: str) -> str:
        '''
        replacing every (all) instance of a string occuring in a text with another instance

        Args:
            text (str): the entire text that has to be looked at
            target (str): the string that has to be looked after and that has to be replaced
            replacement (str): the string that should replace the target string.

        Returns:
           The entire text with the replaced strings
        '''
        pattern = r'(?<!\w)' + re.escape(target) + r'(?!\w)'
        return re.sub(pattern, replacement, text)

    def setup(self):
        '''
        Setting up the main function in another file and modifying the file accordingly (for communication).

        Steps:
            1. Copy source to target folder.
            2. Extract new main functions and save as separate files.
            3. Insert valid markers into all new main functions.
            4. Merge updated new main functions back into entire text.
            5. Insert beginning code in main and new main functions as required.
            6. Write final main.py to target folder.
        '''
        try:
            if self.working_dir != self.target_dir:
                self.working_dir = os.path.join(self.working_dir, 'src')
                print('setting up fake main...', flush=True)

                # Prepare paths
                target_src_dir = os.path.join(self.target_dir, 'src')
                main_text_filepath = os.path.join(target_src_dir, 'main_only_text.py')
                os.makedirs(target_src_dir, exist_ok=True)

                # Copy source to target folder
                subprocess.run(['cp', '-R', self.working_dir, self.target_dir])
                subprocess.run(['sudo', 'chmod', '-R', '777', self.target_dir])

                # Initialize main_only_text.py
                open(main_text_filepath, 'a').close()

                # Read old main.py
                main_py_path = os.path.join(self.working_dir, 'main.py')
                old_entire_text = self.file_Manager.reader(main_py_path)

                # Late import of old main
                self._late_import(True)
                params = self._extract_params_and_assign(self.fake_main)

                # Determine communication usage
                if len(params) == 0:
                    self.comm_wanted = False
                    log('No parameters in main() found, starting the main not in a thread...')
                elif len(params) == 1:
                    self.comm_wanted = False
                    log('Only one parameter found in main(), if you use communication you will need 2! Starting the main not in a thread...')
                elif len(params) >= 2:
                    self.comm_wanted = True
                    self.inserted_line = params[0] + self.inserted_method
                    self.communicator_instance_name = params[1]

                # Replace pause_event assignments
                old_entire_text = self._replace_first_valid_event_assignment(old_entire_text)

                # Extract additional new main functions
                self.another_main_function_names = self._extract_on_new_main_functions(old_entire_text)

                # Save new main functions to separate files
                self._save_functions_to_files(old_entire_text, target_src_dir)

                # Insert valid markers in all new main function files first
                for file_path in self.another_main_file_names:
                    self._insert_valid_markers_in_file(file_path)
                    code = self.file_Manager.reader(file_path)
                    edited_code = self._insert_beginning_in_code(code_str=code, is_new_main=True)
                    self.file_Manager.writer(file_path, "w", edited_code)

                # Merge updated new main functions back into entire text
                entire_text = self._merge_functions_back_into_text(old_entire_text)

                # Now handle main() function
                tree = ast.parse(entire_text)
                main_node = None
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef) and node.name == 'main':
                        main_node = node
                        break

                if not main_node:
                    log('main() function not found!', important=True)
                    raise Exception('main() function not found!')

                main_start = main_node.lineno - 1
                main_end = getattr(main_node, 'end_lineno', main_node.lineno) - 1
                main_lines = entire_text.splitlines()[main_start:main_end + 1]
                main_code = "\n".join(main_lines)

                # Write temp main file to insert markers in main
                temp_main_path = os.path.join(target_src_dir, 'main_temp.py')
                with open(temp_main_path, 'w', encoding='utf-8') as f:
                    f.write(main_code)

                # Insert markers in temp main file
                self._insert_valid_markers_in_file(temp_main_path)

                # Read back main with markers
                with open(temp_main_path, 'r', encoding='utf-8') as f:
                    main_code_with_markers = f.read()

                # Insert beginning code in main
                main_code_with_markers = self._insert_beginning_in_code(main_code_with_markers)

                # Merge modified main back into entire text
                lines = entire_text.splitlines()
                new_entire_text = lines[:main_start] + main_code_with_markers.splitlines() + lines[main_end + 1:]
                final_entire_text = "\n".join(new_entire_text)

                # Write final main.py
                target_main_path = os.path.join(target_src_dir, 'main.py')
                self.file_Manager.writer(target_main_path, 'w', final_entire_text)

                log(f"Setup completed. Final main.py written to {target_main_path}", important=True)

            else:
                log('Normal main will be executed...')

        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def get_current_path(self) -> str:  # not in use
        '''
        Get the path of the current executing file

        Args:
            None

        Returns:
           The path of the current file that is being executed
        '''
        try:
            result = subprocess.run(['pwd'], capture_output=True, text=True)
            path = result.stdout.strip()
            path_rev = path[::-1]
            path_rev_index = path_rev.find(
                '/') + 1  # +1 since the / counts as a character as well and it should be removed
            actual_path = path[0:len(path) - path_rev_index]
            return actual_path
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def start(self):
        '''
        executing the "fake" main in the other directory

        Args:
            None

        Returns:
           None
        '''
        try:
            self.check_instance_thread()
            self.check_instance_comm()
            self._late_import(False)
            if self.fake_main is None:
                log("main could not be found", important=True)
                return
            if self.comm_wanted:
                t = Thread(target=self.fake_main, args=(self.thread_instance, self.comm_instance,))
                t.start()
                t.join()
            else:
                from main import main
                main()
        except Exception as e:
            log(str(e), important=True, in_exception=True)

