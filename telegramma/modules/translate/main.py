#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from deepl import Translator
from sebaubuntu_libs.liblogging import LOGE
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown

from telegramma.api import get_config_namespace

CONFIG_NAMESPACE = get_config_namespace("translate")

DEEPL_API_KEY = CONFIG_NAMESPACE.get("deepl_api_key")

DEFAULT_LANG = "en-us"
TRANSLATOR = Translator(DEEPL_API_KEY) if DEEPL_API_KEY else None

async def translate(update: Update, context: CallbackContext):
	reply_to_message = update.effective_message.reply_to_message
	if not reply_to_message:
		await update.effective_message.reply_text("Please reply to a message to translate it")
		return

	text = reply_to_message.text if reply_to_message.text else reply_to_message.caption
	if not text:
		await update.effective_message.reply_text("No text to translate")
		return

	if not TRANSLATOR:
		await update.effective_message.reply_text("API key not set, if you're a user it's not your fault")
		LOGE("DeepL API key not set")
		return

	usage = TRANSLATOR.get_usage()
	if usage.character.limit_exceeded:
		await update.effective_message.reply_text("API character limit exceeded")
		return

	to_lang = context.args[0] if context.args and len(context.args) > 0 else DEFAULT_LANG

	try:
		text_result = TRANSLATOR.translate_text(text, target_lang=to_lang)
	except Exception as e:
		await update.effective_message.reply_text(f"Error while translating the message, `{escape_markdown(to_lang, 2)}` is probably wrong: {escape_markdown(str(e), 2)}",
		                                          parse_mode=ParseMode.MARKDOWN_V2)
		return

	reply_text = (
		f"From `{escape_markdown(text_result.detected_source_lang, 2)}` to `{escape_markdown(to_lang, 2)}`:\n"
		"\n"
		f"{escape_markdown(text_result.text, 2)}"
	)

	await update.effective_message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN_V2)
