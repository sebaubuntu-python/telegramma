#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from aiohttp import ClientSession
from typing import Optional

class SomeRandomAPIAnime:
	"""some-random-api.com API wrapper."""
	API_ENDPOINT = "https://some-random-api.com"

	@classmethod
	async def _get_some_random_api_anime_result(cls, path: str) -> Optional[str]:
		"""Get a result from the Some Random API Anime endpoint."""
		url = f"{cls.API_ENDPOINT}/animu/{path}"
		async with ClientSession() as session:
			try:
				async with session.get(url, raise_for_status=True) as response:
					response_json = await response.json()
					return response_json["link"]
			except Exception:
				return None

	@classmethod
	async def get_hug(cls) -> Optional[str]:
		"""Get a hug GIF URL."""
		return await cls._get_some_random_api_anime_result("hug")

	@classmethod
	async def get_pat(cls) -> Optional[str]:
		"""Get a pat GIF URL."""
		return await cls._get_some_random_api_anime_result("pat")

	@classmethod
	async def get_wink(cls) -> Optional[str]:
		"""Get a wink GIF URL."""
		return await cls._get_some_random_api_anime_result("wink")
