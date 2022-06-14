#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""Remote upload utils library."""

from ftplib import FTP, error_perm
import os
from pathlib import Path

from telegramma.modules.ci.types.uploader import BaseUploader

class UploaderFTP(BaseUploader):
	def _upload(self, file: Path, destination_path: Path):
		with FTP(self.server) as ftp: 
			ftp.login(self.username, self.password)
			self.chdir(ftp, destination_path)
			with open(file, 'rb') as f:
				ftp.storbinary(f"STOR {file.name}", f)

	def chdir(self, ftp: FTP, remote_directory: Path):
		if remote_directory == '/':
			ftp.cwd(str(remote_directory))
			return

		if remote_directory == '':
			return

		try:
			ftp.cwd(str(remote_directory))
		except error_perm:
			dirname, basename = os.path.split(str(remote_directory).rstrip('/'))
			self.chdir(ftp, dirname)
			ftp.mkd(basename)
			ftp.cwd(basename)
			return
