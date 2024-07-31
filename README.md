Bien sûr, voici le message exact en anglais, prêt à être utilisé :

---

# DM All Bot by @Sparkle | kda_delta (discord)

![DM All Bot](https://img.shields.io/badge/DM%20All%20Bot-v1.0-blue.svg)

## 📜 Introduction

**DM All Bot** is a Python Discord bot developed for educational purposes to send direct messages to all members in a Discord server. The bot provides various commands to manage exclusions and send messages to multiple servers. Note that any misuse of this bot is not the responsibility of the creator.

## ✨ Features

- Send direct messages to all members of a specified server.
- Send direct messages to all members in all servers.
- Exclude specific roles or members from receiving messages.
- List excluded roles and members.
- List all servers the bot is in.

## ⚙️ Commands

### Message Commands

- **`!dm <server_id> <message>`**: Send a direct message to all members of the specified server.
- **`!dmall <message>`**: Send a direct message to all members of all servers.

### Exclusion Commands

- **`!addrole <role_id>`**: Add a role to the exclusion list.
- **`!addmember <member_id>`**: Add a member to the exclusion list.
- **`!roles`**: List all roles in the exclusion list.
- **`!members`**: List all members in the exclusion list.

### Information Commands

- **`!servers`**: List all servers the bot is in with invite links.
- **`!help`**: Display the list of available commands.

## 🛠️ Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/KDA-sparkle/DM-All-Bot.git
   cd DM-All-Bot
   ```

2. Install the required modules:
   ```sh
   pip install discord.py
   ```

3. Create a `config.json` file in the root directory with the following structure:
   ```json
   {
     "token": "YOUR_BOT_TOKEN",
     "excluded_roles": [],
     "excluded_members": []
   }
   ```

4. Run the bot:
   ```sh
   python bot.py
   ```

## 🔑 Getting Your Bot Token

To get your bot token, follow these steps:
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a new application.
3. Navigate to the "Bot" section and create a new bot.
4. Copy the bot token and paste it into your `config.json` file.

## ⚠️ Disclaimer

This bot is created for educational purposes only. Any misuse of this bot is not the responsibility of the creator. Use it wisely and respect the Discord terms of service.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

## 📬 Contact

For any questions or issues, feel free to open an issue on GitHub or contact me on Discord at `kda_delta`.

---

Happy coding! 🚀
