import os
import discord
from discord.ext import commands
import requests
import json
import asyncio
import io
from datetime import datetime, timezone
import logging

# Setup
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Config
TOKEN = os.getenv("TOKEN")
ADMIN_ROLE = os.getenv("ADMIN_ROLE", "Admin")
API_URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
LOADER_URL = os.getenv("LOADER_URL", "https://midnightponywka.com/loader/data01.png")

# Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

def api_call(action, data=None):
    """Simple API request"""
    try:
        url = f"{API_URL}?api=1&token={API_TOKEN}&action={action}"
        response = requests.post(url, data=data, timeout=8) if data else requests.get(url, timeout=8)
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Server timeout"}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection failed"}
    except json.JSONDecodeError:
        return {"error": "Invalid response"}
    except Exception as e:
        return {"error": str(e)}

def is_admin():
    """Admin check"""
    def predicate(ctx):
        return any(role.name == ADMIN_ROLE for role in ctx.author.roles)
    return commands.check(predicate)

def embed(title, desc=None, color=0x00ff00):
    """Clean embed"""
    e = discord.Embed(title=title, description=desc, color=color, timestamp=datetime.now(timezone.utc))
    e.set_footer(text="Midnight Keylogin System", icon_url="https://cdn.discordapp.com/emojis/🔐.png")
    return e

async def cleanup(ctx, msg=None, delay=20):
    """Auto cleanup"""
    try:
        await ctx.message.delete()
        if msg:
            await asyncio.sleep(delay)
            await msg.delete()
    except:
        pass

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="🔐 Keylogin"))
    logger.info(f'Bot ready: {bot.user}')

# Loader komutunu ekle
@bot.command(name='loader')
@is_admin()
async def download_loader(ctx):
    """Download latest loader"""
    try:
        # PNG dosyasını indir
        logger.info(f"Loader download requested by {ctx.author}")
        response = requests.get(LOADER_URL, timeout=30)
        
        if response.status_code == 200:
            # Dosya boyutunu kontrol et (Discord 25MB limit)
            file_size = len(response.content)
            if file_size > 25 * 1024 * 1024:  # 25MB
                error_embed = embed("❌ Dosya Çok Büyük", f"Dosya boyutu: {file_size / (1024*1024):.1f}MB", 0xff0000)
                msg = await ctx.send(embed=error_embed)
                await cleanup(ctx, msg)
                return
            
            # Discord dosya objesi oluştur
            file = discord.File(
                io.BytesIO(response.content), 
                filename='MidnightLoader.exe'
            )
            
            # Minimal ama bilgilendirici embed
            success_embed = embed("📁 Loader Hazır", None, 0x00ff00)
            success_embed.add_field(name="📦 Dosya", value="`MidnightLoader.exe`", inline=True)
            success_embed.add_field(name="📊 Boyut", value=f"`{file_size/1024:.0f} KB`", inline=True)
            success_embed.add_field(name="✅ Durum", value="Güncel", inline=True)
            
            # Dosyayı gönder
            msg = await ctx.send(embed=success_embed, file=file)
            
            # Otomatik temizlik (20 saniye sonra)
            await cleanup(ctx, msg, 20)
            logger.info(f"Loader successfully sent to {ctx.author}")
            
        else:
            error_embed = embed("❌ İndirme Hatası", f"HTTP {response.status_code}", 0xff0000)
            msg = await ctx.send(embed=error_embed)
            await cleanup(ctx, msg)
            logger.error(f"Loader download failed: HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        error_embed = embed("⏱️ Zaman Aşımı", "Sunucu yanıt vermiyor", 0xff0000)
        msg = await ctx.send(embed=error_embed)
        await cleanup(ctx, msg)
        logger.error("Loader download timeout")
        
    except requests.exceptions.ConnectionError:
        error_embed = embed("🌐 Bağlantı Hatası", "Sunucuya ulaşılamıyor", 0xff0000)
        msg = await ctx.send(embed=error_embed)
        await cleanup(ctx, msg)
        logger.error("Loader download connection error")
        
    except Exception as e:
        error_embed = embed("❌ Hata", f"{str(e)}", 0xff0000)
        msg = await ctx.send(embed=error_embed)
        await cleanup(ctx, msg)
        logger.error(f"Loader download error: {e}")

@bot.command(name='key')
@is_admin()
async def gen_key(ctx):
    """Generate new key"""
    result = api_call('generate-key')
    
    if 'error' in result:
        e = embed("❌ Key Generation Error", f"```{result['error']}```", 0xff0000)
    else:
        key = result.get('key', 'N/A')
        e = embed("✅ Key Generated Successfully", None, 0x00ff00)
        e.add_field(name="🔑 New License Key", value=f"`{key}`", inline=False)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='ban')
