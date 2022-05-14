#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""telegramma API version."""

from telegramma import __version__

VERSION: str = __version__
"""telegramma version."""

API_VERSION: int = 1
"""The current API version."""

def assert_min_api_version(min_api_version: int) -> None:
    """Assert that the current API version is at least the specified one."""
    assert API_VERSION >= min_api_version, \
        f"API version {API_VERSION} is lower than {min_api_version}."
