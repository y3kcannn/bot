import os
import discord
from discord.ext import commands
import requests
import json
import asyncio
from datetime import datetime, timezone
import logging
from typing import Optional, List
import math
import aiohttp

# Advanced Setup
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv("TOKEN")
ADMIN_ROLE = os.getenv("ADMIN_ROLE", "🔑")
API_URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(
    command_prefix=['!', 'kl!'],
    intents=intents,
    help_command=None,
    case_insensitive=True,
    strip_after_prefix=True
)

# Advanced API Handler
class APIHandler:
    @staticmethod
    async def call(action: str, data: Optional[dict] = None) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                params = {'api': '1', 'action': action, 'token': API_TOKEN}
                if data:
                    params.update(data)
                
                async with session.get(API_URL, params=params) as response:
                    return await response.json()
        except Exception as e:
            return {'error': f'API connection failed: {str(e)}'}

# Auto-delete function
async def auto_delete_interaction(interaction: discord.Interaction, delay: int = 60):
    """Auto-delete interaction response after specified delay"""
    await asyncio.sleep(delay)
    try:
        await interaction.delete_original_response()
    except:
        pass

# Prefix command permission check
def has_admin_role():
    """Admin role check for prefix commands"""
    def predicate(ctx):
        # Check for admin role
        if any(role.name == ADMIN_ROLE for role in ctx.author.roles):
            return True
        # Check for administrator permission
        if ctx.author.guild_permissions.administrator:
            return True
        # Check for manage_guild permission
        if ctx.author.guild_permissions.manage_guild:
            return True
        return False
    return commands.check(predicate)

# Auto-delete function for prefix commands
async def auto_delete_message(ctx, msg=None, delay: int = 60):
    """Auto-delete message after specified delay"""
    await asyncio.sleep(delay)
    try:
        if msg:
            await msg.delete()
        await ctx.message.delete()
    except:
        pass

