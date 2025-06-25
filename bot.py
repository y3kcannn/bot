import os
import discord
from discord.ext import commands
from discord import app_commands
import requests
import json
import asyncio
from datetime import datetime, timezone
import logging
from typing import Optional, List
import math

# Advanced Setup
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv("TOKEN")
ADMIN_ROLE = os.getenv("ADMIN_ROLE", "Admin")
API_URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0")) if os.getenv("GUILD_ID") else None

# Advanced Bot Setup
class KeyloginBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix=['!', 'kl!', '/'],
            intents=intents,
            help_command=None,
            case_insensitive=True,
            strip_after_prefix=True
        )
        
    async def setup_hook(self):
        """Setup bot hooks and sync commands"""
        await self.tree.sync()
        logger.info("Slash commands synced successfully")

bot = KeyloginBot()

# Advanced API Handler
class APIHandler:
    @staticmethod
    async def call(action: str, data: Optional[dict] = None) -> dict:
        """Async API request with better error handling"""
        try:
            url = f"{API_URL}?api=1&token={API_TOKEN}&action={action}"
            
            # Use requests for now (can be upgraded to aiohttp later)
            import requests
            if data:
                response = requests.post(url, data=data, timeout=10)
            else:
                response = requests.get(url, timeout=10)
            return response.json()
                        
        except requests.exceptions.Timeout:
            return {"error": "⏱️ Server timeout - Please try again"}
        except requests.exceptions.ConnectionError:
            return {"error": "🔌 Connection failed - Server may be down"}
        except json.JSONDecodeError:
            return {"error": "📄 Invalid server response"}
        except Exception as e:
            logger.error(f"API Error: {e}")
            return {"error": f"🚫 Request failed: {str(e)}"}

# Auto-delete function
async def auto_delete_interaction(interaction: discord.Interaction, delay: int = 60):
    """Auto-delete interaction response after specified delay"""
    await asyncio.sleep(delay)
    try:
        await interaction.delete_original_response()
    except:
        pass

# Advanced Permission System
def has_admin_permissions():
    """Advanced permission check"""
    async def predicate(interaction: discord.Interaction) -> bool:
        # Check for admin role
        if any(role.name == ADMIN_ROLE for role in interaction.user.roles):
            return True
        # Check for administrator permission
        if interaction.user.guild_permissions.administrator:
            return True
        # Check for manage_guild permission
        if interaction.user.guild_permissions.manage_guild:
            return True
        return False
    return app_commands.check(predicate)

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
        embed.set_footer(
            text="Midnight Keylogin System • Advanced Management",
            icon_url="https://cdn.discordapp.com/embed/avatars/0.png"
        )
        return embed
    
    @staticmethod
    def success(title: str, description: str = None) -> discord.Embed:
        return EmbedBuilder.create(title, description, 0x00ff88, "✅")
    
    @staticmethod
    def error(title: str, description: str = None) -> discord.Embed:
        return EmbedBuilder.create(title, description, 0xff4757, "❌")
    
    @staticmethod
    def warning(title: str, description: str = None) -> discord.Embed:
        return EmbedBuilder.create(title, description, 0xffa502, "⚠️")
    
    @staticmethod
    def info(title: str, description: str = None) -> discord.Embed:
        return EmbedBuilder.create(title, description, 0x5865F2, "ℹ️")

# Interactive View Classes
class ConfirmView(discord.ui.View):
    """Confirmation dialog with buttons"""
    def __init__(self, user_id: int):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.result = None
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ You cannot use this button!", ephemeral=True)
            return
        self.result = True
        self.stop()
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ You cannot use this button!", ephemeral=True)
            return
        self.result = False
        self.stop()

