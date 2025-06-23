import discord
from discord.ext import commands
import requests
import os
import asyncio
import time

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
API_TOKEN = "ADMIN_API_SECRET_TOKEN_2024"
BASE_URL = "https://midnightponywka.com/index.php?api=1&token=" + API_TOKEN

ALLOWED_USER_IDS = [
    389844191263457291,  # schwarz_44
    1065720631401926768  # midnightponywka
]
ALLOWED_CHANNEL_ID = 1244284695103637654  # Sadece bu kanalda çalışacak

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

start_time = time.time()

def is_authorized(ctx):
    return ctx.channel.id == ALLOWED_CHANNEL_ID and ctx.author.id in ALLOWED_USER_IDS

async def delete_after(ctx, msg, delay=30):
    await asyncio.sleep(delay)
    await ctx.message.delete()
    await msg.delete()

def embed_msg(title, description, color=0x2F3136):
    return discord.Embed(title=title, description=description, color=color)

@bot.event
async def on_ready():
    print(f"[+] Bot aktif: {bot.user}")

async def handle_permission(ctx):
    msg = await ctx.send(embed=embed_msg("🚫 Yetkisiz", "Nice try, daddy 👀"))
    await delete_after(ctx, msg)

@bot.command()
async def ping(ctx):
    if not is_authorized(ctx): return await handle_permission(ctx)
    embed = embed_msg("🏓 Pong!", "Bot çalışıyor.")
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def uptime(ctx):
    if not is_authorized(ctx): return await handle_permission(ctx)
    uptime_sec = int(time.time() - start_time)
    m, s = divmod(uptime_sec, 60)
    h, m = divmod(m, 60)
    embed = embed_msg("⏱️ Uptime", f"{h} saat {m} dakika {s} saniye")
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def key(ctx):
    if not is_authorized(ctx): return await handle_permission(ctx)
    r = requests.post(BASE_URL + "&action=generate-key")
    data = r.json()
    if data["status"] == "success":
        embed = embed_msg("✅ Yeni Key", f"🔒 Gizli: ||`{data['data']['key']}`||")
    else:
        embed = embed_msg("❌ Hata", data['message'], color=0xFF0000)
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def deletekey(ctx, key):
    if not is_authorized(ctx): return await handle_permission(ctx)
    r = requests.post(BASE_URL + "&action=delete-key", data={"key": key})
    data = r.json()
    embed = embed_msg("🔑 Key Silme", data['message'])
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def keylist(ctx):
    if not is_authorized(ctx): return await handle_permission(ctx)
    keys = requests.get("https://midnightponywka.com/data/keys.txt").text.splitlines()[:20]
    embed = embed_msg("🗝️ İlk 20 Key", "\n".join(f"🔑 ||`{k}`||" for k in keys))
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def ban(ctx, username):
    if not is_authorized(ctx): return await handle_permission(ctx)
    r = requests.post(BASE_URL + "&action=ban", data={"username": username})
    data = r.json()
    embed = embed_msg("🔨 Ban İşlemi", data['message'])
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def unban(ctx, username):
    if not is_authorized(ctx): return await handle_permission(ctx)
    r = requests.post(BASE_URL + "&action=unban", data={"username": username})
    data = r.json()
    embed = embed_msg("🔓 Unban İşlemi", data['message'])
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def userlist(ctx):
    if not is_authorized(ctx): return await handle_permission(ctx)
    banned = requests.get("https://midnightponywka.com/data/user.txt").text.splitlines()
    if banned:
        embed = embed_msg("🚫 Banlı Kullanıcılar", "\n".join(f"🔸 {u}" for u in banned[:20]))
    else:
        embed = embed_msg("✅ Temiz Liste", "Hiçbir kullanıcı banlı değil.")
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def reset(ctx):
    if not is_authorized(ctx): return await handle_permission(ctx)
    r = requests.get(BASE_URL + "&action=reset")
    data = r.json()
    embed = embed_msg("♻️ Sistem Sıfırlandı", data['message'])
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def version(ctx, new_version=None):
    if not is_authorized(ctx): return await handle_permission(ctx)
    if new_version:
        r = requests.post(BASE_URL + "&action=update-version", data={"version": new_version})
        embed = embed_msg("🔁 Versiyon Güncellendi", f"Yeni versiyon: `{new_version}`")
    else:
        r = requests.get(BASE_URL + "&action=version")
        v = r.json()["data"]["version"]
        embed = embed_msg("🧩 Mevcut Versiyon", f"`{v}`")
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def stats(ctx):
    if not is_authorized(ctx): return await handle_permission(ctx)
    r = requests.get(BASE_URL + "&action=stats")
    data = r.json()["data"]
    description = (
        f"🔑 **Toplam:** {data['total_keys']}\n"
        f"📥 **Kullanılan:** {data['used_keys']}\n"
        f"📤 **Kullanılmamış:** {data['unused_keys']}\n"
        f"🚫 **Banlı Kullanıcı:** {data['banned_users']}\n"
        f"🧩 **Sürüm:** {data['version']}"
    )
    embed = embed_msg("📊 Sistem Durumu", description)
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def auth(ctx, key):
    if not is_authorized(ctx): return await handle_permission(ctx)
    r = requests.post(BASE_URL + "&action=key-login", data={"key": key})
    data = r.json()
    color = 0x00FF00 if data['status'] == 'success' else 0xFF0000
    embed = embed_msg("🔐 Key Doğrulama", data['message'], color)
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def logs(ctx):
    if not is_authorized(ctx): return await handle_permission(ctx)
    log_raw = requests.get("https://midnightponywka.com/data/system.log").text.splitlines()
    embed = embed_msg("📝 Son 10 Log", "```\n" + "\n".join(log_raw[-10:]) + "\n```")
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command(name="komut")
async def command_list(ctx):
    if not is_authorized(ctx): return await handle_permission(ctx)
    embed = embed_msg("📘 Komut Listesi", (
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
    ))
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

bot.run(DISCORD_TOKEN)
