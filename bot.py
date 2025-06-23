import discord
from discord.ext import commands
import requests
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

API_URL = "https://midnightponywka.com/loader/discord/api.php"

async def delete_after(ctx, msg):
    await asyncio.sleep(5)
    await msg.delete()
    await ctx.message.delete()

async def send_api_request(data):
    try:
        response = requests.post(API_URL, data=data)
        return response.text.strip()
    except Exception as e:
        return f"API Hatası: {e}"

@bot.event
async def on_ready():
    print(f"[+] Bot giriş yaptı: {bot.user}")

@bot.command()
async def ban(ctx, username: str):
    result = await send_api_request({'type': 'ban', 'username': username})
    msg = await ctx.send(f"`{username}` başarıyla banlandı! 🔨" if "Success" in result else f"❌ Ban başarısız: {result}")
    await delete_after(ctx, msg)

@bot.command()
async def unban(ctx, username: str):
    result = await send_api_request({'type': 'unban', 'username': username})
    msg = await ctx.send(f"`{username}` başarıyla unbanlandı ✅" if "Success" in result else f"❌ Unban başarısız: {result}")
    await delete_after(ctx, msg)

@bot.command()
async def create(ctx, _, member: discord.Member):
    result = await send_api_request({'type': 'create', 'username': member.name})
    msg = await ctx.send(f"🔑 `{member.name}` için key oluşturuldu: `{result}`" if "Success" not in result else result)
    await delete_after(ctx, msg)

@bot.command()
async def reset(ctx, username: str):
    result = await send_api_request({'type': 'reset', 'username': username})
    msg = await ctx.send(f"`{username}` kullanımı sıfırlandı 🔁" if "Success" in result else f"❌ Sıfırlama başarısız: {result}")
    await delete_after(ctx, msg)

@bot.command()
async def listkeys(ctx):
    result = await send_api_request({'type': 'list'})
    msg = await ctx.send(f"📋 Key Listesi:\n```{result}```")
    await delete_after(ctx, msg)

@bot.command()
async def delete(ctx, key: str):
    result = await send_api_request({'type': 'delete', 'key': key})
    msg = await ctx.send(f"`{key}` silindi 🗑️" if "Success" in result else f"❌ Silinemedi: {result}")
    await delete_after(ctx, msg)

@bot.command()
async def stats(ctx):
    result = await send_api_request({'type': 'stats'})
    msg = await ctx.send(f"📊 İstatistik:\n```{result}```")
    await delete_after(ctx, msg)

bot.run(TOKEN)
