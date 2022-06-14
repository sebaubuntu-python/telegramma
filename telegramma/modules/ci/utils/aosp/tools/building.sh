#!/bin/bash
#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

set -o pipefail

# Set return codes
STATUS=(
	"SUCCESS"
	"MISSING_ARGS"
	"MISSING_DIR"
	"REPO_SYNC_FAILED"
	"LUNCH_FAILED"
	"CLEAN_FAILED"
	"BUILD_FAILED"
)

status_len="$((${#STATUS[@]} - 1))"
for returncode in $(seq 0 "${status_len}"); do
	eval "${STATUS[${returncode}]}"="${returncode}"
done

# Parse arguments passed by the ROM or recovery's script
while [ "${#}" -gt 0 ]; do
	case "${1}" in
		--sources )
			CI_SOURCES="${2}"
			shift
			;;
		--lunch_prefix )
			CI_LUNCH_PREFIX="${2}"
			shift
			;;
		--lunch_suffix )
			CI_LUNCH_SUFFIX="${2}"
			shift
			;;
		--build_target )
			CI_BUILD_TARGET="${2}"
			shift
			;;
		--clean )
			CI_CLEAN="${2}"
			shift
			;;
		--with_gms )
			CI_WITH_GMS="${2}"
			shift
			;;
		--repo_sync )
			CI_REPO_SYNC="${2}"
			shift
			;;
		--enable_ccache )
			CI_ENABLE_CCACHE="${2}"
			shift
			;;
		--ccache_exec )
			CI_CCACHE_EXEC="${2}"
			shift
			;;
		--ccache_dir )
			CI_CCACHE_DIR="${2}"
			shift
			;;
		--device )
			CI_DEVICE="${2}"
			shift
			;;
	esac
	shift
done

if [ "${CI_DEVICE}" = "" ]; then
	exit "${MISSING_ARGS}"
fi

if [ ! -d "${CI_SOURCES}" ]; then
	exit "${MISSING_DIR}"
fi

cd "${CI_SOURCES}"

if [ "${CI_REPO_SYNC}" = "True" ]; then
	repo sync -j$(nproc) --force-sync &> repo_sync_log.txt
	CI_REPO_SYNC_STATUS=$?
	if [ "${CI_REPO_SYNC_STATUS}" != 0 ]; then
		exit "${REPO_SYNC_FAILED}"
	fi
fi

if [ "${CI_ENABLE_CCACHE}" == "True" ]; then
	export USE_CCACHE=1
	export CCACHE_EXEC="${CI_CCACHE_EXEC}"
	export CCACHE_DIR="${CI_CCACHE_DIR}"
fi

. build/envsetup.sh

if [ "${CI_WITH_GMS}" = "True" ]; then
	export TARGET_INCLUDE_GAPPS=true
	export WITH_GMS=true
fi

lunch "${CI_LUNCH_PREFIX}_${CI_DEVICE}-${CI_LUNCH_SUFFIX}" &> lunch_log.txt
CI_LUNCH_STATUS=$?
if [ "${CI_LUNCH_STATUS}" != 0 ]; then
	exit "${LUNCH_FAILED}"
fi

if [ "${CI_CLEAN}" != "" ] && [ "${CI_CLEAN}" != "none" ]; then
	mka "${CI_CLEAN}" &> clean_log.txt
	CI_CLEAN_STATUS=$?
	if [ "${CI_CLEAN_STATUS}" != 0 ]; then
		exit "${CLEAN_FAILED}"
	fi
fi

mka "${CI_BUILD_TARGET}" "-j$(nproc --all)" 2>&1 | tee build_log.txt
CI_BUILD_STATUS=$?
if [ ${CI_BUILD_STATUS} != 0 ]; then
	exit "${BUILD_FAILED}"
fi

exit "${SUCCESS}"
