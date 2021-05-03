# Standard libraries
import asyncio
from io import BytesIO
import json
import random
import re
# 3rd party libraries - aiohttp is installed when installing discordpy
import aiohttp
import discord
from discord.ext import commands

BOT_TOKEN = ""  # Discord bot token from the discord developer portal
SERVER_IP = ""  # Rust server IP, eg: 1.1.1.1
SERVER_PORT = ""  # Rust server port, eg: 28015
SERVER_RCON_PASS = ""  # Rust server rcon password

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
# commands will be prefixed with !, eg: !command users
# intents need to be toggled on the discord developer portal


async def get_resp(ws, timeout=10.0):
    try:
        resp = await asyncio.wait_for(ws.receive(), timeout=timeout)
    except asyncio.TimeoutError:
        return False
    else:
        return resp


async def send_command(command_string, ctx, identifier):
    await client.server_ws.send_str(
        json.dumps({"Identifier": identifier, "Message": command_string, "Name": "DiscordBotRcon"})
    )

    resp = await get_resp(client.server_ws)
    if resp is False:
        return await ctx.send("Command timed out! Does this command exist?")

    counter = 0  # try 3 times to get the response wanted if the wrong response was received (wrong identifier)
    while json.loads(resp.data)["Identifier"] != identifier and counter < 4:
        resp = await get_resp(client.server_ws)
        if resp is False:
            return await ctx.send("Command timed out! Does this command exist?")
        counter += 1

    data = json.loads(resp.data)
    for i in range(5):  # handle commands with more than 1 response string sent out, eg, save
        resp = await get_resp(client.server_ws, timeout=0.25)
        if resp is not False:
            extra_data = json.loads(resp.data)
            if extra_data["Identifier"] == data["Identifier"]:
                data["Message"] += ("\n"+extra_data["Message"])

    if not data["Message"] and data["Identifier"] == identifier:
        await ctx.send("No message")  # basically, something went wrong
    elif data["Identifier"] == identifier:
        with BytesIO(str.encode(data["Message"])) as byt_f:  # send to the discord channel in a txt (avoids char limit)
            await ctx.send("Response:", file=discord.File(fp=byt_f, filename="server_response.txt"))
    else:
        await ctx.send("Did not receive response with correct ID")  # something went wrong


@commands.has_permissions(administrator=True)  # only roles with admin perms can use this command in discord 
@commands.max_concurrency(number=1, wait=True)  # commands will be queued after one another
@client.command()
async def command(ctx, *, command_string: str):
    # allows you to run any rcon command to the Rust server getting the response sent back to the discord channel
    async with ctx.channel.typing():
        # a random identifier is used to prevent responses conflicting and being handled wrong
        await send_command(command_string, ctx, random.randint(10, 10000))


@commands.has_permissions(administrator=True)  # only roles with admin perms can use this command in discord
@client.command()
async def ping(ctx):
    # get the latency of the discord bot (does not relate to the Rust server)
    await ctx.send(f"Pong! {round(client.latency * 1000)}ms")


@client.event
async def on_ready():
    # create a websocket connection attached to the discord bot instance to be used everywhere
    client.server_ws = await aiohttp.ClientSession().ws_connect(f"ws://{SERVER_IP}:{SERVER_PORT}/{SERVER_RCON_PASS}")
    print("I am ready to go!")


@client.event
async def on_command_error(ctx, error):
    # very basic error handling for badly inputted commands and any custom checks
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention} Missing arguments! :robot:")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send(f"{ctx.author.mention} You lack the required roles to use this command! :sweat:")
    else:
        await ctx.send(f"An unexpected error has occurred!\n{str(error)[:1000]}")


# start the discord bot
client.run(BOT_TOKEN)
