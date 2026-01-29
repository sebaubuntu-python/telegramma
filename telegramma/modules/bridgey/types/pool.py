#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import asyncio
from sebaubuntu_libs.liblogging import LOGW
from threading import Lock
from typing import TYPE_CHECKING, Any, Dict, Type

from telegramma.api import Database, get_config_namespace
from telegramma.modules.bridgey.types.platform import BasePlatform

if TYPE_CHECKING:
	from telegramma.modules.bridgey.types.message import Message
else:
	Message = Any

# Platforms
from telegramma.modules.bridgey.platforms.discord import DiscordPlatform
from telegramma.modules.bridgey.platforms.matrix import MatrixPlatform
from telegramma.modules.bridgey.platforms.telegram import TelegramPlatform

CONFIG_NAMESPACE = get_config_namespace("bridgey")

PLATFORMS: Dict[str, Type[BasePlatform]] = {
	DiscordPlatform.NAME: DiscordPlatform,
	MatrixPlatform.NAME: MatrixPlatform,
	TelegramPlatform.NAME: TelegramPlatform,
}

class Pool:
	"""A class representing a pool (a group of connected chats)."""
	def __init__(self, name: str) -> None:
		"""Initialize the pool."""
		self.name = name

		self.database_key_prefix = f"bridgey.pools.{self.name}"
		self.last_message_id_key = f"{self.database_key_prefix}.last_message_id"
		self.messages_key = f"{self.database_key_prefix}.messages"
		self.platforms_key = f"{self.database_key_prefix}.platforms"

		self.last_message_id: int = (Database.get(self.last_message_id_key)
		                             if Database.has(self.last_message_id_key)
		                             else 0)
		self.last_message_id_lock = Lock()

		self.pool_config = CONFIG_NAMESPACE.get("pools", {}).get(self.name, {})

		self.platforms: Dict[str, BasePlatform] = {}

		for platform_name, platform_data in self.pool_config.items():
			if "platform" not in platform_data:
				LOGW(f"Pool {self.name} has an invalid platform, skipping")
				continue

			platform_type = platform_data["platform"]

			if platform_type not in PLATFORMS:
				LOGW(f"Pool {self.name} has an invalid platform type, skipping")
				continue

			platform_class = PLATFORMS[platform_type]

			self.platforms[platform_name] = platform_class(self, platform_name, platform_data)

	async def start(self):
		tasks = [asyncio.create_task(platform.start()) for platform in self.platforms.values()]
		await asyncio.gather(*tasks)

	async def stop(self):
		tasks = [asyncio.create_task(platform.stop()) for platform in self.platforms.values()]
		await asyncio.gather(*tasks)

	def get_new_message_id(self) -> int:
		"""Reserve a new generic message ID."""
		with self.last_message_id_lock:
			self.last_message_id += 1
			Database.set(self.last_message_id_key, self.last_message_id)
			return self.last_message_id

	async def on_message(self, message: Message, original_message_id: int) -> None:
		message_id = self.get_new_message_id()

		message.platform.set_platform_message_id(message_id, original_message_id)

		for platform in self.platforms.values():
			# Skip platform where the message is from
			if platform is message.platform:
				continue

			try:
				await platform.send_message(message, message_id)
			except Exception as e:
				LOGW(f"Failed to send message to {platform}: {e}")
				continue
