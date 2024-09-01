import discord
import json
import asyncio

# Load the configuration file
with open('config.json') as config_file:
    config = json.load(config_file)

# Retrieve the token and exclusion lists
TOKEN = config.get('token')
excluded_roles = config.get('excluded_roles', [])
excluded_members = config.get('excluded_members', [])

# Set up the bot's intents
intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

# Set to track users who have already received a DM
messaged_users = set()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!dm ') or message.content.startswith('!dmall '):
        args = message.content.split(' ')[1:]
        is_dm_all = message.content.startswith('!dmall')

        if (is_dm_all and len(args) < 1) or (not is_dm_all and len(args) < 2):
            await message.channel.send(f"Usage: `{'!dmall <message>' if is_dm_all else '!dm <server_id> <message>'}`")
            return

        msg_to_send = ' '.join(args[1:]) if not is_dm_all else ' '.join(args)
        embed = discord.Embed(
            title="Send Confirmation",
            description=f"Are you sure you want to send the following message as a DM?\n\n**Message:**\n{msg_to_send}\n\n*Note: The message will be sent without embed in the DMs.*",
            color=0xFF69B4  # Pink color
        )

        # Create confirmation buttons
        confirm_button = discord.ui.Button(label='Accept', style=discord.ButtonStyle.success, custom_id='confirm')
        cancel_button = discord.ui.Button(label='Reject', style=discord.ButtonStyle.danger, custom_id='cancel')
        view = discord.ui.View()
        view.add_item(confirm_button)
        view.add_item(cancel_button)

        # Send confirmation message
        confirmation_message = await message.channel.send(embed=embed, view=view)

        async def handle_interaction(interaction):
            if interaction.user.id != message.author.id:
                await interaction.response.send_message("You're not allowed to confirm this action.", ephemeral=True)
                return

            if interaction.custom_id == 'confirm':
                await interaction.response.edit_message(content='Message confirmed. Sending...', view=None)

                if is_dm_all:
                    await send_dms_to_all_guilds(message, msg_to_send)
                else:
                    guild_id = args[0]
                    guild = client.get_guild(int(guild_id))
                    if not guild:
                        await message.channel.send("Guild not found.")
                        return
                    await send_dms_to_guild(message, guild, msg_to_send)

                await message.channel.send(f"{message.author.mention}, the messages have been successfully sent!")
            elif interaction.custom_id == 'cancel':
                await interaction.response.edit_message(content='Sending canceled. Please rewrite your message.', view=None)

        view.interaction_check = handle_interaction

    elif message.content.startswith('!addrole '):
        args = message.content.split(' ')
        if len(args) != 2:
            await message.channel.send("Usage: `!addrole <role_id>`")
            return

        role_id = int(args[1])
        if role_id not in excluded_roles:
            excluded_roles.append(role_id)
            save_config()
            await message.channel.send(f"Role ID {role_id} added to the exclusion list.")
        else:
            await message.channel.send(f"Role ID {role_id} is already in the exclusion list.")

    elif message.content.startswith('!addmember '):
        args = message.content.split(' ')
        if len(args) != 2:
            await message.channel.send("Usage: `!addmember <member_id>`")
            return

        member_id = int(args[1])
        if member_id not in excluded_members:
            excluded_members.append(member_id)
            save_config()
            await message.channel.send(f"Member ID {member_id} added to the exclusion list.")
        else:
            await message.channel.send(f"Member ID {member_id} is already in the exclusion list.")

    elif message.content == '!roles':
        if not excluded_roles:
            await message.channel.send("No roles in the exclusion list.")
        else:
            roles = [f"<@&{role_id}>" for role_id in excluded_roles]
            await message.channel.send("Excluded Roles:\n" + "\n".join(roles))

    elif message.content == '!members':
        if not excluded_members:
            await message.channel.send("No members in the exclusion list.")
        else:
            members = [f"<@{member_id}>" for member_id in excluded_members]
            await message.channel.send("Excluded Members:\n" + "\n".join(members))

    elif message.content == '!servers':
        embed = discord.Embed(title="Servers", color=0xFF69B4)  # Pink color

        for guild in client.guilds:
            try:
                if guild.system_channel and guild.me.guild_permissions.create_instant_invite:
                    invite = await guild.system_channel.create_invite(max_age=0, max_uses=1)
                    embed.add_field(name=guild.name, value=f"[Join {guild.name}]({invite.url})")
                else:
                    embed.add_field(name=guild.name, value="No invite link available")
            except Exception as e:
                print(e)
                embed.add_field(name=guild.name, value="No invite link available")

        await message.channel.send(embed=embed)

    elif message.content == '!help':
        embed = discord.Embed(
            title="Help",
            description=(
                "Available commands:\n\n"
                "`!dm <server_id> <message>` - Send a direct message to all members of the specified server.\n"
                "`!dmall <message>` - Send a direct message to all members of all servers.\n"
                "`!addrole <role_id>` - Add a role to the exclusion list.\n"
                "`!addmember <member_id>` - Add a member to the exclusion list.\n"
                "`!roles` - List all roles in the exclusion list.\n"
                "`!members` - List all members in the exclusion list.\n"
                "`!servers` - List all servers the bot is in.\n"
                "`!help` - Display this help message."
            ),
            color=0xFF69B4  # Pink color
        )
        await message.channel.send(embed=embed)

async def send_dm(member, msg_to_send):
    if member.id in messaged_users:
        print(f"Message not sent to {member} (ID: {member.id}) because they have already received a message.")
        return

    try:
        await member.send(msg_to_send)
        print(f"Message sent to {member} (ID: {member.id}): {msg_to_send}")
        messaged_users.add(member.id)  # Add user to the set after sending the message
        await asyncio.sleep(2)  # Pause of 2 seconds between each message
    except Exception as e:
        if isinstance(e, discord.Forbidden):
            print(f"Cannot send message to {member} (DMs disabled or bot blocked).")
        else:
            print(f"Could not send message to {member}: {e}")

async def send_dms_to_guild(message, guild, msg_to_send):
    await message.channel.send(f"{message.author.mention}, starting to send messages to members of the server {guild.name}...")
    try:
        members = await guild.fetch_members(limit=None).flatten()
        for member in members:
            if not member.bot and not any(role.id in excluded_roles for role in member.roles) and member.id not in excluded_members:
                await send_dm(member, msg_to_send)
        await message.channel.send(f"{message.author.mention}, the messages have been sent to the members of the server {guild.name}.")
    except Exception as e:
        print(e)
        await message.channel.send(f"{message.author.mention}, an error occurred while sending the messages.")

async def send_dms_to_all_guilds(message, msg_to_send):
    await message.channel.send(f"{message.author.mention}, starting to send messages to all members in all servers...")
    try:
        for guild in client.guilds:
            await send_dms_to_guild(message, guild, msg_to_send)
        await message.channel.send(f"{message.author.mention}, the messages have been sent to all members in all servers.")
    except Exception as e:
        print(e)
        await message.channel.send(f"{message.author.mention}, an error occurred while sending the messages.")

def save_config():
    with open('config.json', 'w') as config_file:
        json.dump({
            "token": TOKEN,
            "excluded_roles": excluded_roles,
            "excluded_members": excluded_members
        }, config_file, indent=2)

client.run(TOKEN)
