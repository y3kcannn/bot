import discord
import aiohttp
import os
import hmac
import hashlib
import time
import uuid
from discord.ext import commands

# Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
API_URL = os.getenv('API_URL')
API_TOKEN = os.getenv('TOKEN')
HMAC_SECRET = os.getenv('HMAC_SECRET')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Session for HTTP requests
session = None

def generate_signature(action, owner_id, loader="", key="", hwid=""):
    """HMAC signature oluşturur"""
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
    global session
    session = aiohttp.ClientSession()
    print(f"🚀 {bot.user} aktif!")
    
    # Bot aktifleşince help komutunu gönder
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="🤖 Midnight Auth Bot Aktif!",
                    description="Komutlar için `!help` yazın",
                    color=0x00ff00
                )
                await channel.send(embed=embed)
                break

@bot.event
async def on_disconnect():
    if session:
        await session.close()

@bot.event 
async def on_command(ctx):
    """Komut çalıştığında komut mesajını sil"""
    try:
        await ctx.message.delete()
    except:
        pass

@bot.command(name='stats')
async def stats(ctx):
    """API istatistiklerini gösterir"""
    try:
        async with session.post(f"{API_URL}?token={API_TOKEN}", 
                               data={'action': 'stats'},
                               headers={'User-Agent': 'DiscordBot'}) as response:
            
            if response.status == 200:
                try:
                    import json
                    data = json.loads(await response.text())
                    
                    embed = discord.Embed(
                        title="📊 Midnight Auth",
                        color=0x2f3136
                    )
                    
                    embed.add_field(name="🔑 Toplam", value=data.get('total_keys', 0), inline=True)
                    embed.add_field(name="✅ Kullanılan", value=data.get('used_keys', 0), inline=True)
                    embed.add_field(name="🟢 Aktif", value=data.get('active_keys', 0), inline=True)
                    embed.add_field(name="🚫 Ban", value=data.get('banned_users', 0), inline=True)
                    embed.add_field(name="⏰ Zaman", value=data.get('server_time', 'Bilinmiyor')[:19], inline=True)
                    embed.add_field(name="📡 Status", value="🟢 Online", inline=True)
                    
                    await ctx.send(embed=embed)
                    
                except:
                    await ctx.send("❌ Veri hatası")
            else:
                await ctx.send("❌ API erişilemez")
                
    except:
        await ctx.send("❌ Bağlantı hatası")

@bot.command(name='key')
async def create_key(ctx, loader: str):
    """Yeni key oluşturur ve DM ile gönderir (!key <loader>)"""
    try:
        owner_id = str(ctx.author.id)
        payload = generate_signature("create", owner_id, loader)
        
        async with session.post(f"{API_URL}?token={API_TOKEN}", 
                               data=payload,
                               headers={'User-Agent': 'DiscordBot'}) as response:
            
            result = await response.text()
            
            if "KEY_CREATED:" in result:
                key = result.split(": ")[1]
                
                # Key'i DM ile gönder
                dm_embed = discord.Embed(
                    title="🔑 Yeni Key Oluşturuldu",
                    color=0x00ff00
                )
                dm_embed.add_field(name="🔑 Key", value=f"```{key}```", inline=False)
                dm_embed.add_field(name="📁 Loader", value=loader, inline=True)
                dm_embed.add_field(name="⏰ Geçerlilik", value="7 gün", inline=True)
                dm_embed.add_field(name="👤 Sahibi", value=ctx.author.mention, inline=True)
                dm_embed.set_footer(text="Bu key'i güvende tutun!")
                
                # Kanal için onay mesajı
                public_embed = discord.Embed(
                    title="✅ Key Oluşturuldu",
                    description=f"**{ctx.author.mention}** için `{loader}` key'i oluşturuldu ve DM ile gönderildi.",
                    color=0x00ff00
                )
                public_embed.add_field(name="📁 Loader", value=loader, inline=True)
                public_embed.add_field(name="⏰ Süre", value="7 gün", inline=True)
                
                try:
                    # Önce DM'e gönder
                    await ctx.author.send(embed=dm_embed)
                    # Sonra kanala onay mesajı
                    await ctx.send(embed=public_embed)
                except discord.Forbidden:
                    # DM gönderilemezse kanala gönder ama uyarı ver
                    warning_embed = discord.Embed(
                        title="⚠️ DM Gönderilemedi",
                        description="Key oluşturuldu ama DM'iniz kapalı. Key'iniz aşağıda:",
                        color=0xffaa00
                    )
                    warning_embed.add_field(name="🔑 Key", value=f"```{key}```", inline=False)
                    warning_embed.add_field(name="📁 Loader", value=loader, inline=True)
                    warning_embed.add_field(name="⏰ Süre", value="7 gün", inline=True)
                    warning_embed.set_footer(text="DM'lerinizi açmanızı öneriyoruz!")
                    await ctx.send(embed=warning_embed)
                    
            else:
                await ctx.send(f"❌ {result}")
                
    except Exception as e:
        await ctx.send("❌ Key oluşturulamadı")

