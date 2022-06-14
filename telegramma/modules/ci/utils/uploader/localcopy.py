#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""Remote upload utils library."""

from os import makedirs
from pathlib import Path
from shutil import copy

from telegramma.modules.ci.types.uploader import BaseUploader

class UploaderLocalcopy(BaseUploader):
	def _upload(self, file: Path, destination_path: Path):
		makedirs(destination_path, exist_ok=True)
		copy(file, destination_path)
