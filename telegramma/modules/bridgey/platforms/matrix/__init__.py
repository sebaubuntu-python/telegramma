#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from datetime import datetime
from nio import (
	AsyncClient,
	JoinResponse,
	LoginResponse,
	MatrixRoom,
	ProfileGetAvatarResponse,
	RoomMessage,
	RoomMessageAudio,
	RoomMessageFile,
	RoomMessageImage,
	RoomMessageText,
	RoomMessageVideo,
	RoomSendResponse,
	SyncResponse,
)
from sebaubuntu_libs.libexception import format_exception
from sebaubuntu_libs.liblogging import LOGE

from telegramma.api import Database
from telegramma.modules.bridgey.platforms.matrix.utils.files import upload_file_to_matrix
from telegramma.modules.bridgey.types.platform import BasePlatform
from telegramma.modules.bridgey.types.file import File
from telegramma.modules.bridgey.types.message import Message
from telegramma.modules.bridgey.types.message_type import MessageType
from telegramma.modules.bridgey.types.user import User

class MatrixPlatform(BasePlatform):
	NAME = "Matrix"
	ICON_URL = "https://matrix.org/blog/wp-content/uploads/2015/01/logo1.png"
	FILE_TYPE = str
	MESSAGE_TYPE = RoomMessage
	USER_TYPE = str

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.username: str = self.data["username"]
		self.password: str = self.data["password"]
		self.homeserver_url: str = self.data["homeserver_url"]
		self.room_alias: str = self.data["room_alias"]

		if not self.homeserver_url.startswith("https://") and not self.homeserver_url.startswith("http://"):
			self.homeserver_url = f"https://{self.homeserver_url}"

		self.client: AsyncClient = None
		self.last_sync_token: str = None
		self.room_id: str = None

	async def start(self) -> None:
		self.client = AsyncClient(self.homeserver_url, self.username)
		self.client.add_response_callback(self.sync_callback, SyncResponse)
		self.client.add_event_callback(self.handle_msg, RoomMessage)

		if Database.has(f"{self.database_key_prefix}.logged_in"):
			self.client.access_token = Database.get(f"{self.database_key_prefix}.access_token")
			self.client.user_id = Database.get(f"{self.database_key_prefix}.user_id")
			self.client.device_id = Database.get(f"{self.database_key_prefix}.device_id")
		else:
			login_response = await self.client.login(self.password, device_name="telegramma-bridgey")
			if not isinstance(login_response, LoginResponse):
				LOGE(f"Failed to login to {self.homeserver_url}")
				return

			Database.set(f"{self.database_key_prefix}.access_token", login_response.access_token)
			Database.set(f"{self.database_key_prefix}.device_id", login_response.device_id)
			Database.set(f"{self.database_key_prefix}.user_id", login_response.user_id)
			Database.set(f"{self.database_key_prefix}.logged_in", True)

		LOGE("Joining room...")
		join_response = await self.client.join(self.room_alias)
		if not isinstance(join_response, JoinResponse):
			LOGE(f"Failed to join room: {join_response.message}")
			return

		self.room_id = join_response.room_id

		if Database.has(f"{self.database_key_prefix}.last_sync_token"):
			self.last_sync_token = Database.get(f"{self.database_key_prefix}.last_sync_token")

		await self.client.sync_forever(since=self.last_sync_token)

	async def stop(self):
		await self.client.close()

	async def sync_callback(self, sync_response: SyncResponse) -> None:
		if sync_response.next_batch == self.last_sync_token:
			return

		Database.set(f"{self.database_key_prefix}.last_sync_token", sync_response.next_batch)
		self.last_sync_token = sync_response.next_batch

	async def handle_msg(self, room: MatrixRoom, event: RoomMessage):
		if room.room_id != self.room_id:
			return

		# Make sure we didn't send this message
		if event.sender == self.client.user_id:
			return

		try:
			await self.on_message(await self.message_to_generic(event), event.event_id)
		except Exception as e:
			LOGE(f"Failed to handle message: {format_exception(e)}")

	@property
	def running(self):
		return self.client is not None

	async def file_to_generic(self, file: FILE_TYPE) -> File:
		url = await self.client.mxc_to_http(file)
		return File(platform=self,
		            url=url)

	async def user_to_generic(self, user: USER_TYPE) -> User:
		avatar_url = ""

		get_avatar_response = await self.client.get_avatar(user)
		if isinstance(get_avatar_response, ProfileGetAvatarResponse):
			if get_avatar_response.avatar_url:
				avatar_url = await self.client.mxc_to_http(get_avatar_response.avatar_url)

		return User(platform=self,
		            name=user,
		            url=f"https://matrix.to/#/{user}",
		            avatar_url=avatar_url)

	async def message_to_generic(self, message: MESSAGE_TYPE) -> Message:
		json = message.flattened()
		message_type = MessageType.UNKNOWN
		text = ""
		file = None
		reply_to = None

		if isinstance(message, RoomMessageText):
			message_type = MessageType.TEXT
		elif isinstance(message, RoomMessageImage):
			message_type = MessageType.IMAGE
		elif isinstance(message, RoomMessageVideo):
			message_type = MessageType.VIDEO
		elif isinstance(message, RoomMessageAudio):
			message_type = MessageType.AUDIO
		elif isinstance(message, RoomMessageFile):
			message_type = MessageType.DOCUMENT

		if "content.body" in json:
			text = json["content.body"]

		user = await self.user_to_generic(json["sender"])

		if "content.url" in json:
			file = await self.file_to_generic(json["content.url"])

		if "content.m.relates_to.m.in_reply_to.event_id" in json:
			in_reply_to = json["content.m.relates_to.m.in_reply_to.event_id"]
			reply_to = reply_to = self.get_generic_message_id(in_reply_to)

		return Message(platform=self,
					   message_type=message_type,
					   user=user,
					   timestamp=datetime.fromtimestamp(message.server_timestamp / 1000),
					   text=text,
					   file=file,
					   reply_to=reply_to)

	async def send_message(self, message: Message, message_id: int):
		if not self.running:
			return

		if self.room_id is None:
			LOGE("Room is None")
			return

		text = f"[{message.platform.NAME}] {message.user}:"
		if message.text:
			text += f"\n{message.text}"

		if message.message_type.is_file():
			try:
				matrix_file = await upload_file_to_matrix(self.client, message.file.url)
			except Exception as e:
				LOGE(f"Failed to upload file: {format_exception(e)}")
				return
			response = await matrix_file.send(
				self.client,
				self.room_id,
			)
		else:
			content = {
				"msgtype": "m.text",
				"body": text,
			}

			response = await self.client.room_send(
				room_id=self.room_id,
				message_type="m.room.message",
				content=content,
			)

		if not isinstance(response, RoomSendResponse):
			LOGE(f"Failed to send message: {response}")
			return

		self.set_platform_message_id(message_id, response.event_id)
