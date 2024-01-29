#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from __future__ import annotations
from aiohttp import ClientSession
from discord import (
	Attachment,
	Bot,
	Embed,
	File as DiscordFile,
	Intents,
	Message as DiscordMessage,
	TextChannel,
	User as DiscordUser,
)
from io import BytesIO
from sebaubuntu_libs.liblogging import LOGE

from telegramma.modules.bridgey.types.platform import BasePlatform
from telegramma.modules.bridgey.types.file import File
from telegramma.modules.bridgey.types.message import Message
from telegramma.modules.bridgey.types.message_type import MessageType
from telegramma.modules.bridgey.types.user import User

class BridgeyDiscordClient(Bot):
	"""Discord client that pass the message to DiscordPlatform."""
	def __init__(self, platform: DiscordPlatform, *, loop=None, **options):
		"""Initialize the client."""
		super().__init__(loop=loop, **options)

		self.platform = platform

	async def on_ready(self):
		channel = self.get_channel(self.platform.channel_id)

		if not channel:
			LOGE(f"Failed to get channel {self.platform.channel_id}")
			return

		if not isinstance(channel, TextChannel):
			LOGE(f"Channel {self.platform.channel_id} is not a text channel")
			return

		self.platform.channel = channel

	async def on_message(self, message: DiscordMessage):
		if message.author == self.user:
			return
		if message.channel.id != self.platform.channel_id:
			return

		await self.platform.on_message(await self.platform.message_to_generic(message), message.id)

class DiscordPlatform(BasePlatform):
	"""Discord platform."""
	NAME = "Discord"
	ICON_URL = "https://discord.com/assets/f9bb9c4af2b9c32a2c5ee0014661546d.png"
	FILE_TYPE = Attachment
	MESSAGE_TYPE = DiscordMessage
	USER_TYPE = DiscordUser

	def __init__(self, *args, **kwargs):
		"""Initialize the platform."""
		super().__init__(*args, **kwargs)

		self.channel_id: int = self.data["channel_id"]
		self.token: str = self.data["token"]

		self.client = None
		self.channel: TextChannel = None

		self.client = BridgeyDiscordClient(self, intents=Intents.all())

	async def start(self):
		await self.client.start(self.token)

	async def stop(self):
		await self.client.close()

	@property
	def running(self) -> bool:
		return self.channel is not None

	async def file_to_generic(self, file: FILE_TYPE):
		return File(platform=self,
		            url=file.url,
		            name=file.filename)

	async def user_to_generic(self, user: USER_TYPE):
		return User(platform=self,
		            name=user.name,
					url=f"https://discordapp.com/users/{user.id}",
					avatar_url=user.avatar)

	async def message_to_generic(self, message: MESSAGE_TYPE):
		message_type = MessageType.TEXT
		text = message.content
		file = None
		reply_to = None

		if message.attachments:
			message_type = MessageType.DOCUMENT
			file = message.attachments[0]
			if file.content_type:
				file_type = str(file.content_type)
				if file_type.startswith("audio/"):
					message_type = MessageType.AUDIO
				elif file_type.startswith("image/"):
					message_type = MessageType.IMAGE
				elif file_type.startswith("video/"):
					message_type = MessageType.VIDEO

			if len(message.attachments) > 1:
				text += "\n[Additional attached files]"
				for attachment in message.attachments[1:]:
					text += f"\n - {attachment.url}"

		if message.reference:
			reply_to = self.get_generic_message_id(message.reference.message_id)

		return Message(platform=self,
		               message_type=message_type,
		               user=(await self.user_to_generic(message.author)),
					   timestamp=message.created_at,
		               text=text,
					   file=(await self.file_to_generic(file)) if file else None,
					   reply_to=reply_to)

	async def send_message(self, message: Message, message_id: int):
		if not self.running:
			return

		title = ""
		description = message.text
		file = None

		if message.message_type is MessageType.STICKER:
			title = "Sticker"
			description = message.sticker_emoji

		embed = Embed(title=title, description=description, timestamp=message.timestamp)
		embed.set_author(name=str(message.user), url=message.user.url,
		                 icon_url=message.user.avatar_url)
		embed.set_footer(text=message.platform.NAME, icon_url=message.platform.ICON_URL)

		if message.file:
			# This thing leaks bot token...
			# This way Discord keeps the original URL that contains the token
			#if message.message_type is MessageType.IMAGE:
			#	embed.set_image(url=message.file.url)
			#elif message.message_type is MessageType.STICKER:
			#	embed.set_thumbnail(url=message.file.url)
			#else:
				async with ClientSession() as session:
					try:
						async with session.get(message.file.url, raise_for_status=True) as response:
							file = DiscordFile(BytesIO(await response.read()),
							                   filename=message.file.name)
					except Exception as e:
						LOGE(f"Failed to download file: {e}")
						return

		reference = None
		if message.reply_to:
			reply_to_message_id = self.get_platform_message_id(message.reply_to)
			if reply_to_message_id is not None:
				reference = self.channel.get_partial_message(reply_to_message_id)

		try:
			discord_message = await self.channel.send(embed=embed, file=file, reference=reference)
		except Exception as e:
			LOGE(f"Failed to send message to Discord: {e}")
			return

		self.set_platform_message_id(message_id, discord_message.id)
