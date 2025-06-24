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
        async with aiohttp.ClientSession() as session:
            if data:
                async with session.post(url, data=data) as response:
                    return await response.json()
            else:
                async with session.get(url) as response:
                    return await response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Key generation
def generate_key(key_type="normal"):
    if key_type.lower() == "vip":
        return f"SPFR-VIP-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"
    elif key_type.lower() in ["premium", "prem"]:
        return f"SPFR-PREM-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"
    else:
        return f"SPFR-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"

# 1. !key [tip] [sayı] - Key üretme
@bot.command(name='key')
async def key_command(ctx, key_type="normal", count=1):
    try:
        count = int(count)
        if count < 1 or count > 10:
            await ctx.send("❌ Key sayısı 1-10 arasında olmalı!")
            return
            
        # Tip kontrolü
        if key_type.lower() not in ["normal", "premium", "prem", "vip"]:
            await ctx.send("❌ Geçersiz tip! Kullanım: `!key [normal/premium/vip] [sayı]`")
            return
            
        # Key'leri üret ve ekle
        generated_keys = []
        failed_keys = []
        
        for i in range(count):
            new_key = generate_key(key_type)
            result = await make_api_request("add-key", {"key": new_key})
            
            if result.get("status") == "success":
                generated_keys.append(new_key)
            else:
                failed_keys.append(new_key)
        
        # Sonuçları göster
        if generated_keys:
            keys_text = "\n".join([f"`{key}`" for key in generated_keys])
            type_emoji = "👑" if key_type.lower() == "vip" else "💎" if key_type.lower() in ["premium", "prem"] else "🔑"
            await ctx.send(f"{type_emoji} **{len(generated_keys)} adet {key_type.upper()} key oluşturuldu:**\n{keys_text}")
        
        if failed_keys:
            await ctx.send(f"❌ {len(failed_keys)} key oluşturulamadı (muhtemelen zaten var)")
            
    except ValueError:
        await ctx.send("❌ Geçersiz sayı! Kullanım: `!key [tip] [sayı]`")
    except Exception as e:
        await ctx.send(f"❌ Hata: {str(e)}")

# 2. !keylist - Key listesi
@bot.command(name='keylist')
async def keylist_command(ctx):
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
            for key in vip_keys[:5]:  # İlk 5'ini göster
                status = "🔗 Bağlı" if key.get("bound") else "🆓 Boş"
                message += f"`{key['key']}` - {status}\n"
            if len(vip_keys) > 5:
                message += f"... ve {len(vip_keys) - 5} tane daha\n"
            message += "\n"
            
        if premium_keys:
            message += "💎 **Premium Keys:**\n"
            for key in premium_keys[:5]:
                status = "🔗 Bağlı" if key.get("bound") else "🆓 Boş"
                message += f"`{key['key']}` - {status}\n"
            if len(premium_keys) > 5:
                message += f"... ve {len(premium_keys) - 5} tane daha\n"
            message += "\n"
            
        if normal_keys:
            message += "🔑 **Normal Keys:**\n"
            for key in normal_keys[:5]:
                status = "🔗 Bağlı" if key.get("bound") else "🆓 Boş"
                message += f"`{key['key']}` - {status}\n"
            if len(normal_keys) > 5:
                message += f"... ve {len(normal_keys) - 5} tane daha\n"
            message += "\n"
            
        if legacy_keys:
            message += "📜 **Legacy Keys:**\n"
            for key in legacy_keys[:3]:
                status = "🔗 Bağlı" if key.get("bound") else "🆓 Boş"
                message += f"`{key['key']}` - {status}\n"
            if len(legacy_keys) > 3:
                message += f"... ve {len(legacy_keys) - 3} tane daha\n"
            message += "\n"
        
        # İstatistikler
        total = result.get("total_keys", 0)
        bound = result.get("bound_keys", 0)
        available = result.get("available_keys", 0)
        
        message += f"📊 **Toplam:** {total} | **Bağlı:** {bound} | **Boş:** {available}"
        
        await ctx.send(message[:2000])  # Discord limit
    else:
        await ctx.send(f"❌ Hata: {result.get('message', 'Bilinmeyen hata')}")

# 3. !delete <key> - Key silme
@bot.command(name='delete')
async def delete_command(ctx, key=None):
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

# 8. !bansid <sid> - SID ban
@bot.command(name='bansid')
async def bansid_command(ctx, sid=None):
    if not sid:
        await ctx.send("❌ SID belirtmelisiniz! Kullanım: `!bansid <sid>`")
        return
    
    result = await make_api_request("ban-sid", {"sid": sid})
    
    if result.get("status") == "success":
        await ctx.send(f"🔨 SID banlandı: `{sid}`")
    else:
        await ctx.send(f"❌ Hata: {result.get('message', 'SID banlanamadı')}")

# 9. !unbansid <sid> - SID unban
@bot.command(name='unbansid')
async def unbansid_command(ctx, sid=None):
    if not sid:
        await ctx.send("❌ SID belirtmelisiniz! Kullanım: `!unbansid <sid>`")
        return
    
    result = await make_api_request("unban-sid", {"sid": sid})
    
    if result.get("status") == "success":
        await ctx.send(f"✅ SID banı kaldırıldı: `{sid}`")
    else:
        await ctx.send(f"❌ Hata: {result.get('message', 'SID ban kaldırılamadı')}")

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
    help_text = """🔰 **KEYLOGIN BOT KOMUTLARI**

**🔑 Key İşlemleri:**
`!key [tip] [sayı]` - Key üret (normal/premium/vip)
`!keylist` - Key listesi
`!delete <key>` - Key sil
`!reset <key>` - Key SID resetle
`!keyinfo <key>` - Key bilgisi

**🔨 Ban İşlemleri:**
`!ban <user>` - Kullanıcı banla
`!unban <user>` - Kullanıcı ban kaldır
`!bansid <sid>` - SID banla
`!unbansid <sid>` - SID ban kaldır
`!userinfo <user>` - Kullanıcı durumu

**📊 Sistem:**
`!stats` - İstatistikler
`!help` - Bu yardım menüsü

**Örnek:** `!key vip 3` - 3 adet VIP key üret"""

    await ctx.send(help_text)

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
