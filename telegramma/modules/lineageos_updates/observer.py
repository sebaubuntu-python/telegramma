#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from asyncio import CancelledError, Event, sleep
from datetime import datetime
from liblineage.hudson.build_target import BuildTarget
from liblineage.ota.full_update_info import FullUpdateInfo
from sebaubuntu_libs.libexception import format_exception
from sebaubuntu_libs.liblogging import LOGE, LOGI
from typing import Dict

from telegramma.api import get_config_namespace
from telegramma.core.bot import Bot
from telegramma.modules.lineageos_updates.poster import Poster

CONFIG_NAMESPACE = get_config_namespace("lineageos_updates")

class Observer:
	last_device_post: Dict[str, datetime] = {}
	poster: Poster = None
	event = Event()

	now = datetime.now()
	for build_target in BuildTarget.get_lineage_build_targets():
		last_device_post[build_target.device] = now

	if CONFIG_NAMESPACE.get("enable", False):
		event.set()

	@classmethod
	async def task(cls, bot: Bot):
		try:
			cls.poster = Poster(bot.application.bot)
			while True:
				await cls.event.wait()

				try:
					build_targets = BuildTarget.get_lineage_build_targets()
				except Exception as e:
					LOGE(f"Can't get build targets: {format_exception(e)}")
					continue

				for device in [build_target.device for build_target in build_targets]:
					try:
						response = FullUpdateInfo.get_nightlies(device)
					except Exception:
						response = []

					if not response:
						LOGI(f"No updates for {device}")
						continue

					last_update = response[-1]

					build_date = last_update.datetime
					if device in cls.last_device_post and build_date <= cls.last_device_post[device]:
						continue

					cls.last_device_post[device] = build_date

					try:
						await cls.poster.post(device, last_update)
					except Exception as e:
						LOGE(f"Failed to post {device} {build_date} build\n"
						     f"{format_exception(e)}")

				# Wait 10 minutes
				await sleep(10 * 60)
		except CancelledError:
			pass

	@classmethod
	def set_start_date(cls, date: datetime):
		for build_target in BuildTarget.get_lineage_build_targets():
			cls.last_device_post[build_target.device] = date
