import discord
import aiohttp
import os
import asyncio
from discord.ext import commands

# Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
API_URL = os.getenv('API_URL')
API_TOKEN = os.getenv('TOKEN')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Session for HTTP requests
session = None

@bot.event
async def on_ready():
    global session
    session = aiohttp.ClientSession()
    print(f"🚀 {bot.user} BOT AKTİF!")
    print(f"📡 API: {API_URL}")

@bot.event
async def on_disconnect():
    if session:
        await session.close()

@bot.command(name='stats')
async def stats(ctx):
    """Bot ve API istatistiklerini gösterir"""
    try:
        await ctx.typing()
        
        # API'den stats al
        async with session.post(f"{API_URL}?token={API_TOKEN}", 
                               data={'action': 'stats'},
                               headers={'User-Agent': 'DiscordBot'}) as response:
            
            # Her durumda önce text olarak al
            text_response = await response.text()
            
            if response.status == 200:
                try:
                    # JSON parse etmeye çalış
                    import json
                    data = json.loads(text_response)
                    
                    embed = discord.Embed(
                        title="📊 Midnight Auth İstatistikleri",
                        color=0x00ff00
                    )
                    
                    embed.add_field(name="🔑 Toplam Key", value=str(data.get('total_keys', 0)), inline=True)
                    embed.add_field(name="✅ Kullanılan", value=str(data.get('used_keys', 0)), inline=True)
                    embed.add_field(name="🟢 Aktif", value=str(data.get('active_keys', 0)), inline=True)
                    embed.add_field(name="🚫 Banlanan", value=str(data.get('banned_users', 0)), inline=True)
                    embed.add_field(name="⏰ Zaman", value=str(data.get('server_time', 'Bilinmiyor')), inline=True)
                    
                    embed.set_footer(text=f"Talep eden: {ctx.author.display_name}")
                    await ctx.send(embed=embed)
                    
                except Exception as e:
                    # Debug için gerçek yanıtı göster
                    await ctx.send(f"❌ JSON Parse Hatası!\n**API Yanıtı:** `{text_response[:1000]}`\n**Hata:** {str(e)}")
            else:
                await ctx.send(f"❌ API HTTP Hatası {response.status}: `{text_response[:500]}`")
                
    except Exception as e:
        await ctx.send(f"❌ Bağlantı hatası: {str(e)}")

@bot.command(name='ping')
async def ping(ctx):
    """Bot ping değerini gösterir"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Gecikme: {latency}ms",
        color=0x00ff00
    )
    await ctx.send(embed=embed)

@bot.command(name='test')
async def test(ctx):
    """API bağlantısını test eder"""
    try:
        await ctx.typing()
        async with session.post(f"{API_URL}?token={API_TOKEN}", 
                               data={'action': 'stats'},
                               headers={'User-Agent': 'DiscordBot'}) as response:
            
            if response.status == 200:
                await ctx.send("✅ API bağlantısı başarılı!")
            else:
                await ctx.send(f"❌ API test başarısız: {response.status}")
    except Exception as e:
        await ctx.send(f"❌ Test hatası: {str(e)}")

@bot.command(name='help')
async def help_command(ctx):
    """Yardım menüsünü gösterir"""
    embed = discord.Embed(
        title="🤖 Midnight Auth Bot",
        description="Kullanılabilir komutlar:",
        color=0x3498db
    )
    
    embed.add_field(name="!stats", value="API istatistiklerini gösterir", inline=False)
    embed.add_field(name="!ping", value="Bot ping değerini gösterir", inline=False)
    embed.add_field(name="!test", value="API bağlantısını test eder", inline=False)
    embed.add_field(name="!help", value="Bu yardım menüsünü gösterir", inline=False)
    
    await ctx.send(embed=embed)

# Error handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Böyle bir komut yok. `!help` yazarak komutları görün.")
    else:
        await ctx.send(f"❌ Hata: {str(error)}")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ DISCORD_TOKEN bulunamadı! Railway environment variables kontrol et.")
        exit(1)
    
    if not API_URL:
        print("❌ API_URL bulunamadı! Railway environment variables kontrol et.")
        exit(1)
        
    if not API_TOKEN:
        print("❌ TOKEN bulunamadı! Railway environment variables kontrol et.")
        exit(1)
    
    print("🔄 Bot başlatılıyor...")
    print(f"📡 API bağlantısı test ediliyor...")
    bot.run(DISCORD_TOKEN)
