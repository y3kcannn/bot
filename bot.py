import discord
from discord.ext import commands
import requests
import os
import asyncio

# Railway üzerinden gelen environment değişkenini al
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
API_TOKEN = "ADMIN_API_SECRET_TOKEN_2024"
BASE_URL = "https://midnightponywka.com/index.php?api=1&token=" + API_TOKEN

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def delete_after(ctx, msg):
    await asyncio.sleep(5)
    await ctx.message.delete()
    await msg.delete()

@bot.event
async def on_ready():
    print(f"[+] Bot aktif: {bot.user}")

@bot.command()
async def key(ctx):
    r = requests.post(BASE_URL + "&action=generate-key")
    data = r.json()
    if data["status"] == "success":
        msg = await ctx.send(f"✅ Key: `{data['data']['key']}`")
    else:
        msg = await ctx.send(f"❌ Hata: {data['message']}")
    await delete_after(ctx, msg)

@bot.command()
async def deletekey(ctx, key):
    r = requests.post(BASE_URL + "&action=delete-key", data={"key": key})
    data = r.json()
    msg = await ctx.send(f"{data['message']}")
    await delete_after(ctx, msg)

@bot.command()
async def keylist(ctx):
    keys = requests.get("https://midnightponywka.com/data/keys.txt").text.splitlines()[:20]
    msg = await ctx.send("🗝️ İlk 20 key:\n" + "\n".join(f"`{k}`" for k in keys))
    await delete_after(ctx, msg)

@bot.command()
async def ban(ctx, username):
    r = requests.post(BASE_URL + "&action=ban", data={"username": username})
    data = r.json()
    msg = await ctx.send(f"{data['message']}")
    await delete_after(ctx, msg)

@bot.command()
async def unban(ctx, username):
    r = requests.post(BASE_URL + "&action=unban", data={"username": username})
    data = r.json()
    msg = await ctx.send(f"{data['message']}")
    await delete_after(ctx, msg)

@bot.command()
async def userlist(ctx):
    banned = requests.get("https://midnightponywka.com/data/user.txt").text.splitlines()
    if banned:
        msg = await ctx.send("Banlı kullanıcılar:\n" + "\n".join(f"🚫 {u}" for u in banned[:20]))
    else:
        msg = await ctx.send("✅ Hiçbir kullanıcı banlı değil.")
    await delete_after(ctx, msg)

@bot.command()
async def reset(ctx):
    r = requests.get(BASE_URL + "&action=reset")
    data = r.json()
    msg = await ctx.send(f"♻️ {data['message']}")
    await delete_after(ctx, msg)

@bot.command()
async def version(ctx, new_version=None):
    if new_version:
        r = requests.post(BASE_URL + "&action=update-version", data={"version": new_version})
        msg = await ctx.send("🔁 Versiyon güncellendi.")
    else:
        r = requests.get(BASE_URL + "&action=version")
        v = r.json()["data"]["version"]
        msg = await ctx.send(f"🧩 Mevcut versiyon: `{v}`")
    await delete_after(ctx, msg)

@bot.command()
async def stats(ctx):
    r = requests.get(BASE_URL + "&action=stats")
    data = r.json()["data"]
    msg = await ctx.send(
        f"📊 **Sistem Durumu**\n"
        f"🔑 Total: {data['total_keys']} | Used: {data['used_keys']} | Unused: {data['unused_keys']}\n"
        f"🚫 Banlı kullanıcı: {data['banned_users']}\n"
        f"🧩 Sürüm: {data['version']}"
    )
    await delete_after(ctx, msg)

@bot.command()
async def auth(ctx, key):
    r = requests.post(BASE_URL + "&action=key-login", data={"key": key})
    data = r.json()
    msg = await ctx.send(f"🔐 {data['message']}")
    await delete_after(ctx, msg)

@bot.command()
async def logs(ctx):
    log_raw = requests.get("https://midnightponywka.com/data/system.log").text.splitlines()
    msg = await ctx.send(f"📝 Son 10 log:\n```\n" + "\n".join(log_raw[-10:]) + "\n```")
    await delete_after(ctx, msg)

@bot.command()
async def komut(ctx):
    msg = await ctx.send(
        "📘 **Komut Listesi:**\n"
        "`!key` - Yeni key üret\n"
        "`!deletekey <key>` - Key sil\n"
        "`!keylist` - Key listesini göster\n"
        "`!ban <kullanıcı>` - Kullanıcıyı banla\n"
        "`!unban <kullanıcı>` - Banı kaldır\n"
        "`!userlist` - Banlı kullanıcıları göster\n"
        "`!reset` - Sistemi sıfırla\n"
        "`!version [versiyon]` - Versiyonu göster/güncelle\n"
        "`!stats` - Sistem istatistikleri\n"
        "`!auth <key>` - Key doğrula\n"
        "`!logs` - Son logları göster"
    )
    await delete_after(ctx, msg)

bot.run(DISCORD_TOKEN)
