#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from sebaubuntu_libs.libsed import sed
from telegram import Update
from telegram.ext import CallbackContext

async def sed_handler(update: Update, context: CallbackContext):
	if not update.message.reply_to_message:
		return

	string = update.message.reply_to_message.text

	if not string:
		return

	message_text = update.message.text
	if not message_text:
		return

	result = string
	force_reply = False

	for command in message_text.split(';'):
		command = command.lstrip()
		if not command.strip():
			continue

		if not command.startswith("s/"):
			return

		sed_command = command.split("/")
		if len(sed_command) < 3 or len(sed_command) > 4:
			return

		pattern = sed_command[1]
		repl = sed_command[2]
		if len(sed_command) == 4:
			flags = sed_command[3]
		else:
			flags = ""

		try:
			result = sed(string, pattern, repl, flags)
		except Exception as e:
			result = (
				f"fuck me\n"
				f"{e}"
			)
			force_reply = True
			break

	if not force_reply and result == string:
		return

	result = result.strip()

	if not result:
		result = "Result is an empty string you fuck"

	await update.message.reply_text(result)
