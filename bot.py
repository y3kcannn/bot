import discord
from discord.ext import commands
import requests
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"[+] Bot giriş yaptı: {bot.user}")

@bot.command()
async def create(ctx, arg1: str, member: discord.Member = None):
    if arg1.lower() != "key" or member is None:
        await ctx.send("❗ Kullanım: `!create key @kullanıcı`")
        return

    url = "https://midnightponywka.com/loader/create_key.php"
    data = {
        "secret": "123456",  # PHP tarafındaki sabit gizli anahtar
        "username": member.name
    }

    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            key = response.text.strip()
            msg = await ctx.send(f"🔑 `{member.name}` için key oluşturuldu:\n```{key}```")
            await asyncio.sleep(5)
            await ctx.message.delete()
            await msg.delete()
        else:
            await ctx.send(f"❌ Key oluşturulamadı: `{response.text}`")
    except Exception as e:
        await ctx.send(f"⚠️ Sunucu hatası: `{str(e)}`")

# BOT TOKEN
bot.run("BOT_TOKENİNİ_BURAYA_YAPIŞTIR")
