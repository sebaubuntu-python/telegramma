#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""Remote upload utils library."""

from typing import Dict, Type

from telegramma.api import get_config_namespace
from telegramma.modules.ci.types.uploader import BaseUploader

# Backends
from telegramma.modules.ci.utils.uploader.ftp import UploaderFTP
from telegramma.modules.ci.utils.uploader.localcopy import UploaderLocalcopy
from telegramma.modules.ci.utils.uploader.sftp import UploaderSFTP

CONFIG_NAMESPACE = get_config_namespace("ci")

UPLOAD_PROFILES: Dict[str, Dict] = CONFIG_NAMESPACE.get("upload_profiles", {})

METHODS: Dict[str, Type[BaseUploader]] = {
	"localcopy": UploaderLocalcopy,
	"ftp": UploaderFTP,
	"sftp": UploaderSFTP,
}

uploaders: Dict[str, BaseUploader] = {
	profile_name: METHODS.get(profile.get("method"), BaseUploader)(profile)
	for profile_name, profile in UPLOAD_PROFILES.items()
}

def Uploader(profile: str = "default", fallback_to_default: bool = False) -> BaseUploader:
	if fallback_to_default:
		if not profile in uploaders:
			profile = "default"

	if not profile in uploaders:
		raise AssertionError(f"Profile {profile} not found")

	return uploaders[profile]
