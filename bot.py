import discord
from discord.ext import commands
import requests
import os
import time
import hmac
import hashlib
import uuid

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("ℹ️ python-dotenv yüklü değil, Railway ortamında çalıştığı varsayılıyor.")

# Ortam değişkenlerinden gizli verileri al
TOKEN = os.environ.get("DISCORD_TOKEN")
API_URL = "https://midnightponywka.com/api.php"
API_TOKEN = os.environ.get("API_TOKEN")
HMAC_SECRET = os.environ.get("HMAC_SECRET")

if not TOKEN:
    print("❌ DISCORD_TOKEN bulunamadı. Railway'de 'Variables' kısmına eklediğinizden emin olun.")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# HMAC + nonce + timestamp üretici
def generate_signature(action, owner_id, loader, key, hwid):
    nonce = str(uuid.uuid4())
    timestamp = str(int(time.time()))
    data = f"{action}|{owner_id}|{loader}|{key}|{hwid}|{timestamp}|{nonce}"
    signature = hmac.new(HMAC_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()
    return {
        "action": action,
        "owner_id": owner_id,
        "loader": loader,
        "key": key,
        "hwid": hwid,
        "timestamp": timestamp,
        "nonce": nonce,
        "signature": signature
    }

@bot.event
async def on_ready():
    print(f"[+] Bot aktif: {bot.user}")

@bot.command()
async def key(ctx, loader: str):
    owner_id = str(ctx.author.id)
    hwid = ""
    key = "_"
    payload = generate_signature("create", owner_id, loader, key, hwid)
    try:
        res = requests.post(API_URL + f"?token={API_TOKEN}", data=payload)
        await ctx.send(f"🔑 Key oluşturuldu: `{res.text}`")
    except Exception as e:
        await ctx.send(f"❌ Hata: {e}")

@bot.command()
async def reset(ctx, loader: str, key: str):
    owner_id = str(ctx.author.id)
    hwid = "_"
    payload = generate_signature("reset", owner_id, loader, key, hwid)
    try:
        res = requests.post(API_URL + f"?token={API_TOKEN}", data=payload)
        await ctx.send(f"♻️ Key sıfırlandı: `{res.text}`")
    except Exception as e:
        await ctx.send(f"❌ Hata: {e}")

@bot.command()
async def ban(ctx, loader: str, hwid: str):
    owner_id = str(ctx.author.id)
    key = "_"
    payload = generate_signature("ban", owner_id, loader, key, hwid)
    try:
        res = requests.post(API_URL + f"?token={API_TOKEN}", data=payload)
        await ctx.send(f"🚫 Ban sonucu: `{res.text}`")
    except Exception as e:
        await ctx.send(f"❌ Hata: {e}")

@bot.command()
async def unban(ctx, loader: str, hwid: str):
    owner_id = str(ctx.author.id)
    key = "_"
    payload = generate_signature("unban", owner_id, loader, key, hwid)
    try:
        res = requests.post(API_URL + f"?token={API_TOKEN}", data=payload)
        await ctx.send(f"✅ Unban sonucu: `{res.text}`")
    except Exception as e:
        await ctx.send(f"❌ Hata: {e}")

@bot.command()
async def removekey(ctx, loader: str, key: str):
    owner_id = str(ctx.author.id)
    hwid = "_"
    payload = generate_signature("removekey", owner_id, loader, key, hwid)
    try:
        res = requests.post(API_URL + f"?token={API_TOKEN}", data=payload)
        await ctx.send(f"🗑️ Key silindi: `{res.text}`")
    except Exception as e:
        await ctx.send(f"❌ Hata: {e}")

@bot.command()
async def stats(ctx):
    owner_id = str(ctx.author.id)
    loader = "_"
    key = "_"
    hwid = "_"
    payload = generate_signature("stats", owner_id, loader, key, hwid)
    try:
        res = requests.post(API_URL + f"?token={API_TOKEN}", data=payload)
        await ctx.send(f"📊 Stats: `{res.text}`")
    except Exception as e:
        await ctx.send(f"❌ Hata: {e}")

bot.run(TOKEN)
