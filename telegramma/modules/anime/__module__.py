#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.api import Module, assert_min_api_version

assert_min_api_version(2)

from telegram import BotCommand
from telegram.ext import CommandHandler

from telegramma.modules.anime.main import (
	hug,
	pat,
	wink,
	anigirl_holding_programming_book,
)

class AnimeModule(Module):
	NAME = "anime"
	VERSION = "1.0"
	HANDLERS = [
		CommandHandler(["hug"], hug),
		CommandHandler(["pat"], pat),
		CommandHandler(["wink"], wink),
		CommandHandler(["anigirl_holding_programming_book"], anigirl_holding_programming_book),
	]
	COMMANDS = [
		BotCommand("hug", "Do you feel lonely?"),
		BotCommand("pat", "Good boy"),
		BotCommand("wink", "*wink wink*"),
		BotCommand("anigirl_holding_programming_book", "Get an anime girl holding a programming book"),
	]

module = AnimeModule()
