#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import asyncio
from typing import Dict

from telegramma.api import get_config_namespace
from telegramma.modules.bridgey.types.pool import Pool

CONFIG_NAMESPACE = get_config_namespace("bridgey")

class Coordinator:
	"""This class is responsible for coordinating messages between platforms"""

	enabled = bool(CONFIG_NAMESPACE.get("enabled", False))
	pools: Dict[str, Pool] = {}

	if enabled:
		for pool_name in CONFIG_NAMESPACE.get("pools", {}).keys():
			pools[pool_name] = Pool(pool_name)

	@classmethod
	async def start(cls):
		"""Start the coordinator"""
		if not cls.enabled:
			return

		tasks = [asyncio.create_task(pool.start()) for pool in cls.pools.values()]
		await asyncio.gather(*tasks)
