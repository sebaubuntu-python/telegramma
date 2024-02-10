#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from aiohttp import ClientSession
from git.exc import GitCommandError
from git.repo import Repo
from github import Github, GithubException
from pathlib import Path
from sebaubuntu_libs.libexception import format_exception
from sebaubuntu_libs.liblogging import LOGE
from telegram import Update
from telegram.ext import CallbackContext
from tempfile import TemporaryDirectory
from twrpdtgen.device_tree import DeviceTree

from telegramma.api import get_config_namespace

CONFIG_NAMESPACE = get_config_namespace("twrpdtgen")

GITHUB_USERNAME = CONFIG_NAMESPACE.get("github_username")
GITHUB_TOKEN = CONFIG_NAMESPACE.get("github_token")
GITHUB_ORG = CONFIG_NAMESPACE.get("github_org")
CHAT_ID = CONFIG_NAMESPACE.get("chat_id")

DATA_IS_VALID = bool(GITHUB_USERNAME and GITHUB_TOKEN and GITHUB_ORG)

async def twrpdtgen(update: Update, context: CallbackContext):
	if not update.message:
		return

	if not context.args or len(context.args) != 1:
		await update.message.reply_text("Usage: /twrpdtgen <url>")
		return

	url = context.args[0]

	if not DATA_IS_VALID:
		await update.message.reply_text("Error: Missing configuration")
		return

	progress_text = ["Downloading file..."]
	progress_message = await update.message.reply_text("\n".join(progress_text))

	async def update_message(status: str):
		progress_text.append(status)
		await progress_message.edit_text("\n".join(progress_text), disable_web_page_preview=True)

	# Download file
	tempdir = TemporaryDirectory()
	path = Path(tempdir.name)
	file = path / "recovery.img"

	async with ClientSession() as session:
		try:
			async with session.get(url, allow_redirects=True, raise_for_status=True) as response:
				file.write_bytes(await response.read())
		except Exception as e:
			await update_message("Error: Failed to download file")
			LOGE("Failed to download file:\n"
			     f"{format_exception(e)}")
			return

	# Generate device tree
	await update_message("Generating device tree...")
	try:
		device_tree = DeviceTree(file)
		device_tree_folder = device_tree.dump_to_folder(path / "working", git=True)
	except Exception as e:
		await update_message(f"Error: Device tree generation failed: {e}")
		return

	branch = device_tree.device_info.build_description.replace(" ", "-")

	# Upload to GitHub
	await update_message("Pushing to GitHub...")
	repo_name = f"android_device_{device_tree.device_info.manufacturer}_{device_tree.device_info.codename}"
	git_repo_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_ORG}/{repo_name}"

	# Get organization
	try:
		gh = Github(GITHUB_TOKEN)
		gh_org = gh.get_organization(GITHUB_ORG)
	except GithubException as error:
		await update_message(f"Error: Failed to get GitHub organization: {error}")
		return

	# Create repo if needed
	await update_message("Creating repo if needed...")
	try:
		device_tree_repo = gh_org.create_repo(name=repo_name, private=False, auto_init=False)
	except GithubException as error:
		if error.status != 422:
			await update_message(f"Error: Repo creation failed {error.status} {error}")
			return

		device_tree_repo = gh_org.get_repo(name=repo_name)

	await update_message("Pushing...")
	try:
		Repo(device_tree_folder).git.push(git_repo_url, f"HEAD:refs/heads/{branch}")
		device_tree_repo.edit(default_branch=branch)
	except GitCommandError as e:
		await update_message("Error: Push to remote failed!")
		LOGE("Push to GitHub failed:\n"
		     f"{format_exception(e)}")
		return

	repo_url = f"{device_tree_repo.html_url}/tree/{branch}"

	await update_message(f"Done, {repo_url}")

	if not CHAT_ID:
		return

	await context.bot.send_message(
		CHAT_ID,
		"TWRP device tree generated\n"
		f"Codename: {device_tree.device_info.codename}\n"
		f"Manufacturer: {device_tree.device_info.manufacturer}\n"
		f"Build description: {device_tree.device_info.build_description}\n"
		f"Device tree: {repo_url}",
		disable_web_page_preview=True
	)
