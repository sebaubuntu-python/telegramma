#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from requests import get
from typing import Generator, List, Union
from urllib.request import pathname2url

class Image:
	"""Image result."""
	def __init__(self, language: str, image: str):
		"""Initialize image result."""
		self.language = language
		self.image = image

	def get_description(self) -> str:
		"""Get a readable image description from the URL."""
		# Get the file name from the URL
		description = self.image.split("/")[-1]
		# Remove extension
		description = description.split(".")[0]
		# Swap "_" with space
		description = description.replace("_", " ")

		return description

class SenpyClubAPI:
	"""senpy.club API wrapper (anime girls holding programming books)"""
	API_ENDPOINT = "https://api.senpy.club/v2"

	@classmethod
	def _get_senpy_club_api_result(cls, path: str):
		# Make sure the API is alive
		assert cls.status()

		url = f"{cls.API_ENDPOINT}/{path}"
		response = get(url)
		try:
			response.raise_for_status()
		except Exception:
			return None

		try:
			response_json = response.json()
		except Exception:
			return None

		return response_json

	@classmethod
	def status(cls) -> bool:
		"""Check the API status."""
		try:
			response = get(cls.API_ENDPOINT)
		except Exception:
			return False

		return response.status_code == 200

	@classmethod
	def get_languages(cls) -> List[str]:
		"""Returns a list of programming languages supported by the API."""
		return cls._get_senpy_club_api_result("languages") or []

	@classmethod
	def is_language_supported(cls, language: str, languages: List[str] = None) -> Union[str, None]:
		"""
		Check if the provided language is supported by the API.

		Returns the case sensitive string if supported, None otherwise.
		To avoid useless API calls, you can pass a list of supported languages.
		"""
		languages = cls.get_languages()

		language_casefolded = language.casefold()
		for l in languages:
			if l.casefold() == language_casefolded:
				return l

		return None

	@classmethod
	def get_images_of_language(cls, language: str) -> List[Image]:
		"""
		Returns a list of images of the given programming language.

		Note: It's case sensitive, make sure you're passing the correct language
		with is_language_supported().
		"""
		images = []

		# Handle cases like C#
		language_url = pathname2url(language)

		for image in cls._get_senpy_club_api_result(f"language/{language_url}") or []:
			images.append(Image(language, image))

		return images

	@classmethod
	def get_random_image(cls) -> Image:
		"""Returns a random image of any programming language from the API."""
		result = cls._get_senpy_club_api_result("random")
		assert result is not None
		return Image(**result)
