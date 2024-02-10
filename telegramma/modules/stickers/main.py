#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import CallbackContext
from typing import List

from telegramma.api import TelegramArgumentParser
from telegramma.modules.stickers.utils.shared_sticker_pack import SharedStickerPack

async def newpack(update: Update, context: CallbackContext, args: List[str]):
	if not update.message:
		return

	if not update.message.from_user:
		return

	command_name = "/stickers newpack"

	parser = TelegramArgumentParser(
		prog=command_name,
		description="Create a sticker pack"
	)
	parser.add_argument(
		"name", help="Short name of sticker set, to be used in t.me/addstickers/ URLs"
	)
	parser.add_argument("title", help="Sticker set title")
	try:
		parsed_args = parser.parse_args(args)
	except Exception as e:
		await update.message.reply_text(str(e))
		return

	if not update.message.reply_to_message:
		await update.message.reply_text(
			"Reply to a sticker to use as the first sticker in the sticker pack"
		)
		return

	sticker = update.message.reply_to_message.sticker
	if not sticker:
		await update.message.reply_text("Error: Replied message is not a sticker message")
		return

	try:
		shared_sticker_pack = await SharedStickerPack.create(
			name=parsed_args.name,
			title=parsed_args.title,
			owner_id=update.message.from_user.id,
			first_sticker=sticker,
			telegram_bot=context.bot,
		)
	except Exception as e:
		await update.message.reply_text(f"Error while creating sticker set: {e}")
		return

	await update.message.reply_text("\n".join([
		f"Sticker set created ({shared_sticker_pack.get_url()})",
		"",
		"You can add stickers to this set using"
		f' "/stickers addsticker {shared_sticker_pack.name}" while replying to a sticker message',
		"To delete the sticker set, use @Stickers",
	]))

async def addsticker(update: Update, context: CallbackContext, args: List[str]):
	if not update.message:
		return

	if not update.message.from_user:
		return

	if not update.message.reply_to_message:
		await update.message.reply_text("Reply to a sticker message to add it to a sticker pack")
		return

	sticker = update.message.reply_to_message.sticker
	if not sticker:
		await update.message.reply_text("Error: Replied message is not a sticker message")
		return

	if not args:
		await update.message.reply_text("Specify a sticker pack name after the command")
		return

	sticker_pack_name = args[0]

	shared_sticker_pack = SharedStickerPack.from_sticker_pack_name(sticker_pack_name, context.bot)
	if not shared_sticker_pack:
		await update.message.reply_text("I don't know this sticker pack")
		return

	if not shared_sticker_pack.user_is_admin(update.message.from_user.id):
		await update.message.reply_text("You are not an admin of this sticker pack")
		return

	try:
		result = await context.bot.add_sticker_to_set(
			user_id=update.message.from_user.id,
			name=shared_sticker_pack.name,
			png_sticker=sticker.file_id if not sticker.is_animated and not sticker.is_video else None,
			tgs_sticker=sticker.file_id if sticker.is_animated else None,
			webm_sticker=sticker.file_id if sticker.is_video else None,
			emojis=sticker.emoji,
		)
	except TelegramError as e:
		await update.message.reply_text(f"Error while adding sticker to sticker set: {e.message}")
		return

	if not result:
		await update.message.reply_text(
			"Error: It seems that this sticker is already in this sticker pack"
		)
		return

	await update.message.reply_text(f"Sticker added to sticker set {shared_sticker_pack.name}")

async def removesticker(update: Update, context: CallbackContext, args: List[str]):
	if not update.message:
		return

	if not update.message.from_user:
		return

	if not update.message.reply_to_message:
		await update.message.reply_text(
			"Reply to a sticker message to delete it from a sticker pack"
		)
		return

	sticker = update.message.reply_to_message.sticker
	if not sticker:
		await update.message.reply_text("Error: Replied message is not a sticker message")
		return

	if not sticker.set_name:
		await update.message.reply_text(
			"Error: It seems that this sticker isn't in any sticker pack"
		)
		return

	shared_sticker_pack = SharedStickerPack.from_sticker_pack_name(sticker.set_name, context.bot)
	if not shared_sticker_pack:
		await update.message.reply_text(
			f"Error: I don't know this sticker pack ({sticker.set_name})"
		)
		return

	if not shared_sticker_pack.user_is_admin(update.message.from_user.id):
		await update.message.reply_text("Error: You are not an admin of this sticker pack")
		return

	try:
		result = await context.bot.delete_sticker_from_set(sticker.file_id)
	except TelegramError as e:
		await update.message.reply_text(
			f"Error while deleting sticker from sticker set: {e.message}"
		)
		return

	if not result:
		await update.message.reply_text(
			"Error: It seems that this sticker is not in this sticker pack"
		)
		return

	await update.message.reply_text(f"Sticker deleted from sticker set {shared_sticker_pack.name}")

