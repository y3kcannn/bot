import discord
from discord.ext import commands
import requests
import os
import asyncio
import time

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
API_TOKEN = "ADMIN_API_SECRET_TOKEN_2024"
BASE_URL = "https://midnightponywka.com/index.php?api=1&token=" + API_TOKEN

BOT_TOKEN = "DISCORD_BOT_SECRET_TOKEN_2024_ULTRA_SECURE"
BOT_DATA_URL = f"https://midnightponywka.com/bot-data.php?bot_token={BOT_TOKEN}"

ALLOWED_CHANNEL_ID = 1385706278357303356

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

async def delete_after(ctx, msg, delay=30):
    await asyncio.sleep(delay)
    await msg.delete()
    await ctx.message.delete()

# ---------------------- Komutlar ----------------------

@bot.command()
async def ping(ctx):
    if not is_authorized(ctx): return
    msg = await ctx.send("🏓 **Pong!** Bot çalışıyor.")
    await delete_after(ctx, msg)

@bot.command()
async def uptime(ctx):
    if not is_authorized(ctx): return
    uptime_sec = int(time.time() - start_time)
    m, s = divmod(uptime_sec, 60)
    h, m = divmod(m, 60)
    msg = await ctx.send(f"⏱️ **Uptime:** `{h}` saat `{m}` dakika `{s}` saniye")
    await delete_after(ctx, msg)

@bot.command()
async def key(ctx):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=generate-key")
    data = r.json()
    if data["status"] == "success":
        msg = await ctx.send(f"✅ **Yeni Key:** ||`{data['data']['key']}`||")
    else:
        msg = await ctx.send(f"❌ **Hata:** {data['message']}")
    await delete_after(ctx, msg)

@bot.command()
async def deletekey(ctx, key):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=delete-key", data={"key": key})
    data = r.json()
    msg = await ctx.send(f"🗑️ **Key Silindi:** {data['message']}")
    await delete_after(ctx, msg)

@bot.command()
async def keylist(ctx):
    if not is_authorized(ctx): return
    r = requests.get(BOT_DATA_URL + "&file=keys")
    data = r.json()
    if data["status"] == "success":
        keys = data["data"]["lines"][:20]
        msg = await ctx.send("📜 **İlk 20 Key:**\n" + "\n".join(f"||`{k}`||" for k in keys))
    else:
        msg = await ctx.send(f"❌ **Hata:** {data['message']}")
    await delete_after(ctx, msg)

@bot.command()
async def ban(ctx, username):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=ban", data={"username": username})
    data = r.json()
    msg = await ctx.send(f"🚫 **Banlandı:** {data['message']}")
    await delete_after(ctx, msg)

@bot.command()
async def unban(ctx, username):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=unban", data={"username": username})
    data = r.json()
    msg = await ctx.send(f"🔓 **Unban:** {data['message']}")
    await delete_after(ctx, msg)

@bot.command()
async def userlist(ctx):
    if not is_authorized(ctx): return
    r = requests.get(BOT_DATA_URL + "&file=users")
    data = r.json()
    if data["status"] == "success":
        users = data["data"]["lines"]
        if users:
            msg = await ctx.send("📛 **Banlı Kullanıcılar:**\n" + "\n".join(f"🔸 `{u}`" for u in users[:20]))
        else:
            msg = await ctx.send("✅ **Hiçbir kullanıcı banlı değil.**")
    else:
        msg = await ctx.send(f"❌ **Hata:** {data['message']}")
    await delete_after(ctx, msg)

@bot.command()
async def reset(ctx):
    if not is_authorized(ctx): return
    r = requests.get(BASE_URL + "&action=reset")
    data = r.json()
    msg = await ctx.send(f"♻️ **Sistem sıfırlandı:** {data['message']}")
    await delete_after(ctx, msg)

@bot.command()
async def version(ctx, new_version=None):
    if not is_authorized(ctx): return
    if new_version:
        r = requests.post(BASE_URL + "&action=update-version", data={"version": new_version})
        msg = await ctx.send(f"🔁 **Versiyon güncellendi:** `{new_version}`")
    else:
        r = requests.get(BASE_URL + "&action=version")
        v = r.json()["data"]["version"]
        msg = await ctx.send(f"🪩 **Mevcut Versiyon:** `{v}`")
    await delete_after(ctx, msg)

@bot.command()
async def stats(ctx):
    if not is_authorized(ctx): return
    r = requests.get(BASE_URL + "&action=stats")
    data = r.json()["data"]
    description = (
        f"🔑 **Toplam Key:** `{data['total_keys']}`\n"
        f"📅 **Kullanılan:** `{data['used_keys']}`\n"
        f"📆 **Kullanılmamış:** `{data['unused_keys']}`\n"
        f"❌ **Banlı Kullanıcılar:** `{data['banned_users']}`\n"
        f"🪩 **Sürüm:** `{data['version']}`"
    )
    msg = await ctx.send("📊 **Sistem Durumu:**\n" + description)
    await delete_after(ctx, msg)

@bot.command()
async def auth(ctx, key):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=key-login", data={"key": key})
    data = r.json()
    msg = await ctx.send(f"🔐 **Key Doğrulama:** {data['message']}")
    await delete_after(ctx, msg)

@bot.command()
async def logs(ctx):
    if not is_authorized(ctx): return
    r = requests.get(BOT_DATA_URL + "&file=logs")
    data = r.json()
    if data["status"] == "success":
        logs = data["data"]["lines"][-10:]
        log_text = "\n".join(logs)
        msg = await ctx.send(f"📝 **Son 10 Log:**\n```{log_text}```")
    else:
        msg = await ctx.send(f"❌ **Hata:** {data['message']}")
    await delete_after(ctx, msg)

@bot.command(name="komut")
async def command_list(ctx):
    if not is_authorized(ctx): return
    msg = await ctx.send(
        "📘 **Komut Listesi:**\n"
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
    await delete_after(ctx, msg)

bot.run(DISCORD_TOKEN)
