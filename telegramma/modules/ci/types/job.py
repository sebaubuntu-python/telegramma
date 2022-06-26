#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from typing import List
from telegram import Update
from telegram.ext import CallbackContext

from telegramma.api import TelegramArgumentParser

class BaseJob:
	def __init__(self,
				 update: Update,
				 context: CallbackContext,
				 parser: TelegramArgumentParser,
				 args: List[str],
				) -> None:
		self.update = update
		self.context = context
		self.parser = parser
		self.args = args

		self.check_args()

	def check_args(self) -> None:
		"""Check self.args for validity."""
		raise NotImplementedError

	async def start(self) -> None:
		raise NotImplementedError
