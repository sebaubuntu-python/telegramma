#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from random import choices
from requests import HTTPError, get
from telegram import Update
from telegram.ext import CallbackContext

DOMAIN = "https://some-random-api.ml"

def get_random_item():
	response = get("https://itvends.com/vend.php?format=text")
	try:
		response.raise_for_status()
	except HTTPError:
		return None

	return response.text.strip()

async def roll(update: Update, context: CallbackContext):
	chances = {
		"yes": 0.05,
		"no": 0.65,
		"maybe": 0.30,
	}

	choice = choices(list(chances.keys()), weights=list(chances.values()))[0]

	await update.message.reply_text(f"The answer is: {choice}")

async def slap(update: Update, context: CallbackContext):
	username = update.message.from_user.username
	if not username:
		username = update.message.from_user.full_name

	slapped_username = None
	if context.args:
		slapped_username = " ".join(context.args)
	elif update.message.reply_to_message:
		slapped_username = update.message.reply_to_message.from_user.username
		if not slapped_username:
			slapped_username = update.message.reply_to_message.from_user.full_name

	if not slapped_username:
		await update.message.reply_text("I don't know who's the one you want to slap, "
		                                "reply to a message or specify a username")
		return

	text = f"*{username} slaps {slapped_username}"

	random_item = get_random_item()
	if random_item:
		text += f" with {random_item}"

	text += "*"

	await update.message.reply_text(text)

async def whatis(update: Update, context: CallbackContext):
	if not context.args:
		await update.message.reply_text(f"Error: You need to specify something")
		return

	text = " ".join(context.args)

	random_item = get_random_item()
	if not random_item:
		await update.message.reply_text(f"Error: Couldn't understand what's that")
		return

	await update.message.reply_text(f"{text} is {random_item}")
