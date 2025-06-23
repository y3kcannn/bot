import discord
from discord.ext import commands
import requests
import os
import asyncio
import time

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
API_TOKEN = "ADMIN_API_SECRET_TOKEN_2024"
BASE_URL = "https://midnightponywka.com/index.php?api=1&token=" + API_TOKEN

ALLOWED_CHANNEL_ID = 1385706278357303356  # Sadece bu kanalda çalışacak

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

start_time = time.time()

def is_authorized(ctx):
    return ctx.channel.id == ALLOWED_CHANNEL_ID

def embed_msg(title, description, color=0x2F3136):
    return discord.Embed(title=title, description=description, color=color)

@bot.event
async def on_ready():
    print(f"[+] Bot aktif: {bot.user}")

@bot.command()
async def ping(ctx):
    if not is_authorized(ctx): return
    await ctx.send("\U0001F3D3 Pong! Bot çalışıyor.")

@bot.command()
async def uptime(ctx):
    if not is_authorized(ctx): return
    uptime_sec = int(time.time() - start_time)
    m, s = divmod(uptime_sec, 60)
    h, m = divmod(m, 60)
    await ctx.send(f"⏱️ Uptime: {h} saat {m} dakika {s} saniye")

@bot.command()
async def key(ctx):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=generate-key")
    data = r.json()
    if data["status"] == "success":
        await ctx.send(f"✅ Yeni Key: 🔐 Gizli: ||`{data['data']['key']}`||")
    else:
        await ctx.send(f"❌ Hata: {data['message']}")

@bot.command()
async def deletekey(ctx, key):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=delete-key", data={"key": key})
    data = r.json()
    await ctx.send(f"🔑 Key Silme: {data['message']}")

@bot.command()
async def keylist(ctx):
    if not is_authorized(ctx): return
    keys = requests.get("https://midnightponywka.com/data/keys.txt").text.splitlines()[:20]
    await ctx.send("🔑 İlk 20 Key:\n" + "\n".join(f"🔑 ||`{k}`||" for k in keys))

@bot.command()
async def ban(ctx, username):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=ban", data={"username": username})
    data = r.json()
    await ctx.send(f"🔨 Ban İşlemi: {data['message']}")

@bot.command()
async def unban(ctx, username):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=unban", data={"username": username})
    data = r.json()
    await ctx.send(f"🔓 Unban İşlemi: {data['message']}")

@bot.command()
async def userlist(ctx):
    if not is_authorized(ctx): return
    banned = requests.get("https://midnightponywka.com/data/user.txt").text.splitlines()
    if banned:
        await ctx.send("❌ Banlı Kullanıcılar:\n" + "\n".join(f"🔸 {u}" for u in banned[:20]))
    else:
        await ctx.send("✅ Temiz Liste: Hiçbir kullanıcı banlı değil.")

@bot.command()
async def reset(ctx):
    if not is_authorized(ctx): return
    r = requests.get(BASE_URL + "&action=reset")
    data = r.json()
    await ctx.send(f"♻️ Sistem Sıfırlandı: {data['message']}")

@bot.command()
async def version(ctx, new_version=None):
    if not is_authorized(ctx): return
    if new_version:
        r = requests.post(BASE_URL + "&action=update-version", data={"version": new_version})
        await ctx.send(f"🔁 Versiyon Güncellendi: `{new_version}`")
    else:
        r = requests.get(BASE_URL + "&action=version")
        v = r.json()["data"]["version"]
        await ctx.send(f"🪩 Mevcut Versiyon: `{v}`")

@bot.command()
async def stats(ctx):
    if not is_authorized(ctx): return
    r = requests.get(BASE_URL + "&action=stats")
    data = r.json()["data"]
    description = (
        f"🔑 **Toplam:** {data['total_keys']}\n"
        f"📅 **Kullanılan:** {data['used_keys']}\n"
        f"📆 **Kullanılmamış:** {data['unused_keys']}\n"
        f"❌ **Banlı Kullanıcı:** {data['banned_users']}\n"
        f"🪩 **Sürüm:** {data['version']}"
    )
    await ctx.send("📊 Sistem Durumu:\n" + description)

@bot.command()
async def auth(ctx, key):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=key-login", data={"key": key})
    data = r.json()
    await ctx.send(f"🔐 Key Doğrulama: {data['message']}")

@bot.command()
async def logs(ctx):
    if not is_authorized(ctx): return
    log_raw = requests.get("https://midnightponywka.com/data/system.log").text.splitlines()
    log_text = "\n".join(log_raw[-10:])
    await ctx.send(f"📝 Son 10 Log:\n```\n{log_text}\n```")

@bot.command(name="komut")
async def command_list(ctx):
    if not is_authorized(ctx): return
    await ctx.send(
        "📘 Komut Listesi:\n"
        "`!ping` - Botun durumu\n"
        "`!uptime` - Açık kalma süresi\n"
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

bot.run(DISCORD_TOKEN)
