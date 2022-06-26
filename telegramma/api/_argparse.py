#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from argparse import ArgumentParser
from gettext import gettext

class TelegramArgumentParser(ArgumentParser):
	"""
	An argument parser for telegramma.
	
	Instead of calling system.exit(), this class raises an Exception with the error message
	plus the usage message if needed.

	Typical usage is:

	parser = TelegramArgumentParser(prog='/command')
	parser.add_argument("foo")
	...
	try:
		parser.parse_args(context.args)
	except Exception as e:
		await update.message.reply_text(str(e))
		return
	"""
	def __init__(self, *args, **kwargs):
		"""Initialize the parser."""
		super().__init__(*args, **kwargs)

		self._msg_buffer = []

	def _print_message(self, message, file=None):
		if message:
			self._msg_buffer.append(message)

	def exit(self, status=0, message=None):
		if message:
			self._print_message(message)
		raise Exception('\n'.join(self._msg_buffer))

	def error(self, message):
		self.print_usage()
		args = {'prog': self.prog, 'message': message}
		self.exit(2, gettext('%(prog)s: error: %(message)s\n') % args)
