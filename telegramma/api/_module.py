#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""telegramma module model."""

from telegram import BotCommand
from telegram.ext import BaseHandler
from typing import TYPE_CHECKING, Any, Callable, Coroutine

if TYPE_CHECKING:
	from telegramma.core.bot import Bot
else:
	Bot = Any

class Module:
	"""telegramma module interface."""
	NAME: str
	"""Module name."""
	VERSION: str
	"""Module version."""
	CORE: bool = False
	"""The module provides core functionality."""
	HANDLERS: list[BaseHandler] = []
	"""List of handlers."""
	COMMANDS: list[BotCommand] = []
	"""List of commands which the bot provides."""
	TASKS: list[Callable[[Bot], Coroutine[Any, Any, None]]] = []
	"""List of tasks to be executed after the bot is started. They must run forever and be non-blocking."""

	def __init__(self):
		"""Initialize the module."""
		assert self.NAME, "Module name is not defined."
		assert self.VERSION, "Module version is not defined."