@is_admin()
async def ban_user(ctx, username=None, ip=None):
    """Ban user/ip"""
    if not username and not ip:
        e = embed("❌ Invalid Usage", None, 0xff0000)
        e.add_field(name="📋 Usage", value="`!ban <username> [ip]`", inline=False)
        e.add_field(name="📝 Example", value="`!ban TestUser 192.168.1.1`", inline=False)
        msg = await ctx.send(embed=e)
        await cleanup(ctx, msg)
        return
    
    # Eğer sadece kullanıcı adı verilmişse, IP'sini bulmaya çalış
    user_ip = ip
    if username and not ip:
        # Kullanıcının IP'sini bulmak için key listesini kontrol et
        keys_result = api_call('list-keys')
        if 'keys' in keys_result:
            keys_data = keys_result['keys']
            # Eğer keys bir dictionary ise
            if isinstance(keys_data, dict):
                for key, data in keys_data.items():
                    if data.get('username') == username and data.get('ip'):
                        user_ip = data.get('ip')
                        break
            # Eğer keys bir liste ise (bazı API'lerde böyle olabilir)
            elif isinstance(keys_data, list):
                for key_info in keys_data:
                    if key_info.get('username') == username and key_info.get('ip'):
                        user_ip = key_info.get('ip')
                        break
    
    data = {}
    if username: data['username'] = username
    if user_ip: data['ip'] = user_ip
    
    result = api_call('ban-user', data)
    
    if 'error' in result:
        e = embed("❌ Ban Failed", f"```{result['error']}```", 0xff0000)
    else:
        e = embed("🚫 User Banned Successfully", None, 0xff6600)
        e.add_field(name="👤 Username", value=f"`{username or 'Not specified'}`", inline=True)
        e.add_field(name="🌐 IP Address", value=f"`{user_ip or 'Not found'}`", inline=True)
        
        # Eğer IP bulunduysa bilgi ver
        if username and user_ip and not ip:
            e.add_field(name="ℹ️ Info", value=f"{username} kişisi {ctx.author.display_name} tarafından banlandı", inline=False)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='unban')
@is_admin()
async def unban_user(ctx, username=None, ip=None):
    """Remove ban"""
    if not username and not ip:
        e = embed("❌ Invalid Usage", None, 0xff0000)
        e.add_field(name="📋 Usage", value="`!unban <username> [ip]`", inline=False)
        e.add_field(name="📝 Example", value="`!unban TestUser`", inline=False)
        msg = await ctx.send(embed=e)
        await cleanup(ctx, msg)
        return
    
    data = {}
    if username: data['username'] = username
    if ip: data['ip'] = ip
    
    result = api_call('unban-user', data)
    
    if 'error' in result:
        e = embed("❌ Unban Failed", f"```{result['error']}```", 0xff0000)
    else:
        e = embed("✅ Ban Removed Successfully", None, 0x00ff00)
        e.add_field(name="👤 Username", value=f"`{username or 'Not specified'}`", inline=True)
        e.add_field(name="🌐 IP Address", value=f"`{ip or 'Not specified'}`", inline=True)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='check')
@is_admin()
async def check_ban(ctx, username=None, ip=None):
    """Check ban status"""
    if not username and not ip:
        e = embed("❌ Invalid Usage", None, 0xff0000)
        e.add_field(name="📋 Usage", value="`!check <username> [ip]`", inline=False)
        e.add_field(name="📝 Example", value="`!check TestUser`", inline=False)
        msg = await ctx.send(embed=e)
        await cleanup(ctx, msg)
        return
    
    data = {}
    if username: data['username'] = username
    if ip: data['ip'] = ip
    
    result = api_call('check-ban', data)
    
    if 'error' in result:
        e = embed("❌ Check Failed", f"```{result['error']}```", 0xff0000)
    elif result.get('banned'):
        e = embed("🚫 USER IS BANNED", None, 0xff0000)
        e.add_field(name="👤 Username", value=f"`{username or 'Not specified'}`", inline=True)
        e.add_field(name="🌐 IP Address", value=f"`{ip or 'Not specified'}`", inline=True)
    else:
        e = embed("✅ USER IS CLEAN", None, 0x00ff00)
        e.add_field(name="👤 Username", value=f"`{username or 'Not specified'}`", inline=True)
        e.add_field(name="🌐 IP Address", value=f"`{ip or 'Not specified'}`", inline=True)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='stats')
