import discord
from discord.ext import commands
import requests
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Ortam değişkeninden token çekme yerine doğrudan token koyabilirsin
TOKEN = "BURAYA_DISCORD_BOT_TOKENINI_YAZ"

@bot.event
async def on_ready():
    print(f"[+] Bot giriş yaptı: {bot.user}")

# Helper: 5 saniye sonra mesaj sil
async def delete_after(ctx, response):
    await asyncio.sleep(5)
    await response.delete()
    await ctx.message.delete()

@bot.command()
async def ban(ctx, username: str):
    url = "https://midnightponywka.com/loader/banned.php"
    data = {'username': username}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200 and "Success" in response.text:
            msg = await ctx.send(f"`{username}` başarıyla banlandı! 🔨")
        else:
            msg = await ctx.send(f"❌ Banlama başarısız: {response.text}")
    except Exception as e:
        msg = await ctx.send(f"⚠️ Hata oluştu: {str(e)}")
    await delete_after(ctx, msg)

@bot.command()
async def unban(ctx, username: str):
    url = "https://midnightponywka.com/loader/unban.php"
    data = {'username': username}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200 and "Success" in response.text:
            msg = await ctx.send(f"`{username}` başarıyla unbanlandı ✅")
        else:
            msg = await ctx.send(f"❌ Unban başarısız: {response.text}")
    except Exception as e:
        msg = await ctx.send(f"⚠️ Hata oluştu: {str(e)}")
    await delete_after(ctx, msg)

@bot.command()
async def create(ctx, _, member: discord.Member):
    url = "https://midnightponywka.com/loader/create_key.php"
    data = {'username': member.name}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            key = response.text.strip()
            msg = await ctx.send(f"🔑 `{member.name}` için key oluşturuldu: `{key}`")
        else:
            msg = await ctx.send(f"❌ Key oluşturulamadı: {response.text}")
    except Exception as e:
        msg = await ctx.send(f"⚠️ Hata oluştu: {str(e)}")
    await delete_after(ctx, msg)

@bot.command()
async def reset(ctx, username: str):
    url = "https://midnightponywka.com/loader/reset.php"
    data = {'username': username}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200 and "Success" in response.text:
            msg = await ctx.send(f"`{username}` için kullanım sıfırlandı 🔁")
        else:
            msg = await ctx.send(f"❌ Sıfırlama başarısız: {response.text}")
    except Exception as e:
        msg = await ctx.send(f"⚠️ Hata oluştu: {str(e)}")
    await delete_after(ctx, msg)

@bot.command()
async def listkeys(ctx):
    url = "https://midnightponywka.com/loader/list_keys.php"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            msg = await ctx.send(f"📋 Mevcut Keyler:\n```{response.text.strip()}```")
        else:
            msg = await ctx.send("❌ Key listesi alınamadı.")
    except Exception as e:
        msg = await ctx.send(f"⚠️ Hata oluştu: {str(e)}")
    await delete_after(ctx, msg)

@bot.command()
async def delete(ctx, key: str):
    url = "https://midnightponywka.com/loader/delete_key.php"
    data = {'key': key}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200 and "Success" in response.text:
            msg = await ctx.send(f"`{key}` başarıyla silindi 🗑️")
        else:
            msg = await ctx.send(f"❌ Silinemedi: {response.text}")
    except Exception as e:
        msg = await ctx.send(f"⚠️ Hata oluştu: {str(e)}")
    await delete_after(ctx, msg)

@bot.command()
async def stats(ctx):
    url = "https://midnightponywka.com/loader/stats.php"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            msg = await ctx.send(f"📊 Key İstatistikleri:\n```{response.text.strip()}```")
        else:
            msg = await ctx.send("❌ İstatistik alınamadı.")
    except Exception as e:
        msg = await ctx.send(f"⚠️ Hata oluştu: {str(e)}")
    await delete_after(ctx, msg)

bot.run(TOKEN)
