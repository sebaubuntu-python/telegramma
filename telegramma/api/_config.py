#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""telegramma config utils."""

config: dict
try:
    from config import config
except ModuleNotFoundError:
    config = {}

def get_config_namespace(name: str) -> dict:
	"""Get a properties namespace from config.py."""
	return config[name] if name in config else {}
