import discord
from discord.ext import commands
import aiohttp
import json
import asyncio
import random
import string
import os

# Bot token - Railway environment variables
TOKEN = os.getenv('DISCORD_TOKEN') or os.getenv('BOT_TOKEN')

# Token kontrolü
if not TOKEN:
    print("❌ HATA: Bot token bulunamadı!")
    print("Railway Dashboard'da environment variable ekleyin:")
    print("1. https://railway.app/dashboard")
    print("2. Projenizi seçin")
    print("3. Variables sekmesine gidin")
    print("4. DISCORD_TOKEN = 'your_bot_token_here' ekleyin")
    exit(1)

# API ayarları
API_URL = "https://midnightponywka.com"
API_TOKEN = "ADMIN_API_SECRET_TOKEN_2024"

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'{bot.user} başarıyla giriş yaptı!')

# Helper function - API çağrıları
async def make_api_request(action, data=None):
    url = f"{API_URL}/?api=1&token={API_TOKEN}&action={action}"
    try:
        timeout = aiohttp.ClientTimeout(total=30)  # 30 saniye timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            if data:
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}
            else:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}
    except asyncio.TimeoutError:
        return {"status": "error", "message": "Request timeout"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Key generation - 16 basamaklı random
def generate_key(key_type="normal"):
    import time
    # Daha random seed için timestamp kullan
    random.seed(int(time.time() * 1000000) % 2**32)
    
    chars = string.ascii_uppercase + string.digits
    # 16 basamaklı random key: 1231ASD235FFS123 gibi
    return ''.join(random.choices(chars, k=16))

# 1. !key [sayı] - Key üretme (16 basamaklı)
@bot.command(name='key')
async def key_command(ctx, count=1):
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
    
    try:
        count = int(count)
        if count < 1 or count > 10:
            await ctx.send("❌ Key sayısı 1-10 arasında olmalı!")
            return
            
        # Key'leri üret ve ekle - Gelişmiş sistem
        generated_keys = []
        failed_keys = []
        
        for i in range(count):
            # 20 deneme yap unique key için (artırdık)
            key_generated = False
            last_error = "Unknown error"
            
            for attempt in range(20):
                new_key = generate_key()
                result = await make_api_request("add-key", {"key": new_key})
                
                # Response kontrolü
                if isinstance(result, dict):
                    if result.get("status") == "success":
                        generated_keys.append(new_key)
                        key_generated = True
                        break
                    elif "already exists" in result.get("message", "").lower():
                        # Key zaten var, tekrar dene
                        continue
                    else:
                        # Başka bir hata
                        last_error = result.get("message", "API error")
                        # Rate limit kontrolü
                        if "request" in last_error.lower() or "wait" in last_error.lower():
                            await asyncio.sleep(2)  # 2 saniye bekle
                            continue
                        break
                else:
                    # Response dict değilse
                    last_error = "Invalid API response"
                    break
                    
                # Her deneme arasında kısa pause
                if attempt < 19:
                    await asyncio.sleep(0.1)
            
            if not key_generated:
                failed_keys.append(f"Key {i+1}: {last_error}")
        
        # Sonuçları göster
        if generated_keys:
            embed = discord.Embed(
                title="🔑 Key Oluşturuldu",
                color=0x00ff00,  # Yeşil
                description=f"**{len(generated_keys)} adet key başarıyla oluşturuldu**"
            )
            
            # Key'leri embed field olarak ekle
            keys_text = "\n".join([f"`{key}`" for key in generated_keys])
            embed.add_field(
                name="📋 Key Listesi", 
                value=keys_text,
                inline=False
            )
            
            # Bot profil resmi
            if bot.user and bot.user.avatar:
                embed.set_thumbnail(url=bot.user.avatar.url)
            
            # Footer
            embed.set_footer(
                text="Keylogin Key Management",
                icon_url=bot.user.avatar.url if bot.user and bot.user.avatar else None
            )
            
            message = await ctx.send(embed=embed)
            # 10 saniye sonra bot mesajını sil
            await asyncio.sleep(10)
            try:
                await message.delete()
            except:
                pass
        
        if failed_keys:
            if len(failed_keys) == 1:
                message = await ctx.send(f"⚠️ 1 key oluşturulamadı. Sunucu yoğun, tekrar deneyin.")
            else:
                message = await ctx.send(f"⚠️ {len(failed_keys)} key oluşturulamadı. Sunucu yoğun, tekrar deneyin.")
            # 10 saniye sonra sil
            await asyncio.sleep(10)
            try:
                await message.delete()
            except:
                pass
            
    except ValueError:
        message = await ctx.send("❌ Geçersiz sayı girdiniz!")
        await asyncio.sleep(10)
        try:
            await message.delete()
        except:
            pass
    except Exception as e:
        error_msg = str(e)
        if "too many requests" in error_msg.lower():
            message = await ctx.send("⏳ Çok hızlı komut gönderiyorsunuz. Biraz bekleyin.")
        elif "connection" in error_msg.lower():
            message = await ctx.send("🔗 Sunucu bağlantı sorunu. Tekrar deneyin.")
        else:
            message = await ctx.send("❌ Beklenmeyen hata oluştu. Tekrar deneyin.")
        await asyncio.sleep(10)
        try:
            await message.delete()
        except:
            pass

# 2. !keylist - Key listesi
@bot.command(name='keylist')
async def keylist_command(ctx):
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
    
    result = await make_api_request("list-keys")
    
    if result.get("status") == "success":
        keys = result.get("key_details", [])
        if not keys:
            await ctx.send("📝 Hiç key bulunamadı!")
            return
            
        # Key'leri türe göre grupla
        vip_keys = [k for k in keys if k.get("type") == "VIP"]
        premium_keys = [k for k in keys if k.get("type") == "Premium"] 
        normal_keys = [k for k in keys if k.get("type") == "Normal"]
        legacy_keys = [k for k in keys if k.get("type") == "Legacy"]
        
        message = "📝 **KEY LİSTESİ**\n\n"
        
        if vip_keys:
            message += "👑 **VIP Keys:**\n"
            for key in vip_keys:  # Tüm VIP key'leri göster
                status = "🔗 Bağlı" if key.get("bound") else "🆓 Boş"
                message += f"`{key['key']}` - {status}\n"
            message += "\n"
            
        if premium_keys:
            message += "💎 **Premium Keys:**\n"
            for key in premium_keys:  # Tüm Premium key'leri göster
                status = "🔗 Bağlı" if key.get("bound") else "🆓 Boş"
                message += f"`{key['key']}` - {status}\n"
            message += "\n"
            
        if normal_keys:
            message += "🔑 **Normal Keys:**\n"
            for key in normal_keys:  # Tüm Normal key'leri göster
                status = "🔗 Bağlı" if key.get("bound") else "🆓 Boş"
                message += f"`{key['key']}` - {status}\n"
            message += "\n"
            
        if legacy_keys:
            message += "📜 **Legacy Keys:**\n"
            for key in legacy_keys:  # Tüm Legacy key'leri göster
                status = "🔗 Bağlı" if key.get("bound") else "🆓 Boş"
                message += f"`{key['key']}` - {status}\n"
            message += "\n"
        
        # İstatistikler
        total = result.get("total_keys", 0)
        bound = result.get("bound_keys", 0)
        available = result.get("available_keys", 0)
        
        message += f"📊 **Toplam:** {total} | **Bağlı:** {bound} | **Boş:** {available}"
        
        # Mesaj 2000 karakterden uzunsa parçalara böl
        if len(message) <= 2000:
            await ctx.send(message)
        else:
            # Mesajı parçalara böl
            parts = []
            current_part = ""
            lines = message.split('\n')
            
            for line in lines:
                if len(current_part + line + '\n') <= 1900:  # Biraz margin bırak
                    current_part += line + '\n'
                else:
                    if current_part:
                        parts.append(current_part.strip())
                    current_part = line + '\n'
            
            if current_part:
                parts.append(current_part.strip())
            
            # Her parçayı gönder
            for i, part in enumerate(parts):
                if i == 0:
                    await ctx.send(part)
                else:
                    await ctx.send(f"**Devamı (Sayfa {i+1}):**\n\n{part}")
    else:
        await ctx.send(f"❌ Hata: {result.get('message', 'Bilinmeyen hata')}")

# 3. !delete <key> - Key silme
@bot.command(name='delete')
async def delete_command(ctx, key=None):
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
    
    if not key:
        await ctx.send("❌ Key belirtmelisiniz! Kullanım: `!delete <key>`")
        return
    
    result = await make_api_request("delete-key", {"key": key})
    
    if result.get("status") == "success":
        await ctx.send(f"✅ Key silindi: `{key}`")
    else:
        await ctx.send(f"❌ Hata: {result.get('message', 'Key silinemedi')}")

# 4. !reset <key> - Key SID reset
@bot.command(name='reset')
async def reset_command(ctx, key=None):
    if not key:
        await ctx.send("❌ Key belirtmelisiniz! Kullanım: `!reset <key>`")
        return
    
    result = await make_api_request("unbind-key", {"key": key})
    
    if result.get("status") == "success":
        await ctx.send(f"✅ Key SID'i resetlendi: `{key}`")
    else:
        await ctx.send(f"❌ Hata: {result.get('message', 'SID resetlenemedi')}")

# 5. !keyinfo <key> - Key bilgisi
@bot.command(name='keyinfo')
async def keyinfo_command(ctx, key=None):
    if not key:
        await ctx.send("❌ Key belirtmelisiniz! Kullanım: `!keyinfo <key>`")
        return
    
    result = await make_api_request("key-info", {"key": key})
    
    if result.get("status") == "success":
        bound = result.get("bound", False)
        sid = result.get("sid", "Yok")
        key_type = result.get("type", "Unknown")
        created = result.get("created", "Bilinmiyor")
        
        type_emoji = "👑" if key_type == "VIP" else "💎" if key_type == "Premium" else "🔑" if key_type == "Normal" else "📜"
        status_emoji = "🔗" if bound else "🆓"
        
        message = f"{type_emoji} **Key Bilgisi**\n"
        message += f"🔑 **Key:** `{key}`\n"
        message += f"📁 **Tip:** {key_type}\n"
        message += f"{status_emoji} **Durum:** {'Bağlı' if bound else 'Boş'}\n"
        message += f"🆔 **SID:** `{sid if bound else 'Yok'}`\n"
        message += f"📅 **Oluşturulma:** {created}"
        
        await ctx.send(message)
    else:
        await ctx.send(f"❌ Hata: {result.get('message', 'Key bulunamadı')}")

# 6. !ban <user> - Kullanıcı ban
@bot.command(name='ban')
async def ban_command(ctx, username=None):
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
    
    if not username:
        await ctx.send("❌ Kullanıcı adı belirtmelisiniz! Kullanım: `!ban <username>`")
        return
    
    result = await make_api_request("ban-user", {"username": username})
    
    if result.get("status") == "success":
        await ctx.send(f"🔨 Kullanıcı banlandı: `{username}`")
    else:
        await ctx.send(f"❌ Hata: {result.get('message', 'Kullanıcı banlanamadı')}")

# 7. !unban <user> - Kullanıcı unban
@bot.command(name='unban')
async def unban_command(ctx, username=None):
    if not username:
        await ctx.send("❌ Kullanıcı adı belirtmelisiniz! Kullanım: `!unban <username>`")
        return
    
    result = await make_api_request("unban-user", {"username": username})
    
    if result.get("status") == "success":
        await ctx.send(f"✅ Kullanıcı banı kaldırıldı: `{username}`")
    else:
        await ctx.send(f"❌ Hata: {result.get('message', 'Ban kaldırılamadı')}")

# 8. (SID ban komutları kaldırıldı - !ban komutu otomatik SID banlar)

# 10. !userinfo <user> - Kullanıcı durumu
@bot.command(name='userinfo')
async def userinfo_command(ctx, username=None):
    if not username:
        await ctx.send("❌ Kullanıcı adı belirtmelisiniz! Kullanım: `!userinfo <username>`")
        return
    
    result = await make_api_request("check-ban", {"username": username})
    
    if result.get("banned"):
        ban_type = result.get("ban_type", "unknown")
        ban_target = result.get("ban_target", "unknown")
        await ctx.send(f"🔨 **{username}** banlandı!\n🎯 **Ban türü:** {ban_type}\n📍 **Ban hedefi:** `{ban_target}`")
    else:
        await ctx.send(f"✅ **{username}** banlı değil")

# 11. !stats - İstatistikler
@bot.command(name='stats')
async def stats_command(ctx):
    result = await make_api_request("stats")
    
    if result.get("status") == "success":
        total_keys = result.get("total_keys", 0)
        bound_keys = result.get("bound_keys", 0)
        available_keys = result.get("available_keys", 0)
        banned_users = result.get("banned_users", 0)
        banned_sids = result.get("banned_sids", 0)
        version = result.get("version", "Unknown")
        
        message = "📊 **SİSTEM İSTATİSTİKLERİ**\n\n"
        message += f"🔑 **Keys:** {total_keys} toplam\n"
        message += f"🔗 **Bağlı:** {bound_keys}\n"
        message += f"🆓 **Boş:** {available_keys}\n\n"
        message += f"🔨 **Banlı kullanıcı:** {banned_users}\n"
        message += f"🚫 **Banlı SID:** {banned_sids}\n\n"
        message += f"📱 **Versiyon:** {version}"
        
        await ctx.send(message)
    else:
        await ctx.send(f"❌ Hata: {result.get('message', 'İstatistikler alınamadı')}")

# 12. !help - Yardım
@bot.command(name='help')
async def help_command(ctx):
    # Kullanıcının mesajını sil
    try:
        await ctx.message.delete()
    except:
        pass
    
    # Güzel embed oluştur
    embed = discord.Embed(
        title="🤖 Keylogin Bot Komutları",
        description="Hardware spoofer key yönetim sistemi",
        color=0x00ff88
    )
    
    # Bot'un profil fotoğrafını ekle
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
    
    # Key işlemleri
    embed.add_field(
        name="🔑 Key İşlemleri",
        value="`!key` - Yeni key üret\n"
              "`!keylist` - Key listesini görüntüle\n"
              "`!delete <key>` - Key'i sistemden sil\n"
              "`!reset <key>` - Key'i sıfırla\n"
              "`!keyinfo <key>` - Key detaylarını göster",
        inline=False
    )
    
    # Ban işlemleri
    embed.add_field(
        name="🔨 Ban İşlemleri",
        value="`!ban <user>` - Kullanıcıyı tamamen banla\n"
              "`!unban <user>` - Kullanıcı banını kaldır\n"
              "`!userinfo <user>` - Kullanıcı durumunu kontrol et",
        inline=False
    )
    
    # Sistem
    embed.add_field(
        name="📊 Sistem",
        value="`!stats` - Sistem istatistikleri\n"
              "`!help` - Bu yardım menüsü",
        inline=False
    )
    
    # Footer
    embed.set_footer(
        text="Keylogin Management System | Sade ve Güçlü",
        icon_url=bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
    )
    
    await ctx.send(embed=embed)

# Bot'u çalıştır
if __name__ == "__main__":
    print("🚀 Keylogin Discord Bot Starting...")
    print(f"🌐 API URL: {API_URL}")
    print("-" * 50)
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ HATA: {e}")
        print("Token'ı kontrol edin veya yenileyin!")
        exit(1)
