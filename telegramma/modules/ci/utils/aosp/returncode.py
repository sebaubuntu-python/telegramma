#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from typing import Optional

class _AOSPReturnCode:
	def __init__(
		self,
		return_code: int,
		string: str = "Build failed: Unknown error",
		log_file: Optional[str] = None,
	):
		self.return_code = return_code
		self.string = string
		self.log_file = log_file

	def __int__(self):
		return self.return_code

	def __str__(self):
		return self.string

	def needs_logs_upload(self):
		return not not self.log_file

class AOSPReturnCode(_AOSPReturnCode):
	"""AOSP return code.

	This class indicates the status of a AOSP build.
	Can be casted to int and str.
	"""
	(
		_SUCCESS,
		_MISSING_ARGS,
		_MISSING_DIR,
		_REPO_SYNC_FAILED,
		_LUNCH_FAILED,
		_CLEAN_FAILED,
		_BUILD_FAILED,
	) = range(7)

	SUCCESS = _AOSPReturnCode(_SUCCESS, "Build completed successfully")
	MISSING_ARGS = _AOSPReturnCode(_MISSING_ARGS, "Build failed: Missing arguments")
	MISSING_DIR = _AOSPReturnCode(_MISSING_DIR, "Build failed: Project dir doesn't exists")
	REPO_SYNC_FAILED = _AOSPReturnCode(_REPO_SYNC_FAILED, "Build failed: repo sync failed", "repo_sync_log.txt")
	LUNCH_FAILED = _AOSPReturnCode(_LUNCH_FAILED, "Build failed: Lunching failed", "lunch_log.txt")
	CLEAN_FAILED = _AOSPReturnCode(_CLEAN_FAILED, "Build failed: Cleaning failed", "clean_log.txt")
	BUILD_FAILED = _AOSPReturnCode(_BUILD_FAILED, "Build failed: Building failed", "build_log.txt")

	_CODES = {
		_SUCCESS: SUCCESS,
		_MISSING_ARGS: MISSING_ARGS,
		_MISSING_DIR: MISSING_DIR,
		_REPO_SYNC_FAILED: REPO_SYNC_FAILED,
		_LUNCH_FAILED: LUNCH_FAILED,
		_CLEAN_FAILED: CLEAN_FAILED,
		_BUILD_FAILED: BUILD_FAILED,
	}

	@classmethod
	def from_code(cls, code: int) -> _AOSPReturnCode:
		return cls._CODES.get(code, cls(code))
