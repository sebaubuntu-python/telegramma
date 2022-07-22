#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from telegramma.modules.bridgey.types.platform import BasePlatform

from urllib.parse import urlparse

class File:
	"""Class representing a file.

	Attributes:
	- platform: The platform this file is from.
	- url: The url of the file.
	- name: The name of the file. When not provided it will become the basename of the URL.
	"""
	def __init__(self,
	             platform: BasePlatform,
	             url: str,
	             name: str = "",
	            ) -> None:
		"""Initialize file class."""
		self.platform = platform
		self.url = url
		self.name = name if name else urlparse(self.url).path.rsplit('/', 1)[-1]
