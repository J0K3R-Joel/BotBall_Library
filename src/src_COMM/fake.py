import os, sys
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
except Exception as e:
    log(f'Import Exception: {str(e)}',  important=True, in_exception=True)


class FakeR():
    def __init__(self, thread_instance: Event = None, comm_instance: RobotCommunicator = None):
        self.file_Manager = FileR()
        self.working_dir = '/home/kipr/Documents/KISS/Base/actual'
        self.target_dir = '/home/kipr/Joel'
        self.inserted_method = ".wait()"
        self.inserted_line = ''
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
        Create or overwrite the existance of the thread instance

        Args:
            Instance_thread (Thread): the instance of the thread

       Returns:
            None
        '''
        self.thread_instance = Instance_thread

    def set_instance_comm(self, communication_instance: RobotCommunicator) -> None:
        '''
        Create or overwrite the existance of the Communicator instance

        Args:
            Instance_thread (Thread): the instance of the Communicator

       Returns:
            None
        '''
        self.comm_instance = communication_instance


    # ======================== CHECK INSTANCES ========================

    def check_instance_thread(self) -> bool:
        '''
        Inspect the existance of the thread instance

        Args:
            None

       Returns:
            if there is an instance of the thread sensor in existance
        '''
        if not isinstance(self.thread_instance, Event):
            log('The thread instance is not initialized!', in_exception=True)
            raise Exception('The thread instance is not initialized!')
        return True

    def check_instance_comm(self) -> bool:
        '''
        Inspect the existance of the communication instance

        Args:
            None

        Returns:
            if there is an instance of the thread sensor in existance (True) or not (False)
        '''
        if not isinstance(self.comm_instance, RobotCommunicator):
            log('The Communicator instance is not initialized!', in_exception=True)
            raise Exception('The Communicator instance is not initialized!')
        return True


    # ======================== PRIVATE METHODS ========================

    def __late_import(self):
        '''
        All the imports that have to be done after initializing of the class

        Args:
            None

        Returns:
            None
       '''
        sys.path.append(f"{self.target_dir}/src")
        try:
            main_module = self.__import_main_from_path(self.target_dir + '/src/main.py')
            self.fake_main = main_module.main
        except Exception as e:
            log(str(e), important=True, in_exception=True)
            self.fake_main = None

    def __extract_on_new_main_functions(self, code: str) -> list:
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

    def __insert_valid_markers_in_file(self, file_path: str) -> None:
        '''
        Inserts pause-event markers into 'main()' and all functions registered via 'on_new_main',
        but only if the function has a parameter named "p_event".

        Args:
            file_path (str): The file to modify.

        Returns:
            None. Overwrites the file.
        '''
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        lines = code.splitlines()
        tree = ast.parse(code)

        target_functions = ['main'] + getattr(self, 'another_main_function_names', [])

        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in target_functions:
                param_names = [arg.arg for arg in node.args.args]
                if "p_event" not in param_names:
                    log(f"[SKIP] '{node.name}' has no parameter 'p_event'. No marker will be added.", important=True)
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
                        lines.insert(insert_at, indent + self.inserted_line)

                else:
                    log(f"try/except was not found as the first statement in function '{node.name}'. Writing marker in the first line instead. ADD a try/except block at the very beginning of the function!",
                        important=True)
                    func_start = node.lineno
                    indent = lines[func_start][:len(lines[func_start]) - len(lines[func_start].lstrip())]
                    lines.insert(func_start, indent + self.inserted_line)
                    print(f"'{node.name}': Marker inserted in the first line, since there is no try/except as the first statement", flush=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def __merge_functions_back_into_text(self, entire_text: str) -> str:
        '''
        Reads each function file saved in self.another_main_file_names and replaces the original
        function definition in entire_text with the (possibly modified) function code from the file.

        Returns:
            The updated entire_text with functions replaced by their updated versions.
        '''
        import ast
        # split lines once for easier slicing
        lines = entire_text.splitlines()

        # build a list of (start_idx, end_idx, replacement_text) for each target function
        replacements = []

        try:
            tree = ast.parse(entire_text)
        except Exception as e:
            log(f"Could not parse entire_text for merging functions: {e}", important=True)
            return entire_text

        # map function name -> (start_line, end_line)
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

    def __insert_beginning_in_code(self, code_str: str) -> str:
        '''
        Insert pre-defined code in the beginning of a code snippet in the beginning in the main

        Args:
            code_str (str): the code that has to be changed

        Returns:
           The changed code with the new pre-defined lines
        '''
        lines = code_str.splitlines()
        tree = ast.parse(code_str)

        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == 'main':
                for child in node.body:
                    if isinstance(child, ast.Try):
                        try_block = child
                        break
                else:
                    log("No 'try:'-block found in main().", important=True)
                    return code_str
                break
        else:
            log("No main()-function found.", important=True)
            return code_str

        if not try_block.body:
            log("Try-block is empty.", important=True)
            return code_str

        first_statement_line = try_block.body[0].lineno
        first_line = lines[first_statement_line - 1]
        indent = first_line[:len(first_line) - len(first_line.lstrip())]

        if self.kipr_module_name != '':
            insert_lines = [
                indent + f'{self.kipr_module_name}.console_clear()'
            ]
        else:
            insert_lines = [
                indent + ''
            ]

        lines = lines[:first_statement_line - 1] + insert_lines + lines[first_statement_line - 1:]
        return '\n'.join(lines)

    def __import_main_from_path(self, path_to_main_py : str) -> None:
        '''
        Let's you import a main from another python file in another directory

        Args:
            path_to_main_py (str): the directory of the python file that has to be imported

        Returns:
           The module that needs to be imported
        '''
        module_name = "fake_main"
        spec = importlib.util.spec_from_file_location(module_name, path_to_main_py)
        if spec is None:
            log(f"No spec could be created on {path_to_main_py}.", in_exception=True)
            raise ImportError(f"No spec could be created on {path_to_main_py}.")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def __extract_params_and_assign(self, method) -> list:
        '''
        Let's you see all the params of a method from another file

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

    def __replace_first_valid_event_assignment(self, code: str) -> str:
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

    def __save_functions_to_files(self, code: str, target_dir: str) -> None:
        '''
        Saves each function from self.another_main_function_names as a separate file.

        Args:
            code (str): The entire source code to extract functions from.
            target_dir (str): Directory where the function files will be saved.

        Returns:
            None
        '''

        import ast
        import os

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

    def __resolve_import_alias(self, module_name: str, class_name: str, code: str) -> List[Optional[str]]:
        '''
        Returns the alias of an import or the exact import path

        Return:
            [0, alias]                      -> with 'as'
            [1, 'modulename.classname']     -> Class without alias
            [2, 'modulename']               -> Module without alias
            [3, None]                       -> Module nor class found
        '''
        if class_name:
            # from modulename import classname as alias
            pattern_with_as = rf'from\s+{re.escape(module_name)}\s+import\s+{re.escape(class_name)}\s+as\s+(\w+)'
            match = re.search(pattern_with_as, code)
            if match:
                return [0, match.group(1)]

            # from modulename import classname
            pattern_without_as = rf'from\s+{re.escape(module_name)}\s+import\s+{re.escape(class_name)}(\s|$)'
            if re.search(pattern_without_as, code):
                return [1, f"{module_name}.{class_name}"]

        else:
            # import modulename as alias
            pattern_with_as = rf'import\s+{re.escape(module_name)}\s+as\s+(\w+)'
            match = re.search(pattern_with_as, code)
            if match:
                return [0, match.group(1)]

            # import modulename
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
        setting up the main in another file and change the file accordingly (to the commnunication)

        Args:
            None

        Returns:
           None
        '''
        try:
            if self.working_dir != self.target_dir:
                self.working_dir = self.working_dir + '/src/'
                print('setting up fake main...', flush=True)

                main_text_filename = 'main_only_text.py'
                main_text_filepath = os.path.join(self.target_dir, 'src', main_text_filename)

                # Setting up the target path
                subprocess.run(['mkdir', '-p', os.path.join(self.target_dir, 'src')])
                subprocess.run(['cp', '-R', self.working_dir, os.path.join(self.target_dir)])
                subprocess.run(['sudo', 'chmod', '-R', '777', os.path.join(self.target_dir)])

                # Setting up main_only_text.py
                subprocess.run(['touch', main_text_filepath])

                # read old main.py
                main_py_path = os.path.join(self.working_dir, 'main.py')
                old_entire_text = self.file_Manager.reader(main_py_path)

                # import the old main on the new directory into this class
                self.__late_import()
                params = self.__extract_params_and_assign(self.fake_main)
                if len(params) == 0:
                    self.comm_wanted = False
                    log('No parameters in main() found, starting the main not in a thread...')
                    return
                elif len(params) == 1:
                    self.comm_wanted = False
                    log('Only one parameter found in main(), if you use communication you wil need 2! Starting the main not in a thread...')
                    return
                elif len(params) == 2:
                    self.comm_wanted = True
                    self.inserted_line = params[0] + self.inserted_method

                # replace every pause_event = threading.Event() with or without .set()
                pattern = r'(^\s*pause_event\s*=\s*)threading\.Event\(\)(\.set\(\))?'
                replacement = r'\1None'

                entire_text = self.__replace_first_valid_event_assignment(old_entire_text)
                self.another_main_function_names = self.__extract_on_new_main_functions(entire_text)
                self.__save_functions_to_files(entire_text, os.path.join(self.target_dir, 'src'))

                for file in self.another_main_file_names:
                    self.__insert_valid_markers_in_file(file)

                entire_text = self.__merge_functions_back_into_text(entire_text)

                # find positions of main() and end_main()
                main_start = entire_text.find('def main(')
                if main_start == -1:
                    log('main() function not found!', in_exception=True)
                    raise Exception('main() function not found!')

                main_end_relative = entire_text[main_start:].find('end_main(')
                if main_end_relative == -1:
                    log('"end_main()" function not found in main!', in_exception=True)
                    raise Exception('"end_main()" function not found in main!')

                main_end_newLine = entire_text[main_start + main_end_relative:].find('\n')

                main_end = main_start + main_end_relative + main_end_newLine


                # get the name of the kipr module
                kpr = self.__resolve_import_alias("_kipr", "", entire_text[0:main_start])
                if kpr[0] != 3:
                    self.kipr_module_name = kpr[1]

                # extract and save main() in the new file
                changed_main = entire_text[main_start:main_end]
                self.file_Manager.writer(main_text_filepath, 'w', changed_main)

                # Insert marker
                self.__insert_valid_markers_in_file(main_text_filepath)

                # read main() from the new file
                old_main_from_file = self.file_Manager.reader(main_text_filepath)

                # addoing the lines for a clean beginning
                main_from_file = self.__insert_beginning_in_code(old_main_from_file)

                # build new text: replace old main with new one
                new_entire_text = entire_text[:main_start] + main_from_file + entire_text[main_end:]

                final_entire_text = self.replace_exact_word(new_entire_text, 'comm', 'AkommunikatorA')  # this is only to avoid further problems

                # write in target main.py
                target_main_path = os.path.join(self.target_dir, 'src', 'main.py')
                self.file_Manager.writer(target_main_path, 'w', final_entire_text)

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
        executing the main in the other directory

        Args:
            None

        Returns:
           None
        '''
        try:
            self.check_instance_thread()
            self.check_instance_comm()
            self.__late_import()
            if self.fake_main is None:
                log("main could not be found", important=True)
                return
            if self.comm_wanted:
                t = Thread(target=self.fake_main, args=(self.thread_instance, self.comm_instance,))
                t.start()
            else:
                from main import main
                main()
        except Exception as e:
            log(str(e), important=True, in_exception=True)

