#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from asyncio import create_subprocess_exec, wait_for
from asyncio.subprocess import PIPE, STDOUT
from contextlib import suppress
from datetime import datetime
from pathlib import Path
import re
from sebaubuntu_libs.libstring import removesuffix
from typing import Optional

from telegramma.api import get_config_namespace
from telegramma.modules.ci.types.job import BaseJob
from telegramma.modules.ci.types.post_manager import PostManager
from telegramma.modules.ci.utils.aosp.returncode import AOSPReturnCode
from telegramma.modules.ci.types.artifacts import Artifacts
from telegramma.modules.ci.utils.uploader import Uploader

LIB_PATH = Path(__file__).parent

ADDITIONAL_ARTIFACTS = [
	"boot.img",
	"dtbo.img",
	"recovery.img",
	"super_empty.img",
	"vbmeta.img",
	"vbmeta_system.img",
	"vbmeta_vendor.img",
	"vendor_boot.img",
]

CONFIG_NAMESPACE = get_config_namespace("ci")

CCACHE_DIR = CONFIG_NAMESPACE.get("ccache_dir")
CCACHE_EXEC = CONFIG_NAMESPACE.get("ccache_exec")
ENABLE_CCACHE = CONFIG_NAMESPACE.get("enable_ccache", False)
MAIN_DIR = Path(CONFIG_NAMESPACE.get("main_dir", ""))
UPLOAD_ARTIFACTS = CONFIG_NAMESPACE.get("upload_artifacts", False)

class AOSPJob(BaseJob):
	"""This class represent an AOSP project."""
	# This value will also be used for folder name
	name: str
	# Version of the project
	version: str
	# Android version to display on Telegram post
	android_version: str
	# Filename of the zip. You can also use wildcards if the name isn't fixed
	zip_name: str
	# These next 2 values are needed for lunch (e.g. "lineage"_whyred-"userdebug")
	lunch_prefix: str
	lunch_suffix: str = "userdebug"
	# Target to build (e.g. to build a ROM's OTA package, use "bacon" or "otapackage", for a recovery project, use "recoveryimage")
	build_target: str = "bacon"
	# Regex to extract date from zip name, empty string to just use full name minus ".zip"
	date_regex: Optional[str] = None

	def check_args(self):
		"""Initialize AOSP project class."""
		self.parser.add_argument('device', help='device codename')
		self.parser.add_argument('-ic', '--installclean', help='make installclean before building', action='store_true')
		self.parser.add_argument('-c', '--clean', help='make clean before building', action='store_true')
		self.parser.add_argument('--release', help='upload build to release profile', action='store_true')
		self.parser.add_argument('--with_gms', help='include gapps', action='store_true')
		self.parser.add_argument('--repo_sync', help='run repo sync before building', action='store_true')
		self.parsed_args = self.parser.parse_args(self.args)

		self.device: str = self.parsed_args.device

		self.project_dir = MAIN_DIR / f"{self.name}-{self.version}"
		self.device_out_dir = self.project_dir / "out" / "target" / "product" / self.device

		if self.parsed_args.clean:
			self.clean_type = "clean"
		elif self.parsed_args.installclean:
			self.clean_type = "installclean"
		else:
			self.clean_type = "none"

		self.uploader_profile = "release" if self.parsed_args.release else "ci"

	async def start(self):
		header = f"{self.name} {self.version} ({self.android_version}"
		infos = {
			"Device": self.device,
			"Lunch flavor": f"{self.lunch_prefix}_{self.device}-{self.lunch_suffix}",
			"Build type": "Release" if self.parsed_args.release else "CI",
			"With GMS": str(self.parsed_args.with_gms),
		}
		post_manager = PostManager(header, infos, self.context.bot)

		await post_manager.update("Building")

		command = [
			LIB_PATH / "tools" / "building.sh",
			"--sources", self.project_dir,
			"--lunch_prefix", self.lunch_prefix,
			"--lunch_suffix", self.lunch_suffix,
			"--build_target", self.build_target,
			"--clean", self.clean_type,
			"--with_gms", str(self.parsed_args.with_gms),
			"--repo_sync", str(self.parsed_args.repo_sync),
			"--enable_ccache", str(ENABLE_CCACHE),
			"--ccache_exec", str(CCACHE_EXEC),
			"--ccache_dir", str(CCACHE_DIR),
			"--device", self.device,
		]

		last_edit = datetime.now()
		process = await create_subprocess_exec(*command, stdout=PIPE, stderr=STDOUT)
		while True:
			with suppress(TimeoutError):
				await wait_for(process.wait(), 1e-6)
			if process.returncode is not None:
				break

			assert process.stdout is not None, "stdout is None"
			output = (await process.stdout.readline()).decode("utf-8", errors="ignore")
			if not output:
				continue

			result = re.search(r"\[ +([0-9]+% [0-9]+/[0-9]+)\]", output.strip())
			if result is None:
				continue
			result_split = str(result.group(1)).split()
			if len(result_split) != 2:
				continue

			# Make sure we wait at least 2 minutes before editing post
			now = datetime.now()
			delta_time = now - last_edit
			if delta_time.seconds < 120:
				continue

			percentage, targets = re.split(" +", result.group(1))
			await post_manager.update(f"Building: {percentage} ({targets})")

			last_edit = datetime.now()

		# Process return code
		build_result = AOSPReturnCode.from_code(process.returncode)

		if build_result.needs_logs_upload():
			with (self.project_dir / str(build_result.log_file)).open("rb") as log_file:
				await post_manager.send_document(log_file)

		if build_result is AOSPReturnCode.SUCCESS and UPLOAD_ARTIFACTS:
			await self.upload(post_manager)
		else:
			await post_manager.update(build_result.string)

	async def upload(self, post_manager: PostManager):
		artifacts = Artifacts(self.device_out_dir, [self.zip_name] + ADDITIONAL_ARTIFACTS)
		try:
			uploader = Uploader(self.uploader_profile)
		except Exception as e:
			await post_manager.update(f"Upload failed: {type(e)}: {e}")
			return

		zip_filename = list(self.device_out_dir.glob(self.zip_name))
		if not zip_filename:
			await post_manager.update("Upload failed: No zip file found")
			return

		zip_filename = zip_filename[0].name
		folder_name = removesuffix(zip_filename, ".zip")
		if self.date_regex:
			date_match = re.search(self.date_regex, zip_filename)
			if date_match:
				folder_name = date_match.group(1)

		upload_path = Path() / self.device / folder_name

		await artifacts.upload(upload_path, uploader, post_manager)
