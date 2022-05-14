#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""telegramma bot."""

import asyncio
from os import execl, getpid, kill
from signal import SIGTERM
import sys
from telegram.ext import Application, ContextTypes

from telegramma import __name__ as __bot_name__
from telegramma.api import Module
from telegramma.core.error_handler import error_handler
from telegramma.core.modules import get_all_modules, get_module

class ModuleInstance:
	def __init__(self, module: Module, group_id: int):
		self.module = module
		self.group_id = group_id

		self.enabled = False

class Bot:
	def __init__(self, token: str) -> None:
		self.application = (Application.builder()
		                    .token(token)
		                    .context_types(ContextTypes(bot_data=lambda: self))
		                    .build())

		self._should_restart = False

		self.max_module_group = 0

		self.modules: dict[str, ModuleInstance] = {}
		for module in get_all_modules():
			self.modules[module.NAME] = ModuleInstance(module, self.max_module_group)
			self.max_module_group += 1

		self.application.add_error_handler(error_handler)

		loop = asyncio.get_event_loop()

		for module_name in self.modules:
			loop.run_until_complete(self.toggle_module(module_name, True, False))

		loop.run_until_complete(self.update_my_commands())

	def run(self) -> None:
		self.application.run_polling()

		if self._should_restart:
			execl(sys.executable, sys.executable, *["-m", __bot_name__])

	def stop(self, restart: bool = False) -> None:
		self._should_restart = restart
		kill(getpid(), SIGTERM)

	def get_module_instance(self, module_name: str):
		if not module_name in self.modules:
			module = get_module(module_name)
			if not module:
				return None

			self.modules[module_name] = ModuleInstance(module)

		return self.modules[module_name]

	async def toggle_module(self, module_name: str, enable: bool, update_my_commands: bool = True):
		module_instance = self.get_module_instance(module_name)
		if not module_instance:
			raise ModuleNotFoundError(f"Module {module_name} not found")

		if module_instance.enabled == enable:
			raise ValueError(f"Trying to disable module {module_name} that isn't enabled")

		if not enable and module_instance.module.core:
			raise ValueError(f"Trying to disable core module {module_name}")

		for handler in module_instance.module.HANDLERS:
			if enable:
				self.application.add_handler(handler, module_instance.group_id)
			else:
				self.application.remove_handler(handler, module_instance.group_id)

		module_instance.enabled = enable

		if update_my_commands:
			await self.update_my_commands()

	async def update_my_commands(self):
		commands = []

		for module_name in self.modules:
			module = get_module(module_name)
			commands.extend(module.COMMANDS)

		await self.application.bot.set_my_commands(commands)
