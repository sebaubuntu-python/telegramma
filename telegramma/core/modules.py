#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""telegramma modules framework."""

from importlib import import_module
from sebaubuntu_libs.libexception import format_exception
from sebaubuntu_libs.liblogging import LOGE

from telegramma.api import Module
from telegramma.modules import modules_path

def get_module(name: str) -> Module:
	"""Import a module from telegramma/modules."""
	try:
		module = import_module(f"telegramma.modules.{name}.__module__")
		return module.module
	except Exception as e:
		LOGE(f"Failed to import module {name}:\n"
		     f"{format_exception(e)}")

	return None

def get_all_modules():
	"""Import all modules."""
	for path in modules_path.iterdir():
		if not (path / "__module__.py").is_file():
			continue

		module = get_module(path.name)

		if not module:
			continue

		yield module
