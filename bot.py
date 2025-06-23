import discord
from discord.ext import commands
import requests
import os
import asyncio
import time

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
API_TOKEN = "ADMIN_API_SECRET_TOKEN_2024"
BASE_URL = "https://midnightponywka.com/index.php?api=1&token=" + API_TOKEN

ALLOWED_CHANNEL_ID = 1244284695103637654  # Sadece bu kanalda çalışacak

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

start_time = time.time()

def is_authorized(ctx):
    return ctx.channel.id == ALLOWED_CHANNEL_ID

async def delete_after(ctx, msg, delay=30):
    await asyncio.sleep(delay)
    await ctx.message.delete()
    await msg.delete()

def embed_msg(title, description, color=0x2F3136):
    return discord.Embed(title=title, description=description, color=color)

@bot.event
async def on_ready():
    print(f"[+] Bot aktif: {bot.user}")

@bot.command()
async def ping(ctx):
    if not is_authorized(ctx): return
    embed = embed_msg("\ud83c\udfd3 Pong!", "Bot \u00e7al\u0131\u015f\u0131yor.")
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def uptime(ctx):
    if not is_authorized(ctx): return
    uptime_sec = int(time.time() - start_time)
    m, s = divmod(uptime_sec, 60)
    h, m = divmod(m, 60)
    embed = embed_msg("\u23f1\ufe0f Uptime", f"{h} saat {m} dakika {s} saniye")
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def key(ctx):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=generate-key")
    data = r.json()
    if data["status"] == "success":
        embed = embed_msg("\u2705 Yeni Key", f"\ud83d\udd10 Gizli: ||`{data['data']['key']}`||")
    else:
        embed = embed_msg("\u274c Hata", data['message'], color=0xFF0000)
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def deletekey(ctx, key):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=delete-key", data={"key": key})
    data = r.json()
    embed = embed_msg("\ud83d\udd11 Key Silme", data['message'])
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def keylist(ctx):
    if not is_authorized(ctx): return
    keys = requests.get("https://midnightponywka.com/data/keys.txt").text.splitlines()[:20]
    embed = embed_msg("\ud83d\udd11 \u0130lk 20 Key", "\n".join(f"\ud83d\udd11 ||`{k}`||" for k in keys))
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def ban(ctx, username):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=ban", data={"username": username})
    data = r.json()
    embed = embed_msg("\ud83d\udd28 Ban \u0130\u015flemi", data['message'])
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def unban(ctx, username):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=unban", data={"username": username})
    data = r.json()
    embed = embed_msg("\ud83d\udd13 Unban \u0130\u015flemi", data['message'])
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def userlist(ctx):
    if not is_authorized(ctx): return
    banned = requests.get("https://midnightponywka.com/data/user.txt").text.splitlines()
    if banned:
        embed = embed_msg("\u274c Banl\u0131 Kullan\u0131c\u0131lar", "\n".join(f"\ud83d\udd38 {u}" for u in banned[:20]))
    else:
        embed = embed_msg("\u2705 Temiz Liste", "Hi\u00e7bir kullan\u0131c\u0131 banl\u0131 de\u011fil.")
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def reset(ctx):
    if not is_authorized(ctx): return
    r = requests.get(BASE_URL + "&action=reset")
    data = r.json()
    embed = embed_msg("\u267b\ufe0f Sistem S\u0131f\u0131rland\u0131", data['message'])
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def version(ctx, new_version=None):
    if not is_authorized(ctx): return
    if new_version:
        r = requests.post(BASE_URL + "&action=update-version", data={"version": new_version})
        embed = embed_msg("\ud83d\udd01 Versiyon G\u00fcncellendi", f"Yeni versiyon: `{new_version}`")
    else:
        r = requests.get(BASE_URL + "&action=version")
        v = r.json()["data"]["version"]
        embed = embed_msg("\ud83e\udde9 Mevcut Versiyon", f"`{v}`")
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def stats(ctx):
    if not is_authorized(ctx): return
    r = requests.get(BASE_URL + "&action=stats")
    data = r.json()["data"]
    description = (
        f"\ud83d\udd11 **Toplam:** {data['total_keys']}\n"
        f"\ud83d\udcc5 **Kullan\u0131lan:** {data['used_keys']}\n"
        f"\ud83d\udcc6 **Kullan\u0131lmam\u0131\u015f:** {data['unused_keys']}\n"
        f"\u274c **Banl\u0131 Kullan\u0131c\u0131:** {data['banned_users']}\n"
        f"\ud83e\udde9 **S\u00fcr\u00fcm:** {data['version']}"
    )
    embed = embed_msg("\ud83d\udcca Sistem Durumu", description)
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def auth(ctx, key):
    if not is_authorized(ctx): return
    r = requests.post(BASE_URL + "&action=key-login", data={"key": key})
    data = r.json()
    color = 0x00FF00 if data['status'] == 'success' else 0xFF0000
    embed = embed_msg("\ud83d\udd10 Key Do\u011frulama", data['message'], color)
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def logs(ctx):
    if not is_authorized(ctx): return
    log_raw = requests.get("https://midnightponywka.com/data/system.log").text.splitlines()
    embed = embed_msg("\ud83d\udcdc Son 10 Log", "```\n" + "\n".join(log_raw[-10:]) + "\n```")
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command(name="komut")
async def command_list(ctx):
    if not is_authorized(ctx): return
    embed = embed_msg("\ud83d\udcd8 Komut Listesi", (
        "`!ping` - Botun durumu\n"
        "`!uptime` - A\u00e7\u0131k kalma s\u00fcresi\n"
        "`!key` - Yeni key \u00fcret\n"
        "`!deletekey <key>` - Key sil\n"
        "`!keylist` - Key listesini g\u00f6ster\n"
        "`!ban <kullan\u0131c\u0131>` - Kullan\u0131c\u0131y\u0131 banla\n"
        "`!unban <kullan\u0131c\u0131>` - Ban\u0131 kald\u0131r\n"
        "`!userlist` - Banl\u0131 kullan\u0131c\u0131lar\u0131 g\u00f6ster\n"
        "`!reset` - Sistemi s\u0131f\u0131rla\n"
        "`!version [versiyon]` - Versiyonu g\u00f6ster/g\u00fcncelle\n"
        "`!stats` - Sistem istatistikleri\n"
        "`!auth <key>` - Key do\u011frula\n"
        "`!logs` - Son loglar\u0131 g\u00f6ster"
    ))
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

bot.run(DISCORD_TOKEN)