@is_admin()
async def show_stats(ctx):
    """System stats"""
    result = api_call('stats')
    
    if 'error' in result:
        e = embed("❌ Stats Error", f"```{result['error']}```", 0xff0000)
    else:
        total = int(result.get('total_keys', 0))
        used = int(result.get('used_keys', 0))
        available = total - used
        banned_users = int(result.get('banned_users', 0))
        banned_ips = int(result.get('banned_ips', 0))
        usage_percent = (used/max(1,total)*100)
        
        e = embed("📊 System Statistics", None, 0x0099ff)
        e.add_field(name="🔑 License Keys", value=f"```Total: {total}\nUsed: {used}\nAvailable: {available}\nUsage: {usage_percent:.1f}%```", inline=True)
        e.add_field(name="🚫 Security Bans", value=f"```Users: {banned_users}\nIPs: {banned_ips}\nTotal: {banned_users + banned_ips}```", inline=True)
        e.add_field(name="📈 System Health", value=f"```Status: {'🟢 Healthy' if usage_percent < 80 else '🟡 Busy' if usage_percent < 95 else '🔴 Critical'}\nSecurity: {'🛡️ Active' if banned_users + banned_ips > 0 else '⚪ Normal'}```", inline=False)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='version')
@is_admin()
async def version_cmd(ctx, new_version=None):
    """Check/update version"""
    if new_version:
        result = api_call('update-version', {'version': new_version})
        if 'error' in result:
            e = embed("❌ Version Update Failed", f"```{result['error']}```", 0xff0000)
        elif result.get('success'):
            e = embed("✅ Version Updated Successfully", None, 0x00ff00)
            e.add_field(name="📝 New Version", value=f"`{new_version}`", inline=False)
        else:
            e = embed("❌ Version Update Failed", "Unknown error", 0xff0000)
    else:
        result = api_call('version')
        if 'error' in result:
            e = embed("❌ Version Check Error", f"```{result['error']}```", 0xff0000)
        else:
            current_version = result.get('version', 'Unknown')
            e = embed("📋 Current Version", None, 0x7289da)
            e.add_field(name="🔢 Version", value=f"`{current_version}`", inline=False)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='license')
@is_admin()
async def check_license(ctx, key=None):
    """Check license"""
    if not key:
        e = embed("❌ Invalid Usage", None, 0xff0000)
        e.add_field(name="📋 Usage", value="`!license <key>`", inline=False)
        e.add_field(name="📝 Example", value="`!license ABC123DEF456`", inline=False)
        msg = await ctx.send(embed=e)
        await cleanup(ctx, msg)
        return
    
    result = api_call('check-license', {'key': key})
    
    if 'error' in result:
        e = embed("❌ License Check Error", f"```{result['error']}```", 0xff0000)
    else:
        status = result.get('status', 'unknown')
        key_short = key[:8] + "..." if len(key) > 8 else key
        
        if status == 'unused':
            e = embed("🔑 LICENSE: UNUSED", None, 0xffaa00)
            e.add_field(name="🔐 Key", value=f"`{key_short}`", inline=False)
        elif status == 'expired':
            e = embed("❌ LICENSE: EXPIRED", None, 0xff0000)
            e.add_field(name="🔐 Key", value=f"`{key_short}`", inline=True)
            e.add_field(name="⏰ Expired", value=f"`{result.get('license_expiry', 'N/A')}`", inline=True)
        elif status == 'active':
            user = result.get('username', 'N/A')
            expiry = result.get('license_expiry', 'N/A')
            e = embed("✅ LICENSE: ACTIVE", None, 0x00ff00)
            e.add_field(name="🔐 Key", value=f"`{key_short}`", inline=True)
            e.add_field(name="👤 User", value=f"`{user}`", inline=True)
            e.add_field(name="⏰ Expires", value=f"`{expiry}`", inline=True)
        else:
            e = embed("❓ LICENSE: UNKNOWN", None, 0x888888)
            e.add_field(name="🔐 Key", value=f"`{key_short}`", inline=False)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='keylist')
