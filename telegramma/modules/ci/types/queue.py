#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from asyncio import Queue
from sebaubuntu_libs.libexception import format_exception

from telegramma.api import log_to_logging_chat
from telegramma.core.bot import Bot
from telegramma.modules.ci.types.job import BaseJob

_queue: Queue[BaseJob] = Queue()

async def ci_task(bot: Bot):
	while True:
		if bot._stopping:
			break

		job = await _queue.get()

		try:
			await job.start()
		except Exception as e:
			text = "\n".join([
				"Error: Unhandled exception in job",
				f"{format_exception(e)}"
			])
			await log_to_logging_chat(bot.application.bot, text)

		_queue.task_done()

async def put_job(job: BaseJob):
	return await _queue.put(job)

async def format_queue_list():
	return "\n".join([
		f"On queue: {_queue.qsize()}",
	])
