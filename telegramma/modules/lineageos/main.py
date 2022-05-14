#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from calendar import day_name
from humanize import naturalsize
from random import Random
from requests import HTTPError
from sebaubuntu_libs.liblineage.ota import get_nightlies
from sebaubuntu_libs.liblineage.wiki import get_device_data
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown

async def info(update: Update, context: CallbackContext):
	if len(context.args) < 2:
		await update.message.reply_text("Device codename not specified")
		return

	device = context.args[1]
	try:
		device_data = get_device_data(device)
	except HTTPError:
		await update.message.reply_text("Error: Device not found")
		return

	await update.message.reply_text(f"{device_data}", disable_web_page_preview=True)

async def last(update: Update, context: CallbackContext):
	if len(context.args) < 2:
		await update.message.reply_text("Device codename not specified")
		return

	device = context.args[1]
	response = get_nightlies(device)
	if not response:
		await update.message.reply_text(f"Error: no updates found for {device}")
		return

	last_update = response[-1]
	await update.message.reply_text(f"Last update for {escape_markdown(device, 2)}:\n"
	                                f"Version: {escape_markdown(last_update.version, 2)}\n"
	                                f"Date: {last_update.datetime.strftime('%Y/%m/%d')}\n"
	                                f"Size: {escape_markdown(naturalsize(last_update.size), 2)}\n"
	                                f"Download: [{escape_markdown(last_update.filename, 2)}]({escape_markdown(last_update.url, 2)})",
	                                parse_mode=ParseMode.MARKDOWN_V2)

async def when(update: Update, context: CallbackContext):
	if len(context.args) < 2:
		await update.message.reply_text("Device codename not specified")
		return

	device = context.args[1]

	try:
		device_data = get_device_data(device)
	except HTTPError:
		await update.message.reply_text("Error: Device not found")
		return

	if not device_data.maintainers:
		await update.message.reply_text("Error: Device not maintained")
		return

	random = Random()
	random.seed(device, version=1)
	day_int = int(1+7*random.random())
	day = day_name[day_int - 1]
	await update.message.reply_text(f"The next build for {device_data.vendor} {device_data.name} ({device}) will be on {day}")

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
