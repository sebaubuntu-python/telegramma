#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from typing import Any, Dict
from PIL import Image
from io import BytesIO
import magic
from nio import AsyncClient, UploadResponse
from os.path import basename
import requests
from urllib.parse import urlparse

class MatrixFile:
	def __init__(self,
	             upload_response: UploadResponse,
	             decryption_keys: Dict[str, Any],
	             filename: str,
	             filesize: int,
	             mime_type: str,
				 width: int = None,
	             height: int = None,
	            ) -> None:
		self.upload_response = upload_response
		self.decryption_keys = decryption_keys
		self.filename = filename
		self.filesize = filesize
		self.mime_type = mime_type
		self.width = width
		self.height = height

	async def send(self, client: AsyncClient, room_id: str, force_file: bool = False):
		"""Wrapper for sending a file to a room."""
		if self.mime_type.startswith("image/") and not force_file:
			msg_type = "m.image"
		elif self.mime_type.startswith("audio/"):
			msg_type = "m.audio"
		elif self.mime_type.startswith("video/"):
			msg_type = "m.video"
		else:
			msg_type = "m.file"

		content = {
			"body": self.filename,
			"info": {
				"size": self.filesize,
				"mimetype": self.mime_type,
			},
			"msgtype": msg_type,
		}

		if self.decryption_keys:
			content["file"] = {
				"url": self.upload_response.content_uri,
				"key": self.decryption_keys["key"],
				"iv": self.decryption_keys["iv"],
				"hashes": self.decryption_keys["hashes"],
				"v": self.decryption_keys["v"],
			}
		else:
			content["url"] = self.upload_response.content_uri

		if msg_type == "m.image":
			content["info"]["w"] = self.width
			content["info"]["h"] = self.height
			content["info"]["thumbnail_info"] = None
			content["info"]["thumbnail_url"] = None

		return await client.room_send(
			room_id=room_id,
			message_type="m.room.message",
			content=content,
		)

async def upload_file_to_matrix(client: AsyncClient, file: str):
	"""Upload file to Matrix server."""
	url = urlparse(file)
	filename = basename(url.path)

	# Download the file, not gonna be happy with big files
	response = requests.get(file)
	response.raise_for_status()
	file_bytes = response.content

	mime_type: str = magic.from_buffer(file_bytes, mime=True)

	if mime_type.startswith("image/"):
		with BytesIO(file_bytes) as f:
			with Image.open(f) as i:
				width, height = i.size
	else:
		width, height = None, None

	# first do an upload of image, then send URI of upload to room
	with BytesIO(file_bytes) as f:
		upload_response, decryption_keys = await client.upload(
			data_provider=f,
			content_type=mime_type,
			filename=filename,
			filesize=len(file_bytes),
		)
	assert isinstance(upload_response, UploadResponse), "Failed to upload file to Matrix"

	return MatrixFile(
		upload_response=upload_response,
		decryption_keys=decryption_keys,
		filename=filename,
		filesize=len(file_bytes),
		mime_type=mime_type,
		width=width,
		height=height
	)
