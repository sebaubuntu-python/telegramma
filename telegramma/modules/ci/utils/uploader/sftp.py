#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""Remote upload utils library."""

import os
from paramiko import SFTPClient, Transport
from pathlib import Path

from telegramma.modules.ci.types.uploader import BaseUploader

class UploaderSFTP(BaseUploader):
	def _upload(self, file: Path, destination_path: Path):
		assert self.server, "Server not set"
		transport = Transport(self.server)
		username = self.username or ""
		password = self.password or None
		transport.connect(username=username, password=password)
		sftp = SFTPClient.from_transport(transport)
		assert sftp, "SFTP not initialized"
		self.chdir(sftp, str(destination_path))
		sftp.put(file, file.name)
		sftp.close()
		transport.close()

	def chdir(self, sftp: SFTPClient, remote_directory: str):
		if remote_directory == '/':
			sftp.chdir(str(remote_directory))
			return

		if remote_directory == '':
			return

		try:
			sftp.chdir(remote_directory)
		except IOError:
			dirname, basename = os.path.split(remote_directory.rstrip('/'))
			self.chdir(sftp, dirname)
			sftp.mkdir(basename)
			sftp.chdir(basename)
			return
