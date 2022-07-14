#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from importlib import import_module
from telegram import Update
from telegram.ext import CallbackContext
from typing import Type

from telegramma.api import TelegramArgumentParser, user_is_admin
from telegramma.modules.ci.jobs import JOB_MODULES_PREFIX
from telegramma.modules.ci.types.job import BaseJob
from telegramma.modules.ci.types.queue import format_queue_list, put_job

async def ci(update: Update, context: CallbackContext):
	if not user_is_admin(update.message.from_user.id):
		await update.message.reply_text("Error: You are not authorized to run CI")
		return

	if not context.args:
		await update.message.reply_text("Error: No CI job specified")
		return

	job_name, job_args = context.args[0], context.args[1:]

	if job_name == "--queue":
		await update.message.reply_text(await format_queue_list())
		return

	try:
		job_module = import_module(f"{JOB_MODULES_PREFIX}.{job_name}", package="Job")
	except ModuleNotFoundError as e:
		await update.message.reply_text(f"Error: No CI job named {job_name}")
		return

	job_class: Type[BaseJob] = job_module.Job
	parser = TelegramArgumentParser(prog=f"/ci {job_name}")
	try:
		job = job_class(update, context, parser, job_args)
	except Exception as e:
		await update.message.reply_text(str(e))
		return

	await put_job(job)
	await update.message.reply_text(f"Job added to queue")
