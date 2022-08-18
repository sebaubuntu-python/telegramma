#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from datetime import datetime
from sebaubuntu_libs.liblineage.ota import get_nightlies
from telegram import Update
from telegram.ext import CallbackContext

from telegramma.api import user_is_admin
from telegramma.modules.lineageos_updates.observer import Observer
from telegramma.modules.lineageos_updates.poster import Poster

async def disable(update: Update, context: CallbackContext):
	Observer.event.clear()
	await update.message.reply_text("Observer disabled")

async def enable(update: Update, context: CallbackContext):
	Observer.event.set()
	await update.message.reply_text("Observer enabled")

async def info(update: Update, context: CallbackContext):
	alive = Observer.event.is_set()
	caption = (
		"Status:\n"
		f"Enabled: {str(alive)}\n"
	)
	text = ""
	if alive:
		caption += "List of devices:\n"
		text += (
			"Device | Last post\n"
		)
		for device in Observer.last_device_post:
			date = Observer.last_device_post[device]
			text += f"{device} | {date.strftime('%Y/%m/%d, %H:%M:%S')}\n"

	if text:
		await update.message.reply_document(document=text.encode("UTF-8", errors="ignore"),
		                                    filename="output.txt", caption=caption)
	else:
		await update.message.reply_text(caption)

async def set_start_date(update: Update, context: CallbackContext):
	if len(context.args) < 2:
		update.message.reply_text("Error: No timestamp provided")
		return

	try:
		date = datetime.fromtimestamp(int(context.args[1]))
	except Exception:
		update.message.reply_text(f"Error: Invalid timestamp: {context.args[1]}")
		return

	Observer.set_start_date(date)

	await update.message.reply_text(f"Start date set to {date.strftime('%Y/%m/%d, %H:%M:%S')}")

async def test_post(update: Update, context: CallbackContext):
	if len(context.args) < 2:
		await update.message.reply_text("Error: No device provided")
		return

	if not Observer.poster:
		await update.message.reply_text("Error: Poster not initialized")
		return

	device = context.args[1]
	chat_id = update.message.chat_id

	try:
		response = get_nightlies(device)
	except Exception:
		response = []

	if not response:
		await update.message.reply_text(f"No updates for {device}")
		return

	last_update = response[-1]

	build_date = last_update.datetime

	try:
		await Observer.poster.post(device, last_update, chat_id)
	except Exception:
		pass
	else:
		return

	await update.message.reply_text(f"Error: Could not post {device} {build_date}")

# name: callback
COMMANDS = {
	"disable": disable,
	"enable": enable,
	"info": info,
	"set_start_date": set_start_date,
	"test_post": test_post,
}

HELP_TEXT = "\n".join([
	"Available commands:",
	*COMMANDS.keys()
])

async def lineageos_updates(update: Update, context: CallbackContext):
	if not user_is_admin(update.message.from_user.id):
		await update.message.reply_text("Error: You are not authorized to use this command")
		return

	if not context.args:
		await update.message.reply_text(
			"Error: No argument provided\n\n"
			f"{HELP_TEXT}"
		)
		return

	command = context.args[0]

	if command not in COMMANDS:
		await update.message.reply_text(
			f"Error: Unknown command {command}\n\n"
			f"{HELP_TEXT}"
		)
		return

	func = COMMANDS[command]

	await func(update, context)
