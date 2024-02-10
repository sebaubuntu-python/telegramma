#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegram import Update
from telegram.ext import CallbackContext

from telegramma.modules.bridgey.platforms.telegram import TelegramPlatform
from telegramma.modules.bridgey.types.coordinator import Coordinator

async def handle_telegram_update(update: Update, context: CallbackContext):
	if not update.message:
		return

	for pool in Coordinator.pools.values():
		for platform in pool.platforms.values():
			if not isinstance(platform, TelegramPlatform):
				continue

			if platform.chat_id != update.message.chat.id:
				continue

			await platform.on_message(await platform.message_to_generic(update.message), update.message.message_id)

async def bridgey(update: Update, context: CallbackContext):
	if not update.message:
		return

	reply = "Bridgey status:\n"
	reply += f"Enabled: {Coordinator.enabled}\n\n"

	if Coordinator.enabled:
		for pool_name, pool in Coordinator.pools.items():
			reply += "\n".join([
				f"{pool_name}:",
				"\n".join([
					f"    {platform_name}: Running: {platform.running}"
					for platform_name, platform in pool.platforms.items()
				]),
			])

	await update.message.reply_text(reply)
