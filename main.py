# Standard libraries
import asyncio
from io import BytesIO
from collections import deque
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


async def ws_response_loop():
    await client.wait_until_ready()
    await asyncio.sleep(1)
    while not client.is_closed():
        resp = await get_resp(client.server_ws, timeout=0.25)
        if resp is not False:
            data = json.loads(resp.data)
            if data["Identifier"] != 0:  # we only care about responses to commands we've given
                client.resp_deque.appendleft(data)


async def send_command(command_string, ctx, identifier):
    await client.server_ws.send_str(
        json.dumps({"Identifier": identifier, "Message": command_string, "Name": "DiscordBotRcon"})
    )
    # give the responses some time to come through
    await asyncio.sleep(1)
    resp_string = '\n'.join(
        [r["Message"] for r in [c for c in client.resp_deque if c is not None] if r["Identifier"] == identifier]
    )
    print(resp_string)
    print(client.resp_deque)
    if resp_string:
        if len(resp_string) > 1000:  # send to the discord channel in a txt (avoids char limit + looks nicer)
            with BytesIO(str.encode(resp_string)) as byt_f:
                await ctx.send("Response:", file=discord.File(fp=byt_f, filename="server_response.txt"))
        else:
            await ctx.send(f"```{resp_string}```")
    else:
        await ctx.send("No response! Did you use the right command?")


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
    if not hasattr(client, 'server_ws'):
        client.server_ws = await aiohttp.ClientSession().ws_connect(
            f"ws://{SERVER_IP}:{SERVER_PORT}/{SERVER_RCON_PASS}"
        )
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

        
# instantiate the response queue buffer
client.resp_deque = deque(10*[None], 30)
# instantiate the ws_response_loop
client.loop.create_task(ws_response_loop())
# start the discord bot
client.run(BOT_TOKEN)
