#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from requests import get

class SomeRandomAPIAnime:
	"""some-random-api.ml API wrapper."""
	API_ENDPOINT = "https://some-random-api.ml"

	@classmethod
	def _get_some_random_api_anime_result(cls, path: str) -> str:
		"""Get a result from the Some Random API Anime endpoint."""
		url = f"{cls.API_ENDPOINT}/animu/{path}"
		response = get(url)
		try:
			response.raise_for_status()
		except Exception as e:
			return None

		try:
			response_json = response.json()
		except Exception as e:
			return None

		return response_json["link"]

	@classmethod
	def get_hug(cls) -> str:
		"""Get a hug GIF URL."""
		return cls._get_some_random_api_anime_result("hug")

	@classmethod
	def get_pat(cls) -> str:
		"""Get a pat GIF URL."""
		return cls._get_some_random_api_anime_result("pat")

	@classmethod
	def get_wink(cls) -> str:
		"""Get a wink GIF URL."""
		return cls._get_some_random_api_anime_result("wink")
