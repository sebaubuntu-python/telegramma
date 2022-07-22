#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import requests
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

	def __init__(self, pool, instance_name: str, data: dict):
		super().__init__(pool, instance_name, data)

		self.chat_id: int = data["chat_id"]

	async def start(self) -> None:
		# telegramma is our event loop
		return None

	@property
	def running(self) -> bool:
		return True

	async def file_to_generic(self, file: FILE_TYPE):
		return File(platform=self,
		            url=file.file_path)

	async def user_to_generic(self, user: USER_TYPE):
		try:
			user_propics = (await user.get_profile_photos()).photos
		except BadRequest:
			user_propics = []

		if user_propics:
			avatar_url = (await user_propics[0][0].get_file()).file_path
		else:
			avatar_url = ""

		return User(platform=self,
		            name=user.full_name,
		            username=user.username,
					url=f"https://t.me/{user.username}" if user.username else "",
		            avatar_url=avatar_url)

	async def message_to_generic(self, message: MESSAGE_TYPE):
		text = ""
		file = None
		sticker_emoji = ""
		reply_to = None

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
			file = await (message.animation if message.animation else message.video).get_file()
		elif message.audio or message.voice:
			message_type = MessageType.AUDIO
			text = message.caption
			file = await (message.voice if message.voice else message.audio).get_file()
		elif message.sticker:
			message_type = MessageType.STICKER
			file = await message.sticker.thumb.get_file()
			sticker_emoji = message.sticker.emoji
		elif message.document:
			message_type = MessageType.DOCUMENT
			text = message.caption
			file = await message.document.get_file()
		else:
			message_type = MessageType.UNKNOWN

		if message.reply_to_message:
			reply_to = self.get_generic_message_id(message.reply_to_message.message_id)

		return Message(platform=self,
		               message_type=message_type,
		               user=(await self.user_to_generic(message.from_user)),
		               timestamp=message.date,
		               text=text if text else "",
		               file=(await self.file_to_generic(file)) if file else None,
					   sticker_emoji=sticker_emoji,
		               reply_to=reply_to)

	async def send_message(self, message: Message, message_id: int):
		text = f"[{message.platform.NAME}] {message.user}:"
		if message.text:
			text += f"\n{message.text}"

		content = None
		if message.file:
			try:
				response = requests.get(message.file.url)
			except Exception as e:
				LOGE(f"Failed to download file: {e}")
				return

			content = response.content

		reply_to_message_id = None
		if message.reply_to:
			reply_to_message_id = self.get_platform_message_id(message.reply_to)

		to_telegram_message = ToTelegramMessage(self, message, message_id, self.chat_id, text, content, reply_to_message_id)
		await put_message(to_telegram_message)
