#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegram import Chat, Message, Update, User
from telegram.ext import CallbackContext

def format_chat_info(chat: Chat):
	return (
		f"ID: {chat.id}\n"
		f"Name: {chat.title if chat.title else chat.full_name}\n"
		f"Type: {chat.type}\n"
	)

def format_message_info(message: Message):
	return (
		f"ID: {message.message_id}\n"
		f"File ID: {message.effective_attachment.file_id if message.effective_attachment else None}\n"
	)

def format_user_info(user: User):
	return (
		f"ID: {user.id}\n"
		f"Name: {user.full_name}\n"
		f"Username: {f'@{user.username}' if user.username else None}\n"
		f"Bot: {user.is_bot}\n"
	)

async def info(update: Update, context: CallbackContext):
	chat = None
	message = None
	user = None
	if context.args:
		try:
			user = (await update.message.chat.get_member(context.args[0])).user
		except Exception:
			await update.message.reply_text(f"Error: Failed to get info about {context.args[0]}\n"
			                                "Is the user in this group?\n"
			                                "Note that using username is not supported yet")
			return
	elif update.message.reply_to_message:
		message = update.message.reply_to_message
		user = update.message.reply_to_message.from_user
	else:
		chat = update.message.chat
		user = update.message.from_user

	response = ("Info about the user:\n"
		        f"{format_user_info(user)}")

	if chat:
		response += ("\n"
			         "Info about the chat:\n"
		             f"{format_chat_info(chat)}")

	if message:
		response += ("\n"
		             "Info about the message:\n"
		             f"{format_message_info(message)}")

	await update.message.reply_text(response)