async def addadmin(update: Update, context: CallbackContext, args: List[str]):
	if not update.message:
		return

	if not update.message.from_user:
		return

	command_name = "/stickers addadmin"

	parser = TelegramArgumentParser(prog=command_name,
	                                description="Add a user to the admin list of a sticker pack")
	parser.add_argument("sticker_pack_name", help="Sticker pack name")
	parser.add_argument("user_id", nargs='?', type=int, help="Sticker set title")
	try:
		parsed_args = parser.parse_args(args)
	except Exception as e:
		await update.message.reply_text(str(e))
		return

	user_id = parsed_args.user_id
	if not user_id:
		if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
			await update.message.reply_text(
				"Reply to a user message to add them to the admin list of a sticker pack"
			)
			return

		user_id = update.message.reply_to_message.from_user.id

	shared_sticker_pack = SharedStickerPack.from_sticker_pack_name(
		parsed_args.sticker_pack_name, context.bot
	)
	if not shared_sticker_pack:
		await update.message.reply_text(
			f"Error: I don't know this sticker pack ({parsed_args.sticker_pack_name})"
		)
		return

	if not shared_sticker_pack.user_is_admin(update.message.from_user.id):
		await update.message.reply_text("Error: You are not an admin of this sticker pack")
		return

	shared_sticker_pack.add_admin(user_id)

	await update.message.reply_text(
		f"User {user_id} added to admin list of sticker pack {shared_sticker_pack.name}"
	)

async def removeadmin(update: Update, context: CallbackContext, args: List[str]):
	if not update.message:
		return

	if not update.message.from_user:
		return

	command_name = "/stickers removeadmin"

	parser = TelegramArgumentParser(
		prog=command_name,
		description="Remove a user from the admin list of a sticker pack"
	)
	parser.add_argument("sticker_pack_name", help="Sticker pack name")
	parser.add_argument("user_id", nargs='?', type=int, help="Sticker set title")
	try:
		parsed_args = parser.parse_args(args)
	except Exception as e:
		await update.message.reply_text(str(e))
		return

	user_id = parsed_args.user_id
	if not user_id:
		if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
			await update.message.reply_text(
				"Reply to a user message to remove them from the admin list of a sticker pack"
			)
			return

		user_id = update.message.reply_to_message.from_user.id

	shared_sticker_pack = SharedStickerPack.from_sticker_pack_name(
		parsed_args.sticker_pack_name, context.bot
	)
	if not shared_sticker_pack:
		await update.message.reply_text(
			f"Error: I don't know this sticker pack ({parsed_args.sticker_pack_name})"
		)
		return

	if not shared_sticker_pack.user_is_admin(update.message.from_user.id):
		await update.message.reply_text("Error: You are not an admin of this sticker pack")
		return

	shared_sticker_pack.remove_admin(user_id)

	await update.message.reply_text(
		f"User {user_id} removed from admin list of sticker pack {shared_sticker_pack.name}"
	)

async def help(update: Update, context: CallbackContext, args: List[str]):
	if not update.message:
		return

	await update.message.reply_text("\n".join([
		"Sticker pack management commands",
		"",
		"/stickers newpack \"<sticker_pack_name>\" \"<sticker_pack_title>\"",
		"Create a new sticker pack",
		"",
		"/stickers addsticker <sticker_pack_name>",
		"Reply to a sticker to add it to a sticker pack",
		"",
		"/stickers removesticker",
		"Reply to a sticker to delete it from its sticker pack",
		"",
		"/stickers addadmin <sticker_pack_name> [<user_id>]",
		"Reply to a user or specify a user ID to add them to the admin list of a sticker pack",
		"",
		"/stickers removeadmin <sticker_pack_name> [<user_id>]",
		"Reply to a user or specify a user ID to remove them from the admin list of a sticker pack",
	]))

COMMANDS = {
	"newpack": newpack,
	"addsticker": addsticker,
	"removesticker": removesticker,
	"addadmin": addadmin,
	"removeadmin": removeadmin,
	"help": help,
}

async def stickers(update: Update, context: CallbackContext):
	if not update.message:
		return

	if not context.args:
		await update.message.reply_text(
			"Error: Specify a command after the command\n"
			"/stickers help for more information"
		)
		return

	command_name, command_args = context.args[0], context.args[1:]
	if command_name not in COMMANDS:
		await update.message.reply_text(
			f"Unknown command {command_name}\n"
			"/stickers help for more information"
		)
		return

	await COMMANDS[command_name](update, context, command_args)
