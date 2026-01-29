#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""telegramma bot."""

from asyncio import Task, create_task, get_event_loop, new_event_loop, set_event_loop
from os import execl, getpid, kill
from signal import SIGTERM
import sys
from telegram.ext import Application, ContextTypes
from typing import Dict, List

from telegramma import __name__ as __bot_name__
from telegramma.api import Database, Module
from telegramma.core.error_handler import error_handler
from telegramma.core.modules import get_all_modules, get_module

class ModuleInstance:
	def __init__(self, module: Module, group_id: int):
		self.module = module
		self.group_id = group_id

		self.enabled = False

class Bot:
	def __init__(self, token: str) -> None:
		self._should_restart = False

		self.tasks: List[Task] = []

		self.modules: Dict[str, ModuleInstance] = {}
		self.max_module_group = 0
		for module in get_all_modules():
			self.modules[module.NAME] = ModuleInstance(module, self.max_module_group)
			self.max_module_group += 1

		self.application = (Application.builder()
		                    .token(token)
		                    .context_types(ContextTypes(bot_data=lambda: self))
		                    .post_init(self._post_init)
		                    .post_shutdown(self._post_shutdown)
		                    .build())

	async def _post_init(self, application: Application):
		application.add_error_handler(error_handler)

		for module_name, module_instance in self.modules.items():
			await self.toggle_module(module_name, True, False)
			for task in module_instance.module.TASKS:
				self.tasks.append(create_task(task(self)))

		await self.update_my_commands()

	async def _post_shutdown(self, application: Application):
		# Stop all tasks
		(task.cancel() for task in self.tasks)

		# Sync the database
		Database.sync(force=True)

	def run(self) -> None:
		try:
			get_event_loop()
		except RuntimeError:
			set_event_loop(new_event_loop())

		self.application.run_polling()

		if self._should_restart:
			execl(sys.executable, sys.executable, *["-m", __bot_name__])

	async def stop(self, restart: bool = False) -> None:
		self._should_restart = restart

		kill(getpid(), SIGTERM)

	def get_module_instance(self, module_name: str):
		if not module_name in self.modules:
			module = get_module(module_name)
			if not module:
				return None

			self.modules[module_name] = ModuleInstance(module, self.max_module_group)
			self.max_module_group += 1

		return self.modules[module_name]

	async def toggle_module(self, module_name: str, enable: bool, update_my_commands: bool = True):
		module_instance = self.get_module_instance(module_name)
		if not module_instance:
			raise ModuleNotFoundError(f"Module {module_name} not found")

		if module_instance.enabled == enable:
			raise ValueError(f"Trying to disable module {module_name} that isn't enabled")

		if not enable and module_instance.module.CORE:
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

		for module_instance in self.modules.values():
			if not module_instance.enabled:
				continue

			commands.extend(module_instance.module.COMMANDS)

		await self.application.bot.set_my_commands(commands)
