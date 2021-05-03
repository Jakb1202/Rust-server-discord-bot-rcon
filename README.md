# Rust-server-discord-bot-rcon
An rcon tool for Rust game servers that is interacted with through a Discord bot written in Python
# Dependencies
1. discordpy: [Pypi](https://pypi.org/project/discord.py/), [Github](https://github.com/Rapptz/discord.py), [Docs](https://discordpy.readthedocs.io/en/latest/)
2. aiohttp: [Pypi](https://pypi.org/project/aiohttp/), [Github](https://github.com/aio-libs/aiohttp), [Docs](https://docs.aiohttp.org/en/stable/)

~~ You do not need to install aiohttp separately as installing discordpy will do it for you since it also has it as a dependency ~~

# Setup
Simply edit the 4 constants at the top of the file with the your Discord bot token and Rust server info and then run the `main.py` file.
```python
BOT_TOKEN = ""  # Discord bot token from the discord developer portal
SERVER_IP = ""  # Rust server IP, eg: 1.1.1.1
SERVER_PORT = ""  # Rust server port, eg: 28015
SERVER_RCON_PASS = ""  # Rust server rcon password
```
You can also change the command prefix as you wish at the Discord bot definition, simply change the exclamation mark to whatever you wish. This will be the symbol/phrase you write at the start of your discord message to indicate to the bot that this is a command it should invoke. By default you would do `!command` followed by your input.
```python
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
```
# Usage
#### By default, all commands are restricted to Discord users in your server who have the administrator role permission.
Use `!command` followed by the Rust rcon server command you want to invoke onto the server and then the response for it will be returned to the Discord channel you used the command in. Eg, use `!command users` to get a list of users currently connected to your Rust server and `!command sleepingusers` to get a list of users who are currently asleep on your Rust server.

![image](https://user-images.githubusercontent.com/63066020/116911941-6f96c100-ac3f-11eb-8908-bbbb7c838911.png)
