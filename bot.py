import discord
from discord.ext import commands
import requests
import os
import asyncio
import time

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
API_TOKEN = "ADMIN_API_SECRET_TOKEN_2024"
BASE_URL = "https://midnightponywka.com/index.php?api=1&token=" + API_TOKEN

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

@bot.command()
async def ping(ctx):
    if not is_authorized(ctx): return
    msg = await ctx.send(embed=embed_msg("🏓 Pong!", "Bot çalışıyor."))
    await delete_after(ctx, msg)

@bot.command()
async def uptime(ctx):
    if not is_authorized(ctx): return
    uptime_sec = int(time.time() - start_time)
    m, s = divmod(uptime_sec, 60)
    h, m = divmod(m, 60)
    msg = await ctx.send(embed=embed_msg("⏱️ Uptime", f"`{h}` saat `{m}` dakika `{s}` saniye"))
    await delete_after(ctx, msg)

@bot.command()
async def key(ctx):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=generate-key")
    data = r.json()
    if data["status"] == "success":
        msg = await ctx.send(embed=embed_msg("✅ Yeni Key", f"||`{data['data']['key']}`||"))
    else:
        msg = await ctx.send(embed=embed_msg("❌ Hata", data['message']))
    await delete_after(ctx, msg)

@bot.command()
async def deletekey(ctx, key):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=delete-key", data={"key": key})
    data = r.json()
    msg = await ctx.send(embed=embed_msg("🗑️ Key Silindi", data['message']))
    await delete_after(ctx, msg)

@bot.command()
async def keylist(ctx):
    if not is_authorized(ctx): return
    r = requests.get(BASE_URL + "&action=key-list")
    data = r.json()
    keys = data["data"][:20]
    msg = await ctx.send(embed=embed_msg("📜 İlk 20 Key", "\n".join(f"||`{k}`||" for k in keys)))
    await delete_after(ctx, msg)

@bot.command()
async def ban(ctx, username):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=ban", data={"username": username})
    data = r.json()
    msg = await ctx.send(embed=embed_msg("🚫 Banlandı", data['message']))
    await delete_after(ctx, msg)

@bot.command()
async def unban(ctx, username):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=unban", data={"username": username})
    data = r.json()
    msg = await ctx.send(embed=embed_msg("🔓 Unban", data['message']))
    await delete_after(ctx, msg)

@bot.command()
async def userlist(ctx):
    if not is_authorized(ctx): return
    r = requests.get(BASE_URL + "&action=banned-users")
    data = r.json()
    banned = data["data"]
    if banned:
        msg = await ctx.send(embed=embed_msg("📛 Banlı Kullanıcılar", "\n".join(f"🔸 `{u}`" for u in banned[:20])))
    else:
        msg = await ctx.send(embed=embed_msg("✅ Temiz", "Hiçbir kullanıcı banlı değil."))
    await delete_after(ctx, msg)

@bot.command()
async def reset(ctx):
    if not is_authorized(ctx): return
    r = requests.get(BASE_URL + "&action=reset")
    data = r.json()
    msg = await ctx.send(embed=embed_msg("♻️ Sistem Sıfırlandı", data['message']))
    await delete_after(ctx, msg)

@bot.command()
async def version(ctx, new_version=None):
    if not is_authorized(ctx): return
    if new_version:
        r = requests.post(BASE_URL + "&action=update-version", data={"version": new_version})
        msg = await ctx.send(embed=embed_msg("🔁 Versiyon Güncellendi", f"Yeni sürüm: `{new_version}`"))
    else:
        r = requests.get(BASE_URL + "&action=version")
        v = r.json()["data"]["version"]
        msg = await ctx.send(embed=embed_msg("🪩 Mevcut Versiyon", f"`{v}`"))
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
    msg = await ctx.send(embed=embed_msg("📊 Sistem Durumu", description))
    await delete_after(ctx, msg)

@bot.command()
async def auth(ctx, key):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=key-login", data={"key": key})
    data = r.json()
    msg = await ctx.send(embed=embed_msg("🔐 Key Doğrulama", data['message']))
    await delete_after(ctx, msg)

@bot.command()
async def logs(ctx):
    if not is_authorized(ctx): return
    r = requests.get(BASE_URL + "&action=logs")
    data = r.json()
    log_raw = data["data"]
    log_text = "\n".join(log_raw[-10:])
    embed = embed_msg("📝 Son 10 Log", f"```{log_text}```")
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command(name="komut")
async def command_list(ctx):
    if not is_authorized(ctx): return
    komutlar = (
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
    msg = await ctx.send(embed=embed_msg("📘 Komut Listesi", komutlar))
    await delete_after(ctx, msg)

bot.run(DISCORD_TOKEN)
