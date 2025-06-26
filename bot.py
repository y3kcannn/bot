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
    e.set_footer(text="Midnight Keylogin System", icon_url="https://cdn.discordapp.com/emojis/🔐.png")
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
        e = embed("❌ Key Generation Error", f"```{result['error']}```", 0xff0000)
    else:
        key = result.get('key', 'N/A')
        e = embed("✅ Key Generated Successfully", None, 0x00ff00)
        e.add_field(name="🔑 New License Key", value=f"`{key}`", inline=False)
        e.add_field(name="📌 Important", value="Save this key securely!", inline=False)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='ban')
@is_admin()
async def ban_user(ctx, username=None, ip=None):
    """Ban user/ip"""
    if not username and not ip:
        e = embed("❌ Invalid Usage", None, 0xff0000)
        e.add_field(name="📋 Usage", value="`!ban <username> [ip]`", inline=False)
        e.add_field(name="📝 Example", value="`!ban TestUser 192.168.1.1`", inline=False)
        msg = await ctx.send(embed=e)
        await cleanup(ctx, msg)
        return
    
    data = {}
    if username: data['username'] = username
    if ip: data['ip'] = ip
    
    result = api_call('ban-user', data)
    
    if 'error' in result:
        e = embed("❌ Ban Failed", f"```{result['error']}```", 0xff0000)
    else:
        e = embed("🚫 User Banned Successfully", None, 0xff6600)
        e.add_field(name="👤 Username", value=f"`{username or 'Not specified'}`", inline=True)
        e.add_field(name="🌐 IP Address", value=f"`{ip or 'Not specified'}`", inline=True)
        e.add_field(name="⚠️ Status", value="Access blocked from system", inline=False)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='unban')
@is_admin()
async def unban_user(ctx, username=None, ip=None):
    """Remove ban"""
    if not username and not ip:
        e = embed("❌ Invalid Usage", None, 0xff0000)
        e.add_field(name="📋 Usage", value="`!unban <username> [ip]`", inline=False)
        e.add_field(name="📝 Example", value="`!unban TestUser`", inline=False)
        msg = await ctx.send(embed=e)
        await cleanup(ctx, msg)
        return
    
    data = {}
    if username: data['username'] = username
    if ip: data['ip'] = ip
    
    result = api_call('unban-user', data)
    
    if 'error' in result:
        e = embed("❌ Unban Failed", f"```{result['error']}```", 0xff0000)
    else:
        e = embed("✅ Ban Removed Successfully", None, 0x00ff00)
        e.add_field(name="👤 Username", value=f"`{username or 'Not specified'}`", inline=True)
        e.add_field(name="🌐 IP Address", value=f"`{ip or 'Not specified'}`", inline=True)
        e.add_field(name="✅ Status", value="Access restored to system", inline=False)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='check')
@is_admin()
async def check_ban(ctx, username=None, ip=None):
    """Check ban status"""
    if not username and not ip:
        e = embed("❌ Invalid Usage", None, 0xff0000)
        e.add_field(name="📋 Usage", value="`!check <username> [ip]`", inline=False)
        e.add_field(name="📝 Example", value="`!check TestUser`", inline=False)
        msg = await ctx.send(embed=e)
        await cleanup(ctx, msg)
        return
    
    data = {}
    if username: data['username'] = username
    if ip: data['ip'] = ip
    
    result = api_call('check-ban', data)
    
    if 'error' in result:
        e = embed("❌ Check Failed", f"```{result['error']}```", 0xff0000)
    elif result.get('banned'):
        e = embed("🚫 USER IS BANNED", None, 0xff0000)
        e.add_field(name="👤 Username", value=f"`{username or 'Not specified'}`", inline=True)
        e.add_field(name="🌐 IP Address", value=f"`{ip or 'Not specified'}`", inline=True)
        e.add_field(name="📊 Status", value="🔴 **BLOCKED** - Access denied", inline=False)
    else:
        e = embed("✅ USER IS CLEAN", None, 0x00ff00)
        e.add_field(name="👤 Username", value=f"`{username or 'Not specified'}`", inline=True)
        e.add_field(name="🌐 IP Address", value=f"`{ip or 'Not specified'}`", inline=True)
        e.add_field(name="📊 Status", value="🟢 **CLEAN** - Access allowed", inline=False)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='stats')
@is_admin()
async def show_stats(ctx):
    """System stats"""
    result = api_call('stats')
    
    if 'error' in result:
        e = embed("❌ Stats Error", f"```{result['error']}```", 0xff0000)
    else:
        total = int(result.get('total_keys', 0))
        used = int(result.get('used_keys', 0))
        available = total - used
        banned_users = int(result.get('banned_users', 0))
        banned_ips = int(result.get('banned_ips', 0))
        usage_percent = (used/max(1,total)*100)
        
        e = embed("📊 System Statistics", None, 0x0099ff)
        e.add_field(name="🔑 License Keys", value=f"```Total: {total}\nUsed: {used}\nAvailable: {available}\nUsage: {usage_percent:.1f}%```", inline=True)
        e.add_field(name="🚫 Security Bans", value=f"```Users: {banned_users}\nIPs: {banned_ips}\nTotal: {banned_users + banned_ips}```", inline=True)
        e.add_field(name="📈 System Health", value=f"```Status: {'🟢 Healthy' if usage_percent < 80 else '🟡 Busy' if usage_percent < 95 else '🔴 Critical'}\nSecurity: {'🛡️ Active' if banned_users + banned_ips > 0 else '⚪ Normal'}```", inline=False)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='version')
