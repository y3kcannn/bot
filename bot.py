import discord
from discord.ext import commands
import requests
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

API_URL = "https://midnightponywka.com/loader/discord/api.php"

async def send_and_delete(ctx, message):
    msg = await ctx.send(message)
    await asyncio.sleep(5)
    await msg.delete()
    await ctx.message.delete()

@bot.event
async def on_ready():
    print(f"[+] Bot giriş yaptı: {bot.user}")

@bot.command()
async def ban(ctx, username: str):
    data = {"action": "ban", "username": username}
    r = requests.post(API_URL, data=data)
    if r.ok and "success" in r.text.lower():
        await send_and_delete(ctx, f"🔨 `{username}` başarıyla banlandı!")
    else:
        await send_and_delete(ctx, f"❌ Ban işlemi başarısız!")

@bot.command()
async def unban(ctx, username: str):
    data = {"action": "unban", "username": username}
    r = requests.post(API_URL, data=data)
    if r.ok and "success" in r.text.lower():
        await send_and_delete(ctx, f"✅ `{username}` başarıyla unbanlandı!")
    else:
        await send_and_delete(ctx, f"❌ Unban işlemi başarısız!")

@bot.command()
async def create(ctx, mention: discord.Member):
    data = {"action": "create"}
    r = requests.post(API_URL, data=data)
    if r.ok and r.text.strip():
        key = r.text.strip()
        try:
            await mention.send(f"🔑 Key'in: `{key}`\nSite: https://midnightponywka.com")
            await send_and_delete(ctx, f"📩 Key gönderildi: {mention.mention}")
        except discord.Forbidden:
            await send_and_delete(ctx, "❌ DM gönderilemedi, kullanıcının gizliliği kapalı.")
    else:
        await send_and_delete(ctx, "❌ Key oluşturulamadı.")

@bot.command()
async def delete(ctx, key: str):
    data = {"action": "delete", "key": key}
    r = requests.post(API_URL, data=data)
    if r.ok and "success" in r.text.lower():
        await send_and_delete(ctx, f"🗑️ `{key}` silindi.")
    else:
        await send_and_delete(ctx, f"❌ Key silinemedi.")

@bot.command()
async def reset(ctx, username: str):
    data = {"action": "reset", "username": username}
    r = requests.post(API_URL, data=data)
    if r.ok and "success" in r.text.lower():
        await send_and_delete(ctx, f"🔄 `{username}` sıfırlandı.")
    else:
        await send_and_delete(ctx, "❌ Reset işlemi başarısız.")

@bot.command()
async def listkeys(ctx):
    data = {"action": "listkeys"}
    r = requests.post(API_URL, data=data)
    if r.ok:
        try:
            await ctx.author.send(f"📋 Key Listesi:\n```\n{r.text.strip()}\n```")
            await send_and_delete(ctx, "✅ Key listesi DM'den gönderildi.")
        except discord.Forbidden:
            await send_and_delete(ctx, "❌ DM gönderilemedi, kullanıcı gizliliği kapalı.")
    else:
        await send_and_delete(ctx, "❌ Liste alınamadı.")

@bot.command()
async def stats(ctx):
    data = {"action": "stats"}
    r = requests.post(API_URL, data=data)
    if r.ok:
        await send_and_delete(ctx, f"📊 {r.text.strip()}")
    else:
        await send_and_delete(ctx, "❌ İstatistik alınamadı.")

# Bot tokenini buraya yaz veya çevre değişkeni kullan
bot.run(os.getenv("DISCORD_TOKEN"))  # ya da doğrudan token: bot.run("TOKEN")
