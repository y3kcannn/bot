import discord
from discord.ext import commands
import requests
import json
import asyncio
import datetime
import os

# Bot ayarları - Railway'den environment variable'ı al
BOT_TOKEN = os.getenv('DISCORD_TOKEN')  # Railway'de DISCORD_TOKEN olarak kayıtlı
API_BASE_URL = "https://midnightponywka.com"
ADMIN_TOKEN = "ADMIN_API_SECRET_TOKEN_2024"

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
        activity=discord.Game(name="Keylogin SID Management | !help")
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

@bot.command(name='addkey', aliases=['add'])
async def add_key(ctx, key=None):
    """Key ekle - Kullanım: !addkey <key>"""
    if key is None:
        embed = discord.Embed(
            title="❌ Hatalı Kullanım",
            description="**Kullanım:** `!addkey <key>`\n**Örnek:** `!addkey ABC123DEF456`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Loading mesajı
    loading_msg = await ctx.send("⏳ Key ekleniyor...")
    
    result = make_api_request('add-key', 'POST', {'key': key})
    
    await loading_msg.delete()
    
    if result.get('status') == 'success':
        embed = discord.Embed(
            title="✅ Key Başarıyla Eklendi",
            description=f"**Key:** `{key}`\n**Durum:** Aktif (SID'ye bağlanmayı bekliyor)",
            color=0x00ff00
        )
        embed.add_field(name="📝 Not", value="Key artık C++ uygulamasında kullanılabilir\nİlk kullanımda otomatik olarak SID'ye bağlanacak", inline=False)
        embed.set_footer(text=f"Ekleyen: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    else:
        embed = discord.Embed(
            title="❌ Key Eklenemedi",
            description=f"**Hata:** {result.get('message', 'Bilinmeyen hata')}",
            color=0xff0000
        )
        embed.add_field(name="💡 Çözüm Önerileri", value="• Key formatını kontrol edin\n• Key zaten mevcut olabilir\n• Sunucu bağlantısını kontrol edin", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='deletekey', aliases=['delete', 'remove'])
async def delete_key(ctx, key=None):
    """Key sil - Kullanım: !deletekey <key>"""
    if key is None:
        embed = discord.Embed(
            title="❌ Hatalı Kullanım",
            description="**Kullanım:** `!deletekey <key>`\n**Örnek:** `!deletekey ABC123DEF456`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Onay mesajı
    confirm_embed = discord.Embed(
        title="⚠️ Key Silme Onayı",
        description=f"**Silinecek Key:** `{key}`\n\n**Bu işlem geri alınamaz!**\n**SID bağlantısı da silinecek!**",
        color=0xffa500
    )
    confirm_msg = await ctx.send(embed=confirm_embed)
    
    # Reaction'lar ekle
    await confirm_msg.add_reaction("✅")
    await confirm_msg.add_reaction("❌")
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == confirm_msg.id
    
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        
        if str(reaction.emoji) == "✅":
            # Key'i sil
            loading_msg = await ctx.send("⏳ Key siliniyor...")
            result = make_api_request('delete-key', 'POST', {'key': key})
            await loading_msg.delete()
            
            if result.get('status') == 'success':
                embed = discord.Embed(
                    title="✅ Key Başarıyla Silindi",
                    description=f"**Key:** `{key}`\n**Durum:** Silindi\n**SID Bağlantısı:** Temizlendi",
                    color=0x00ff00
                )
                embed.set_footer(text=f"Silen: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            else:
                embed = discord.Embed(
                    title="❌ Key Silinemedi",
                    description=f"**Hata:** {result.get('message', 'Bilinmeyen hata')}",
                    color=0xff0000
                )
        else:
            embed = discord.Embed(
                title="❌ İşlem İptal Edildi",
                description="Key silme işlemi iptal edildi.",
                color=0x808080
            )
        
        await confirm_msg.delete()
        await ctx.send(embed=embed)
        
    except asyncio.TimeoutError:
        await confirm_msg.delete()
        timeout_embed = discord.Embed(
            title="⏱️ Zaman Aşımı",
            description="30 saniye içinde cevap verilmediği için işlem iptal edildi.",
            color=0x808080
        )
        await ctx.send(embed=timeout_embed)

@bot.command(name='keylist', aliases=['keys', 'list'])
async def list_keys(ctx):
    """Tüm key'leri listele (SID bilgisi ile)"""
    loading_msg = await ctx.send("⏳ Key'ler getiriliyor...")
    
    result = make_api_request('list-keys')
    
    await loading_msg.delete()
    
    if result.get('status') == 'success':
        key_details = result.get('key_details', [])
        total_keys = result.get('total_keys', 0)
        bound_keys = result.get('bound_keys', 0)
        
        if key_details:
            # Key'leri sayfa sayfa göster (Discord embed limiti)
            keys_per_page = 8
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
                    
                    if bound:
                        status_icon = "🔒"
                        status_text = f"Bağlı (SID: `{sid[:8]}...`)"
                    else:
                        status_icon = "🔓"
                        status_text = "Kullanılabilir"
                    
                    key_list.append(f"{status_icon} `{key}` - {status_text}")
                
                embed = discord.Embed(
                    title="📋 Key Listesi (SID Durumu)",
                    description='\n'.join(key_list),
                    color=0x0099ff
                )
                
                # İstatistikler
                embed.add_field(
                    name="📊 İstatistikler",
                    value=f"**Toplam:** {total_keys} key\n**Bağlı:** {bound_keys} key\n**Kullanılabilir:** {total_keys - bound_keys} key",
                    inline=False
                )
                
                embed.set_footer(text=f"Sayfa {page + 1}/{total_pages} • 🔒 = SID'ye bağlı, 🔓 = Kullanılabilir")
                
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="📋 Key Listesi",
                description="Henüz hiç key eklenmemiş.",
                color=0xffa500
            )
            embed.add_field(name="💡 İpucu", value="Yeni key eklemek için `!addkey <key>` komutunu kullanın", inline=False)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Hata",
            description=f"Key'ler alınamadı: {result.get('message', 'Bilinmeyen hata')}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='testkey', aliases=['test', 'check'])
async def test_key(ctx, key=None, sid=None):
    """Key'i test et - Kullanım: !testkey <key> [sid]"""
    if key is None:
        embed = discord.Embed(
            title="❌ Hatalı Kullanım",
            description="**Kullanım:** `!testkey <key> [sid]`\n**Örnek:** `!testkey ABC123DEF456`\n**Örnek:** `!testkey ABC123DEF456 test-sid-123`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if sid is None:
        sid = f"test-{ctx.author.id}-{int(datetime.datetime.now().timestamp())}"
    
    loading_msg = await ctx.send("⏳ Key test ediliyor...")
    
    result = make_api_request('key-login', 'POST', {'key': key, 'sid': sid})
    
    await loading_msg.delete()
    
    if result.get('authenticated') and result.get('status') == 'success':
        embed = discord.Embed(
            title="✅ Key Geçerli",
            description=f"**Test Edilen Key:** `{key}`\n**SID:** `{sid}`\n**Sonuç:** Başarılı ✅",
            color=0x00ff00
        )
        embed.add_field(name="📝 Detay", value=result.get('message', 'Authentication successful'), inline=False)
        embed.add_field(name="🕒 Test Zamanı", value=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), inline=True)
    else:
        embed = discord.Embed(
            title="❌ Key Test Başarısız",
            description=f"**Test Edilen Key:** `{key}`\n**SID:** `{sid}`\n**Sonuç:** Başarısız ❌",
            color=0xff0000
        )
        embed.add_field(name="📝 Hata", value=result.get('message', 'Bilinmeyen hata'), inline=False)
        embed.add_field(name="💡 Çözüm", value="• Key'in doğru yazıldığından emin olun\n• Key başka bir SID'ye bağlı olabilir\n• Key'in sistemde kayıtlı olduğunu kontrol edin", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='keyinfo', aliases=['info'])
async def key_info(ctx, key=None):
    """Key bilgilerini göster - Kullanım: !keyinfo <key>"""
    if key is None:
        embed = discord.Embed(
            title="❌ Hatalı Kullanım",
            description="**Kullanım:** `!keyinfo <key>`\n**Örnek:** `!keyinfo ABC123DEF456`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    loading_msg = await ctx.send("⏳ Key bilgileri getiriliyor...")
    
    result = make_api_request('key-info', 'POST', {'key': key})
    
    await loading_msg.delete()
    
    if result.get('status') == 'success':
        bound = result.get('bound', False)
        sid = result.get('sid')
        status = result.get('status', 'unknown')
        
        if bound:
            embed = discord.Embed(
                title="🔒 Key Bilgileri (Bağlı)",
                description=f"**Key:** `{key}`\n**Durum:** Bağlı\n**SID:** `{sid}`",
                color=0xff9900
            )
            embed.add_field(name="⚠️ Uyarı", value="Bu key şu anda bir kullanıcıya bağlı.\nBaşka kullanıcılar bu key'i kullanamaz.", inline=False)
            embed.add_field(name="🔧 İşlemler", value="`!unbindkey <key>` - Key'i SID'den ayır", inline=False)
        else:
            embed = discord.Embed(
                title="🔓 Key Bilgileri (Kullanılabilir)",
                description=f"**Key:** `{key}`\n**Durum:** Kullanılabilir\n**SID:** Bağlı değil",
                color=0x00ff00
            )
            embed.add_field(name="✅ Bilgi", value="Bu key henüz hiçbir kullanıcıya bağlı değil.\nİlk kullanan kişiye otomatik bağlanacak.", inline=False)
        
        embed.set_footer(text=f"Sorgulayan: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    else:
        embed = discord.Embed(
            title="❌ Hata",
            description=f"Key bilgileri alınamadı: {result.get('message', 'Bilinmeyen hata')}",
            color=0xff0000
        )
    
    await ctx.send(embed=embed)

@bot.command(name='unbindkey', aliases=['unbind'])
async def unbind_key(ctx, key=None):
    """Key'i SID'den ayır - Kullanım: !unbindkey <key>"""
    if key is None:
        embed = discord.Embed(
            title="❌ Hatalı Kullanım",
            description="**Kullanım:** `!unbindkey <key>`\n**Örnek:** `!unbindkey ABC123DEF456`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Onay mesajı
    confirm_embed = discord.Embed(
        title="⚠️ Key SID Ayırma Onayı",
        description=f"**Key:** `{key}`\n\n**Bu key SID bağlantısından ayrılacak!**\nKey tekrar kullanılabilir hale gelecek.",
        color=0xffa500
    )
    confirm_msg = await ctx.send(embed=confirm_embed)
    
    # Reaction'lar ekle
    await confirm_msg.add_reaction("✅")
    await confirm_msg.add_reaction("❌")
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == confirm_msg.id
    
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        
        if str(reaction.emoji) == "✅":
            # Key'i SID'den ayır
            loading_msg = await ctx.send("⏳ Key SID'den ayrılıyor...")
            result = make_api_request('unbind-key', 'POST', {'key': key})
            await loading_msg.delete()
            
            if result.get('status') == 'success':
                embed = discord.Embed(
                    title="✅ Key SID'den Ayrıldı",
                    description=f"**Key:** `{key}`\n**Durum:** Kullanılabilir\n**SID:** Bağlantı kaldırıldı",
                    color=0x00ff00
                )
                embed.add_field(name="📝 Not", value="Key artık tekrar kullanılabilir", inline=False)
                embed.set_footer(text=f"İşlemi yapan: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            else:
                embed = discord.Embed(
                    title="❌ Key Ayrılamadı",
                    description=f"**Hata:** {result.get('message', 'Bilinmeyen hata')}",
                    color=0xff0000
                )
        else:
            embed = discord.Embed(
                title="❌ İşlem İptal Edildi",
                description="Key SID ayırma işlemi iptal edildi.",
                color=0x808080
            )
        
        await confirm_msg.delete()
        await ctx.send(embed=embed)
        
    except asyncio.TimeoutError:
        await confirm_msg.delete()
        timeout_embed = discord.Embed(
            title="⏱️ Zaman Aşımı",
            description="30 saniye içinde cevap verilmediği için işlem iptal edildi.",
            color=0x808080
        )
        await ctx.send(embed=timeout_embed)

@bot.command(name='stats', aliases=['status'])
async def show_stats(ctx):
    """Sistem istatistiklerini göster"""
    loading_msg = await ctx.send("⏳ İstatistikler getiriliyor...")
    
    result = make_api_request('stats')
    
    await loading_msg.delete()
    
    if result.get('status') in ['success', 'online']:  # Both success and online are valid
        embed = discord.Embed(
            title="📊 Keylogin SID Sistem İstatistikleri",
            color=0x0099ff
        )
        
        # Ana istatistikler
        total_keys = result.get('total_keys', 0)
        bound_keys = result.get('bound_keys', 0)
        available_keys = result.get('available_keys', 0)
        
        embed.add_field(name="🔑 Toplam Key", value=f"**{total_keys}** adet", inline=True)
        embed.add_field(name="🔒 Bağlı Key", value=f"**{bound_keys}** adet", inline=True)
        embed.add_field(name="🔓 Kullanılabilir", value=f"**{available_keys}** adet", inline=True)
        
        # Kullanım oranı
        if total_keys > 0:
            usage_percent = round((bound_keys / total_keys) * 100, 1)
            embed.add_field(name="📈 Kullanım Oranı", value=f"**%{usage_percent}**", inline=True)
        
        embed.add_field(name="🚫 Banned User", value=f"**{result.get('banned_users', 0)}** kişi", inline=True)
        embed.add_field(name="📦 API Version", value=f"**{result.get('version', 'N/A')}**", inline=True)
        
        # Sunucu bilgileri
        embed.add_field(name="🕒 Server Time", value=result.get('server_time', 'N/A'), inline=False)
        embed.add_field(name="🟢 API Status", value=f"**{result.get('status', 'N/A').upper()}**", inline=True)
        embed.add_field(name="🌐 Server", value="midnightponywka.com", inline=True)
        
        embed.set_footer(text=f"Son güncelleme: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        embed = discord.Embed(
            title="❌ Hata",
            description=f"İstatistikler alınamadı: {result.get('message', 'Bilinmeyen hata')}",
            color=0xff0000
        )
    
    await ctx.send(embed=embed)

@bot.command(name='ban')
async def ban_user(ctx, username=None):
    """Kullanıcı banla - Kullanım: !ban <username>"""
    if username is None:
        embed = discord.Embed(
            title="❌ Hatalı Kullanım",
            description="**Kullanım:** `!ban <username>`\n**Örnek:** `!ban testuser`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    loading_msg = await ctx.send("⏳ Kullanıcı banlanıyor...")
    
    result = make_api_request('ban-user', 'POST', {'username': username})
    
    await loading_msg.delete()
    
    if result.get('status') == 'success':
        embed = discord.Embed(
            title="🚫 Kullanıcı Banlandı",
            description=f"**Username:** `{username}`\n**Durum:** Banlandı",
            color=0xff0000
        )
        embed.add_field(name="📝 Not", value="Bu kullanıcı artık C++ uygulamasını kullanamayacak", inline=False)
        embed.set_footer(text=f"Banlayan: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    else:
        embed = discord.Embed(
            title="❌ Hata",
            description=f"Kullanıcı banlanamadı: {result.get('message', 'Bilinmeyen hata')}",
            color=0xff0000
        )
    
    await ctx.send(embed=embed)

@bot.command(name='unban')
async def unban_user(ctx, username=None):
    """Kullanıcı ban kaldır - Kullanım: !unban <username>"""
    if username is None:
        embed = discord.Embed(
            title="❌ Hatalı Kullanım",
            description="**Kullanım:** `!unban <username>`\n**Örnek:** `!unban testuser`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    loading_msg = await ctx.send("⏳ Ban kaldırılıyor...")
    
    result = make_api_request('unban-user', 'POST', {'username': username})
    
    await loading_msg.delete()
    
    if result.get('status') == 'success':
        embed = discord.Embed(
            title="✅ Ban Kaldırıldı",
            description=f"**Username:** `{username}`\n**Durum:** Ban kaldırıldı",
            color=0x00ff00
        )
        embed.add_field(name="📝 Not", value="Bu kullanıcı artık C++ uygulamasını kullanabilir", inline=False)
        embed.set_footer(text=f"Ban kaldıran: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    else:
        embed = discord.Embed(
            title="❌ Hata",
            description=f"Ban kaldırılamadı: {result.get('message', 'Bilinmeyen hata')}",
            color=0xff0000
        )
    
    await ctx.send(embed=embed)

@bot.command(name='help', aliases=['yardim', 'commands'])
async def show_help(ctx):
    """Yardım menüsü"""
    embed = discord.Embed(
        title="🤖 Keylogin SID Bot Komutları",
        description="SID (System ID) tabanlı key yönetim sistemi:",
        color=0x0099ff
    )
    
    # Key yönetimi
    embed.add_field(
        name="🔑 Key Yönetimi",
        value="`!addkey <key>` - Yeni key ekle\n"
              "`!deletekey <key>` - Key'i sil\n"
              "`!keylist` - Tüm key'leri listele (SID durumu ile)\n"
              "`!testkey <key> [sid]` - Key'i SID ile test et",
        inline=False
    )
    
    # SID yönetimi
    embed.add_field(
        name="🔒 SID Yönetimi",
        value="`!keyinfo <key>` - Key SID bilgilerini göster\n"
              "`!unbindkey <key>` - Key'i SID'den ayır",
        inline=False
    )
    
    # Kullanıcı yönetimi
    embed.add_field(
        name="👥 Kullanıcı Yönetimi",
        value="`!ban <username>` - Kullanıcı banla\n"
              "`!unban <username>` - Ban kaldır",
        inline=False
    )
    
    # Sistem
    embed.add_field(
        name="📊 Sistem",
        value="`!stats` - Sistem istatistikleri\n"
              "`!help` - Bu yardım menüsü\n"
              "`!ping` - Bot gecikmesi",
        inline=False
    )
    
    # SID açıklaması
    embed.add_field(
        name="💡 SID Sistemi",
        value="• Her key sadece bir SID'ye bağlanabilir\n"
              "• Aynı key birden fazla kullanıcı tarafından kullanılamaz\n"
              "• Key ilk kullanımda otomatik olarak SID'ye bağlanır",
        inline=False
    )
    
    embed.set_footer(text="Keylogin SID Management Bot v2.0")
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping_command(ctx):
    """Bot gecikme süresi"""
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"**Bot Gecikmesi:** {latency}ms",
        color=0x00ff00 if latency < 100 else 0xffa500 if latency < 200 else 0xff0000
    )
    
    await ctx.send(embed=embed)

# Hata yakalama
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Bilinmeyen Komut",
            description=f"**'{ctx.message.content.split()[0]}'** komutu bulunamadı.\n\nMevcut komutları görmek için `!help` yazın.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Eksik Parametre",
            description=f"Bu komut için gerekli parametreler eksik.\n\nYardım için `!help` yazın.",
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

# Ana çalıştırma - Railway için optimize edilmiş
if __name__ == "__main__":
    print("🚀 Keylogin SID Discord Bot Starting...")
    print(f"🔑 Token Status: {'✅ Found' if BOT_TOKEN else '❌ Missing'}")
    print(f"🌐 API URL: {API_BASE_URL}")
    print("-" * 50)
    
    if not BOT_TOKEN:
        print("❌ HATA: DISCORD_TOKEN environment variable bulunamadı!")
        print("📝 Railway Variables sekmesinde DISCORD_TOKEN'ı kontrol et")
        # Railway için input() kullanma - direkt exit
        import sys
        sys.exit(1)
    
    try:
        bot.run(BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ HATA: Geçersiz bot token!")
        print("📝 Discord Developer Portal'dan doğru token'ı aldığından emin ol")
        import sys
        sys.exit(1)
    except Exception as e:
        print(f"❌ HATA: {e}")
        print("📝 Detaylı hata bilgisi için logları kontrol et")
        import sys
        sys.exit(1) 