@is_admin()
async def key_list(ctx):
    """Key list"""
    result = api_call('list-keys')
    
    if 'error' in result:
        e = embed("❌ Keylist Error", f"```{result['error']}```", 0xff0000)
    else:
        keys = result.get('keys', {})
        if not keys:
            e = embed("📋 Key List", "Hiç anahtar bulunamadı", 0xffaa00)
        else:
            key_text = ""
            count = 0
            
            # Eğer keys bir dictionary ise
            if isinstance(keys, dict):
                for key, data in keys.items():
                    if count >= 10:  # İlk 10 anahtarı göster
                        break
                    status = "🟢" if data.get('used') else "🟡"
                    user = data.get('username', 'Kullanılmamış')
                    key_text += f"`{key}` {status} {user}\n"
                    count += 1
            # Eğer keys bir liste ise
            elif isinstance(keys, list):
                for key_info in keys:
                    if count >= 10:  # İlk 10 anahtarı göster
                        break
                    status = "🟢" if key_info.get('used') else "🟡"
                    user = key_info.get('username', 'Kullanılmamış')
                    key = key_info.get('key', 'N/A')
                    key_text += f"`{key}` {status} {user}\n"
                    count += 1
            
            if len(keys) > 10:
                key_text += f"\n... ve {len(keys)-10} anahtar daha"
            
            e = embed("📋 Key List", key_text, 0x0099ff)
            e.add_field(name="📊 Toplam", value=f"{len(keys)} anahtar", inline=True)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='banlist')
@is_admin()
async def ban_list(ctx):
    """Ban list"""
    result = api_call('list-banned')
    
    if 'error' in result:
        e = embed("❌ Banlist Error", f"```{result['error']}```", 0xff0000)
    else:
        banned = result.get('banned', {})
        banned_users = banned.get('usernames', [])
        banned_ips = banned.get('ips', [])
        
        if not banned_users and not banned_ips:
            e = embed("✅ Ban List", "Hiç yasaklı kullanıcı yok", 0x00ff00)
        else:
            ban_text = ""
            
            if banned_users:
                ban_text += "**👤 Kullanıcılar:**\n"
                for i, user in enumerate(banned_users[:5], 1):
                    ban_text += f"{i}. `{user}`\n"
                if len(banned_users) > 5:
                    ban_text += f"... ve {len(banned_users)-5} kullanıcı daha\n"
            
            if banned_ips:
                ban_text += "\n**🌐 IP Adresleri:**\n"
                for i, ip in enumerate(banned_ips[:5], 1):
                    ban_text += f"{i}. `{ip}`\n"
                if len(banned_ips) > 5:
                    ban_text += f"... ve {len(banned_ips)-5} IP daha"
            
            e = embed("🚫 Ban List", ban_text, 0xff6600)
            e.add_field(name="👤 Kullanıcı", value=f"{len(banned_users)}", inline=True)
            e.add_field(name="🌐 IP", value=f"{len(banned_ips)}", inline=True)
            e.add_field(name="📊 Toplam", value=f"{len(banned_users) + len(banned_ips)}", inline=True)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='help')
async def help_cmd(ctx):
    """Help menu"""
    e = embed("📋 Komutlar", None, 0x7289DA)
    
    # Key Management Commands
    e.add_field(
        name="🔑 Lisans İşlemleri", 
        value="`!key` - Yeni lisans oluştur\n`!keylist` - Tüm anahtarları listele\n`!license <anahtar>` - Lisans durumunu kontrol et\n`!version` - Sistem versiyonunu göster", 
        inline=False
    )
    
    # Security Commands
    e.add_field(
        name="🛡️ Güvenlik İşlemleri", 
        value="`!ban <kullanıcı>` - Kullanıcıyı yasakla\n`!unban <kullanıcı>` - Yasağı kaldır\n`!banlist` - Yasaklı kullanıcıları listele\n`!check <kullanıcı>` - Yasak durumunu kontrol et", 
        inline=False
    )
    
    # System Commands
    e.add_field(
        name="📊 Sistem Bilgileri", 
        value="`!stats` - İstatistikleri göster\n`!loader` - Güncel loader'ı indir\n`!help` - Bu menüyü göster", 
        inline=False
    )
    
    msg = await ctx.send(embed=e)
    # Help mesajı kalıcı - sadece kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass

@bot.event
async def on_command_error(ctx, error):
    """Handle errors"""
    try:
        await ctx.message.delete()
    except:
        pass
    
    if isinstance(error, commands.CheckFailure):
        e = embed("🔒 Access Denied", f"Admin role required", 0xff0000)
    elif isinstance(error, commands.CommandNotFound):
        e = embed("❓ Unknown Command", "Use `!help` for commands", 0xffaa00)
    else:
        e = embed("⚠️ Error", str(error), 0xff0000)
        logger.error(f"Command error: {error}")
    
    msg = await ctx.send(embed=e)
    asyncio.create_task(cleanup(ctx, msg, 20))

if __name__ == "__main__":
    # Check config
    missing = [var for var, val in [("TOKEN", TOKEN), ("API_URL", API_URL), ("API_TOKEN", API_TOKEN)] if not val]
    if missing:
        logger.error(f"Missing: {', '.join(missing)}")
        exit(1)
    
    logger.info("Starting bot...")
    bot.run(TOKEN)
