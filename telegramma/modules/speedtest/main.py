#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from datetime import datetime
from sebaubuntu_libs.libexception import format_exception
from speedtest import Speedtest
from telegram import Update
from telegram.ext import CallbackContext

from telegramma.api import Database, log_to_logging_chat

def format_result(date: datetime, download: int, upload: int) -> str:
	return (
		f"Date: {date.strftime('%Y-%m-%d %H:%M:%S')}\n"
		f"Download: {download // 10 ** 6} mbps\n"
		f"Upload: {upload // 10 ** 6} mbps"
	)

async def speedtest(update: Update, context: CallbackContext):
	now = datetime.now()

	last_speedtest_timestamp = Database.get("speedtest.last_speedtest.timestamp")
	if last_speedtest_timestamp:
		last_speedtest_download = Database.get("speedtest.last_speedtest.download")
		last_speedtest_upload = Database.get("speedtest.last_speedtest.upload")

		last_speedtest_datetime = datetime.fromtimestamp(last_speedtest_timestamp)
		if (now - last_speedtest_datetime).seconds < 5 * 60:
			message = format_result(last_speedtest_datetime, last_speedtest_download, last_speedtest_upload)
			await update.message.reply_text(message)
			return

	message = await update.message.reply_text("Running speedtest...")

	try:
		speedtest = Speedtest()
		speedtest.get_best_server()
		speedtest.download()
		speedtest.upload()
	except Exception as e:
		await message.edit_text("Error: Failed to run speedtest")
		log_to_logging_chat(
			f"Error: failed to run speedtest:\n"
			f"{format_exception(e)}"
		)
		return

	Database.set("speedtest.last_speedtest.timestamp", int(now.timestamp()))
	Database.set("speedtest.last_speedtest.download", speedtest.results.download)
	Database.set("speedtest.last_speedtest.upload", speedtest.results.upload)

	await message.edit_text(format_result(now, speedtest.results.download, speedtest.results.upload))
