#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade
import threading
import builtins
import pathlib
# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-07-28

class FileR:
	def __init__(self, base_directory: str = '/home/kipr/BotBall-data/', allowed_path_seperator: str = '/', forbidden_path_seperator: str = '\\'):
		"""
        Class for threadsafe file management (reading, writing, cleaning)

        Args:
            base_directory (str, optional): The path at which this instance should reference all the time (default: '/home/kipr/BotBall-data/')
            allowed_path_seperator (str, optional): The string to separate paths (default: '/')
            forbidden_path_seperator (str, optional): The string that needs to be replaced if found in a path (default: '\\')
        """
		self.allowed_path_seperator = allowed_path_seperator
		self.forbidden_path_seperator = forbidden_path_seperator
		self.base_directory = base_directory if base_directory.endswith(self.allowed_path_seperator) else ''.join([base_directory, self.allowed_path_seperator])
		self._writer_lock = threading.Lock()


	# ======================== PRIVATE METHODS =======================
	def _separate_file_from_path(self, path: str) -> tuple[str, str, bool]:
		"""
		Separate a string into the included path and the potential file (if it is included in the path)

		Args:
			path (str): The path you want to extract from

		Returns:
			tuple[
				str: The entire path excluding the file (if there is one)
				str: The file name with suffix (if there is a file, else just -> '')
				bool: If a filename got detected (True) or not (False)
			]: Extracted file from path
		"""
		path = path.replace(self.forbidden_path_seperator, self.allowed_path_seperator)
		index_last_end = path[::-1].find(self.allowed_path_seperator)
		index_last_end = index_last_end if index_last_end != -1 else len(path)

		pure_path = path[:len(path) - index_last_end]
		potential_file_name = path[len(path) - index_last_end:]
		p = pathlib.Path(potential_file_name)

		# Not necessary since the value is by default on False
		# if str(p).endswith(('/', '\\')):
		#     contains_file = False

		contains_file = True if p.suffix or '.' in p.name else False

		if not contains_file:
			pure_path = os.path.join(pure_path + potential_file_name)
			potential_file_name = ''

		return pure_path, potential_file_name, contains_file


	def _build_file_path(self, file_name: str) -> str:
		"""
		Create the entire file path

		Args:
			file_name (str): Either the entire path (including file name) leading to the file or just the file name

		Returns:
			str: Complete path to the desired file
		"""
		file_name = file_name.replace(self.forbidden_path_seperator, self.allowed_path_seperator)

		if file_name.find(self.base_directory) != 0:
			if self.base_directory.endswith(self.allowed_path_seperator):
				if file_name.find(self.allowed_path_seperator) == 0:
					file_name = file_name[1:]
			file_name = os.path.join(self.base_directory + file_name)

		return file_name


	# ======================== GETTER =======================
	def get_base_directory(self) -> str:
		"""
		Receive the current base path

		Args:
			None

		Returns:
			str: base path
		"""
		return self.base_directory

	# ======================== SETTER =======================
	def set_base_directory(self, path: str) -> None:
		"""
		Set a new base path which this instance should reference all the time

		Args:
			path (str): The base path

		Returns:
			None
		"""
		self.base_directory = path if path.endswith(self.allowed_path_seperator) else ''.join([path, self.allowed_path_seperator])


	# =================== PUBLIC METHODS ==================
	def creator(self, path: str, text: str = '') -> None:
		"""
		Create a file or directory

		Args:
			path (str): The file or directory name which should get created
			text (str, optional):

		Returns:
			None
		"""
		file_path = self._build_file_path(path)

		if os.path.exists(file_path):
			log(f'Path {file_path} already exists, nothing to create.', important=True)
			return

		path, potential_file, contains_file = self._separate_file_from_path(file_path)
		if not os.path.exists(path):
			os.makedirs(path, exist_ok=True)

		if contains_file:
			self.writer(file_path, 'w', text)

		log(f'Path {file_path} created!')


	def reader(self, file_name: str, type_name: str = 'str'):
		"""
        read the content of a file

        Args:
            file_name (str): the file (and/or path) to the desired file
            type_name (str, optional): the type of value which you want to get returned

        Returns:
            content of the file
        """
		file_path = self._build_file_path(file_name)
		try:
			with open(file_path, 'r') as f:
				text = f.read()
				return getattr(builtins, type_name)(text)
		except Exception as e:
			log(file_path + ': ' + str(e), important=True, in_exception=True)

	def writer(self, file_name: str, mode: str, msg: str) -> None:
		"""
        Writes / appends / ... content to a file.

        Args:
            file_name (str): the file (and/or path) to the desired file
            mode (str): the mode in which the file should be opened.See (for example) this website for more information: https://www.freecodecamp.org/news/file-handling-in-python
            msg (str): the message that needs to get into the file

        See Also:
        	https://www.freecodecamp.org/news/file-handling-in-python

        Returns:
            None
    	"""
		try:
			file_path = self._build_file_path(file_name)
			with self._writer_lock:
				with open(file_path, mode) as f:
					f.write(str(msg))
		except Exception as e:
			log(str(e), important=True, in_exception=True)

	def cleaner(self, file_name: str) -> None:
		"""
        removes all content in a file

        Args:
            file_name (str): the file (and/or path) to the desired file

           Returns:
            None
        """
		try:
			file_path = self._build_file_path(file_name)
			open(file_path, 'w').close()
		except Exception as e:
			log(str(e), important=True, in_exception=True)

	def remover(self, file_name: str) -> None:
		"""
		Deletes a file

		Args:
			file_name (str): The file which should get deleted

		Returns:
			None
		"""
		file_path = self._build_file_path(file_name)
		if not os.path.exists(file_path):
			log(f'File {file_path} does not exist, nothing to remove', important=True)
			return

		os.remove(file_path)
		log(f'Successfully removed file: {file_path}')

	def transfer(self, from_file: str, to_file: str, create_to_transfer_file: bool = False) -> None:
		"""
		Write the text from one file to another

		Args:
			from_file (str): The file you want to read and copy the text from
			to_file (str): The file you want to insert the copied text
			create_to_transfer_file (bool, optional): If the file - that receives the copied text - does not exist should be created (True) or in this case just return with a message(False)

		Returns:
			None
		"""
		file_path_from = self._build_file_path(from_file)
		file_path_to = self._build_file_path(to_file)
		if not os.path.exists(file_path_from):
			log(f'File {file_path_from} does not exist', important=True)
			return

		if not os.path.exists(file_path_to) and not create_to_transfer_file:
			log(f'File {file_path_to} does not exist', important=True)
			return

		text = self.reader(file_path_from)
		self.writer(file_path_to, 'w', text)
		log(f'Successfully transferred text from {file_path_from} -> {file_path_to}')