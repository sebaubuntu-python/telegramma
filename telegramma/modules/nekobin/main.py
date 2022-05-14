#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from io import BytesIO
from requests import HTTPError
from sebaubuntu_libs.libnekobin import to_nekobin
from telegram import Update
from telegram.ext import CallbackContext

async def nekobin(update: Update, context: CallbackContext):
	reply_to_message = update.message.reply_to_message

	if not reply_to_message:
		await update.message.reply_text("Usage: Reply /nekobin to a message")
		return

	if not reply_to_message.document and not reply_to_message.text:
		await update.message.reply_text("Usage: Reply /nekobin to a message containing a document or text")
		return

	message = await update.message.reply_text("Uploading...")

	if reply_to_message.document:
		try:
			file = await reply_to_message.document.get_file()
			with await file.download(out=BytesIO()) as f:
				text = f.getvalue().decode(encoding="utf-8", errors="ignore")
		except Exception:
			await message.edit_text("Error: failed to download file from Telegram (probably too big)")
			return
	else:
		text = reply_to_message.text

	try:
		url = to_nekobin(text)
	except HTTPError as e:
		await message.edit_text(f"Error: failed to upload to Nekobin: {e.response.status_code}")
	except Exception:
		await message.edit_text("Error: failed to upload to Nekobin: unknown error")
	else:
		await message.edit_text(f"Done, uploaded to Nekobin: {url}", disable_web_page_preview=True)
