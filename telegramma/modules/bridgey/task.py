#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.core.bot import Bot
from telegramma.modules.bridgey.types.coordinator import Coordinator

async def bridgey_task(bot: Bot):
	await Coordinator.start()
