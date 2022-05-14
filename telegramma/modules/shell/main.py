#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import subprocess
from telegram import Update
from telegram.constants import MessageLimit, ParseMode
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown
from tempfile import TemporaryFile

from telegramma.api import user_is_admin

async def shell(update: Update, context: CallbackContext):
	if not user_is_admin(update.message.from_user.id):
		await update.message.reply_text("Error: You are not authorized to use the shell")
		return

	if len(update.message.text.split(' ', 1)) < 2:
		await update.message.reply_text("No command provided")
		return

	command = update.message.text.split(' ', 1)[1]
	try:
		process = subprocess.check_output(command, shell=True, executable="/bin/bash",
		                                  stderr=subprocess.STDOUT, universal_newlines=True,
		                                  encoding="utf-8")
	except subprocess.CalledProcessError as e:
		returncode = e.returncode
		output = e.output
	else:
		returncode = 0
		output = process

	text = (
		f"Command: `{escape_markdown(command, 2)}`\n"
		f"Return code: {returncode}\n"
		"\n"
	)

	text_message = (
		"Output:\n"
		"```\n"
		f"{escape_markdown(output, 2)}\n"
		"```"
	)

	text_document = "Output: sent as document"

	if len(text) + len(text_message) < MessageLimit.TEXT_LENGTH:
		text += text_message
		await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN_V2)
	else:
		text += text_document
		fd = TemporaryFile(mode='r+')
		fd.write(output)
		fd.seek(0)
		await update.message.reply_document(document=fd, filename="output.txt", caption=text,
		                              parse_mode=ParseMode.MARKDOWN_V2)
		fd.close()
