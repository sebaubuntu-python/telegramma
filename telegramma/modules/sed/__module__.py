#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.api import Module, assert_min_api_version

assert_min_api_version(1)

from telegram.ext import MessageHandler, filters

from telegramma.modules.sed.main import (
	sed_handler,
)

class SedModule(Module):
	NAME = "sed"
	VERSION = "1.0"
	HANDLERS = [
		MessageHandler(filters.UpdateType.MESSAGE, sed_handler),
	]

module = SedModule()
