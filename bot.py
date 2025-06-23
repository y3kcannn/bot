import discord
from discord.ext import commands
import requests
import asyncio

TOKEN = "YOUR_DISCORD_BOT_TOKEN"
API_URL = "https://midnightponywka.com/loader/discord/api.php"
API_SECRET = "BEDIRHAN_SECRET"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def send_request(action, username="", extra={}):
    data = {"action": action, "token": API_SECRET}
    if username:
        data["username"] = username
    data.update(extra)
    try:
        r = requests.post(API_URL, data=data)
        return r.text.strip()
    except Exception as e:
        return f"Error: {e}"

@bot.event
async def on_ready():
    print(f"[+] Bot aktif: {bot.user}")

@bot.command()
async def ban(ctx, username: str):
    msg = await ctx.send(f"🔨 Banning `{username}`...")
    result = await send_request("ban", username)
    await msg.edit(content=result)
    await asyncio.sleep(5)
    await msg.delete()
    await ctx.message.delete()

@bot.command()
async def unban(ctx, username: str):
    msg = await ctx.send(f"♻️ Unbanning `{username}`...")
    result = await send_request("unban", username)
    await msg.edit(content=result)
    await asyncio.sleep(5)
    await msg.delete()
    await ctx.message.delete()

@bot.command()
async def reset(ctx, username: str):
    msg = await ctx.send(f"🔄 Resetting `{username}`...")
    result = await send_request("reset", username)
    await msg.edit(content=result)
    await asyncio.sleep(5)
    await msg.delete()
    await ctx.message.delete()

@bot.command()
async def create(ctx, member: discord.Member):
    msg = await ctx.send(f"🔐 Creating key for `{member.display_name}`...")
    result = await send_request("create", member.display_name)
    await msg.edit(content=f"`{result}`")
    await asyncio.sleep(10)
    await msg.delete()
    await ctx.message.delete()

@bot.command()
async def listkeys(ctx):
    keys = await send_request("listkeys")
    await ctx.send(f"```{keys}```")

@bot.command()
async def delete(ctx, key: str):
    result = await send_request("delete", extra={"key": key})
    await ctx.send(f"🗑️ {result}")

bot.run(TOKEN)
