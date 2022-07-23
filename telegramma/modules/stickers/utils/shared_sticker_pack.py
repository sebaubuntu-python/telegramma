#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegram import Bot, Sticker
from telegram.error import TelegramError
from typing import List

from telegramma.api import Database

class SharedStickerPack:
	def __init__(self, name: str, owner_id: int, admins: List[int] = None):
		self.name = name
		self._owner_id = owner_id
		self._admins = admins or []

	@classmethod
	def from_sticker_pack_name(cls, name: str, telegram_bot: Bot = None):
		"""
		Create a SharedStickerPack from a sticker pack name.

		If telegram_bot is provided, the sticker pack name will be corrected with the proper suffix.
		"""
		sticker_set_name = (
			f"{name}_by_{telegram_bot.username}"
			if telegram_bot and not name.endswith(f"_by_{telegram_bot.username}")
			else name
		)

		if not Database.has(f"stickers.sticker_packs.{sticker_set_name}"):
			return None

		sticker_pack_data = Database.get(f"stickers.sticker_packs.{sticker_set_name}")

		return cls(sticker_set_name, sticker_pack_data["owner_id"], sticker_pack_data["admins"])

	@classmethod
	async def create(cls, name: str, title: str, owner_id: int, first_sticker: Sticker, telegram_bot: Bot):
		"""Add a shared sticker pack to the database."""
		sticker_set_name = (
			f"{name}_by_{telegram_bot.username}"
			if not name.endswith(f"_by_{telegram_bot.username}")
			else name
		)

		if Database.has(f"stickers.sticker_packs.{sticker_set_name}"):
			try:
				await telegram_bot.get_sticker_set(sticker_set_name)
			except TelegramError:
				# The sticker pack doesn't exist anymore, continue
				pass
			else:
				# The sticker pack already exists, bail out
				raise ValueError(f"Sticker pack {sticker_set_name} already exists")

		result = await telegram_bot.create_new_sticker_set(
			user_id=owner_id,
			name=sticker_set_name,
			title=title,
			emojis=first_sticker.emoji,
			png_sticker=first_sticker.file_id,
			contains_masks=first_sticker.mask_position is not None,
			mask_position=first_sticker.mask_position
		)
		assert result, "Failed to create new sticker set"

		sticker_pack = cls(sticker_set_name, owner_id)
		sticker_pack._sync()

		return sticker_pack

	def _sync(self):
		Database.set(f"stickers.sticker_packs.{self.name}.owner_id", self._owner_id)
		Database.set(f"stickers.sticker_packs.{self.name}.admins", self._admins)

	def add_admin(self, user_id: int):
		"""Add an admin to the sticker pack."""
		if user_id in self._admins:
			return

		self._admins.append(user_id)
		self._sync()

	def remove_admin(self, user_id: int):
		"""Remove an admin from the sticker pack."""
		if user_id not in self._admins:
			return

		self._admins.remove(user_id)
		self._sync()

	def clear_admins(self):
		"""Remove all the admins from the sticker pack."""
		self._admins = []
		self._sync()

	def get_owner_id(self):
		return self._owner_id

	def get_admins(self):
		return list(self._admins)

	def user_is_admin(self, user_id: int):
		return user_id == self._owner_id or user_id in self._admins

	async def get_telegram_sticker_set(self, telegram_bot: Bot):
		return await telegram_bot.get_sticker_set(self.name)

	def get_url(self):
		return f"https://t.me/addstickers/{self.name}"