@is_admin()
async def version_cmd(ctx, new_version=None):
    """Check/update version"""
    if new_version:
        result = api_call('update-version', {'version': new_version})
        if 'error' in result:
            e = embed("❌ Version Update Failed", f"```{result['error']}```", 0xff0000)
        else:
            e = embed("✅ Version Updated Successfully", None, 0x00ff00)
            e.add_field(name="📝 New Version", value=f"`{new_version}`", inline=False)
            e.add_field(name="ℹ️ Note", value="Users will auto-update on next login", inline=False)
    else:
        result = api_call('version')
        if 'error' in result:
            e = embed("❌ Version Check Error", f"```{result['error']}```", 0xff0000)
        else:
            current_version = result.get('version', 'Unknown')
            e = embed("📋 Current Version", None, 0x7289da)
            e.add_field(name="🔢 Version", value=f"`{current_version}`", inline=False)
            e.add_field(name="💡 Tip", value="Use `!version <new_version>` to update", inline=False)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='license')
@is_admin()
async def check_license(ctx, key=None):
    """Check license"""
    if not key:
        e = embed("❌ Invalid Usage", None, 0xff0000)
        e.add_field(name="📋 Usage", value="`!license <key>`", inline=False)
        e.add_field(name="📝 Example", value="`!license ABC123DEF456`", inline=False)
        msg = await ctx.send(embed=e)
        await cleanup(ctx, msg)
        return
    
    result = api_call('check-license', {'key': key})
    
    if 'error' in result:
        e = embed("❌ License Check Error", f"```{result['error']}```", 0xff0000)
    else:
        status = result.get('status', 'unknown')
        key_short = key[:8] + "..." if len(key) > 8 else key
        
        if status == 'unused':
            e = embed("🔑 LICENSE: UNUSED", None, 0xffaa00)
            e.add_field(name="🔐 Key", value=f"`{key_short}`", inline=False)
            e.add_field(name="📊 Status", value="🟡 **UNUSED** - Ready for activation", inline=False)
        elif status == 'expired':
            e = embed("❌ LICENSE: EXPIRED", None, 0xff0000)
            e.add_field(name="🔐 Key", value=f"`{key_short}`", inline=True)
            e.add_field(name="⏰ Expired", value=f"`{result.get('license_expiry', 'N/A')}`", inline=True)
            e.add_field(name="📊 Status", value="🔴 **EXPIRED** - No longer valid", inline=False)
        elif status == 'active':
            user = result.get('username', 'N/A')
            expiry = result.get('license_expiry', 'N/A')
            e = embed("✅ LICENSE: ACTIVE", None, 0x00ff00)
            e.add_field(name="🔐 Key", value=f"`{key_short}`", inline=True)
            e.add_field(name="👤 User", value=f"`{user}`", inline=True)
            e.add_field(name="⏰ Expires", value=f"`{expiry}`", inline=True)
            e.add_field(name="📊 Status", value="🟢 **ACTIVE** - Currently in use", inline=False)
        else:
            e = embed("❓ LICENSE: UNKNOWN", None, 0x888888)
            e.add_field(name="🔐 Key", value=f"`{key_short}`", inline=False)
            e.add_field(name="📊 Status", value="⚪ **UNKNOWN** - Unable to determine", inline=False)
    
    msg = await ctx.send(embed=e)
    await cleanup(ctx, msg)

@bot.command(name='help')
async def help_cmd(ctx):
    """Help menu"""
    e = embed("🎯 Midnight Keylogin Commands", None, 0x7289DA)
    
    # Key Management Commands
    e.add_field(
        name="🔑 Key Management", 
        value="**`!key`**\n└ Generate new license key\n\n**`!license <key>`**\n└ Check license status\n\n**`!version [new_version]`**\n└ Check or update system version", 
        inline=False
    )
    
    # Security Commands
    e.add_field(
        name="🛡️ Security Management", 
        value="**`!ban <username> [ip]`**\n└ Ban user from system\n\n**`!unban <username> [ip]`**\n└ Remove user ban\n\n**`!check <username> [ip]`**\n└ Check ban status", 
        inline=False
    )
    
    # System Commands
    e.add_field(
        name="📊 System Information", 
        value="**`!stats`**\n└ View system statistics\n\n**`!help`**\n└ Show this command menu", 
        inline=False
    )
    
    # Footer info
    e.add_field(
        name="📌 Important Notes", 
        value="• All commands require **Admin** role\n• Messages auto-delete after **5 seconds**\n• Use `< >` for required parameters, `[ ]` for optional", 
        inline=False
    )
    
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
