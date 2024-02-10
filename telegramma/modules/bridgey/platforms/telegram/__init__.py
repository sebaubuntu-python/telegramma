#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from aiohttp import ClientSession
from sebaubuntu_libs.liblogging import LOGE
from telegram import (
	File as TelegramFile,
	Message as TelegramMessage,
	User as TelegramUser,
)
from telegram.error import BadRequest

from telegramma.modules.bridgey.telegram_queue import ToTelegramMessage, put_message
from telegramma.modules.bridgey.types.platform import BasePlatform
from telegramma.modules.bridgey.types.file import File
from telegramma.modules.bridgey.types.message import Message
from telegramma.modules.bridgey.types.message_type import MessageType
from telegramma.modules.bridgey.types.user import User

class TelegramPlatform(BasePlatform):
	NAME = "Telegram"
	ICON_URL = "https://telegram.org/img/t_logo.png"
	FILE_TYPE = TelegramFile
	MESSAGE_TYPE = TelegramMessage
	USER_TYPE = TelegramUser

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.chat_id: int = self.data["chat_id"]

	async def start(self) -> None:
		# telegramma is our event loop
		return None

	async def stop(self) -> None:
		# telegramma is our event loop
		return None

	@property
	def running(self) -> bool:
		return True

	async def file_to_generic(self, file: FILE_TYPE):
		assert file.file_path, "File has no path"

		return File(
			platform=self,
			url=file.file_path,
		)

	async def user_to_generic(self, user: USER_TYPE):
		user_propics = []
		try:
			profile_photos = await user.get_profile_photos()
			if profile_photos:
				user_propics = profile_photos.photos
		except BadRequest:
			pass

		avatar_url = (await user_propics[0][0].get_file()).file_path if user_propics else None

		return User(
			platform=self,
			name=user.full_name,
			username=user.username,
			url=f"https://t.me/{user.username}" if user.username else "",
			avatar_url=avatar_url,
		)

	async def message_to_generic(self, message: MESSAGE_TYPE):
		text = ""
		file = None
		sticker_emoji = None
		reply_to = None

		assert message.from_user, "Message has no user"

		if message.text:
			message_type = MessageType.TEXT
			text = message.text
		elif message.photo:
			message_type = MessageType.IMAGE
			text = message.caption
			file = await message.photo[-1].get_file()
		elif message.video or message.animation:
			message_type = (MessageType.ANIMATION if message.animation else MessageType.VIDEO)
			text = message.caption
			animation_or_video = message.animation if message.animation else message.video
			assert animation_or_video, "Message has no video or animation"
			file = await animation_or_video.get_file()
		elif message.audio or message.voice:
			message_type = MessageType.AUDIO
			text = message.caption
			voice_or_audio = message.voice if message.voice else message.audio
			assert voice_or_audio, "Message has no voice or audio"
			file = await voice_or_audio.get_file()
		elif message.sticker:
			message_type = MessageType.STICKER
			assert message.sticker.thumbnail, "Sticker has no thumbnail"
			file = await message.sticker.thumbnail.get_file()
			sticker_emoji = message.sticker.emoji
		elif message.document:
			message_type = MessageType.DOCUMENT
			text = message.caption
			file = await message.document.get_file()
		else:
			message_type = MessageType.UNKNOWN

		if message.reply_to_message:
			reply_to = self.get_generic_message_id(message.reply_to_message.message_id)

		return Message(
			platform=self,
			message_type=message_type,
			user=(await self.user_to_generic(message.from_user)),
			timestamp=message.date,
			text=text if text else "",
			file=(await self.file_to_generic(file)) if file else None,
			sticker_emoji=sticker_emoji,
			reply_to=reply_to,
		)

	async def send_message(self, message: Message, message_id: int):
		text = f"[{message.platform.NAME}] {message.user}:"
		if message.text:
			text += f"\n{message.text}"

		content = None
		if message.file:
			async with ClientSession() as session:
				try:
					async with session.get(message.file.url) as response:
						content = await response.read()
				except Exception as e:
					LOGE(f"Failed to download file: {e}")
					return

		reply_to_message_id = None
		if message.reply_to:
			reply_to_message_id = self.get_platform_message_id(message.reply_to)

		to_telegram_message = ToTelegramMessage(
			self,
			message,
			message_id,
			self.chat_id,
			text,
			content,
			reply_to_message_id,
		)

		await put_message(to_telegram_message)
