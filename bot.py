import discord
from discord.ext import commands
import requests
import os
import asyncio

TOKEN = "YOUR_DISCORD_BOT_TOKEN"  # <-- buraya gerçek Discord bot token'ını koy
API_TOKEN = "BEDIRHAN_SECRET"     # <-- PHP tarafındaki $secret_token ile birebir olmalı
API_URL = "https://midnightponywka.com/loader/discord/api.php"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Ortak mesaj temizleyici
async def delete_after(ctx, msg):
    await asyncio.sleep(5)
    await msg.delete()
    await ctx.message.delete()

# API'ye istek at
def api_post(data):
    try:
        response = requests.post(API_URL, data=data, timeout=5)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ API hatası: {str(e)}"

@bot.event
async def on_ready():
    print(f"[+] Bot giriş yaptı: {bot.user}")

@bot.command()
async def ban(ctx, username: str):
    result = api_post({'token': API_TOKEN, 'action': 'ban', 'username': username})
    msg = await ctx.send(result)
    await delete_after(ctx, msg)

@bot.command()
async def unban(ctx, username: str):
    result = api_post({'token': API_TOKEN, 'action': 'unban', 'username': username})
    msg = await ctx.send(result)
    await delete_after(ctx, msg)

@bot.command()
async def reset(ctx, username: str):
    result = api_post({'token': API_TOKEN, 'action': 'reset', 'username': username})
    msg = await ctx.send(result)
    await delete_after(ctx, msg)

@bot.command()
async def create(ctx, _, member: discord.Member):
    result = api_post({'token': API_TOKEN, 'action': 'create', 'username': member.name})
    msg = await ctx.send(result)
    await delete_after(ctx, msg)

@bot.command()
async def listkeys(ctx):
    result = api_post({'token': API_TOKEN, 'action': 'listkeys'})
    msg = await ctx.send(f"📋 Key Listesi:\n```{result}```")
    await delete_after(ctx, msg)

@bot.command()
async def delete(ctx, key: str):
    result = api_post({'token': API_TOKEN, 'action': 'delete', 'key': key})
    msg = await ctx.send(result)
    await delete_after(ctx, msg)

bot.run(TOKEN)
