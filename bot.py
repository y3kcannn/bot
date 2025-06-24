import discord
from discord.ext import commands
import requests
import json
import asyncio
import datetime
import random
import string
import os

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

def generate_key():
    """Güzel format ile key üret: SPFR-XXXX-XXXX"""
    prefix = "SPFR"
    chars = string.ascii_uppercase + string.digits
    segment1 = ''.join(random.choice(chars) for _ in range(4))
    segment2 = ''.join(random.choice(chars) for _ in range(4))
    return f"{prefix}-{segment1}-{segment2}"

@bot.command(name='key')
async def generate_key_command(ctx, count=None):
    """Key üret - Kullanım: !key [sayı]"""
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
    
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
    
    # Loading mesajı
    loading_msg = await ctx.send(f"⏳ {count} adet key üretiliyor...")
    
    # Key'leri üret ve sisteme ekle
    generated_keys = []
    failed_keys = []
    
    for i in range(count):
        # Unique key üret (10 deneme)
        for attempt in range(10):
            new_key = generate_key()
            
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
                        failed_keys.append("Key eklenemedi")
            else:
                # Key zaten mevcut, yeni key dene
                if attempt == 9:  # Son deneme
                    failed_keys.append("Unique key üretilemedi")
    
    await loading_msg.delete()
    
    # Sonuçları göster
    if generated_keys:
        # Başarılı key'ler
        embed = discord.Embed(
            title=f"🔑 {len(generated_keys)} Key Üretildi",
            color=0x0099ff
        )
        
        # Key'leri göster
        key_list = []
        for i, key in enumerate(generated_keys, 1):
            key_list.append(f"`{key}`")
        
        embed.add_field(
            name="Üretilen Key'ler",
            value='\n'.join(key_list),
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    else:
        # Hiç key üretilemedi
        embed = discord.Embed(
            title="❌ Key Üretilemedi",
            description="Tekrar dene",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='delkey')
async def delete_key(ctx, key=None):
    """Key sil - Kullanım: !delkey <key>"""
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
    
    if key is None:
        embed = discord.Embed(
            title="❌ Hatalı Kullanım",
            description="**Kullanım:** `!delkey <key>`\n**Örnek:** `!delkey ABC123DEF456`",
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

@bot.command(name='hwidreset')
async def hwid_reset(ctx, key=None):
    """Key'i SID'den ayır - Kullanım: !hwidreset <key>"""
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
    
    if key is None:
        embed = discord.Embed(
            title="❌ Hatalı Kullanım",
            description="**Kullanım:** `!hwidreset <key>`\n**Örnek:** `!hwidreset ABC123DEF456`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Onay mesajı
    confirm_embed = discord.Embed(
        title="⚠️ HWID Reset Onayı",
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
            loading_msg = await ctx.send("⏳ HWID reset yapılıyor...")
            result = make_api_request('unbind-key', 'POST', {'key': key})
            await loading_msg.delete()
            
            if result.get('status') == 'success':
                embed = discord.Embed(
                    title="✅ HWID Reset Başarılı",
                    description=f"**Key:** `{key}`\n**Durum:** Kullanılabilir\n**SID:** Bağlantı kaldırıldı",
                    color=0x00ff00
                )
                embed.add_field(name="📝 Not", value="Key artık tekrar kullanılabilir", inline=False)
                embed.set_footer(text=f"İşlemi yapan: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            else:
                embed = discord.Embed(
                    title="❌ HWID Reset Başarısız",
                    description=f"**Hata:** {result.get('message', 'Bilinmeyen hata')}",
                    color=0xff0000
                )
        else:
            embed = discord.Embed(
                title="❌ İşlem İptal Edildi",
                description="HWID reset işlemi iptal edildi.",
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

@bot.command(name='keys')
async def list_keys(ctx):
    """Tüm key'leri listele (SID bilgisi ile)"""
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
                    
                    key_list.append(f"🔑 `{key}` {status_icon} {status_text}")
                
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
                
                embed.set_footer(text=f"Sayfa {page + 1}/{total_pages} • 🔒=Bağlı 🔓=Kullanılabilir")
                
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="📋 Key Listesi",
                description="Henüz hiç key eklenmemiş.",
                color=0xffa500
            )
            embed.add_field(name="💡 İpucu", value="• Yeni key üretmek için `!key` komutunu kullanın", inline=False)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Hata",
            description=f"Key'ler alınamadı: {result.get('message', 'Bilinmeyen hata')}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='test')
async def test_key(ctx, key=None):
    """Key'i test et - Kullanım: !test <key>"""
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
    
    if key is None:
        embed = discord.Embed(
            title="❌ Hatalı Kullanım",
            description="**Kullanım:** `!test <key>`\n**Örnek:** `!test ABC123DEF456`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
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

@bot.command(name='ban')
async def ban_user(ctx, username=None):
    """Kullanıcı banla - Kullanım: !ban <username>"""
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
    
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
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
    
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

@bot.command(name='help')
async def show_help(ctx):
    """Yardım menüsü"""
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
    
    embed = discord.Embed(
        title="🤖 Bot Komutları",
        color=0x0099ff
    )
    
    embed.add_field(
        name="🎯 Key Yönetimi",
        value="`!key [sayı]` - Key üret (1-10)\n"
              "`!delkey <key>` - Key sil\n"
              "`!keys` - Key listesi\n"
              "`!test <key>` - Key test",
        inline=False
    )
    
    embed.add_field(
        name="🔒 HWID Yönetimi",
        value="`!hwidreset <key>` - HWID reset (SID ayır)",
        inline=False
    )
    
    embed.add_field(
        name="👥 Kullanıcı Yönetimi",
        value="`!ban <user>` - Ban\n"
              "`!unban <user>` - Unban",
        inline=False
    )
    
    embed.add_field(
        name="🎨 Key Formatı",
        value="🔑 `SPFR-XXXX-XXXX`",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Hata yakalama
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Komut bulunamadı. `!help` yaz")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Eksik parametre. `!help` yaz")
    else:
        await ctx.send("❌ Hata oluştu")
        print(f"Error: {error}")

# Ana çalıştırma - Railway için optimize edilmiş
if __name__ == "__main__":
    bot.run(BOT_TOKEN) 
