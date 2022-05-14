#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegram import Update
from telegram.ext import CallbackContext

from telegramma.api import VERSION, log_to_logging_chat, user_is_admin

async def start(update: Update, context: CallbackContext):
	await update.message.reply_text("Hi! I'm telegramma, and I'm alive\n"
	                                f"Version {VERSION}\n")

async def modules(update: Update, context: CallbackContext):
	message = "Loaded modules:\n\n"
	for module_name, module_instance in context.bot_data.modules.items():
		message += (
			f"{module_name}\n"
			f"Status: {'en' if module_instance.enabled else 'dis'}abled\n"
			"\n"
		)

	await update.message.reply_text(message)

async def enable(update: Update, context: CallbackContext):
	if not user_is_admin(update.message.from_user.id):
		await update.message.reply_text("Error: You are not authorized to load modules")
		return

	if len(context.args) < 1:
		await update.message.reply_text("Error: Module name not provided")
		return

	result = {}
	for module_name in context.args:
		try:
			await context.bot_data.toggle_module(module_name, True)
		except Exception as e:
			result[module_name] = f"Error: {e}"
			continue

		result[module_name] = "Module enabled"

	text = [f"{module_name}: {status}" for module_name, status in result.items()]
	await update.message.reply_text("\n".join(text))

async def disable(update: Update, context: CallbackContext):
	if not user_is_admin(update.message.from_user.id):
		await update.message.reply_text("Error: You are not authorized to unload modules")
		return

	if len(context.args) < 1:
		await update.message.reply_text("Error: Module name not provided")
		return

	result = {}
	for module_name in context.args:
		try:
			await context.bot_data.toggle_module(module_name, False)
		except Exception as e:
			result[module_name] = f"Error: {e}"
			continue

		result[module_name] = "Module disabled"

	text = [f"{module_name}: {status}" for module_name, status in result.items()]
	await update.message.reply_text("\n".join(text))

async def restart(update: Update, context: CallbackContext):
	if not user_is_admin(update.message.from_user.id):
		await update.message.reply_text("Error: You are not authorized to restart the bot")
		return

	await update.message.reply_text("Restarting...")

	full_name = update.message.from_user.full_name
	username = update.message.from_user.username
	user_id = update.message.from_user.id
	if username:
		full_name += f" (@{username})"
	else:
		full_name += f" ({user_id})"

	text = (
		"Restarting...\n"
		f"Triggered by {full_name}\n"
	)
	await log_to_logging_chat(context.bot, text)

	context.bot_data.stop(True)

async def shutdown(update: Update, context: CallbackContext):
	if not user_is_admin(update.message.from_user.id):
		await update.message.reply_text("Error: You are not authorized to shutdown the bot")
		return

	await update.message.reply_text("Shutting down...")

	full_name = update.message.from_user.full_name
	username = update.message.from_user.username
	user_id = update.message.from_user.id
	if username:
		full_name += f" (@{username})"
	else:
		full_name += f" ({user_id})"

	text = (
		"Shutting down...\n"
		f"Triggered by {full_name}\n"
	)
	await log_to_logging_chat(context.bot, text)

	context.bot_data.stop()