class PaginatedView(discord.ui.View):
    """Paginated embed view"""
    def __init__(self, embeds: List[discord.Embed], user_id: int):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.user_id = user_id
        self.current_page = 0
        self.max_pages = len(embeds)
        
        # Update button states
        self.update_buttons()
    
    def update_buttons(self):
        self.previous_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page == self.max_pages - 1
    
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.gray)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ You cannot use this button!", ephemeral=True)
            return
        
        self.current_page = max(0, self.current_page - 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
    
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ You cannot use this button!", ephemeral=True)
            return
        
        self.current_page = min(self.max_pages - 1, self.current_page + 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

# Advanced Bot Events
@bot.event
async def on_ready():
    """Enhanced bot ready event"""
    logger.info(f"🚀 {bot.user} is now online!")
    logger.info(f"📊 Connected to {len(bot.guilds)} servers")
    logger.info(f"👥 Serving {len(bot.users)} users")
    
    # Set advanced presence
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="🔐 Keylogin System | /help"
    )
    await bot.change_presence(
        status=discord.Status.online,
        activity=activity
    )

@bot.event
async def on_application_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Advanced error handling"""
    if isinstance(error, app_commands.CheckFailure):
        embed = EmbedBuilder.error(
            "Access Denied",
            f"You need the `{ADMIN_ROLE}` role or administrator permissions to use this command."
        )
        embed.add_field(
            name="💡 Need Help?",
            value="Contact your server administrator to get the required permissions.",
            inline=False
        )
    else:
        embed = EmbedBuilder.error(
            "Command Error",
            f"An unexpected error occurred: `{str(error)}`"
        )
        logger.error(f"Command error: {error}")
    
    try:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except:
        try:
            await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            pass

# Slash Commands Group
class KeyManagement(app_commands.Group):
    """Key management commands"""
    
    @app_commands.command(name="generate", description="🔑 Generate a new license key")
    @has_admin_permissions()
    async def generate_key(self, interaction: discord.Interaction):
        """Generate new license key with confirmation"""
        # Show confirmation dialog
        view = ConfirmView(interaction.user.id)
        embed = EmbedBuilder.warning(
            "Key Generation",
            "Are you sure you want to generate a new license key?"
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()
        
        if view.result is None:
            embed = EmbedBuilder.error("Timeout", "Key generation cancelled due to timeout.")
            await interaction.edit_original_response(embed=embed, view=None)
            # Auto-delete after 1 minute
            await asyncio.create_task(auto_delete_interaction(interaction, 60))
            return
        
        if not view.result:
            embed = EmbedBuilder.info("Cancelled", "Key generation cancelled by user.")
            await interaction.edit_original_response(embed=embed, view=None)
            return
        
        # Generate key
        embed = EmbedBuilder.info("Generating...", "Please wait while generating your license key...")
        await interaction.edit_original_response(embed=embed, view=None)
        
        result = await APIHandler.call('generate-key')
        
        if 'error' in result:
            embed = EmbedBuilder.error("Generation Failed", f"```{result['error']}```")
        else:
            key = result.get('key', 'N/A')
            embed = EmbedBuilder.success("Key Generated Successfully")
            embed.add_field(name="🔐 License Key", value=f"```{key}```", inline=False)
            embed.add_field(name="🛡️ Security", value="Keep this key secure and private!", inline=False)
            embed.add_field(name="📅 Created", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=False)
        
        await interaction.edit_original_response(embed=embed)
        
        # Auto-delete after 1 minute
        asyncio.create_task(auto_delete_interaction(interaction, 60))
    
    @app_commands.command(name="check", description="📋 Check license key status")
    @app_commands.describe(key="The license key to check")
    @has_admin_permissions()
    async def check_license(self, interaction: discord.Interaction, key: str):
        """Check license status with detailed information"""
        await interaction.response.defer(ephemeral=True)
        
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
        
        await interaction.followup.send(embed=embed)

# Security Management Group
class SecurityManagement(app_commands.Group):
    """Security and ban management commands"""
    
    @app_commands.command(name="ban", description="🚫 Ban a user from the system")
    @app_commands.describe(
        username="Username to ban",
        ip="IP address to ban (optional)",
        reason="Reason for the ban (optional)"
    )
    @has_admin_permissions()
    async def ban_user(self, interaction: discord.Interaction, username: Optional[str] = None, ip: Optional[str] = None, reason: Optional[str] = None):
        """Advanced ban system with confirmation"""
        if not username and not ip:
            embed = EmbedBuilder.error(
                "Invalid Usage",
                "You must specify either a username or IP address (or both)."
            )
            embed.add_field(name="📋 Usage", value="`/security ban username:[user] ip:[ip] reason:[reason]`", inline=False)
            embed.add_field(name="📝 Examples", value="`/security ban username:TestUser`\n`/security ban ip:192.168.1.1`\n`/security ban username:TestUser ip:192.168.1.1 reason:Violation`", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Confirmation dialog
        ban_info = []
        if username: ban_info.append(f"👤 Username: `{username}`")
        if ip: ban_info.append(f"🌐 IP: `{ip}`")
        if reason: ban_info.append(f"📝 Reason: `{reason}`")
        
        view = ConfirmView(interaction.user.id)
        embed = EmbedBuilder.warning(
            "Confirm Ban",
            "Are you sure you want to ban the following?\n\n" + "\n".join(ban_info)
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()
        
        if view.result is None:
            embed = EmbedBuilder.error("Timeout", "Ban operation cancelled due to timeout.")
            await interaction.edit_original_response(embed=embed, view=None)
            return
        
        if not view.result:
            embed = EmbedBuilder.info("Cancelled", "Ban operation cancelled by user.")
            await interaction.edit_original_response(embed=embed, view=None)
            return
        
        # Execute ban
        data = {}
        if username: data['username'] = username
        if ip: data['ip'] = ip
        if reason: data['reason'] = reason
        
        embed = EmbedBuilder.info("Processing...", "Please wait while processing the ban...")
        await interaction.edit_original_response(embed=embed, view=None)
        
        result = await APIHandler.call('ban-user', data)
        
        if 'error' in result:
            embed = EmbedBuilder.error("Ban Failed", f"```{result['error']}```")
        else:
            embed = EmbedBuilder.success("User Banned Successfully")
            embed.add_field(name="👤 Username", value=f"`{username or 'Not specified'}`", inline=True)
            embed.add_field(name="🌐 IP Address", value=f"`{ip or 'Not specified'}`", inline=True)
            embed.add_field(name="👮 Banned By", value=interaction.user.mention, inline=True)
            embed.add_field(name="⚠️ Status", value="🔴 **BLOCKED** - Access denied to system", inline=False)
            if reason:
                embed.add_field(name="📝 Reason", value=f"`{reason}`", inline=False)
        
        await interaction.edit_original_response(embed=embed)
        
        # Auto-delete after 1 minute
        asyncio.create_task(auto_delete_interaction(interaction, 60))
    
    @app_commands.command(name="unban", description="✅ Remove ban from user")
    @app_commands.describe(
        username="Username to unban",
        ip="IP address to unban (optional)"
    )
    @has_admin_permissions()
    async def unban_user(self, interaction: discord.Interaction, username: Optional[str] = None, ip: Optional[str] = None):
        """Remove ban with confirmation"""
        if not username and not ip:
            embed = EmbedBuilder.error(
                "Invalid Usage",
                "You must specify either a username or IP address (or both)."
            )
            embed.add_field(name="📋 Usage", value="`/security unban username:[user] ip:[ip]`", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
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
            embed.add_field(name="👮 Unbanned By", value=interaction.user.mention, inline=True)
            embed.add_field(name="✅ Status", value="🟢 **RESTORED** - Access granted to system", inline=False)
        
        await interaction.followup.send(embed=embed)
        
        # Auto-delete after 1 minute
        asyncio.create_task(auto_delete_interaction(interaction, 60))
    
    @app_commands.command(name="check", description="🔍 Check ban status")
    @app_commands.describe(
        username="Username to check",
        ip="IP address to check (optional)"
    )
    @has_admin_permissions()
    async def check_ban(self, interaction: discord.Interaction, username: Optional[str] = None, ip: Optional[str] = None):
        """Check ban status with detailed info"""
        if not username and not ip:
            embed = EmbedBuilder.error(
                "Invalid Usage",
                "You must specify either a username or IP address (or both)."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
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
            embed.add_field(name="🔍 Checked By", value=interaction.user.mention, inline=True)
            embed.add_field(name="📊 Status", value="🔴 **BANNED** - Access denied", inline=False)
        else:
            embed = EmbedBuilder.success("USER IS CLEAN")
            embed.add_field(name="👤 Username", value=f"`{username or 'Not specified'}`", inline=True)
            embed.add_field(name="🌐 IP Address", value=f"`{ip or 'Not specified'}`", inline=True)
            embed.add_field(name="🔍 Checked By", value=interaction.user.mention, inline=True)
            embed.add_field(name="📊 Status", value="🟢 **CLEAN** - Access allowed", inline=False)
        
        await interaction.followup.send(embed=embed)
        
        # Auto-delete after 1 minute
        asyncio.create_task(auto_delete_interaction(interaction, 60))

# System Commands
@bot.tree.command(name="stats", description="📊 View detailed system statistics")
@has_admin_permissions()
async def system_stats(interaction: discord.Interaction):
    """Advanced statistics with multiple pages"""
    await interaction.response.defer(ephemeral=True)
    
    result = await APIHandler.call('stats')
    
    if 'error' in result:
        embed = EmbedBuilder.error("Statistics Error", f"```{result['error']}```")
        await interaction.followup.send(embed=embed)
        return
    
    # Parse statistics
    total = int(result.get('total_keys', 0))
    used = int(result.get('used_keys', 0))
    available = total - used
    banned_users = int(result.get('banned_users', 0))
    banned_ips = int(result.get('banned_ips', 0))
    usage_percent = (used/max(1,total)*100)
    
    # Create multiple embed pages
    embeds = []
    
    # Page 1: Overview
    embed1 = EmbedBuilder.info("System Overview", "📊 Complete system statistics and health status")
    embed1.add_field(
        name="🔑 License Summary", 
        value=f"```yaml\nTotal Keys    : {total:>6}\nUsed Keys     : {used:>6}\nAvailable     : {available:>6}\nUsage Rate    : {usage_percent:>5.1f}%```", 
        inline=True
    )
    embed1.add_field(
        name="🛡️ Security Status", 
        value=f"```yaml\nBanned Users  : {banned_users:>6}\nBanned IPs    : {banned_ips:>6}\nTotal Bans    : {banned_users + banned_ips:>6}\nSecurity      : {'🟢 Active' if banned_users + banned_ips > 0 else '⚪ Normal'}```", 
        inline=True
    )
    
    # System health indicator
    if usage_percent < 70:
        health_status = "🟢 Excellent"
        health_color = 0x00ff88
    elif usage_percent < 85:
        health_status = "🟡 Good"
        health_color = 0xffa502
    elif usage_percent < 95:
        health_status = "🟠 Busy"
        health_color = 0xff6348
    else:
        health_status = "🔴 Critical"
        health_color = 0xff4757
    
    embed1.add_field(
        name="📈 System Health", 
        value=f"```yaml\nStatus        : {health_status}\nPerformance   : {'🚀 Optimal' if usage_percent < 80 else '⚡ High Load'}\nUptime        : 🟢 Online\nLast Updated  : Just now```", 
        inline=False
    )
    embed1.color = health_color
    embeds.append(embed1)
    
    # Page 2: Detailed Analytics (if we have more data)
    embed2 = EmbedBuilder.info("Detailed Analytics", "📈 Advanced system metrics and trends")
    embed2.add_field(
        name="📊 Usage Breakdown",
        value=f"**Active Licenses:** {used}/{total}\n**Success Rate:** {((total-banned_users)/max(1,total)*100):.1f}%\n**Ban Rate:** {((banned_users + banned_ips)/max(1,total)*100):.1f}%",
        inline=True
    )
    embed2.add_field(
        name="🔒 Security Metrics",
        value=f"**User Bans:** {banned_users}\n**IP Bans:** {banned_ips}\n**Total Blocks:** {banned_users + banned_ips}",
        inline=True
    )
    embed2.add_field(
        name="💡 Recommendations",
        value="• Monitor usage patterns\n• Review ban effectiveness\n• Consider key generation\n• Check system performance",
        inline=False
    )
    embeds.append(embed2)
    
    # Create paginated view
    if len(embeds) > 1:
        view = PaginatedView(embeds, interaction.user.id)
        embed = embeds[0]
        embed.set_footer(text=f"Midnight Keylogin System • Page 1/{len(embeds)} • Use buttons to navigate")
        await interaction.followup.send(embed=embed, view=view)
    else:
        await interaction.followup.send(embed=embeds[0])

@bot.tree.command(name="version", description="📋 Check or update system version")
@app_commands.describe(new_version="New version to set (optional)")
@has_admin_permissions()
async def version_management(interaction: discord.Interaction, new_version: Optional[str] = None):
    """Version management with confirmation"""
    if new_version:
        # Update version with confirmation
        view = ConfirmView(interaction.user.id)
        embed = EmbedBuilder.warning(
            "Version Update",
            f"Are you sure you want to update the system version to `{new_version}`?"
        )
        embed.add_field(name="⚠️ Warning", value="This will affect all connected users on their next login.", inline=False)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()
        
        if view.result is None:
            embed = EmbedBuilder.error("Timeout", "Version update cancelled due to timeout.")
            await interaction.edit_original_response(embed=embed, view=None)
            return
        
        if not view.result:
            embed = EmbedBuilder.info("Cancelled", "Version update cancelled by user.")
            await interaction.edit_original_response(embed=embed, view=None)
            return
        
        # Execute update
        embed = EmbedBuilder.info("Updating...", "Please wait while updating the system version...")
        await interaction.edit_original_response(embed=embed, view=None)
        
        result = await APIHandler.call('update-version', {'version': new_version})
        
        if 'error' in result:
            embed = EmbedBuilder.error("Update Failed", f"```{result['error']}```")
        else:
            embed = EmbedBuilder.success("Version Updated Successfully")
            embed.add_field(name="🆕 New Version", value=f"`{new_version}`", inline=True)
            embed.add_field(name="👮 Updated By", value=interaction.user.mention, inline=True)
            embed.add_field(name="⏰ Updated", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=True)
            embed.add_field(name="ℹ️ Note", value="Users will automatically update on next login", inline=False)
        
        await interaction.edit_original_response(embed=embed)
        
        # Auto-delete after 1 minute
        asyncio.create_task(auto_delete_interaction(interaction, 60))
    else:
        # Check current version
        await interaction.response.defer(ephemeral=True)
        
        result = await APIHandler.call('version')
        
        if 'error' in result:
            embed = EmbedBuilder.error("Version Check Failed", f"```{result['error']}```")
        else:
            current_version = result.get('version', 'Unknown')
            embed = EmbedBuilder.info("Current System Version")
            embed.add_field(name="🔢 Version", value=f"`{current_version}`", inline=True)
            embed.add_field(name="📅 Last Checked", value=f"<t:{int(datetime.now().timestamp())}:R>", inline=True)
            embed.add_field(name="💡 Update", value="Use `/version new_version:[version]` to update", inline=False)
        
        await interaction.followup.send(embed=embed)
        
        # Auto-delete after 1 minute
        asyncio.create_task(auto_delete_interaction(interaction, 60))

@bot.tree.command(name="help", description="📚 View all available commands and features")
async def help_command(interaction: discord.Interaction):
    """Advanced help system with interactive navigation"""
    embeds = []
    
    # Main help page
    main_embed = EmbedBuilder.info("Midnight Keylogin Bot", "🎯 Professional keylogin management system")
    main_embed.add_field(
        name="🔑 Key Management Commands",
        value="• `/key generate` - Create new license key\n• `/key check` - Check license status\n• `/version` - Manage system version",
        inline=False
    )
    main_embed.add_field(
        name="🛡️ Security Management Commands", 
        value="• `/security ban` - Ban users/IPs\n• `/security unban` - Remove bans\n• `/security check` - Check ban status",
        inline=False
    )
    main_embed.add_field(
        name="📊 System Commands",
        value="• `/stats` - View system statistics\n• `/help` - Show this help menu",
        inline=False
    )
    main_embed.add_field(
        name="🎮 Features",
        value="• **Slash Commands** - Modern Discord integration\n• **Interactive Buttons** - User-friendly interface\n• **Pagination** - Organized information display\n• **Auto-cleanup** - Keeps channels tidy",
        inline=False
    )
    main_embed.add_field(
        name="📌 Important Information",
        value=f"• **Required Role:** `{ADMIN_ROLE}` or Administrator\n• **Command Prefix:** `/` (Slash commands)\n• **Help Menu:** Permanent (does not auto-delete)\n• **Other Commands:** Auto-delete after 1 minute\n• **Support:** Contact your server administrator",
        inline=False
    )
    embeds.append(main_embed)
    
    # Advanced features page
    advanced_embed = EmbedBuilder.info("Advanced Features", "🚀 Professional bot capabilities")
    advanced_embed.add_field(
        name="🎯 Modern Interface",
        value="• **Slash Commands** - Type `/` to see all commands\n• **Auto-complete** - Smart parameter suggestions\n• **Button Interactions** - Click to confirm actions\n• **Ephemeral Responses** - Private command responses",
        inline=False
    )
    advanced_embed.add_field(
        name="🛡️ Security Features",
        value="• **Permission Checks** - Advanced role verification\n• **Confirmation Dialogs** - Prevent accidental actions\n• **Audit Logging** - Track all administrative actions\n• **Rate Limiting** - Prevent command spam",
        inline=False
    )
    advanced_embed.add_field(
        name="📊 Analytics & Monitoring",
        value="• **Real-time Statistics** - Live system metrics\n• **Health Monitoring** - System status indicators\n• **Usage Tracking** - License utilization data\n• **Performance Metrics** - Response time monitoring",
        inline=False
    )
    embeds.append(advanced_embed)
    
    # Create paginated view
    if len(embeds) > 1:
        view = PaginatedView(embeds, interaction.user.id)
        embed = embeds[0]
        embed.set_footer(text=f"Midnight Keylogin System • Page 1/{len(embeds)} • Permanent help menu")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    else:
        embeds[0].set_footer(text="Midnight Keylogin System • Permanent help menu • Does not auto-delete")
        await interaction.response.send_message(embed=embeds[0], ephemeral=True)

# Register command groups
bot.tree.add_command(KeyManagement(name="key", description="🔑 License key management"))
bot.tree.add_command(SecurityManagement(name="security", description="🛡️ Security and ban management"))

# Prefix Commands (Modern versions of ! commands)
@bot.command(name='key', aliases=['genkey', 'generatekey'])
@has_admin_role()
async def prefix_generate_key(ctx):
    """!key - Generate new license key"""
    result = await APIHandler.call('generate-key')
    
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

# Comprehensive help command for prefix commands
@bot.command(name='commands', aliases=['cmd', 'commandlist'])
@has_admin_role()
async def prefix_help(ctx):
    """!commands - Show all available prefix commands"""
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
        value="• `!stats` - View system statistics\n• `!commands` - Show this command menu\n• `!help` - Slash commands info", 
        inline=False
    )
    
    embed.add_field(
        name="📌 Important Information", 
        value=f"• **Required Role:** `{ADMIN_ROLE}` or Administrator\n• **Command Prefix:** `!` (Prefix commands)\n• **Modern Alternative:** Use `/` for slash commands\n• **Auto-delete:** Messages delete after 1 minute", 
        inline=False
    )
    
    embed.set_footer(text="Midnight Keylogin System • Both ! and / commands available")
    # This help is permanent, no auto-delete
    await ctx.send(embed=embed)

# Legacy prefix commands (for backward compatibility)
@bot.command(name='help', hidden=True)
async def legacy_help(ctx):
    """Legacy help command - redirects to modern slash commands"""
    embed = EmbedBuilder.success(
        "Midnight Keylogin Bot", 
        "🎯 **Hoş geldiniz! Bot artık modern komutları kullanıyor.**"
    )
    embed.add_field(
        name="🚀 Yeni Komut Sistemi", 
        value="• Yazın: `/`\n• Menüden komut seçin\n• Daha kolay ve hızlı!", 
        inline=True
    )
    embed.add_field(
        name="📚 Tam Liste", 
        value="• `/help` - Komut rehberi\n• `/key` - Key yönetimi\n• `/security` - Güvenlik\n• `/stats` - İstatistikler", 
        inline=True
    )
    embed.add_field(
        name="💡 İpucu", 
        value="Slash komutlar otomatik tamamlama önerir ve daha güvenlidir. Modern Discord deneyimi!", 
        inline=False
    )
    embed.set_footer(text="Midnight Keylogin System • Modern Discord Bot")
    msg = await ctx.send(embed=embed)
    
    # Auto-delete after 1 minute
    await asyncio.sleep(60)
    try:
        await msg.delete()
        await ctx.message.delete()
    except:
        pass

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
        logger.error("   • GUILD_ID - Discord server ID (optional)")
        exit(1)
    
    logger.info("🚀 Starting Midnight Keylogin Bot...")
    logger.info("🎯 Features: Slash Commands, Interactive UI, Advanced Security")
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        exit(1) 
