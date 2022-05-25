#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.api import Module, assert_min_api_version

assert_min_api_version(1)

from telegram import BotCommand
from telegram.ext import CommandHandler

from telegramma.modules.anime.main import (
	hug,
	pat,
	wink,
)

class AnimeModule(Module):
	NAME = "anime"
	VERSION = "1.0"
	HANDLERS = [
		CommandHandler(["hug"], hug),
		CommandHandler(["pat"], pat),
		CommandHandler(["wink"], wink),
	]
	COMMANDS = [
		BotCommand("hug", "Do you feel lonely?"),
		BotCommand("pat", "Good boy"),
		BotCommand("wink", "*wink wink*"),
	]

module = AnimeModule()
