#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegram import Bot, Message
from telegram.error import TimedOut, RetryAfter
from time import sleep
from typing import Dict, Optional

from telegramma.api import get_config_namespace

CONFIG_NAMESPACE = get_config_namespace("ci")

CHAT_ID = CONFIG_NAMESPACE.get("chat_id")

class PostManager:
	def __init__(
		self,
		header: str,
		infos: Dict[str, str],
		bot: Bot,
	):
		"""Initialize PostManager class."""
		self.header = header
		self.infos = infos
		self.bot = bot

		self.base_message_text = self._get_base_message_text()
		self.message: Optional[Message] = None
		self.build_status = "Starting up"

	def _get_base_message_text(self) -> str:
		return "\n".join([
			f"🛠 CI | {self.header})",
			*[f"{k}: {v}" for k, v in self.infos.items()],
		])

	async def update(self, status: Optional[str] = None):
		if status:
			self.build_status = status

		text = "\n".join([
			f"{self.base_message_text}",
			"",
			f"Status: {self.build_status}",
			"",
		])

		await self._update(text)

	async def _update(self, text: str):
		try:
			if not self.message:
				self.message = await self.bot.send_message(CHAT_ID, text)
			else:
				await self.message.edit_text(text)
			return
		except RetryAfter as e:
			# Just in case
			sleep(e.retry_after + 5)
			return await self.update(text)
		except TimedOut:
			pass

	async def send_document(self, document):
		await self.bot.send_document(CHAT_ID, document)
