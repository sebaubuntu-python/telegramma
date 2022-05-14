#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from sebaubuntu_libs.liblogging import setup_logging

from telegramma.api import get_config_namespace
from telegramma.core.bot import Bot

CONFIG_NAMESPACE = get_config_namespace("bot")

def main():
	setup_logging()

	bot = Bot(CONFIG_NAMESPACE.get("token"))
	bot.run()
