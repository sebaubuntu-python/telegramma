#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegram import Update
from telegram.ext import CallbackContext

from telegramma.modules.anime.some_random_api import SomeRandomAPIAnime

async def hug(update: Update, context: CallbackContext):
	url = SomeRandomAPIAnime.get_hug()
	if not url:
		await update.message.reply_text(f"Error: Failed to give you a hug :(")
		return

	if update.message.reply_to_message:
		await update.message.reply_to_message.reply_animation(url)
	else:
		await update.message.reply_animation(url)

async def pat(update: Update, context: CallbackContext):
	url = SomeRandomAPIAnime.get_pat()
	if not url:
		await update.message.reply_text(f"Error: Failed to give you a pat :(")
		return

	if update.message.reply_to_message:
		await update.message.reply_to_message.reply_animation(url)
	else:
		await update.message.reply_animation(url)

async def wink(update: Update, context: CallbackContext):
	url = SomeRandomAPIAnime.get_wink()
	if not url:
		await update.message.reply_text(f"Error: Failed to give you a wink :(")
		return

	if update.message.reply_to_message:
		await update.message.reply_to_message.reply_animation(url)
	else:
		await update.message.reply_animation(url)
