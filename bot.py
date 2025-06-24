import discord
from discord.ext import commands
import requests
import json
import asyncio
import datetime
import os
import random
import string

# Bot ayarları - Railway'den environment variable'ı al
BOT_TOKEN = os.getenv('DISCORD_TOKEN') or os.getenv('BOT_TOKEN')
API_BASE_URL = "https://midnightponywka.com"
ADMIN_TOKEN = "ADMIN_API_SECRET_TOKEN_2024"

if not BOT_TOKEN:
    print("Bot token bulunamadı!")
    exit(1)

# Bot intents
intents = discord.Intents.default()
intents.message_content = True

# Bot oluştur - Varsayılan help komutunu devre dışı bırak
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print("=" * 50)
    print("🚀 KEYLOGIN DISCORD BOT ONLINE!")
    print(f"📱 Bot Name: {bot.user}")
    print(f"🆔 Bot ID: {bot.user.id}")
    print(f"📊 Servers: {len(bot.guilds)}")
    print(f"👥 Users: {len(bot.users)}")
    print(f"🕒 Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Bot status'unu ayarla
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="Keylogin Management | !help")
    )

def make_api_request(action, method='GET', data=None):
    """API isteği gönder"""
    try:
        url = f"{API_BASE_URL}/?api=1&token={ADMIN_TOKEN}&action={action}"
        
        if method == 'POST' and data:
            response = requests.post(url, data=data, timeout=15)
        else:
            response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error", 
                "message": f"HTTP {response.status_code}: {response.text[:100]}"
            }
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Request timeout (15s)"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": "Connection error - Server unreachable"}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON response from server"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}

def generate_key():
    """Güzel format ile key üret: SPFR-XXXX-XXXX"""
    prefix = "SPFR"
    chars = string.ascii_uppercase + string.digits
    segment1 = ''.join(random.choice(chars) for _ in range(4))
    segment2 = ''.join(random.choice(chars) for _ in range(4))
    return f"{prefix}-{segment1}-{segment2}"

def generate_premium_key():
    """Premium key üret: SPFR-PREM-XXXX"""
    prefix = "SPFR-PREM"
    chars = string.ascii_uppercase + string.digits
    segment = ''.join(random.choice(chars) for _ in range(4))
    return f"{prefix}-{segment}"

def generate_vip_key():
    """VIP key üret: SPFR-VIP-XXXX"""
    prefix = "SPFR-VIP"
    chars = string.ascii_uppercase + string.digits
    segment = ''.join(random.choice(chars) for _ in range(4))
    return f"{prefix}-{segment}"

# === SADE KOMUTLAR ===

