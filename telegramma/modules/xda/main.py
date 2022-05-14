#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import random
from telegram import Update
from telegram.ext import CallbackContext

from telegramma.modules.xda.words import WORDS

async def xda(update: Update, context: CallbackContext):
	length = random.randint(3, 10)
	string = random.choices(list(WORDS.keys()), weights=list(WORDS.values()), k=length)
	random.shuffle(string)
	await update.message.reply_text(" ".join(string))
