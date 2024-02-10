#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
	from telegramma.modules.bridgey.types.platform import BasePlatform

class User:
	"""A class representing a user.

	Attributes:
	- platform (BasePlatform): The platform this user is from
	- name: The user's name
	- username: The user's username
	- url: The user's URL
	- avatar_url: The user's avatar URL
	"""
	def __init__(
		self,
		platform: BasePlatform,
		name: str,
		username: Optional[str] = None,
		url: Optional[str] = None,
		avatar_url: Optional[str] = None,
	):
		self.platform = platform
		self.name = name
		self.username = username
		self.url = url
		self.avatar_url = avatar_url

		if not self.avatar_url and self.platform.ICON_URL:
			self.avatar_url = self.platform.ICON_URL

	def __str__(self) -> str:
		"""
		Returns the formatted user name.

		It doesn't contain the platform name inside it because
		platforms can handle it as they wish.
		"""
		signature = f"{self.name}"

		if self.username:
			signature += f" (@{self.username})"

		return signature
