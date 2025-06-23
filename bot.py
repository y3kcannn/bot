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

def embed_msg(title, description, color=0x2F3136):
    return discord.Embed(title=title, description=description, color=color)

@bot.event
async def on_ready():
    print(f"[+] Bot aktif: {bot.user}")

@bot.command()
async def key(ctx):
    r = requests.post(BASE_URL + "&action=generate-key")
    data = r.json()
    if data["status"] == "success":
        embed = embed_msg("✅ Yeni Key", f"`{data['data']['key']}`")
    else:
        embed = embed_msg("❌ Hata", data['message'], color=0xFF0000)
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def deletekey(ctx, key):
    r = requests.post(BASE_URL + "&action=delete-key", data={"key": key})
    data = r.json()
    embed = embed_msg("🔑 Key Silme", data['message'])
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def keylist(ctx):
    keys = requests.get("https://midnightponywka.com/data/keys.txt").text.splitlines()[:20]
    embed = embed_msg("🗝️ İlk 20 Key", "\n".join(f"`{k}`" for k in keys))
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def ban(ctx, username):
    r = requests.post(BASE_URL + "&action=ban", data={"username": username})
    data = r.json()
    embed = embed_msg("🔨 Ban İşlemi", data['message'])
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def unban(ctx, username):
    r = requests.post(BASE_URL + "&action=unban", data={"username": username})
    data = r.json()
    embed = embed_msg("🔓 Unban İşlemi", data['message'])
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def userlist(ctx):
    banned = requests.get("https://midnightponywka.com/data/user.txt").text.splitlines()
    if banned:
        embed = embed_msg("🚫 Banlı Kullanıcılar", "\n".join(f"🔸 {u}" for u in banned[:20]))
    else:
        embed = embed_msg("✅ Temiz Liste", "Hiçbir kullanıcı banlı değil.")
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def reset(ctx):
    r = requests.get(BASE_URL + "&action=reset")
    data = r.json()
    embed = embed_msg("♻️ Sistem Sıfırlandı", data['message'])
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def version(ctx, new_version=None):
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
    r = requests.post(BASE_URL + "&action=key-login", data={"key": key})
    data = r.json()
    color = 0x00FF00 if data['status'] == 'success' else 0xFF0000
    embed = embed_msg("🔐 Key Doğrulama", data['message'], color)
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def logs(ctx):
    log_raw = requests.get("https://midnightponywka.com/data/system.log").text.splitlines()
    embed = embed_msg("📝 Son 10 Log", "```\n" + "\n".join(log_raw[-10:]) + "\n```")
    msg = await ctx.send(embed=embed)
    await delete_after(ctx, msg)

@bot.command()
async def komut(ctx):
    embed = embed_msg("📘 Komut Listesi", (
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
