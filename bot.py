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
                        title="📊 İstatistikler",
                        description=f"""🔑 **Toplam:** {data.get('total_keys', 0)}
✅ **Kullanılan:** {data.get('used_keys', 0)}
🟢 **Aktif:** {data.get('active_keys', 0)}
🚫 **Ban:** {data.get('banned_users', 0)}
📡 **Status:** Online
⏰ **Zaman:** {data.get('server_time', 'Bilinmiyor')[:19]}""",
                        color=0x2f3136
                    )
                    
                    await ctx.send(embed=embed)
                    
                except:
                    await ctx.send("❌ Veri hatası")
            else:
                await ctx.send("❌ API erişilemez")
                
    except:
        await ctx.send("❌ Bağlantı hatası")

@bot.command(name='key')
async def create_key(ctx, discord_user: str):
    """Yeni key oluşturur ve DM ile gönderir (!key @discordismi)"""
    try:
        owner_id = str(ctx.author.id)
        loader = "spoofer"  # Default loader
        payload = generate_signature("create", owner_id, loader)
        
        async with session.post(f"{API_URL}?token={API_TOKEN}", 
                               data=payload,
                               headers={'User-Agent': 'DiscordBot'}) as response:
            
            result = await response.text()
            
            if "KEY_CREATED:" in result:
                key = result.split(": ")[1]
                
                # Verify bilgileri oluştur
                discord_id = str(ctx.author.id)
                verify_code = f"VERIFY_{discord_id[-4:]}"
                verify_url = f"https://midnightponywka.com/verify?discord_id={discord_id}&code={verify_code}"
                
                # Key'i DM ile gönder
                dm_embed = discord.Embed(
                    title="🔑 Yeni Key Oluşturuldu",
                    color=0x00ff00
                )
                dm_embed.add_field(name="🔑 Key", value=f"```{key}```", inline=False)
                dm_embed.add_field(name="📁 Loader", value=loader, inline=True)
                dm_embed.add_field(name="⏰ Geçerlilik", value="7 gün", inline=True)
                dm_embed.add_field(name="👤 Hedef", value=discord_user, inline=True)
                
                # Verify bilgileri ekle
                dm_embed.add_field(name="🔐 Verify Sayfası", value=f"[Buraya tıkla]({verify_url})", inline=False)
                dm_embed.add_field(name="🆔 Discord ID", value=f"`{discord_id}`", inline=True)
                dm_embed.add_field(name="🔢 Verify Kodu", value=f"`{verify_code}`", inline=True)
                
                dm_embed.set_footer(text="Key'i güvende tutun ve verify sayfasında kullanın!")
                
                # Kanal için onay mesajı
                public_embed = discord.Embed(
                    title="✅ Key Oluşturuldu",
                    description=f"**{discord_user}** için `{loader}` key'i oluşturuldu ve DM ile gönderildi.",
                    color=0x00ff00
                )
                public_embed.add_field(name="📁 Loader", value=loader, inline=True)
                public_embed.add_field(name="⏰ Süre", value="7 gün", inline=True)
                public_embed.add_field(name="🔐 Verify", value="DM'de link var", inline=True)
                
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
                    warning_embed.add_field(name="🔐 Verify", value=f"[Link]({verify_url})", inline=True)
                    warning_embed.set_footer(text="DM'lerinizi açmanızı öneriyoruz!")
                    await ctx.send(embed=warning_embed)
                    
            else:
                await ctx.send(f"❌ {result}")
                
    except Exception as e:
        await ctx.send("❌ Key oluşturulamadı")

