import discord
from discord.ext import commands
import requests
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = os.environ.get("DISCORD_TOKEN")

@bot.event
async def on_ready():
    print(f"[+] Bot giriş yaptı: {bot.user}")

# Mesajları 5 saniye sonra silen yardımcı fonksiyon
async def delete_after(ctx, msg):
    await asyncio.sleep(5)
    await msg.delete()
    await ctx.message.delete()

@bot.command()
async def ban(ctx, username: str):
    url = "https://midnightponywka.com/loader/banned.php"
    data = {'username': username}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200 and "Success" in response.text:
            msg = await ctx.send(f"`{username}` başarıyla banlandı! 🔨")
        else:
            msg = await ctx.send(f"❌ Banlama başarısız: {response.text}")
    except Exception as e:
        msg = await ctx.send(f"⚠️ Hata oluştu: {str(e)}")
    await delete_after(ctx, msg)

@bot.command()
async def unban(ctx, username: str):
    url = "https://midnightponywka.com/loader/unban.php"
    data = {'username': username}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200 and "Success" in response.text:
            msg = await ctx.send(f"`{username}` başarıyla unbanlandı ✅")
        else:
            msg = await ctx.send(f"❌ Unban başarısız: {response.text}")
    except Exception as e:
        msg = await ctx.send(f"⚠️ Hata oluştu: {str(e)}")
    await delete_after(ctx, msg)

@bot.command()
async def key(ctx):
    url = "https://midnightponywka.com/loader/create_key.php"
    data = {'username': ctx.author.name}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            key = response.text.strip()
            msg = await ctx.send(f"🔑 Key oluşturuldu: `{key}`")
        else:
            msg = await ctx.send(f"❌ Key oluşturulamadı: {response.text}")
    except Exception as e:
        msg = await ctx.send(f"⚠️ Hata oluştu: {str(e)}")
    await delete_after(ctx, msg)

@bot.command()
async def keylist(ctx):
    file_path = __DIR__ + '/../data/keys.txt'
    try:
        with open(file_path, 'r') as file:
            keys = file.readlines()
        if keys:
            keys_list = ''.join([key.strip() + "\n" for key in keys])
            msg = await ctx.send(f"**Key Listesi:**\n{keys_list}")
        else:
            msg = await ctx.send("❌ Key dosyasında anahtar bulunamadı.")
    except Exception as e:
        msg = await ctx.send(f"⚠️ Hata oluştu: {str(e)}")
    await delete_after(ctx, msg)

@bot.command()
async def komut(ctx):
    commands_list = """
    **Bot Komutları:**
    `!ban <kullanıcı_adı>` - Kullanıcıyı banlar
    `!unban <kullanıcı_adı>` - Kullanıcının yasağını kaldırır
    `!key` - Yeni bir key oluşturur
    `!keylist` - Anahtarları listeler
    `!komut` - Botun komutlarını gösterir
    """
    await ctx.send(commands_list)

bot.run(TOKEN)
