#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade
import threading

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-07-28

class FileR:
	def __init__(self):
		print()
		self._writer_lock = threading.Lock()

	def reader(self, file_name: str) -> str:
		'''
		read the content of a file

		Args:
			file_name (str): the file (and/or path) to the desired file

		Returns:
			content of the file
		'''
		try:
			with open(file_name, 'r') as f:
				return f.read()
		except Exception as e:
			log(str(e), important=True, in_exception=True)

	def writer(self, file_name: str, mode: str, msg: str) -> None:
		'''
        writes / appends / ... content to a file.

        Args:
            file_name (str): the file (and/or path) to the desired file
            mode (str): the mode in which the file should be opened. See (for exmaple) this website for more information: https://www.freecodecamp.org/news/file-handling-in-python
            msg (str): the message, that needs to get into the file

       Returns:
            None
        '''
		try:
			with self._writer_lock:
				with open(file_name, mode) as f:
					f.write(str(msg))
		except Exception as e:
			log(str(e), important=True, in_exception=True)

	def cleaner(self, file_name: str) -> None:
		'''
        removes all content in a file

        Args:
            file_name (str): the file (and/or path) to the desired file

       Returns:
            None
        '''
		try:
			open(file_name, 'w').close()
		except Exception as e:
			log(str(e), important=True, in_exception=True)

