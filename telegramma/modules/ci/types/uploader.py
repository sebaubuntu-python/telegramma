#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""Remote upload utils library."""

from typing import Dict
from pathlib import Path
from sebaubuntu_libs.liblogging import LOGI

class BaseUploader:
	def __init__(self, profile: Dict):
		"""Initialize the uploader variables."""
		self.profile = profile

		self.base_dir = Path(self.profile.get("base_dir", ""))
		self.host = self.profile.get("host")
		self.port = self.profile.get("port")
		self.server = f"{self.host}:{self.port}" if self.port else self.host
		self.username = self.profile.get("username")
		self.password = self.profile.get("password")

	def upload(self, file: Path, destination: Path):
		"""Upload an artifact using settings from config.env."""
		if not file.is_file():
			raise FileNotFoundError("File doesn't exist")

		if self.base_dir is None:
			destination_path = destination
		else:
			destination_path = self.base_dir / destination

		LOGI(f"Started uploading of {file.name}")

		self._upload(file, destination_path)

		LOGI(f"Finished uploading of {file.name}")

		return True

	def _upload(self, file: Path, destination_path: Path):
		raise NotImplementedError("Trying to upload with UploaderBase")
