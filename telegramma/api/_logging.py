#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""telegramma logging utils."""

from telegram import Bot
from sebaubuntu_libs.liblogging import LOGE

from telegramma.api import get_config_namespace

CONFIG_NAMESPACE = get_config_namespace("bot")
LOGGING_CHAT_ID = CONFIG_NAMESPACE.get("logging_chat_id")

async def log_to_logging_chat(bot: Bot, text: str):
	"""Send a message to the logging chat.

	Returns True if the message was sent successfully, False otherwise."""
	if not LOGGING_CHAT_ID:
		return False

	try:
		await bot.send_message(chat_id=LOGGING_CHAT_ID, text=text)
	except Exception as e:
		LOGE(f"Failed to send message to logging chat: {e}")
		return False
	else:
		return True
