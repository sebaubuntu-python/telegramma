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
