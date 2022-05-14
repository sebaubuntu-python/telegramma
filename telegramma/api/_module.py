#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""telegramma module model."""

from telegram import BotCommand
from telegram.ext import Handler

from telegramma.api._version import API_VERSION

class Module:
	"""telegramma module interface."""
	NAME: str
	"""Module name."""
	VERSION: str
	"""Module version."""
	CORE: bool = False
	"""The module provides core functionality."""
	HANDLERS: list[Handler] = []
	"""List of handlers."""
	COMMANDS: list[BotCommand] = []
	"""List of commands which the bot provides."""

	def __init__(self):
		assert self.NAME, "Module name is not defined."
		assert self.VERSION, "Module version is not defined."
