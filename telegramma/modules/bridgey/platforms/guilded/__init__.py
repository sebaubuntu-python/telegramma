#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from aiohttp import ClientSession
from guilded import (
	Attachment,
	ChatChannel,
	Client,
	Embed,
	File as GuildedFile,
	FileType,
	Member,
	Message as GuildedMessage,
	User as GuildedUser,
)
from io import BytesIO
from sebaubuntu_libs.liblogging import LOGE
from typing import Any, Dict, Optional, Union

from telegramma.modules.bridgey.types.platform import BasePlatform
from telegramma.modules.bridgey.types.file import File
from telegramma.modules.bridgey.types.message import Message
from telegramma.modules.bridgey.types.message_type import MessageType
from telegramma.modules.bridgey.types.user import User

class BridgeyGuildedClient(Client):
	"""Guilded client that pass the message to GuildedPlatform."""
	def __init__(self, platform: "GuildedPlatform"):
		"""Initialize the client."""
		super().__init__()

		self.platform = platform

	async def on_ready(self):
		channel = await self.getch_channel(self.platform.channel_id)

		if not channel:
			LOGE(f"Failed to get channel {self.platform.channel_id}")
			return

		if not isinstance(channel, ChatChannel):
			LOGE(f"Channel {self.platform.channel_id} is not a text channel")
			return

		self.platform.channel = channel

	async def on_message(self, message: GuildedMessage):
		if not self.user:
			LOGE("User is None")
			return
		if not message.author:
			LOGE("Author is None")
			return
		if message.author.id == self.user.id:
			return
		if message.channel.id != self.platform.channel_id:
			return

		await self.platform.on_message(await self.platform.message_to_generic(message), message.id)

class GuildedPlatform(BasePlatform):
	"""Guilded platform."""
	NAME = "Guilded"
	ICON_URL = "https://img.guildedcdn.com/asset/Logos/logomark/Color/Guilded_Logomark_Color.png?ver=3"
	FILE_TYPE = Attachment
	MESSAGE_TYPE = GuildedMessage
	USER_TYPE = GuildedUser

	def __init__(self, *args, **kwargs):
		"""Initialize the platform."""
		super().__init__(*args, **kwargs)

		self.channel_id: str = self.data["channel_id"]
		self.token: str = self.data["token"]

		self.channel: Optional[ChatChannel] = None

		self.client = BridgeyGuildedClient(self)

	async def start(self):
		await self.client.start(self.token)

	async def stop(self):
		await self.client.close()

	@property
	def running(self) -> bool:
		return self.channel is not None

	async def file_to_generic(self, file: FILE_TYPE):
		return File(
			platform=self,
			url=file.url,
			name=file.filename,
		)

	async def user_to_generic(self, user: Union[USER_TYPE, Member]):
		return User(
			platform=self,
			name=user.display_name,
			url=user.profile_url,
			avatar_url=user.avatar.url if user.avatar else None,
		)

	async def message_to_generic(self, message: MESSAGE_TYPE):
		message_type = MessageType.TEXT
		text = message.content
		file = None
		reply_to = None

		if not message.author:
			raise Exception("Author is None")

		if message.attachments:
			message_type = MessageType.DOCUMENT
			file = message.attachments[0]
			if file.file_type == FileType.image:
				message_type = MessageType.IMAGE
			elif file.file_type == FileType.video:
				message_type = MessageType.VIDEO

			if len(message.attachments) > 1:
				text += "\n[Additional attached files]"
				for attachment in message.attachments[1:]:
					text += f"\n - {attachment.url}"

		if message.replied_to_ids:
			reply_to = self.get_generic_message_id(message.replied_to_ids[0])

		return Message(
			platform=self,
			message_type=message_type,
			user=await self.user_to_generic(message.author),
			timestamp=message.created_at,
			text=text,
			file=(await self.file_to_generic(file)) if file else None,
			reply_to=reply_to,
		)

	async def send_message(self, message: Message, message_id: int):
		if not self.running:
			return

		if not self.channel:
			LOGE("Channel is not set")
			return

		title = ""
		description = message.text
		file = None

		if message.message_type is MessageType.STICKER:
			title = "Sticker"
			description = message.sticker_emoji

		embed = Embed(title=title, description=description, timestamp=message.timestamp)
		embed.set_author(
			name=str(message.user),
			url=message.user.url,
			icon_url=message.user.avatar_url,
		)
		embed.set_footer(text=message.platform.NAME, icon_url=message.platform.ICON_URL)

		if message.file:
			# This thing leaks bot token...
			# This way Guilded keeps the original URL that contains the token
			#if message.message_type is MessageType.IMAGE:
			#	embed.set_image(url=message.file.url)
			#elif message.message_type is MessageType.STICKER:
			#	embed.set_thumbnail(url=message.file.url)
			#else:
				async with ClientSession() as session:
					try:
						async with session.get(message.file.url, raise_for_status=True) as response:
							file = GuildedFile(
								BytesIO(await response.read()),
								filename=message.file.name
							)
					except Exception as e:
						LOGE(f"Failed to download file: {e}")
						return

		reference = None
		if message.reply_to:
			reply_to_message_id = self.get_platform_message_id(message.reply_to)
			if reply_to_message_id is not None:
				reference = await self.channel.fetch_message(reply_to_message_id)

		send_kwargs: Dict[str, Any] = {
			"embed": embed,
		}
		if reference:
			send_kwargs["reference"] = reference

		# No file support yet apparently
		#if file:
		#	send_kwargs["file"] = file

		try:
			guilded_message = await self.channel.send(**send_kwargs)
		except Exception as e:
			LOGE(f"Failed to send message to Guilded: {e}")
			return

		self.set_platform_message_id(message_id, guilded_message.id)
