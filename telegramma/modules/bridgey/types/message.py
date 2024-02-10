#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
	from telegramma.modules.bridgey.types.platform import BasePlatform
	from telegramma.modules.bridgey.types.file import File
	from telegramma.modules.bridgey.types.message_type import MessageType
	from telegramma.modules.bridgey.types.user import User
else:
	BasePlatform = Any
	File = Any
	MessageType = Any
	User = Any

class Message:
	"""
	Class representing a message.

	Attributes:
	- platform: The platform where the message comes from
	- message_type: The type of the message (see MessageType class)
	- user: The user that sent the message (see User class)
	- timestamp: datetime object representing when the message has been sent
	- text: The text of the message, can be empty
	- file: The file of the message if message type requires it (see File class)
	- sticker_emoji: The emoji associated with a sticker, applicable only to MessageType.STICKER
	- reply_to: The generic message ID of the message which this message is a reply to, None otherwise
	"""
	def __init__(
		self,
		platform: BasePlatform,
		message_type: MessageType,
		user: User,
		timestamp: datetime,
		text: Optional[str] = None,
		file: Optional[File] = None,
		sticker_emoji: Optional[str] = None,
		reply_to: Optional[int] = None,
	):
		"""Initialize the message."""
		self.platform = platform
		self.message_type = message_type
		self.user = user
		self.timestamp = timestamp
		self.text = text
		self.file = file
		self.sticker_emoji = sticker_emoji
		self.reply_to = reply_to