@bot.command(name='ban')
async def ban_user(ctx, loader: str, hwid: str):
    """Kullanıcı banlar (!ban <loader> <hwid>)"""
    try:
        owner_id = str(ctx.author.id)
        payload = generate_signature("ban", owner_id, loader, "", hwid)
        
        async with session.post(f"{API_URL}?token={API_TOKEN}", 
                               data=payload,
                               headers={'User-Agent': 'DiscordBot'}) as response:
            
            result = await response.text()
            
            if "BANNED_SUCCESS" in result:
                embed = discord.Embed(
                    title="🚫 Kullanıcı Banlandı",
                    color=0xff0000
                )
                embed.add_field(name="HWID", value=f"`{hwid[:16]}...`", inline=True)
                embed.add_field(name="Loader", value=loader, inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ {result}")
                
    except:
        await ctx.send("❌ Ban işlemi başarısız")

@bot.command(name='unban')
async def unban_user(ctx, loader: str, hwid: str):
    """Kullanıcı unbanlar (!unban <loader> <hwid>)"""
    try:
        owner_id = str(ctx.author.id)
        payload = generate_signature("unban", owner_id, loader, "", hwid)
        
        async with session.post(f"{API_URL}?token={API_TOKEN}", 
                               data=payload,
                               headers={'User-Agent': 'DiscordBot'}) as response:
            
            result = await response.text()
            
            if "UNBANNED" in result:
                embed = discord.Embed(
                    title="✅ Kullanıcı Unbanlandı",
                    color=0x00ff00
                )
                embed.add_field(name="HWID", value=f"`{hwid[:16]}...`", inline=True)
                embed.add_field(name="Loader", value=loader, inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ {result}")
                
    except:
        await ctx.send("❌ Unban işlemi başarısız")

@bot.command(name='reset')
async def reset_key(ctx, loader: str, key: str):
    """Key resetler (!reset <loader> <key>)"""
    try:
        owner_id = str(ctx.author.id)
        payload = generate_signature("reset", owner_id, loader, key)
        
        async with session.post(f"{API_URL}?token={API_TOKEN}", 
                               data=payload,
                               headers={'User-Agent': 'DiscordBot'}) as response:
            
            result = await response.text()
            
            if "KEY_RESET" in result:
                embed = discord.Embed(
                    title="♻️ Key Resetlendi",
                    color=0xffff00
                )
                embed.add_field(name="Key", value=f"`{key}`", inline=True)
                embed.add_field(name="Loader", value=loader, inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ {result}")
                
    except:
        await ctx.send("❌ Reset işlemi başarısız")

@bot.command(name='verify')
async def verify_key(ctx):
    """Key doğrulama sayfası verir"""
    try:
        discord_id = str(ctx.author.id)
        verify_code = f"VERIFY_{discord_id[-4:]}"  # Son 4 haneli basit kod
        
        # URL oluştur
        verify_url = f"https://midnightponywka.com/verify.html?discord_id={discord_id}&code={verify_code}"
        
        embed = discord.Embed(
            title="🔐 Key Doğrulama",
            color=0x00ff00
        )
        
        embed.add_field(name="🆔 Discord ID", value=f"`{discord_id}`", inline=False)
        embed.add_field(name="🔢 Doğrulama Kodu", value=f"`{verify_code}`", inline=False)
        embed.add_field(name="🌐 Doğrulama Sayfası", value=f"[Buraya tıkla]({verify_url})", inline=False)
        
        embed.set_footer(text="Bu bilgileri verify sayfasında kullanın")
        
        # Özel mesaj gönder
        try:
            await ctx.author.send(embed=embed)
            await ctx.send("✅ Doğrulama bilgileri özel mesajınıza gönderildi!")
        except:
            await ctx.send(embed=embed)
            
    except:
        await ctx.send("❌ Verify linki oluşturulamadı")

@bot.command(name='list')
async def list_keys(ctx):
    """Keylerini listeler"""
    try:
        owner_id = str(ctx.author.id)
        payload = generate_signature("list", owner_id)
        
        async with session.post(f"{API_URL}?token={API_TOKEN}", 
                               data=payload,
                               headers={'User-Agent': 'DiscordBot'}) as response:
            
            if response.status == 200:
                try:
                    import json
                    keys = json.loads(await response.text())
                    
                    if not keys:
                        await ctx.send("📝 Hiç key bulunamadı")
                        return
                    
                    embed = discord.Embed(
                        title="📝 Keyler",
                        color=0x2f3136
                    )
                    
                    for key_data in keys[:10]:  # İlk 10 key
                        status = "🔴 Kullanıldı" if key_data['used'] else "🟢 Aktif"
                        embed.add_field(
                            name=f"🔑 {key_data['key'][:8]}...",
                            value=f"{status}\n**Loader:** {key_data['loader']}\n**Süre:** {key_data.get('expires_at', 'Belirsiz')[:10]}",
                            inline=True
                        )
                    
                    if len(keys) > 10:
                        embed.set_footer(text=f"İlk 10 key gösteriliyor (Toplam: {len(keys)})")
                    
                    await ctx.send(embed=embed)
                    
                except:
                    await ctx.send("❌ Veri hatası")
            else:
                await ctx.send("❌ Keyler alınamadı")
                
    except:
        await ctx.send("❌ Liste işlemi başarısız")

@bot.command(name='ping')
async def ping(ctx):
    """Bot pingini gösterir"""
    embed = discord.Embed(
        title="🏓 Pong",
        description=f"{round(bot.latency * 1000)}ms",
        color=0x2f3136
    )
    await ctx.send(embed=embed)

@bot.command(name='help')
async def help_command(ctx):
    """Komutları gösterir"""
    embed = discord.Embed(
        title="🤖 Midnight Auth Komutları",
        color=0x2f3136
    )
    
    embed.add_field(name="📊 !stats", value="İstatistikler", inline=True)
    embed.add_field(name="🔑 !key <loader>", value="Yeni key oluştur", inline=True)
    embed.add_field(name="🔐 !verify", value="Key doğrulama sayfası", inline=True)
    embed.add_field(name="📝 !list", value="Keylerini listele", inline=True)
    embed.add_field(name="♻️ !reset <loader> <key>", value="Key resetle", inline=True)
    embed.add_field(name="🚫 !ban <loader> <hwid>", value="Kullanıcı banla", inline=True)
    embed.add_field(name="✅ !unban <loader> <hwid>", value="Kullanıcı unbanla", inline=True)
    embed.add_field(name="🏓 !ping", value="Ping kontrolü", inline=True)
    
    embed.set_footer(text="Örnek: !key TestLoader")
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Eksik parametre. `!help` komutuna bakın.")
    else:
        await ctx.send("❌ Hata oluştu")

if __name__ == "__main__":
    if not all([DISCORD_TOKEN, API_URL, API_TOKEN, HMAC_SECRET]):
        print("❌ Environment variables eksik!")
        exit(1)
    
    bot.run(DISCORD_TOKEN)
