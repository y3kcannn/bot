import os
import discord
from discord.ext import commands
import requests
import json
import asyncio
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
    e.set_footer(text="Keylogin System")
    return e

async def cleanup(ctx, msg=None, delay=5):
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

@bot.command(name='key')
@is_admin()
async def gen_key(ctx):
    """Generate new key"""
    result = api_call('generate-key')
    
    if 'error' in result:
        e = embed("❌ Error", result['error'], 0xff0000)
    else:
        e = embed("✅ Key Generated", f"**Key:** `{result.get('key', 'N/A')}`")
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='ban')
@is_admin()
async def ban_user(ctx, username=None, ip=None):
    """Ban user/ip"""
    if not username and not ip:
        e = embed("❌ Usage", "`!ban <username> [ip]`", 0xff0000)
        msg = await ctx.send(embed=e)
        await cleanup(ctx, msg)
        return
    
    data = {}
    if username: data['username'] = username
    if ip: data['ip'] = ip
    
    result = api_call('ban-user', data)
    
    if 'error' in result:
        e = embed("❌ Ban Failed", result['error'], 0xff0000)
    else:
        e = embed("🚫 Banned", f"User: `{username or 'N/A'}`\nIP: `{ip or 'N/A'}`")
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='unban')
@is_admin()
async def unban_user(ctx, username=None, ip=None):
    """Remove ban"""
    if not username and not ip:
        e = embed("❌ Usage", "`!unban <username> [ip]`", 0xff0000)
        msg = await ctx.send(embed=e)
        await cleanup(ctx, msg)
        return
    
    data = {}
    if username: data['username'] = username
    if ip: data['ip'] = ip
    
    result = api_call('unban-user', data)
    
    if 'error' in result:
        e = embed("❌ Unban Failed", result['error'], 0xff0000)
    else:
        e = embed("✅ Unbanned", f"User: `{username or 'N/A'}`\nIP: `{ip or 'N/A'}`")
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='check')
@is_admin()
async def check_ban(ctx, username=None, ip=None):
    """Check ban status"""
    if not username and not ip:
        e = embed("❌ Usage", "`!check <username> [ip]`", 0xff0000)
        msg = await ctx.send(embed=e)
        await cleanup(ctx, msg)
        return
    
    data = {}
    if username: data['username'] = username
    if ip: data['ip'] = ip
    
    result = api_call('check-ban', data)
    
    if 'error' in result:
        e = embed("❌ Check Failed", result['error'], 0xff0000)
    elif result.get('banned'):
        e = embed("🚫 BANNED", f"User: `{username or 'N/A'}`\nIP: `{ip or 'N/A'}`", 0xff0000)
    else:
        e = embed("✅ CLEAN", f"User: `{username or 'N/A'}`\nIP: `{ip or 'N/A'}`")
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='stats')
@is_admin()
async def show_stats(ctx):
    """System stats"""
    result = api_call('stats')
    
    if 'error' in result:
        e = embed("❌ Stats Error", result['error'], 0xff0000)
    else:
        total = int(result.get('total_keys', 0))
        used = int(result.get('used_keys', 0))
        banned_users = int(result.get('banned_users', 0))
        banned_ips = int(result.get('banned_ips', 0))
        
        stats_text = f"""```
Keys: {used}/{total} ({(used/max(1,total)*100):.1f}%)
Bans: {banned_users + banned_ips} total
```"""
        e = embed("📊 Stats", stats_text, 0x0099ff)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='version')
@is_admin()
async def version_cmd(ctx, new_version=None):
    """Check/update version"""
    if new_version:
        result = api_call('update-version', {'version': new_version})
        if 'error' in result:
            e = embed("❌ Update Failed", result['error'], 0xff0000)
        else:
            e = embed("✅ Version Updated", f"New: `{new_version}`")
    else:
        result = api_call('version')
        if 'error' in result:
            e = embed("❌ Version Error", result['error'], 0xff0000)
        else:
            e = embed("📋 Version", f"Current: `{result.get('version', 'Unknown')}`")
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='license')
@is_admin()
async def check_license(ctx, key=None):
    """Check license"""
    if not key:
        e = embed("❌ Usage", "`!license <key>`", 0xff0000)
        msg = await ctx.send(embed=e)
        await cleanup(ctx, msg)
        return
    
    result = api_call('check-license', {'key': key})
    
    if 'error' in result:
        e = embed("❌ License Error", result['error'], 0xff0000)
    else:
        status = result.get('status', 'unknown')
        key_short = key[:8] + "..."
        
        if status == 'unused':
            e = embed("🔑 UNUSED", f"Key: `{key_short}`", 0xffaa00)
        elif status == 'expired':
            e = embed("❌ EXPIRED", f"Key: `{key_short}`", 0xff0000)
        elif status == 'active':
            user = result.get('username', 'N/A')
            expiry = result.get('license_expiry', 'N/A')
            e = embed("✅ ACTIVE", f"Key: `{key_short}`\nUser: `{user}`\nExpiry: `{expiry}`")
        else:
            e = embed("❓ UNKNOWN", f"Key: `{key_short}`", 0x888888)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='help')
async def help_cmd(ctx):
    """Help menu"""
    help_text = """```
!key              - Generate new key
!ban <user> [ip]  - Ban user/ip
!unban <user> [ip]- Remove ban
!check <user> [ip]- Check ban status
!license <key>    - Check license
!stats            - System stats
!version [ver]    - Check/update version
```"""
    
    e = embed("🎯 Commands", help_text, 0x7289DA)
    e.add_field(name="Note", value="Admin role required • Auto-delete in 5s", inline=False)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

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
    asyncio.create_task(cleanup(ctx, msg, 3))

if __name__ == "__main__":
    # Check config
    missing = [var for var, val in [("TOKEN", TOKEN), ("API_URL", API_URL), ("API_TOKEN", API_TOKEN)] if not val]
    if missing:
        logger.error(f"Missing: {', '.join(missing)}")
        exit(1)
    
    logger.info("Starting bot...")
    bot.run(TOKEN) 
