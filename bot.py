import discord
from discord.ext import commands
import requests
import json
import random
import string
import asyncio
import datetime
import os

# Bot configuration
BOT_TOKEN = os.getenv('DISCORD_TOKEN') or os.getenv('BOT_TOKEN')
API_URL = "https://midnightponywka.com"
ADMIN_TOKEN = "ADMIN_API_SECRET_TOKEN_2024"

if not BOT_TOKEN:
    print("Bot token bulunamadı!")
    exit(1)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

def make_api_request(action, method='GET', data=None):
    """API isteği gönder"""
    try:
        url = f"{API_URL}/?api=1&token={ADMIN_TOKEN}&action={action}"
        
        if method == 'POST':
            response = requests.post(url, data=data, timeout=10)
        else:
            response = requests.get(url, timeout=10)
        
        return response.json()
    except Exception as e:
        return {'status': 'error', 'message': f'API hatası: {str(e)}'}

def generate_key():
    """Normal key üret"""
    return f"SPFR-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"

@bot.event
async def on_ready():
    print(f'{bot.user} aktif!')

@bot.command(name='key')
async def generate_key_command(ctx, count=None):
    """Key üret"""
    if count is None:
        count = 1
    else:
        try:
            count = int(count)
            if count < 1 or count > 10:
                await ctx.send("❌ 1-10 arası")
                return
        except:
            await ctx.send("❌ Geçersiz sayı")
            return
    
    msg = await ctx.send("⏳ Üretiliyor...")
    
    keys = []
    for _ in range(count):
        new_key = generate_key()
        result = make_api_request('add-key', 'POST', {'key': new_key})
        if result.get('status') == 'success':
            keys.append(new_key)
    
    await msg.delete()
    
    if keys:
        key_list = '\n'.join([f"`{key}`" for key in keys])
        await ctx.send(f"✅ **{len(keys)} Key Üretildi**\n{key_list}")
    else:
        await ctx.send("❌ Key üretilemedi")

@bot.command(name='delkey')
async def delete_key(ctx, key=None):
    """Key sil"""
    if not key:
        await ctx.send("❌ `!delkey <key>`")
        return
    
    result = make_api_request('delete-key', 'POST', {'key': key})
    
    if result.get('status') == 'success':
        await ctx.send(f"✅ Key silindi: `{key}`")
    else:
        await ctx.send(f"❌ Silinemedi: {result.get('message', 'Hata')}")

@bot.command(name='hwidreset')
async def hwid_reset(ctx, key=None):
    """Key'i SID'den ayır"""
    if not key:
        await ctx.send("❌ `!hwidreset <key>`")
        return
    
    result = make_api_request('unbind-key', 'POST', {'key': key})
    
    if result.get('status') == 'success':
        await ctx.send(f"✅ HWID reset: `{key}`")
    else:
        await ctx.send(f"❌ Reset edilemedi: {result.get('message', 'Hata')}")

@bot.command(name='ban')
async def ban_user(ctx, username=None):
    """Ban"""
    if not username:
        await ctx.send("❌ `!ban <username>`")
        return
    
    result = make_api_request('ban-user', 'POST', {'username': username})
    
    if result.get('status') == 'success':
        await ctx.send(f"🚫 Banlandı: `{username}`")
    else:
        await ctx.send(f"❌ Banlanamadı: {result.get('message', 'Hata')}")

@bot.command(name='unban')
async def unban_user(ctx, username=None):
    """Unban"""
    if not username:
        await ctx.send("❌ `!unban <username>`")
        return
    
    result = make_api_request('unban-user', 'POST', {'username': username})
    
    if result.get('status') == 'success':
        await ctx.send(f"✅ Ban kaldırıldı: `{username}`")
    else:
        await ctx.send(f"❌ Ban kaldırılamadı: {result.get('message', 'Hata')}")

@bot.command(name='keys')
async def list_keys(ctx):
    """Key listesi"""
    result = make_api_request('list-keys')
    
    if result.get('status') == 'success':
        keys = result.get('key_details', [])
        if keys:
            key_list = []
            for key_info in keys[:20]:  # İlk 20 key
                key = key_info['key']
                bound = "🔒" if key_info['bound'] else "🔓"
                key_list.append(f"{bound} `{key}`")
            
            await ctx.send(f"📋 **Keys ({len(keys)} total)**\n" + '\n'.join(key_list))
        else:
            await ctx.send("📋 Key yok")
    else:
        await ctx.send("❌ Liste alınamadı")

@bot.command(name='test')
async def test_key(ctx, key=None):
    """Key test"""
    if not key:
        await ctx.send("❌ `!test <key>`")
        return
    
    sid = f"test-{ctx.author.id}"
    result = make_api_request('key-login', 'POST', {'key': key, 'sid': sid})
    
    if result.get('authenticated') and result.get('status') == 'success':
        await ctx.send(f"✅ Key geçerli: `{key}`")
    else:
        await ctx.send(f"❌ Key geçersiz: `{key}`")

@bot.command(name='help')
async def show_help(ctx):
    """Komutlar"""
    help_text = """```
🤖 BOT KOMUTLARI

!key [sayı]     - Key üret (1-10)
!delkey <key>   - Key sil  
!hwidreset <key>- HWID reset
!ban <user>     - Ban
!unban <user>   - Unban
!keys           - Key listesi
!test <key>     - Key test
!help           - Bu mesaj
```"""
    await ctx.send(help_text)

# Bot çalıştır
if __name__ == "__main__":
    bot.run(BOT_TOKEN) 
