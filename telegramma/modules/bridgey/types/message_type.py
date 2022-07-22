#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from enum import Enum

class MessageType(Enum):
	"""Class representing a message type.

	Available types:
	- TEXT: A simple text message, only text attribute must be filled.
	- IMAGE: An image message, file_url attribute must have a link to a valid image,
	         while text (interpreted as caption) might be filled.
	- VIDEO: A video message, file_url attribute must have a link to a valid video,
	         while text (interpreted as caption) might be filled.
	- AUDIO: An audio message, file_url attribute must have a link to a valid audio,
	         while text (interpreted as caption) might be filled.
	- DOCUMENT: A document message, file_url attribute must have a link to a valid document,
	            while text (interpreted as caption) might be filled.
	- STICKER: A sticker message, only file_url attribute must be filled with a link to a valid image.
	- ANIMATION: An animation message, file_url attribute must have a link to a valid video without audio,
	             while text (interpreted as caption) might be filled.
	- UNKNOWN: A message which isn't implemented, or is a special message type of the platform.
	           This type should always be avoided and instead convert unhandled types to a closer one
			   (for example, if a user send a contact, you can convert it
			   to a text message containing the contact's name and number).
	           Platforms will decide what to do with this message.
	"""
	UNKNOWN = 0
	TEXT = 1
	IMAGE = 2
	VIDEO = 3
	AUDIO = 4
	DOCUMENT = 5
	STICKER = 6
	ANIMATION = 7

	def __str__(self) -> str:
		return self.name.lower()

	def is_file(self) -> bool:
		return self in (
			MessageType.IMAGE,
			MessageType.VIDEO,
			MessageType.AUDIO,
			MessageType.DOCUMENT,
			MessageType.STICKER,
			MessageType.ANIMATION,
		)
