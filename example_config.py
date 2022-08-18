config = {
	# [START]
	"bot": {
		# Bot API token
		# type: str
		"token": "",

		# List of admin's user IDs
		# type: list[int]
		"admins": [],

		# Chat ID of the logging chat
		# type: int
		"logging_chat_id": 0,
	},

	"bridgey": {
		# Enable bridging
		# type: bool
		"enabled": False,

		# List of pools (don't change pools and platforms name after you start the bridge)
		# type: dict[str, dict[str, dict]]
		"pools": {
			"example": {
				"discord": {
					# The name of the platform
					# type: str
					"platform": "Discord",

					# Bot token
					# type: str
					"token": "",

					# ID of the channel to bridge
					# type: int
					"channel_id": 0,
				},

				"matrix": {
					# The name of the platform
					# type: str
					"platform": "Matrix",

					# User ID of the bot account (e.g. @user:matrix.org)
					# type: str
					"username": "",

					# Password of the bot account
					# type: str
					"password": "",

					# URL of the Matrix server (e.g. https://matrix.org)
					# type: str
					"homeserver_url": "",

					# The alias of the room you want to bridge (e.g. #room:matrix.org)
					# type: str
					"room_alias": "",
				},

				"telegram": {
					# The name of the platform
					# type: str
					"platform": "Telegram",

					# ID of the chat to bridge
					# type: int
					"chat_id": 0,
				},
			},
		},
	},

	"ci": {
		# Main directory where all jobs will read/write from/to
		# type: str
		"main_dir": "",

		# Chat ID of the chat where the bot will send the messages
		# type: int
		"chat_id": 0,

		# Whether to upload artifacts or not
		# type: bool
		"upload_artifacts": False,

		# Enable ccache
		# type: bool
		"enable_ccache": False,

		# Path to ccache executable
		# type: str
		"ccache_exec": "",

		# Path to ccache files
		# type: str
		"ccache_dir": "",

		# Upload profiles
		# type: dict[str, dict]
		"upload_profiles": {
			"default": {
				# Method to use for uploading artifacts
				# type: str
				"method": "",

				# Absolute path to the directory where artifacts will be uploaded
				# type: str
				"base_dir": "",

				# If it's a remote method, the server address
				# type: str
				"host": "",

				# If it's a remote method, the TCP port
				# type: int
				"port": 0,

				# If it's a remote method, the username used for authentication
				# type: str
				"username": "",

				# If it's a remote method, the password used for authentication
				# type: str
				"password": "",
			},
		},
	},

	"lineageos_updates": {
		# Enable new updates observer
		# type: bool
		"enable": False,

		# Chat ID of the chat where the bot will send the update posts
		# type: int
		"chat_id": 0,
	},

	"translate": {
		# DeepL API key
		# type: str
		"deepl_api_key": "",
	},

	"twrpdtgen": {
		# GitHub username
		# type: str
		"github_username": "",

		# GitHub token
		# type: str
		"github_token": "",

		# GitHub organization
		# type: str
		"github_org": "",

		# Chat ID where generated device trees info will be sent
		# type: int
		"chat_id": 0,
	},
	# [END]
}
