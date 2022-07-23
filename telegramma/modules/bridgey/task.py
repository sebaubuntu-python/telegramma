#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from asyncio import CancelledError
from telegramma.core.bot import Bot
from telegramma.modules.bridgey.types.coordinator import Coordinator

async def bridgey_task(bot: Bot):
	try:
		await Coordinator.start()
	except CancelledError:
		await Coordinator.stop()