@bot.command(name='key')
async def generate_key_command(ctx, key_type=None, count=None):
    """🔑 Key üret"""
    try:
        await ctx.message.delete()
    except:
        pass
    
    # Parametreleri ayarla
    if count is None:
        count = 1
    else:
        try:
            count = int(count)
            if count < 1 or count > 10:
                await ctx.send("❌ Key sayısı 1-10 arasında olmalı!")
                return
        except ValueError:
            await ctx.send("❌ Geçersiz sayı!")
            return
    
    # Key tipini belirle
    if key_type is None or key_type.lower() == "normal":
        key_generator = generate_key
        emoji = "🔑"
    elif key_type.lower() in ["premium", "prem", "p"]:
        key_generator = generate_premium_key
        emoji = "💎"
    elif key_type.lower() in ["vip", "v"]:
        key_generator = generate_vip_key
        emoji = "👑"
    else:
        await ctx.send("❌ Geçersiz tip! (normal, premium, vip)")
        return
    
    loading_msg = await ctx.send(f"⏳ {count} key üretiliyor...")
    
    # Key'leri üret
    generated_keys = []
    for i in range(count):
        for attempt in range(10):
            new_key = key_generator()
            check_result = make_api_request('key-info', 'POST', {'key': new_key})
            
            if check_result.get('status') == 'error' and 'Invalid key' in check_result.get('message', ''):
                add_result = make_api_request('add-key', 'POST', {'key': new_key})
                if add_result.get('status') == 'success':
                    generated_keys.append(new_key)
                    break
    
    await loading_msg.delete()
    
    if generated_keys:
        embed = discord.Embed(title=f"{emoji} Key Üretildi", color=0x00ff00)
        key_list = '\n'.join([f"`{key}`" for key in generated_keys])
        embed.add_field(name="Keyler", value=key_list, inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Key üretilemedi!")

@bot.command(name='keylist')
async def list_keys(ctx):
    """📋 Key listesi"""
    try:
        await ctx.message.delete()
    except:
        pass
        
    loading_msg = await ctx.send("⏳ Keyler getiriliyor...")
    result = make_api_request('list-keys')
    await loading_msg.delete()
    
    if result.get('status') == 'success':
        key_details = result.get('key_details', [])
        
        if key_details:
            embed = discord.Embed(title="📋 Key Listesi", color=0x0099ff)
            
            key_list = []
            for key_info in key_details:
                key = key_info['key']
                bound = key_info['bound']
                
                if key.startswith('SPFR-VIP-'):
                    icon = "👑"
                elif key.startswith('SPFR-PREM-'):
                    icon = "💎"
                else:
                    icon = "🔑"
                
                status = "🔒" if bound else "🔓"
                key_list.append(f"{icon} `{key}` {status}")
            
            embed.description = '\n'.join(key_list)
            await ctx.send(embed=embed)
        else:
            await ctx.send("📋 Henüz key yok. `!key` ile üret.")
    else:
        await ctx.send(f"❌ Hata: {result.get('message', 'Bilinmeyen hata')}")

@bot.command(name='delete')
async def delete_key(ctx, key=None):
    """🗑️ Key sil"""
    try:
        await ctx.message.delete()
    except:
        pass
    
    if key is None:
        await ctx.send("❌ Kullanım: `!delete <key>`")
        return
    
    loading_msg = await ctx.send("⏳ Key siliniyor...")
    result = make_api_request('delete-key', 'POST', {'key': key})
    await loading_msg.delete()
    
    if result.get('status') == 'success':
        await ctx.send(f"✅ Key silindi: `{key}`")
    else:
        await ctx.send(f"❌ Silinemedi: {result.get('message', 'Hata')}")

@bot.command(name='reset')
async def reset_key(ctx, key=None):
    """🔄 Key sıfırla"""
    try:
        await ctx.message.delete()
    except:
        pass
    
    if key is None:
        await ctx.send("❌ Kullanım: `!reset <key>`")
        return
    
    loading_msg = await ctx.send("⏳ Key sıfırlanıyor...")
    result = make_api_request('unbind-key', 'POST', {'key': key})
    await loading_msg.delete()
    
    if result.get('status') == 'success':
        await ctx.send(f"✅ Key sıfırlandı: `{key}`")
    else:
        await ctx.send(f"❌ Sıfırlanamadı: {result.get('message', 'Hata')}")

@bot.command(name='keyinfo')
async def key_info(ctx, key=None):
    """ℹ️ Key bilgisi"""
    try:
        await ctx.message.delete()
    except:
        pass
    
    if key is None:
        await ctx.send("❌ Kullanım: `!keyinfo <key>`")
        return
    
    loading_msg = await ctx.send("⏳ Bilgi getiriliyor...")
    result = make_api_request('key-info', 'POST', {'key': key})
    await loading_msg.delete()
    
    if result.get('status') == 'success':
        bound = result.get('bound', False)
        key_type = result.get('type', 'Legacy')
        
        if bound:
            sid = result.get('sid', '')
            embed = discord.Embed(title=f"🔒 {key}", color=0xff9900)
            embed.add_field(name="Durum", value="Bağlı", inline=True)
            embed.add_field(name="Tip", value=key_type, inline=True)
            embed.add_field(name="SID", value=f"`{sid[:8]}...`", inline=True)
        else:
            embed = discord.Embed(title=f"🔓 {key}", color=0x00ff00)
            embed.add_field(name="Durum", value="Kullanılabilir", inline=True)
            embed.add_field(name="Tip", value=key_type, inline=True)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ Key bulunamadı: {result.get('message', 'Hata')}")

@bot.command(name='ban')
async def ban_user(ctx, username=None):
    """🚫 Kullanıcı banla"""
    try:
        await ctx.message.delete()
    except:
        pass
    
    if username is None:
        await ctx.send("❌ Kullanım: `!ban <username>`")
        return
    
    loading_msg = await ctx.send("⏳ Banlıyor...")
    result = make_api_request('ban-user', 'POST', {'username': username})
    await loading_msg.delete()
    
    if result.get('status') == 'success':
        await ctx.send(f"🚫 Banlandı: `{username}`")
    else:
        await ctx.send(f"❌ Banlanamadı: {result.get('message', 'Hata')}")

@bot.command(name='unban')
async def unban_user(ctx, username=None):
    """✅ Ban kaldır"""
    try:
        await ctx.message.delete()
    except:
        pass
    
    if username is None:
        await ctx.send("❌ Kullanım: `!unban <username>`")
        return
    
    loading_msg = await ctx.send("⏳ Ban kaldırılıyor...")
    result = make_api_request('unban-user', 'POST', {'username': username})
    await loading_msg.delete()
    
    if result.get('status') == 'success':
        await ctx.send(f"✅ Ban kaldırıldı: `{username}`")
    else:
        await ctx.send(f"❌ Kaldırılamadı: {result.get('message', 'Hata')}")

@bot.command(name='banip')
async def ban_ip(ctx, ip=None):
    """🚫 IP banla"""
    try:
        await ctx.message.delete()
    except:
        pass
    
    if ip is None:
        await ctx.send("❌ Kullanım: `!banip <ip>`")
        return
    
    loading_msg = await ctx.send("⏳ IP banlıyor...")
    result = make_api_request('ban-ip', 'POST', {'ip': ip})
    await loading_msg.delete()
    
    if result.get('status') == 'success':
        await ctx.send(f"🚫 IP banlandı: `{ip}`")
    else:
        await ctx.send(f"❌ IP banlanamadı: {result.get('message', 'Hata')}")

@bot.command(name='unbanip')
async def unban_ip(ctx, ip=None):
    """✅ IP ban kaldır"""
    try:
        await ctx.message.delete()
    except:
        pass
    
    if ip is None:
        await ctx.send("❌ Kullanım: `!unbanip <ip>`")
        return
    
    loading_msg = await ctx.send("⏳ IP ban kaldırılıyor...")
    result = make_api_request('unban-ip', 'POST', {'ip': ip})
    await loading_msg.delete()
    
    if result.get('status') == 'success':
        await ctx.send(f"✅ IP ban kaldırıldı: `{ip}`")
    else:
        await ctx.send(f"❌ IP ban kaldırılamadı: {result.get('message', 'Hata')}")

@bot.command(name='userinfo')
async def user_info(ctx, username=None):
    """👤 Kullanıcı bilgisi"""
    try:
        await ctx.message.delete()
    except:
        pass
    
    if username is None:
        await ctx.send("❌ Kullanım: `!userinfo <username>`")
        return
    
    loading_msg = await ctx.send("⏳ Kontrol ediliyor...")
    result = make_api_request('check-ban', 'POST', {'username': username})
    await loading_msg.delete()
    
    if result.get('status') == 'success':
        embed = discord.Embed(title=f"👤 {username}", color=0x00ff00)
        embed.add_field(name="Durum", value="✅ Temiz", inline=False)
        await ctx.send(embed=embed)
    elif result.get('status') == 'banned':
        ban_type = result.get('ban_type', 'unknown')
        embed = discord.Embed(title=f"👤 {username}", color=0xff0000)
        embed.add_field(name="Durum", value=f"🚫 Banlı ({ban_type})", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ Kontrol edilemedi: {result.get('message', 'Hata')}")

@bot.command(name='stats')
async def show_stats(ctx):
    """📊 İstatistikler"""
    try:
        await ctx.message.delete()
    except:
        pass
        
    loading_msg = await ctx.send("⏳ İstatistikler...")
    result = make_api_request('stats')
    await loading_msg.delete()
    
    if result.get('status') in ['success', 'online']:
        embed = discord.Embed(title="📊 İstatistikler", color=0x0099ff)
        
        total_keys = result.get('total_keys', 0)
        bound_keys = result.get('bound_keys', 0)
        
        embed.add_field(name="🔑 Toplam", value=str(total_keys), inline=True)
        embed.add_field(name="🔒 Bağlı", value=str(bound_keys), inline=True)
        embed.add_field(name="🔓 Boş", value=str(total_keys - bound_keys), inline=True)
        embed.add_field(name="🚫 Banned", value=str(result.get('banned_users', 0)), inline=True)
        embed.add_field(name="🌐 Status", value=result.get('status', 'N/A').upper(), inline=True)
        embed.add_field(name="📦 Version", value=result.get('version', 'N/A'), inline=True)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ İstatistik alınamadı: {result.get('message', 'Hata')}")

@bot.command(name='help')
async def show_help(ctx):
    """❓ Yardım"""
    try:
        await ctx.message.delete()
    except:
        pass
        
    embed = discord.Embed(title="🤖 Bot Komutları", color=0x0099ff)
    
    embed.add_field(
        name="🔑 Key İşlemleri",
        value="`!key [tip] [sayı]` - Key üret\n"
              "`!keylist` - Key listesi\n"
              "`!delete <key>` - Key sil\n"
              "`!reset <key>` - Key sıfırla\n"
              "`!keyinfo <key>` - Key bilgisi",
        inline=False
    )
    
    embed.add_field(
        name="🚫 Ban İşlemleri",
        value="`!ban <user>` - Kullanıcı banla\n"
              "`!unban <user>` - Ban kaldır\n"
              "`!banip <ip>` - IP banla\n"
              "`!unbanip <ip>` - IP ban kaldır\n"
              "`!userinfo <user>` - Kullanıcı kontrol",
        inline=False
    )
    
    embed.add_field(
        name="📊 Sistem",
        value="`!stats` - İstatistikler\n"
              "`!help` - Bu yardım",
        inline=False
    )
    
    embed.set_footer(text="Keylogin Bot | Sade ve Basit")
    await ctx.send(embed=embed)

# Hata yakalama
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ `{ctx.message.content.split()[0]}` komutu bulunamadı. `!help` yaz.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Eksik parametre. `!help` ile kontrol et.")
    else:
        await ctx.send(f"❌ Hata: {str(error)}")
        print(f"Error: {error}")

# Ana çalıştırma
if __name__ == "__main__":
    print("🚀 Keylogin Discord Bot Starting...")
    print(f"🔑 Token Status: {'✅ Found' if BOT_TOKEN else '❌ Missing'}")
    print(f"🌐 API URL: {API_BASE_URL}")
    print("-" * 50)
    
    try:
        bot.run(BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ HATA: Geçersiz bot token!")
        import sys
        sys.exit(1)
    except Exception as e:
        print(f"❌ HATA: {e}")
        import sys
        sys.exit(1) 
