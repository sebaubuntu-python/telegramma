#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from humanize import naturalsize
from liblineage.device import Device
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown

async def info(update: Update, context: CallbackContext):
	if not context.args or len(context.args) < 2:
		await update.message.reply_text("Device codename not specified")
		return

	device = Device(context.args[1])
	try:
		device_data = device.get_device_data()
	except Exception:
		await update.message.reply_text("Error: Device not found")
		return

	await update.message.reply_text(f"{device_data}", disable_web_page_preview=True)

async def last(update: Update, context: CallbackContext):
	if not context.args or len(context.args) < 2:
		await update.message.reply_text("Device codename not specified")
		return

	device = Device(context.args[1])
	nightlies = device.get_nightlies()
	if not nightlies:
		await update.message.reply_text(f"Error: no updates found for {device.codename}")
		return

	last_update = nightlies[-1]
	await update.message.reply_text(f"Last update for {escape_markdown(device.codename, 2)}:\n"
	                                f"Version: {escape_markdown(last_update.version, 2)}\n"
	                                f"Date: {last_update.datetime.strftime('%Y/%m/%d')}\n"
	                                f"Size: {escape_markdown(naturalsize(last_update.size), 2)}\n"
	                                f"Download: [{escape_markdown(last_update.filename, 2)}]({escape_markdown(last_update.url, 2)})",
	                                parse_mode=ParseMode.MARKDOWN_V2)

async def when(update: Update, context: CallbackContext):
	if not context.args or len(context.args) < 2:
		await update.message.reply_text("Device codename not specified")
		return

	device = Device(context.args[1])

	try:
		device_data = device.get_device_data()
	except Exception:
		device_data = None

	try:
		build_target = device.get_hudson_build_target()
	except Exception:
		await update.message.reply_text(f"Error: Device {'unmaintained' if device_data else 'not found'}")
		return

	device_info = (f"{device_data.vendor} {device_data.name} ({device_data.codename})"
	               if device_data
	               else f"{device.codename}")

	await update.message.reply_text(
		f"The next build for {device_info} will be on {build_target.get_next_build_date()}"
	)

# name: function
COMMANDS = {
	"info": info,
	"last": last,
	"when": when,
}

HELP_TEXT = (
	"Available commands:\n" +
	"\n".join(COMMANDS.keys())
)

async def lineageos(update: Update, context: CallbackContext):
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
