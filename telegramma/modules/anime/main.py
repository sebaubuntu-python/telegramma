#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from random import choice
from telegram import Update
from telegram.ext import CallbackContext

from telegramma.api import TelegramArgumentParser
from telegramma.modules.anime.senpy_club import SenpyClubAPI
from telegramma.modules.anime.some_random_api import SomeRandomAPIAnime

# some-random-api.ml

async def hug(update: Update, context: CallbackContext):
	url = await SomeRandomAPIAnime.get_hug()
	if not url:
		await update.message.reply_text(f"Error: Failed to give you a hug :(")
		return

	if update.message.reply_to_message:
		await update.message.reply_to_message.reply_animation(url)
	else:
		await update.message.reply_animation(url)

async def pat(update: Update, context: CallbackContext):
	url = await SomeRandomAPIAnime.get_pat()
	if not url:
		await update.message.reply_text(f"Error: Failed to give you a pat :(")
		return

	if update.message.reply_to_message:
		await update.message.reply_to_message.reply_animation(url)
	else:
		await update.message.reply_animation(url)

async def wink(update: Update, context: CallbackContext):
	url = await SomeRandomAPIAnime.get_wink()
	if not url:
		await update.message.reply_text(f"Error: Failed to give you a wink :(")
		return

	if update.message.reply_to_message:
		await update.message.reply_to_message.reply_animation(url)
	else:
		await update.message.reply_animation(url)

# senpy.club

async def anigirl_holding_programming_book(update: Update, context: CallbackContext):
	command_name = "/anigirl_holding_programming_book"

	parser = TelegramArgumentParser(prog=command_name,
	                                description="Get a random anime girl holding a programming book")
	parser.add_argument("language", nargs="?",
	                    help="Specify which language you want to get an image from")
	parser.add_argument("--languages",
	                    help="Get a list of supported languages", action='store_true')
	try:
		args = parser.parse_args(context.args)
	except Exception as e:
		await update.message.reply_text(str(e))
		return

	if args.languages:
		languages = await SenpyClubAPI.get_languages()
		if not languages:
			await update.message.reply_text(f"Error: Failed to get a list of supported languages")
			return

		text = "\n".join([
			"Supported languages:",
			", ".join(languages),
			f"You can get an image from a specific programming language with {command_name} <language>",
		])
		await update.message.reply_text(text)
		return

	language = None
	if args.language:
		language = await SenpyClubAPI.is_language_supported(args.language)
		if not language:
			await update.message.reply_text(f"Error: {args.language} is not a supported language")
			return

	if language:
		try:
			images = await SenpyClubAPI.get_images_of_language(language)
		except Exception:
			await update.message.reply_text(f"Error: Failed to get an image")
			return

		if not images:
			await update.message.reply_text(f"Error: Failed to get an image")
			return

		image = choice(images)
	else:
		image = await SenpyClubAPI.get_random_image()

	description = "\n".join([
		f"{image.get_description()}",
		f"Language: {image.language}",
		"",
	])
	if not language:
		description += "\n".join([
			"",
			f"Tip: You can get an image of a specific language with {command_name} <language>",
			f"You can get a list of supported languages with {command_name} --languages",
		])

	await (update.message.reply_animation(image.image, caption=description)
	       if image.image.endswith(".gif")
	       else update.message.reply_photo(image.image, caption=description))
	return
