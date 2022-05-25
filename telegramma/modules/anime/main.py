#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from requests import get
from telegram import Update
from telegram.ext import CallbackContext

DOMAIN = "https://some-random-api.ml"

def get_anime_url(type: str) -> str:
	url = f"{DOMAIN}/animu/{type}"
	response = get(url)
	try:
		response.raise_for_status()
	except Exception as e:
		return None

	try:
		response_json = response.json()
	except Exception as e:
		return None

	return response_json["link"]

async def hug(update: Update, context: CallbackContext):
	url = get_anime_url("hug")
	if not url:
		await update.message.reply_text(f"Error: Failed to give you a hug :(")
		return

	if update.message.reply_to_message:
		await update.message.reply_to_message.reply_animation(url)
	else:
		await update.message.reply_animation(url)

async def pat(update: Update, context: CallbackContext):
	url = get_anime_url("pat")
	if not url:
		await update.message.reply_text(f"Error: Failed to give you a pat :(")
		return

	if update.message.reply_to_message:
		await update.message.reply_to_message.reply_animation(url)
	else:
		await update.message.reply_animation(url)

async def wink(update: Update, context: CallbackContext):
	url = get_anime_url("wink")
	if not url:
		await update.message.reply_text(f"Error: Failed to give you a wink :(")
		return

	if update.message.reply_to_message:
		await update.message.reply_to_message.reply_animation(url)
	else:
		await update.message.reply_animation(url)
