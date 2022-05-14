#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""telegramma admin utils."""

from sebaubuntu_libs.liblogging import LOGI

from telegramma.api._config import get_config_namespace

CONFIG_NAMESPACE = get_config_namespace("bot")
ADMINS: list[int] = CONFIG_NAMESPACE.get("admins", [])

def user_is_admin(user_id: int):
	"""Check if the given user ID is in the list of the admin user IDs."""
	allowed = False

	if user_id in ADMINS:
		allowed = True

	LOGI(f"Access {'granted' if allowed else 'denied'} to user {user_id}")
	return allowed
