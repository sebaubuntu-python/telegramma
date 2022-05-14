#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""telegramma database implementation."""

import json
from pathlib import Path
from threading import Lock

class _DatabaseFile:
	"""HomeBot database file class."""
	__file_name = "data.json"

	__file_path = Path(__file_name)
	__file_lock = Lock()

	@classmethod
	def load(cls):
		with cls.__file_lock:
			if cls.__file_path.is_file():
				return json.loads(cls.__file_path.read_bytes())

			return {}

	@classmethod
	def dump(cls, d: dict):
		with cls.__file_lock:
			cls.__file_path.write_text(json.dumps(d, sort_keys=True))

class Database:
	"""HomeBot database class.

	This class is used to save persistent data.
	"""

	ALLOWED_DATA_TYPES = [
		bool,
		dict,
		float,
		int,
		list,
		# TODO: With 3.10 move to types.NoneType
		type(None),
		str,
	]
	"""List of allowed values data types."""

	__dict = _DatabaseFile.load()
	__dict_lock = Lock()

	@classmethod
	def __has(cls, k: str):
		"""Unprotected cls.has implementation."""
		if type(k) is not str:
			raise TypeError("Key isn't a string")

		if not '.' in k:
			value = k in cls.__dict
		else:
			value = cls.__dict
			for subkey in k.split('.'):
				if subkey not in value:
					value = False
					break

				value = value[subkey]

		return value

	@classmethod
	def has(cls, k: str):
		"""Check if a key is inside the database."""
		with cls.__dict_lock:
			return cls.__has(k)

	@classmethod
	def __get(cls, k: str, default=None):
		"""Unprotected cls.get implementation."""
		if type(k) is not str:
			raise TypeError("Key isn't a string")

		if not '.' in k:
			if not k in cls.__dict:
				return default
			value = cls.__dict[k]
		else:
			value = cls.__dict
			for subkey in k.split('.'):
				if subkey not in value:
					return default
				value = value[subkey]

		return value

	@classmethod
	def get(cls, k: str, default=None):
		"""Get a value from the database."""
		with cls.__dict_lock:
			return cls.__get(k, default)

	@classmethod
	def __set(cls, k: str, v):
		"""Unprotected cls.set implementation."""
		if type(k) is not str:
			raise TypeError("Key isn't a string")

		if type(v) not in cls.ALLOWED_DATA_TYPES:
			raise TypeError("Value data type not allowed")

		if not '.' in k:
			if cls.__has(k) and isinstance(cls.__get(k), dict):
				cls.__get(k).update(v)
			else:
				cls.__dict[k] = v
		else:
			d = v
			current_subkey = ""
			for subkey in k.split('.')[::-1]:
				d = {subkey: d}
				current_subkey = f".{subkey}" if not current_subkey else f".{subkey}{current_subkey}"
				subkey_full = k.removesuffix(current_subkey)
				if cls.__has(subkey_full) and isinstance(cls.__get(subkey_full), dict):
					cls.__get(subkey_full).update(d)
					d = cls.__get(subkey_full)

			cls.__dict.update(d)

		cls.__dump()

	@classmethod
	def set(cls, k: str, v):
		"""Save a value to the database."""
		with cls.__dict_lock:
			return cls.__set(k, v)

	@classmethod
	def __dump(cls):
		"""Dump the database to file."""
		_DatabaseFile.dump(cls.__dict)
