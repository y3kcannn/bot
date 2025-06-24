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

# === ANA KOMUTLAR (Sadece 6 komut) ===

@bot.command(name='key', aliases=['k'])
async def generate_key_command(ctx, key_type=None, count=None):
    """🔑 Key üret - Kullanım: !key [type] [count]"""
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
    
    # Parametreleri kontrol et
    if count is None:
        count = 1
    else:
        try:
            count = int(count)
            if count < 1 or count > 10:
                embed = discord.Embed(
                    title="❌ Geçersiz Sayı",
                    description="Key sayısı 1-10 arasında olmalı!",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
        except ValueError:
            embed = discord.Embed(
                title="❌ Geçersiz Format",
                description="Key sayısı rakam olmalı! (1-10)",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
    
    # Key tipini belirle
    if key_type is None or key_type.lower() == "normal":
        key_type_name = "Normal"
        key_generator = generate_key
        color = 0x0099ff
        emoji = "🔑"
    elif key_type.lower() in ["premium", "prem", "p"]:
        key_type_name = "Premium"
        key_generator = generate_premium_key
        color = 0xffd700
        emoji = "💎"
    elif key_type.lower() in ["vip", "v"]:
        key_type_name = "VIP"
        key_generator = generate_vip_key
        color = 0xff6600
        emoji = "👑"
    else:
        embed = discord.Embed(
            title="❌ Geçersiz Key Tipi",
            description="**Kullanılabilir tipler:**\n• `normal` - Standart key\n• `premium/p` - Premium key\n• `vip/v` - VIP key",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Loading mesajı
    loading_msg = await ctx.send(f"⏳ {count} adet {key_type_name} key üretiliyor...")
    
    # Key'leri üret ve sisteme ekle
    generated_keys = []
    failed_keys = []
    
    for i in range(count):
        # Unique key üret (10 deneme)
        for attempt in range(10):
            new_key = key_generator()
            
            # Key'in sistemde olup olmadığını kontrol et
            check_result = make_api_request('key-info', 'POST', {'key': new_key})
            
            if check_result.get('status') == 'error' and 'Invalid key' in check_result.get('message', ''):
                # Key mevcut değil, kullanılabilir
                add_result = make_api_request('add-key', 'POST', {'key': new_key})
                
                if add_result.get('status') == 'success':
                    generated_keys.append(new_key)
                    break
                else:
                    if attempt == 9:  # Son deneme
                        failed_keys.append(f"Key eklenemedi")
            else:
                # Key zaten mevcut, yeni key dene
                if attempt == 9:  # Son deneme
                    failed_keys.append("Unique key üretilemedi")
    
    await loading_msg.delete()
    
    # Sonuçları göster
    if generated_keys:
        # Başarılı key'ler
        embed = discord.Embed(
            title=f"{emoji} {key_type_name} Key Üretimi Tamamlandı",
            description=f"**{len(generated_keys)} adet key başarıyla üretildi!**",
            color=color
        )
        
        # Key'leri göster
        key_list = []
        for i, key in enumerate(generated_keys, 1):
            key_list.append(f"`{i}.` `{key}`")
        
        # Key'leri sayfa sayfa göster (Discord limit)
        keys_per_page = 8
        if len(key_list) <= keys_per_page:
            embed.add_field(
                name="🔑 Üretilen Key'ler",
                value='\n'.join(key_list),
                inline=False
            )
        else:
            # Çok key varsa ilk sayfayı göster
            embed.add_field(
                name="🔑 Üretilen Key'ler (İlk 8)",
                value='\n'.join(key_list[:8]),
                inline=False
            )
        
        embed.set_footer(
            text=f"Üreten: {ctx.author} | {datetime.datetime.now().strftime('%H:%M:%S')}", 
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        
        await ctx.send(embed=embed)
    
    else:
        # Hiç key üretilemedi
        embed = discord.Embed(
            title="❌ Key Üretimi Başarısız",
            description="Hiçbir key üretilemedi! Tekrar deneyin.",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='keys', aliases=['list', 'l'])
async def list_keys(ctx):
    """📋 Key listesi - SID durumu ile"""
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
        
    loading_msg = await ctx.send("⏳ Key'ler getiriliyor...")
    
    result = make_api_request('list-keys')
    
    await loading_msg.delete()
    
    if result.get('status') == 'success':
        key_details = result.get('key_details', [])
        total_keys = result.get('total_keys', 0)
        bound_keys = result.get('bound_keys', 0)
        
        if key_details:
            # Key'leri sayfa sayfa göster (Discord embed limiti)
            keys_per_page = 10
            total_pages = (len(key_details) + keys_per_page - 1) // keys_per_page
            
            for page in range(total_pages):
                start_idx = page * keys_per_page
                end_idx = min((page + 1) * keys_per_page, len(key_details))
                page_keys = key_details[start_idx:end_idx]
                
                key_list = []
                for key_info in page_keys:
                    key = key_info['key']
                    bound = key_info['bound']
                    sid = key_info['sid']
                    
                    # Key tipini belirle
                    if key.startswith('SPFR-VIP-'):
                        key_icon = "👑"
                    elif key.startswith('SPFR-PREM-'):
                        key_icon = "💎"
                    elif key.startswith('SPFR-'):
                        key_icon = "🔑"
                    else:
                        key_icon = "🗝️"
                    
                    if bound:
                        status_icon = "🔒"
                        status_text = "Bağlı"
                    else:
                        status_icon = "🔓"
                        status_text = "Kullanılabilir"
                    
                    key_list.append(f"{key_icon} `{key}` {status_icon}")
                
                embed = discord.Embed(
                    title="📋 Key Listesi",
                    description='\n'.join(key_list),
                    color=0x0099ff
                )
                
                # İstatistikler
                embed.add_field(
                    name="📊 Özet",
                    value=f"**Toplam:** {total_keys} • **Bağlı:** {bound_keys} • **Kullanılabilir:** {total_keys - bound_keys}",
                    inline=False
                )
                
                if total_pages > 1:
                    embed.set_footer(text=f"Sayfa {page + 1}/{total_pages} • 🔑=Normal 💎=Premium 👑=VIP")
                
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="📋 Key Listesi",
                description="Henüz hiç key eklenmemiş.\n\n💡 **İpucu:** `!key` komutu ile key üretebilirsin",
                color=0xffa500
            )
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Hata",
            description=f"Key'ler alınamadı: {result.get('message', 'Bilinmeyen hata')}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='manage', aliases=['m'])
async def manage_keys(ctx, action=None, target=None):
    """🔧 Key yönetimi - Kullanım: !manage <action> <target>"""
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
    
    if action is None:
        embed = discord.Embed(
            title="🔧 Key Yönetimi",
            description="**Kullanım:** `!manage <action> <target>`",
            color=0x0099ff
        )
        embed.add_field(
            name="📝 Eylemler",
            value="• `delete <key>` - Key sil\n• `reset <key>` - SID sıfırla\n• `info <key>` - Key bilgileri\n• `test <key>` - Key test et",
            inline=False
        )
        embed.add_field(
            name="💡 Örnekler",
            value="`!manage delete SPFR-1234-5678`\n`!manage reset SPFR-1234-5678`\n`!manage info SPFR-1234-5678`",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    if target is None:
        embed = discord.Embed(
            title="❌ Eksik Parametre",
            description=f"**{action}** eylemi için hedef belirtmelisin!\n\n**Örnek:** `!manage {action} SPFR-1234-5678`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    action = action.lower()
    
    if action in ['delete', 'del', 'd']:
        # Key silme
        loading_msg = await ctx.send("⏳ Key siliniyor...")
        result = make_api_request('delete-key', 'POST', {'key': target})
        await loading_msg.delete()
        
        if result.get('status') == 'success':
            embed = discord.Embed(
                title="✅ Key Silindi",
                description=f"**Key:** `{target}`\n**Durum:** Başarıyla silindi",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title="❌ Key Silinemedi",
                description=f"**Hata:** {result.get('message', 'Bilinmeyen hata')}",
                color=0xff0000
            )
    
    elif action in ['reset', 'unbind', 'r']:
        # SID sıfırlama
        loading_msg = await ctx.send("⏳ SID sıfırlanıyor...")
        result = make_api_request('unbind-key', 'POST', {'key': target})
        await loading_msg.delete()
        
        if result.get('status') == 'success':
            embed = discord.Embed(
                title="✅ SID Sıfırlandı",
                description=f"**Key:** `{target}`\n**Durum:** Key tekrar kullanılabilir",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title="❌ SID Sıfırlanamadı",
                description=f"**Hata:** {result.get('message', 'Bilinmeyen hata')}",
                color=0xff0000
            )
    
    elif action in ['info', 'i']:
        # Key bilgileri
        loading_msg = await ctx.send("⏳ Key bilgileri getiriliyor...")
        result = make_api_request('key-info', 'POST', {'key': target})
        await loading_msg.delete()
        
        if result.get('status') == 'success':
            bound = result.get('bound', False)
            sid = result.get('sid')
            key_type = result.get('type', 'Legacy')
            
            if bound:
                embed = discord.Embed(
                    title="🔒 Key Bilgileri (Bağlı)",
                    description=f"**Key:** `{target}`\n**Tip:** {key_type}\n**SID:** `{sid[:8]}...`",
                    color=0xff9900
                )
                embed.add_field(name="⚠️ Durum", value="Bu key şu anda kullanımda", inline=False)
            else:
                embed = discord.Embed(
                    title="🔓 Key Bilgileri (Kullanılabilir)",
                    description=f"**Key:** `{target}`\n**Tip:** {key_type}\n**SID:** Bağlı değil",
                    color=0x00ff00
                )
                embed.add_field(name="✅ Durum", value="Bu key kullanılabilir", inline=False)
        else:
            embed = discord.Embed(
                title="❌ Key Bulunamadı",
                description=f"**Hata:** {result.get('message', 'Bilinmeyen hata')}",
                color=0xff0000
            )
    
    elif action in ['test', 't']:
        # Key test etme
        loading_msg = await ctx.send("⏳ Key test ediliyor...")
        test_sid = f"test-{ctx.author.id}-{int(datetime.datetime.now().timestamp())}"
        result = make_api_request('key-login', 'POST', {'key': target, 'sid': test_sid})
        await loading_msg.delete()
        
        if result.get('authenticated') and result.get('status') == 'success':
            embed = discord.Embed(
                title="✅ Key Geçerli",
                description=f"**Key:** `{target}`\n**Test SID:** `{test_sid[:12]}...`\n**Sonuç:** Başarılı ✅",
                color=0x00ff00
            )
            embed.add_field(name="📝 Detay", value=result.get('message', 'Authentication successful'), inline=False)
        else:
            embed = discord.Embed(
                title="❌ Key Test Başarısız",
                description=f"**Key:** `{target}`\n**Sonuç:** Başarısız ❌",
                color=0xff0000
            )
            embed.add_field(name="📝 Hata", value=result.get('message', 'Bilinmeyen hata'), inline=False)
    
    else:
        embed = discord.Embed(
            title="❌ Geçersiz Eylem",
            description=f"**'{action}'** geçersiz bir eylem!\n\n**Geçerli eylemler:** delete, reset, info, test",
            color=0xff0000
        )
    
    embed.set_footer(text=f"İşlem yapan: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    await ctx.send(embed=embed)

@bot.command(name='ban', aliases=['b'])
async def ban_management(ctx, action=None, target=None):
    """🚫 Ban yönetimi - Kullanım: !ban <action> <target>"""
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
    
    if action is None:
        embed = discord.Embed(
            title="🚫 Ban Yönetimi",
            description="**Kullanım:** `!ban <action> <target>`",
            color=0xff0000
        )
        embed.add_field(
            name="📝 Eylemler",
            value="• `user <username>` - Kullanıcı banla\n• `unuser <username>` - Kullanıcı ban kaldır\n• `ip <ip>` - IP banla\n• `unip <ip>` - IP ban kaldır",
            inline=False
        )
        embed.add_field(
            name="💡 Örnekler",
            value="`!ban user testuser`\n`!ban ip 192.168.1.100`\n`!ban unuser testuser`",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    if target is None:
        embed = discord.Embed(
            title="❌ Eksik Parametre",
            description=f"**{action}** eylemi için hedef belirtmelisin!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    action = action.lower()
    
    if action in ['user', 'u']:
        # Kullanıcı banlama
        loading_msg = await ctx.send("⏳ Kullanıcı banlanıyor...")
        result = make_api_request('ban-user', 'POST', {'username': target})
        await loading_msg.delete()
        
        if result.get('status') == 'success':
            embed = discord.Embed(
                title="🚫 Kullanıcı Banlandı",
                description=f"**Username:** `{target}`\n**Durum:** Banlandı",
                color=0xff0000
            )
            embed.add_field(name="📝 Not", value="Bu kullanıcı artık uygulamayı kullanamayacak", inline=False)
        else:
            embed = discord.Embed(
                title="❌ Hata",
                description=f"Kullanıcı banlanamadı: {result.get('message', 'Bilinmeyen hata')}",
                color=0xff0000
            )
    
    elif action in ['unuser', 'uu']:
        # Kullanıcı ban kaldırma
        loading_msg = await ctx.send("⏳ Ban kaldırılıyor...")
        result = make_api_request('unban-user', 'POST', {'username': target})
        await loading_msg.delete()
        
        if result.get('status') == 'success':
            embed = discord.Embed(
                title="✅ Ban Kaldırıldı",
                description=f"**Username:** `{target}`\n**Durum:** Ban kaldırıldı",
                color=0x00ff00
            )
            embed.add_field(name="📝 Not", value="Bu kullanıcı artık uygulamayı kullanabilir", inline=False)
        else:
            embed = discord.Embed(
                title="❌ Hata",
                description=f"Ban kaldırılamadı: {result.get('message', 'Bilinmeyen hata')}",
                color=0xff0000
            )
    
    elif action in ['ip']:
        # IP banlama
        loading_msg = await ctx.send("⏳ IP banlanıyor...")
        result = make_api_request('ban-ip', 'POST', {'ip': target})
        await loading_msg.delete()
        
        if result.get('status') == 'success':
            embed = discord.Embed(
                title="🚫 IP Banlandı",
                description=f"**IP:** `{target}`\n**Durum:** Banlandı",
                color=0xff0000
            )
            embed.add_field(name="📝 Not", value="Bu IP adresi artık API'ye erişemeyecek", inline=False)
        else:
            embed = discord.Embed(
                title="❌ Hata",
                description=f"IP banlanamadı: {result.get('message', 'Bilinmeyen hata')}",
                color=0xff0000
            )
    
    elif action in ['unip']:
        # IP ban kaldırma
        loading_msg = await ctx.send("⏳ IP ban kaldırılıyor...")
        result = make_api_request('unban-ip', 'POST', {'ip': target})
        await loading_msg.delete()
        
        if result.get('status') == 'success':
            embed = discord.Embed(
                title="✅ IP Ban Kaldırıldı",
                description=f"**IP:** `{target}`\n**Durum:** Ban kaldırıldı",
                color=0x00ff00
            )
            embed.add_field(name="📝 Not", value="Bu IP adresi artık API'ye erişebilir", inline=False)
        else:
            embed = discord.Embed(
                title="❌ Hata",
                description=f"IP ban kaldırılamadı: {result.get('message', 'Bilinmeyen hata')}",
                color=0xff0000
            )
    
    else:
        embed = discord.Embed(
            title="❌ Geçersiz Eylem",
            description=f"**'{action}'** geçersiz bir eylem!\n\n**Geçerli eylemler:** user, unuser, ip, unip",
            color=0xff0000
        )
    
    embed.set_footer(text=f"İşlem yapan: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    await ctx.send(embed=embed)

@bot.command(name='stats', aliases=['s'])
async def show_stats(ctx):
    """📊 Sistem istatistikleri"""
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
        
    loading_msg = await ctx.send("⏳ İstatistikler getiriliyor...")
    
    result = make_api_request('stats')
    
    await loading_msg.delete()
    
    if result.get('status') in ['success', 'online']:
        embed = discord.Embed(
            title="📊 Keylogin Sistem İstatistikleri",
            color=0x0099ff
        )
        
        # Ana istatistikler
        total_keys = result.get('total_keys', 0)
        bound_keys = result.get('bound_keys', 0)
        available_keys = result.get('available_keys', 0)
        
        embed.add_field(name="🔑 Toplam Key", value=f"**{total_keys}**", inline=True)
        embed.add_field(name="🔒 Bağlı Key", value=f"**{bound_keys}**", inline=True)
        embed.add_field(name="🔓 Kullanılabilir", value=f"**{available_keys}**", inline=True)
        
        # Kullanım oranı
        if total_keys > 0:
            usage_percent = round((bound_keys / total_keys) * 100, 1)
            embed.add_field(name="📈 Kullanım", value=f"**%{usage_percent}**", inline=True)
        
        embed.add_field(name="🚫 Banned User", value=f"**{result.get('banned_users', 0)}**", inline=True)
        embed.add_field(name="🔒 Banned IP", value=f"**{result.get('banned_ips', 0)}**", inline=True)
        
        # Sunucu bilgileri
        embed.add_field(name="🟢 Status", value=f"**{result.get('status', 'N/A').upper()}**", inline=True)
        embed.add_field(name="📦 Version", value=f"**{result.get('version', 'N/A')}**", inline=True)
        embed.add_field(name="🌐 Server", value="**midnightponywka.com**", inline=True)
        
        embed.set_footer(text=f"Son güncelleme: {datetime.datetime.now().strftime('%H:%M:%S')}")
    else:
        embed = discord.Embed(
            title="❌ Hata",
            description=f"İstatistikler alınamadı: {result.get('message', 'Bilinmeyen hata')}",
            color=0xff0000
        )
    
    await ctx.send(embed=embed)

@bot.command(name='help', aliases=['h'])
async def show_help(ctx):
    """❓ Yardım menüsü"""
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
        
    embed = discord.Embed(
        title="🤖 Keylogin Bot Komutları",
        description="**Basit ve güçlü key yönetim sistemi**",
        color=0x0099ff
    )
    
    # Ana komutlar
    embed.add_field(
        name="🔑 Key İşlemleri",
        value="`!key [type] [count]` - Key üret\n`!keys` - Key listesi\n`!manage <action> <target>` - Key yönetimi",
        inline=False
    )
    
    embed.add_field(
        name="🚫 Ban İşlemleri",
        value="`!ban <action> <target>` - Ban yönetimi",
        inline=False
    )
    
    embed.add_field(
        name="📊 Sistem",
        value="`!stats` - İstatistikler\n`!help` - Bu menü",
        inline=False
    )
    
    # Örnekler
    embed.add_field(
        name="💡 Hızlı Örnekler",
        value="• `!key premium 3` - 3 premium key üret\n• `!manage delete SPFR-1234-5678` - Key sil\n• `!ban user testuser` - Kullanıcı banla",
        inline=False
    )
    
    embed.set_footer(text="Keylogin Management Bot | Basit ve Etkili")
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    
    await ctx.send(embed=embed)

# Hata yakalama
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Bilinmeyen Komut",
            description=f"**'{ctx.message.content.split()[0]}'** komutu bulunamadı.\n\n`!help` ile komutları görebilirsin.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Eksik Parametre",
            description=f"Bu komut için gerekli parametreler eksik.\n\n`!help` ile yardım alabilirsin.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Beklenmeyen Hata",
            description=f"Bir hata oluştu: {str(error)}",
            color=0xff0000
        )
        await ctx.send(embed=embed)
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
