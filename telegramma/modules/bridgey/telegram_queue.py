#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from asyncio import CancelledError, Queue
from sebaubuntu_libs.libexception import format_exception
from sebaubuntu_libs.liblogging import LOGI

from telegramma.core.bot import Bot
from telegramma.modules.bridgey.types.message import Message
from telegramma.modules.bridgey.types.message_type import MessageType
from telegramma.modules.bridgey.types.platform import BasePlatform

class ToTelegramMessage:
	def __init__(self,
	             platform: BasePlatform,
	             message: Message,
	             message_id: int,
	             chat_id: int,
	             text: str,
	             content: bytes,
	             reply_to_message_id: int):
		self.platform = platform
		self.message = message
		self.message_id = message_id
		self.chat_id = chat_id
		self.text = text
		self.content = content
		self.reply_to_message_id = reply_to_message_id

	async def send(self, bot: Bot):
		telegram_message = None
		kwargs = {
			"chat_id": self.chat_id,
			"reply_to_message_id": self.reply_to_message_id,
		}
		file_kwargs = {
			"caption": self.text,
			"filename": self.message.file.name if self.message.file else None,
		}

		try:
			if self.message.message_type is MessageType.TEXT:
				telegram_message = await bot.application.bot.send_message(text=self.text, **kwargs)
			elif self.message.message_type is MessageType.IMAGE:
				telegram_message = await bot.application.bot.send_photo(photo=self.content, **kwargs, **file_kwargs)
			elif self.message.message_type is MessageType.VIDEO:
				telegram_message = await bot.application.bot.send_video(video=self.content, **kwargs, **file_kwargs)
			elif self.message.message_type is MessageType.AUDIO:
				telegram_message = await bot.application.bot.send_audio(audio=self.content, **kwargs, **file_kwargs)
			elif self.message.message_type is MessageType.DOCUMENT:
				telegram_message = await bot.application.bot.send_document(document=self.content, **kwargs, **file_kwargs)
			elif self.message.message_type is MessageType.STICKER:
				telegram_message = await bot.application.bot.send_sticker(sticker=self.content, **kwargs)
			elif self.message.message_type is MessageType.ANIMATION:
				telegram_message = await bot.application.bot.send_animation(animation=self.content, **kwargs, **file_kwargs)
			else:
				LOGI(f"Unknown message type: {self.message.message_type}")
		except Exception as e:
			LOGI(f"Failed to send message: {format_exception(e)}")

		if telegram_message is None:
			LOGI(f"Telegram message is empty")
			return

		self.platform.set_platform_message_id(self.message_id, telegram_message.message_id)

_queue: "Queue[ToTelegramMessage]" = Queue()

async def to_telegram_task(bot: Bot):
	try:
		while True:
			message = await _queue.get()

			try:
				await message.send(bot)
			except Exception as e:
				LOGI(f"Failed to send message: {format_exception(e)}")

			_queue.task_done()
	except CancelledError:
		pass

async def put_message(message: ToTelegramMessage):
	return await _queue.put(message)
