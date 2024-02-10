#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE, STDOUT
from telegram import Update
from telegram.constants import MessageLimit, ParseMode
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown

from telegramma.api import user_is_admin

async def shell(update: Update, context: CallbackContext):
	if not update.message:
		return

	if not update.message.from_user:
		return

	if not user_is_admin(update.message.from_user.id):
		await update.message.reply_text("Error: You are not authorized to use the shell")
		return

	if not context.args:
		await update.message.reply_text("Error: No command specified")
		return

	assert update.message.text is not None, "update.message.text is None"

	command = update.message.text.split(' ', 1)[1]

	process = await create_subprocess_shell(command, executable="/bin/bash",
	                                        stdout=PIPE, stderr=STDOUT)
	returncode = await process.wait()
	assert process.stdout is not None, "process.stdout is None"
	output = await process.stdout.read()
	output_str = output.decode("utf-8", errors="ignore")

	text = "\n".join([
		f"Command: `{escape_markdown(command, 2)}`",
		f"Return code: {returncode}",
		"",
		"",
	])

	text_message = "\n".join([
		"Output:",
		"```",
		f"{escape_markdown(output_str, 2)}",
		"```",
	])

	text_document = "Output: sent as document"

	if len(text) + len(text_message) < MessageLimit.MAX_TEXT_LENGTH:
		text += text_message
		await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN_V2)
	else:
		text += text_document
		await update.message.reply_document(
			document=output,
			filename="output.txt",
			caption=text,
			parse_mode=ParseMode.MARKDOWN_V2
		)
