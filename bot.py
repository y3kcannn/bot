import discord
from discord.ext import commands
import requests
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"[+] Bot giriş yaptı: {bot.user}")

@bot.command()
async def ban(ctx, username: str):
    url = "https://midnightponywka.com/loader/banned.php"
    data = {'username': username}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200 and "Success" in response.text:
            await ctx.send(f"`{username}` başarıyla banlandı! 🚫")
        else:
            await ctx.send(f"❌ Banlama başarısız: {response.text}")
    except Exception as e:
        await ctx.send(f"⚠️ Hata oluştu: {str(e)}")

@bot.command()
async def unban(ctx, username: str):
    url = "https://midnightponywka.com/loader/unban.php"
    data = {'username': username}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200 and "Success" in response.text:
            await ctx.send(f"`{username}` başarıyla unbanlandı! ✅")
        else:
            await ctx.send(f"❌ Unban başarısız: {response.text}")
    except Exception as e:
        await ctx.send(f"⚠️ Hata oluştu: {str(e)}")

# Bot token'ı Railway'de environment olarak ayarlanmalı
bot.run(os.getenv("DISCORD_TOKEN"))
