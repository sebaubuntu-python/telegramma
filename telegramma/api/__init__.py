#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""telegramma stable API."""

from telegramma.api._admin import (
	user_is_admin,
)
from telegramma.api._config import (
	get_config_namespace,
)
from telegramma.api._database import (
	Database,
)
from telegramma.api._logging import (
	log_to_logging_chat,
)
from telegramma.api._module import (
	Module,
)
from telegramma.api._version import (
	API_VERSION,
	VERSION,
	assert_min_api_version,
)

# Add a comment that separates the symbols per API version.
# Keep sorted with LC_ALL=C
__all__ = [
	# 1
	'API_VERSION',
	'Database',
	'Module',
	'VERSION',
	'assert_min_api_version',
	'get_config_namespace',
	'log_to_logging_chat',
	'user_is_admin',
]
