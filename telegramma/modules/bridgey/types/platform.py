#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from colour import Color
from typing import TYPE_CHECKING, Any

from telegramma.api import Database
from telegramma.modules.bridgey.types.file import File
from telegramma.modules.bridgey.types.message import Message
from telegramma.modules.bridgey.types.user import User

if TYPE_CHECKING:
	from telegramma.modules.bridgey.types.pool import Pool

class BasePlatform:
	"""Base class of a bridge platform"""
	# The name of the platform
	NAME: str = None
	# The icon of the platform, used to indicate platform and as a fallback for user avatar
	ICON_URL: str = None
	# The main accent color of the platform
	ACCENT_COLOR: Color = None
	# The "native" file type of the platform
	FILE_TYPE: type = File
	# The "native" message type of the platform
	MESSAGE_TYPE: type = Message
	# The "native" user type of the platform
	USER_TYPE: type = User

	def __init__(self, pool, instance_name: str, data: dict):
		"""Initialize the platform."""
		self.pool: Pool = pool
		self.instance_name = instance_name
		self.data = data

		self.database_key_prefix = f"{self.pool.platforms_key}.{self.instance_name}"

	def __str__(self) -> str:
		"""Return the name of the platform."""
		return self.NAME

	async def on_message(self, message: Message, original_message_id: int) -> None:
		"""A new message has been received and must be sent to other bridges."""
		return await self.pool.on_message(message, original_message_id)

	def get_generic_message_id(self, platform_message_id) -> int:
		"""Get the common ID of a message given the platform message ID."""
		if not Database.has(self.pool.messages_key):
			return None

		for message_id, platform_message_ids in dict(Database.get(self.pool.messages_key)).items():
			if not self.instance_name in platform_message_ids:
				continue

			if platform_message_ids[self.instance_name] != platform_message_id:
				continue

			return int(message_id)

		return None

	def get_platform_message_id(self, generic_message_id: int) -> Any:
		"""Get the platform message ID of a generic message."""
		key = f"{self.pool.messages_key}.{generic_message_id}.{self.instance_name}"

		if not Database.has(key):
			return None

		return Database.get(key)

	def set_platform_message_id(self, generic_message_id: int, platform_message_id: int) -> None:
		"""Set the platform message ID of a generic message."""
		key = f"{self.pool.messages_key}.{generic_message_id}.{self.instance_name}"

		Database.set(key, platform_message_id)

	async def start(self) -> None:
		"""Start the platform."""
		raise NotImplementedError

	async def stop(self) -> None:
		"""Stop the platform."""
		raise NotImplementedError

	@property
	def running(self) -> bool:
		"""The platform observer is running."""
		raise NotImplementedError

	async def file_to_generic(self, file: FILE_TYPE) -> Message:
		"""Convert a platform-specific file object to a generic message."""
		raise NotImplementedError

	async def user_to_generic(self, user: USER_TYPE) -> User:
		"""Convert a platform-specific user object to a generic user."""
		raise NotImplementedError

	async def message_to_generic(self, message: MESSAGE_TYPE) -> Message:
		"""Convert a platform-specific message object to a generic message."""
		raise NotImplementedError

	async def send_message(self, message: Message, message_id: int) -> None:
		"""Send a message to the platform."""
		raise NotImplementedError