# Advanced Embed Builder
class EmbedBuilder:
    @staticmethod
    def create(
        title: str, 
        description: Optional[str] = None, 
        color: int = 0x5865F2,
        emoji: str = "🔐"
    ) -> discord.Embed:
        """Create professional embed with modern design"""
        embed = discord.Embed(
            title=f"{emoji} {title}",
            description=description,
            color=color,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_footer(text="Midnight Keylogin System")
        return embed
    
    @staticmethod
    def success(title: str, description: Optional[str] = None) -> discord.Embed:
        return EmbedBuilder.create(title, description, 0x00ff88, "✅")
    
    @staticmethod
    def error(title: str, description: Optional[str] = None) -> discord.Embed:
        return EmbedBuilder.create(title, description, 0xff4757, "❌")
    
    @staticmethod
    def warning(title: str, description: Optional[str] = None) -> discord.Embed:
        return EmbedBuilder.create(title, description, 0xffa502, "⚠️")
    
    @staticmethod
    def info(title: str, description: Optional[str] = None) -> discord.Embed:
        return EmbedBuilder.create(title, description, 0x5865F2, "ℹ️")

# Bot Events
@bot.event
async def on_ready():
    """Enhanced bot ready event"""
    logger.info(f"🚀 {bot.user} is now online!")
    logger.info(f"📊 Connected to {len(bot.guilds)} servers")
    logger.info(f"👥 Serving {len(bot.users)} users")
    
    # Set advanced presence
    activity = discord.Activity(
        type=discord.ActivityType.playing,
        name="🔐 Keylogin Management | !help"
    )
    await bot.change_presence(
        status=discord.Status.online,
        activity=activity
    )

@bot.event
async def on_command_error(ctx, error):
    """Advanced error handling"""
    if isinstance(error, commands.CheckFailure):
        embed = EmbedBuilder.error(
            "Access Denied",
            f"You need the `{ADMIN_ROLE}` role or administrator permissions to use this command."
        )
        embed.add_field(
            name="💡 Need Help?",
            value="Contact your server administrator to get the required permissions.",
            inline=False
        )
    elif isinstance(error, commands.CommandNotFound):
        embed = EmbedBuilder.warning(
            "Unknown Command",
            f"Command not found. Use `!help` or `!commands` to see available commands."
        )
    else:
        embed = EmbedBuilder.error(
            "Command Error",
            f"An unexpected error occurred: `{str(error)}`"
        )
        logger.error(f"Command error: {error}")
    
    try:
        msg = await ctx.send(embed=embed)
        asyncio.create_task(auto_delete_message(ctx, msg, 30))
    except:
        pass

# Prefix Commands (! commands)
@bot.command(name='key', aliases=['genkey', 'generatekey'])
@has_admin_role()
async def prefix_generate_key(ctx):
    """!key - Generate new license key"""
    result = await APIHandler.call('add-key')
    
    if 'error' in result:
        embed = EmbedBuilder.error("Key Generation Failed", f"```{result['error']}```")
    else:
        key = result.get('key', 'N/A')
        embed = EmbedBuilder.success("Key Generated Successfully")
        embed.add_field(name="🔐 License Key", value=f"```{key}```", inline=False)
        embed.add_field(name="🛡️ Security", value="Keep this key secure and private!", inline=False)
        embed.add_field(name="📅 Created", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=False)
    
    msg = await ctx.send(embed=embed)
    asyncio.create_task(auto_delete_message(ctx, msg))

@bot.command(name='ban')
@has_admin_role()
async def prefix_ban_user(ctx, username=None, ip=None, *, reason=None):
    """!ban <username> [ip] [reason] - Ban user from system"""
    if not username and not ip:
        embed = EmbedBuilder.error("Invalid Usage")
        embed.add_field(name="📋 Usage", value="`!ban <username> [ip] [reason]`", inline=False)
        embed.add_field(name="📝 Examples", value="`!ban TestUser`\n`!ban TestUser 192.168.1.1`\n`!ban TestUser 192.168.1.1 Violation`", inline=False)
        msg = await ctx.send(embed=embed)
        asyncio.create_task(auto_delete_message(ctx, msg))
        return
    
    data = {}
    if username: data['username'] = username
    if ip: data['ip'] = ip
    if reason: data['reason'] = reason
    
    result = await APIHandler.call('ban-user', data)
    
    if 'error' in result:
        embed = EmbedBuilder.error("Ban Failed", f"```{result['error']}```")
    else:
        embed = EmbedBuilder.success("User Banned Successfully")
        embed.add_field(name="👤 Username", value=f"`{username or 'Not specified'}`", inline=True)
        embed.add_field(name="🌐 IP Address", value=f"`{ip or 'Not specified'}`", inline=True)
        embed.add_field(name="👮 Banned By", value=ctx.author.mention, inline=True)
        embed.add_field(name="⚠️ Status", value="🔴 **BLOCKED** - Access denied to system", inline=False)
        if reason:
            embed.add_field(name="📝 Reason", value=f"`{reason}`", inline=False)
    
    msg = await ctx.send(embed=embed)
    asyncio.create_task(auto_delete_message(ctx, msg))

@bot.command(name='unban')
@has_admin_role()
async def prefix_unban_user(ctx, username=None, ip=None):
    """!unban <username> [ip] - Remove ban from user"""
    if not username and not ip:
        embed = EmbedBuilder.error("Invalid Usage")
        embed.add_field(name="📋 Usage", value="`!unban <username> [ip]`", inline=False)
        embed.add_field(name="📝 Example", value="`!unban TestUser`", inline=False)
        msg = await ctx.send(embed=embed)
        asyncio.create_task(auto_delete_message(ctx, msg))
        return
    
    data = {}
    if username: data['username'] = username
    if ip: data['ip'] = ip
    
    result = await APIHandler.call('unban-user', data)
    
    if 'error' in result:
        embed = EmbedBuilder.error("Unban Failed", f"```{result['error']}```")
    else:
        embed = EmbedBuilder.success("Ban Removed Successfully")
        embed.add_field(name="👤 Username", value=f"`{username or 'Not specified'}`", inline=True)
        embed.add_field(name="🌐 IP Address", value=f"`{ip or 'Not specified'}`", inline=True)
        embed.add_field(name="👮 Unbanned By", value=ctx.author.mention, inline=True)
        embed.add_field(name="✅ Status", value="🟢 **RESTORED** - Access granted to system", inline=False)
    
    msg = await ctx.send(embed=embed)
    asyncio.create_task(auto_delete_message(ctx, msg))

@bot.command(name='check', aliases=['checkban'])
@has_admin_role()
async def prefix_check_ban(ctx, username=None, ip=None):
    """!check <username> [ip] - Check ban status"""
    if not username and not ip:
        embed = EmbedBuilder.error("Invalid Usage")
        embed.add_field(name="📋 Usage", value="`!check <username> [ip]`", inline=False)
        embed.add_field(name="📝 Example", value="`!check TestUser`", inline=False)
        msg = await ctx.send(embed=embed)
        asyncio.create_task(auto_delete_message(ctx, msg))
        return
    
    data = {}
    if username: data['username'] = username
    if ip: data['ip'] = ip
    
    result = await APIHandler.call('check-ban', data)
    
    if 'error' in result:
        embed = EmbedBuilder.error("Check Failed", f"```{result['error']}```")
    elif result.get('banned'):
        embed = EmbedBuilder.error("USER IS BANNED")
        embed.add_field(name="👤 Username", value=f"`{username or 'Not specified'}`", inline=True)
        embed.add_field(name="🌐 IP Address", value=f"`{ip or 'Not specified'}`", inline=True)
        embed.add_field(name="🔍 Checked By", value=ctx.author.mention, inline=True)
        embed.add_field(name="📊 Status", value="🔴 **BANNED** - Access denied", inline=False)
    else:
        embed = EmbedBuilder.success("USER IS CLEAN")
        embed.add_field(name="👤 Username", value=f"`{username or 'Not specified'}`", inline=True)
        embed.add_field(name="🌐 IP Address", value=f"`{ip or 'Not specified'}`", inline=True)
        embed.add_field(name="🔍 Checked By", value=ctx.author.mention, inline=True)
        embed.add_field(name="📊 Status", value="🟢 **CLEAN** - Access allowed", inline=False)
    
    msg = await ctx.send(embed=embed)
    asyncio.create_task(auto_delete_message(ctx, msg))

@bot.command(name='stats', aliases=['statistics'])
@has_admin_role()
async def prefix_stats(ctx):
    """!stats - View system statistics"""
    result = await APIHandler.call('stats')
    
    if 'error' in result:
        embed = EmbedBuilder.error("Statistics Error", f"```{result['error']}```")
    else:
        total = int(result.get('total_keys', 0))
        used = int(result.get('used_keys', 0))
        available = total - used
        banned_users = int(result.get('banned_users', 0))
        banned_ips = int(result.get('banned_ips', 0))
        usage_percent = (used/max(1,total)*100)
        
        embed = EmbedBuilder.info("System Statistics", "📊 Complete system overview")
        embed.add_field(
            name="🔑 License Summary", 
            value=f"```yaml\nTotal Keys    : {total:>6}\nUsed Keys     : {used:>6}\nAvailable     : {available:>6}\nUsage Rate    : {usage_percent:>5.1f}%```", 
            inline=True
        )
        embed.add_field(
            name="🛡️ Security Status", 
            value=f"```yaml\nBanned Users  : {banned_users:>6}\nBanned IPs    : {banned_ips:>6}\nTotal Bans    : {banned_users + banned_ips:>6}\nSecurity      : {'🟢 Active' if banned_users + banned_ips > 0 else '⚪ Normal'}```", 
            inline=True
        )
        
        # System health
        if usage_percent < 70:
            health_status = "🟢 Excellent"
        elif usage_percent < 85:
            health_status = "🟡 Good"
        elif usage_percent < 95:
            health_status = "🟠 Busy"
        else:
            health_status = "🔴 Critical"
        
        embed.add_field(
            name="📈 System Health", 
            value=f"```yaml\nStatus        : {health_status}\nPerformance   : {'🚀 Optimal' if usage_percent < 80 else '⚡ High Load'}\nUptime        : 🟢 Online\nRequested By  : {ctx.author.display_name}```", 
            inline=False
        )
    
    msg = await ctx.send(embed=embed)
    asyncio.create_task(auto_delete_message(ctx, msg))

@bot.command(name='version', aliases=['ver'])
@has_admin_role()
async def prefix_version(ctx, new_version=None):
    """!version [new_version] - Check or update version"""
    if new_version:
        result = await APIHandler.call('update-version', {'version': new_version})
        if 'error' in result:
            embed = EmbedBuilder.error("Version Update Failed", f"```{result['error']}```")
        else:
            embed = EmbedBuilder.success("Version Updated Successfully")
            embed.add_field(name="🆕 New Version", value=f"`{new_version}`", inline=True)
            embed.add_field(name="👮 Updated By", value=ctx.author.mention, inline=True)
            embed.add_field(name="⏰ Updated", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=True)
            embed.add_field(name="ℹ️ Note", value="Users will automatically update on next login", inline=False)
    else:
        result = await APIHandler.call('version')
        if 'error' in result:
            embed = EmbedBuilder.error("Version Check Failed", f"```{result['error']}```")
        else:
            current_version = result.get('version', 'Unknown')
            embed = EmbedBuilder.info("Current System Version")
            embed.add_field(name="🔢 Version", value=f"`{current_version}`", inline=True)
            embed.add_field(name="📅 Last Checked", value=f"<t:{int(datetime.now().timestamp())}:R>", inline=True)
            embed.add_field(name="💡 Update", value="Use `!version <new_version>` to update", inline=False)
    
    msg = await ctx.send(embed=embed)
    asyncio.create_task(auto_delete_message(ctx, msg))

@bot.command(name='license', aliases=['lic'])
@has_admin_role()
async def prefix_license(ctx, key=None):
    """!license <key> - Check license status"""
    if not key:
        embed = EmbedBuilder.error("Invalid Usage")
        embed.add_field(name="📋 Usage", value="`!license <key>`", inline=False)
        embed.add_field(name="📝 Example", value="`!license ABC123DEF456`", inline=False)
        msg = await ctx.send(embed=embed)
        asyncio.create_task(auto_delete_message(ctx, msg))
        return
    
    result = await APIHandler.call('check-license', {'key': key})
    
    if 'error' in result:
        embed = EmbedBuilder.error("License Check Failed", f"```{result['error']}```")
    else:
        status = result.get('status', 'unknown')
        key_short = key[:8] + "..." if len(key) > 8 else key
        
        if status == 'unused':
            embed = EmbedBuilder.warning("License: UNUSED")
            embed.add_field(name="🔐 Key", value=f"`{key_short}`", inline=True)
            embed.add_field(name="📊 Status", value="🟡 **READY** - Awaiting activation", inline=True)
            embed.add_field(name="💡 Next Steps", value="This key can be activated by a user", inline=False)
        
        elif status == 'expired':
            embed = EmbedBuilder.error("License: EXPIRED")
            embed.add_field(name="🔐 Key", value=f"`{key_short}`", inline=True)
            embed.add_field(name="⏰ Expired", value=f"`{result.get('license_expiry', 'N/A')}`", inline=True)
            embed.add_field(name="📊 Status", value="🔴 **EXPIRED** - No longer valid", inline=False)
        
        elif status == 'active':
            user = result.get('username', 'N/A')
            expiry = result.get('license_expiry', 'N/A')
            embed = EmbedBuilder.success("License: ACTIVE")
            embed.add_field(name="🔐 Key", value=f"`{key_short}`", inline=True)
            embed.add_field(name="👤 User", value=f"`{user}`", inline=True)
            embed.add_field(name="⏰ Expires", value=f"`{expiry}`", inline=True)
            embed.add_field(name="📊 Status", value="🟢 **ACTIVE** - Currently in use", inline=False)
            
            if 'first_use' in result:
                embed.add_field(name="📅 First Used", value=f"`{result['first_use']}`", inline=True)
        
        else:
            embed = EmbedBuilder.info("License: UNKNOWN")
            embed.add_field(name="🔐 Key", value=f"`{key_short}`", inline=False)
            embed.add_field(name="📊 Status", value="⚪ **UNKNOWN** - Unable to determine status", inline=False)
    
    msg = await ctx.send(embed=embed)
    asyncio.create_task(auto_delete_message(ctx, msg))

# Main help command
@bot.command(name='help', aliases=['commands', 'cmd', 'commandlist'])
@has_admin_role()
async def main_help(ctx):
    """!help - Show all available commands"""
    embed = EmbedBuilder.info("Midnight Keylogin Commands", "🎯 Complete command reference")
    
    embed.add_field(
        name="🔑 Key Management", 
        value="• `!key` - Generate new license key\n• `!license <key>` - Check license status\n• `!version [ver]` - Check/update version", 
        inline=False
    )
    
    embed.add_field(
        name="🛡️ Security Management", 
        value="• `!ban <user> [ip] [reason]` - Ban user\n• `!unban <user> [ip]` - Remove ban\n• `!check <user> [ip]` - Check ban status", 
        inline=False
    )
    
    embed.add_field(
        name="📊 System Information", 
        value="• `!stats` - View system statistics\n• `!help` - Show this command menu", 
        inline=False
    )
    
    embed.add_field(
        name="🎮 Advanced Features", 
        value="• **Auto-delete** - Messages delete after 1 minute\n• **Aliases** - Multiple names for same command\n• **Error Handling** - Smart error messages\n• **Permission System** - Admin role protection", 
        inline=False
    )
    
    embed.add_field(
        name="📌 Important Information", 
        value=f"• **Required Role:** `{ADMIN_ROLE}` or Administrator\n• **Command Prefix:** `!` - All commands use exclamation mark\n• **Aliases:** Most commands have short versions\n• **Auto-delete:** Messages delete after 1 minute\n• **Help Permanent:** This help menu stays visible", 
        inline=False
    )
    
    embed.set_footer(text="Midnight Keylogin System • Professional Discord Bot")
    # Help command is permanent, no auto-delete
    await ctx.send(embed=embed)

if __name__ == "__main__":
    # Enhanced startup checks
    missing = []
    for var_name, var_value in [("TOKEN", TOKEN), ("API_URL", API_URL), ("API_TOKEN", API_TOKEN)]:
        if not var_value:
            missing.append(var_name)
    
    if missing:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing)}")
        logger.error("🔧 Required variables:")
        logger.error("   • TOKEN - Discord bot token")
        logger.error("   • API_URL - API endpoint URL")
        logger.error("   • API_TOKEN - API authentication token")
        exit(1)
    
    logger.info("🚀 Starting Midnight Keylogin Bot...")
    logger.info("🎯 Features: Prefix Commands (!), Modern Design, Auto-delete")
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        exit(1) 