@bot.command(name='ban')
async def ban_user(ctx, discord_user: str):
    """Kullanıcı banlar (!ban @discordismi)"""
    try:
        owner_id = str(ctx.author.id)
        loader = "spoofer"
        hwid = discord_user  # Discord ismini HWID gibi kullan
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
async def unban_user(ctx, discord_user: str):
    """Kullanıcı unbanlar (!unban @discordismi)"""
    try:
        owner_id = str(ctx.author.id)
        loader = "spoofer"
        hwid = discord_user
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
async def reset_all_keys(ctx):
    """Tüm keyleri siler (!reset)"""
    try:
        owner_id = str(ctx.author.id)
        payload = generate_signature("reset_all", owner_id)
        
        async with session.post(f"{API_URL}?token={API_TOKEN}", 
                               data=payload,
                               headers={'User-Agent': 'DiscordBot'}) as response:
            
            result = await response.text()
            
            if "RESET_ALL_SUCCESS" in result:
                embed = discord.Embed(
                    title="🗑️ Tüm Keyler Silindi",
                    description="Bütün keyler başarıyla silindi!",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ {result}")
                
    except:
        await ctx.send("❌ Reset işlemi başarısız")

@bot.command(name='panic')
async def panic_mode(ctx):
    """Site ile tüm bağlantıyı keser (!panic)"""
    try:
        owner_id = str(ctx.author.id)
        payload = generate_signature("panic", owner_id)
        
        async with session.post(f"{API_URL}?token={API_TOKEN}", 
                               data=payload,
                               headers={'User-Agent': 'DiscordBot'}) as response:
            
            result = await response.text()
            
            if "PANIC_MODE_ENABLED" in result:
                embed = discord.Embed(
                    title="🚨 PANIC MODE AKTIF",
                    description="Site tüm istekleri reddediyor!\nLoader bağlantıları kesildi.",
                    color=0xff0000
                )
                embed.add_field(name="⚠️ Uyarı", value="Bu işlem geri alınamaz!", inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ {result}")
                
    except:
        await ctx.send("❌ Panic işlemi başarısız")



@bot.command(name='keys')
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
                    
                    key_list = []
                    for i, key_data in enumerate(keys[:15], 1):  # İlk 15 key
                        status = "🔴" if key_data['used'] else "🟢"
                        key_short = key_data['key'][:12] + "..."
                        expire_date = key_data.get('expires_at', 'Belirsiz')[:10]
                        key_list.append(f"`{i:02d}.` {status} `{key_short}` - {expire_date}")
                    
                    embed = discord.Embed(
                        title="📝 Keyler",
                        description="\n".join(key_list),
                        color=0x2f3136
                    )
                    
                    if len(keys) > 15:
                        embed.set_footer(text=f"İlk 15 key gösteriliyor (Toplam: {len(keys)})")
                    
                    await ctx.send(embed=embed)
                    
                except:
                    await ctx.send("❌ Veri hatası")
            else:
                await ctx.send("❌ Keyler alınamadı")
                
    except:
        await ctx.send("❌ Liste işlemi başarısız")

@bot.command(name='banlist')
async def ban_list(ctx):
    """Banlı kullanıcıları listeler"""
    try:
        owner_id = str(ctx.author.id)
        payload = generate_signature("banlist", owner_id)
        
        async with session.post(f"{API_URL}?token={API_TOKEN}", 
                               data=payload,
                               headers={'User-Agent': 'DiscordBot'}) as response:
            
            if response.status == 200:
                try:
                    import json
                    bans = json.loads(await response.text())
                    
                    if not bans:
                        await ctx.send("📋 Hiç banlı kullanıcı yok")
                        return
                    
                    ban_list = []
                    for i, ban_data in enumerate(bans[:20], 1):  # İlk 20 ban
                        hwid_short = ban_data['hwid'][:16] + "..."
                        ban_date = ban_data.get('banned_at', 'Bilinmiyor')[:10]
                        ban_list.append(f"`{i:02d}.` 🚫 `{hwid_short}` - {ban_date}")
                    
                    embed = discord.Embed(
                        title="📋 Banlı Kullanıcılar",
                        description="\n".join(ban_list),
                        color=0xff0000
                    )
                    
                    if len(bans) > 20:
                        embed.set_footer(text=f"İlk 20 ban gösteriliyor (Toplam: {len(bans)})")
                    
                    await ctx.send(embed=embed)
                    
                except:
                    await ctx.send("❌ Veri hatası")
            else:
                await ctx.send("❌ Ban listesi alınamadı")
                
    except:
        await ctx.send("❌ Ban listesi işlemi başarısız")

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
        title="🤖 Komutlar",
        description="""📊 `!stats` - İstatistikler
🔑 `!key @user` - Key oluştur
📝 `!keys` - Keylerini listele
📋 `!banlist` - Banlı kullanıcılar
🗑️ `!reset` - Tüm keyleri sil
🚫 `!ban @user` - Kullanıcı banla
✅ `!unban @user` - Kullanıcı unbanla
🚨 `!panic` - Site bağlantısını kes
🏓 `!ping` - Ping kontrolü""",
        color=0x2f3136
    )
    
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
