#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from enum import Enum
from pathlib import Path
from sebaubuntu_libs.libexception import format_exception
from sebaubuntu_libs.liblogging import LOGE

from telegramma.modules.ci.types.post_manager import PostManager
from telegramma.modules.ci.types.uploader import BaseUploader

class ArtifactStatus(Enum):
	ON_QUEUE = "On queue"
	UPLOADING = "Uploading"
	UPLOADED = "Uploaded"
	ERROR = "Error while uploading"

	def __str__(self) -> str:
		return self.value

class Artifacts(dict):
	def __init__(self, path: Path, patterns: list[str]):
		"""Find the artifacts."""
		super().__init__()

		self.path = path
		self.patterns = patterns

		files = [list(self.path.glob(pattern)) for pattern in self.patterns]
		for artifact in [artifact for sublist in files for artifact in sublist]:
			self[artifact] = ArtifactStatus.ON_QUEUE

	def __str__(self):
		artifact_total = len(self)
		artifact_uploaded = len(self.get_artifacts_on_status(ArtifactStatus.UPLOADED))

		text = f"Uploaded {artifact_uploaded} out of {artifact_total} artifact(s)\n"
		text += "\n".join([
			f"{i}) {artifact}: {self[artifact]}"
			for i, artifact in enumerate(self.keys(), 1)
		])

		return text

	async def upload(self, upload_path: Path, uploader: BaseUploader, post_manager: PostManager):
		async def _update_post(status: str = "Uploading"):
			await post_manager.update(
				f"{status}\n"
				f"{self}"
			)

		for artifact in self:
			self[artifact] = ArtifactStatus.UPLOADING
			await _update_post()

			try:
				uploader.upload(artifact, upload_path)
			except Exception as e:
				self[artifact] = ArtifactStatus.ERROR
				LOGE(f"Error while uploading artifact {artifact}:\n"
				     f"{format_exception(e)}")
			else:
				self[artifact] = ArtifactStatus.UPLOADED

			await _update_post()

		await _update_post("Done")

	def get_artifacts_on_status(self, status: ArtifactStatus):
		return [artifact for artifact in self if self[artifact] is not status]
