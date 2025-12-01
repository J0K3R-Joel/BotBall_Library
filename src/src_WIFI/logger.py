#!/usr/bin/python3
import os, sys

sys.path.append("/usr/lib")

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-09-05

from datetime import datetime
import inspect
import subprocess

LOG_FOLDER = "/usr/lib/logger_log"
LOG_FILE = os.path.join(LOG_FOLDER, "log_file.txt")
os.makedirs(LOG_FOLDER, exist_ok=True)
subprocess.run(["sudo", "chmod", "-R", "777", LOG_FOLDER], check=True)


def log(message: str, with_print: bool = True, important: bool = False, in_exception: bool = False) -> None:
    '''
    write the message in the log file and print it to the screen

    Args:
        message (str): The message that should be written into the file
        with_print (bool, optional): If True (default), it prints out the message as well, otherwise it just writes into the log file
        important (bool, optional): If True, it will be marked with some "=", otherwise (False, default) just the message given to the function
        in_exception (bool, optional): If True, the additional label will tell you that an exception was thrown and also sets important automatically to True, otherwise (False, default) it tells you that it's only an information

    Returns:
        None
    '''
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    frame = inspect.currentframe()
    caller_frame = frame.f_back
    func_name = caller_frame.f_code.co_name
    class_name = None

    if in_exception:
        important = True
        label = "EXCEPTION"
        caller_frame = inspect.stack()[1].frame
        location = str(caller_frame)
        location = '<' + location[location.find(',') + 2:]
    else:
        label = "INFO"
        if "self" in caller_frame.f_locals:
            class_name = caller_frame.f_locals["self"].__class__.__name__

        if class_name:
            location = f"{class_name}.{func_name}"
        else:
            filename = caller_frame.f_code.co_filename
            if in_exception:
                if func_name == "<module>":
                    location = filename
                else:
                    location = f"{filename}.{func_name}"
            else:
                if func_name == "<module>":
                    location = os.path.basename(filename)
                else:
                    location = func_name

    message = str(message)
    if important:
        message = '=' * 10 + message + '=' * 10

    log_entry = f"{now} [{location}] - [{label}] {message}\n"

    if in_exception:
        print_text = (
            "=================================\n"
            f"[{location}] - [{label}] {message}\n"
            "================================="
        )
    else:
        print_text = f"[{location}] - [{label}] {message}"

    with open(LOG_FILE, 'a') as fwriter:
        fwriter.write(log_entry)

    if with_print:
        print(print_text, flush=True)


def __log_handler(max_entries: int = 10000, trim_size: int = 500) -> None:
    '''
    handles the file, so there won't be too many entries, otherwise deletes the oldest entries

    Args:
        max_entries (int, optional): The maximum number of newlines
        trim_size (int, optional): The amount of newlines getting deleted

    Returns:
        None
    '''
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()

        if len(lines) > max_entries:
            new_lines = lines[trim_size:]
            with open(LOG_FILE, 'w') as f:
                f.writelines(new_lines)
    except FileNotFoundError:
        pass


def backup_log() -> None:
    '''
    backups the log file

    Args:
        None

    Returns:
        None
    '''
    if not os.path.exists(LOG_FILE):
        return ""

    backups = [f for f in os.listdir(LOG_FOLDER) if f.startswith("backup_log_file_")]
    numbers = []
    for b in backups:
        try:
            num = int(b.replace("backup_log_file_", "").replace(".txt", ""))
            numbers.append(num)
        except ValueError:
            pass

    next_num = max(numbers) + 1 if numbers else 1
    backup_file = os.path.join(LOG_FOLDER, f"backup_log_file_{next_num}.txt")

    with open(LOG_FILE, 'r') as fsrc, open(backup_file, 'w') as fdst:
        fdst.writelines(fsrc.readlines())

    log("Backup successful!", important=True)


