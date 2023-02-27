#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""telegramma database implementation."""

from datetime import datetime, timedelta
import json
from pathlib import Path
from sebaubuntu_libs.liblogging import LOGE, LOGI
from sebaubuntu_libs.libstring import removesuffix
from threading import Lock
from typing import Dict, Optional

from telegramma.api import get_config_namespace

CONFIG_NAMESPACE = get_config_namespace("bot")
DATABASE_SYNC_DELTA: timedelta = CONFIG_NAMESPACE.get("database_sync_delta", timedelta(minutes=5))

class _DatabaseFile:
	"""telegramma database file class."""
	__file_path = Path("data.json")
	__backup_file_path = Path("data.json.bak")
	__last_sync: Optional[datetime] = None
	__lock = Lock()

	@classmethod
	def load(cls) -> Dict[str, Dict]:
		with cls.__lock:
			if cls.__file_path.is_file():
				try:
					return json.loads(cls.__file_path.read_bytes())
				except Exception as e:
					LOGE(f"Error loading database file: {e}")
			if cls.__backup_file_path.is_file():
				try:
					return json.loads(cls.__backup_file_path.read_bytes())
				except Exception as e:
					LOGE(f"Error loading database backup file: {e}")

			LOGI("Creating new database file")
			return {}

	@classmethod
	def sync(cls, d: dict, force: bool = False):
		with cls.__lock:
			now = datetime.now()
			should_sync = False
			if force:
				should_sync = True
			elif not cls.__last_sync:
				should_sync = True
			elif now - cls.__last_sync > DATABASE_SYNC_DELTA:
				should_sync = True

			if not should_sync:
				return

			json_text = json.dumps(d)
			cls.__backup_file_path.unlink(missing_ok=True)
			if cls.__file_path.is_file():
				cls.__file_path.rename(cls.__backup_file_path)
			cls.__file_path.write_text(json_text)

			cls.__last_sync = now

class Database:
	"""telegramma database class.

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
		if not isinstance(k, str):
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
		if not isinstance(k, str):
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
		if not isinstance(k, str):
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
				subkey_full = removesuffix(k, current_subkey)
				if cls.__has(subkey_full) and isinstance(cls.__get(subkey_full), dict):
					cls.__get(subkey_full).update(d)
					d = cls.__get(subkey_full)

			cls.__dict.update(d)

		cls.__sync()

	@classmethod
	def set(cls, k: str, v):
		"""Save a value to the database."""
		with cls.__dict_lock:
			return cls.__set(k, v)

	@classmethod
	def __sync(cls, force: bool = False):
		"""Unprotected cls.sync implementation."""
		_DatabaseFile.sync(cls.__dict, force)

	@classmethod
	def sync(cls, force: bool = False):
		"""Sync the database to file."""
		with cls.__dict_lock:
			cls.__sync(force)
