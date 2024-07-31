import discord
import json
import asyncio

# Charger le fichier de configuration
with open('config.json') as config_file:
    config = json.load(config_file)

# Récupérer le token et les listes d'exclusion
TOKEN = config.get('token')
excluded_roles = config.get('excluded_roles', [])
excluded_members = config.get('excluded_members', [])

# Configurer les intentions du bot
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!dm '):
        args = message.content.split(' ')[1:]
        if len(args) < 2:
            await message.channel.send("Usage: `!dm <server_id> <message>`")
            return

        guild_id = args[0]
        msg_to_send = ' '.join(args[1:])
        guild = client.get_guild(int(guild_id))
        if not guild:
            await message.channel.send("Guild not found.")
            return

        try:
            members = await guild.fetch_members(limit=None).flatten()
            for member in members:
                if not member.bot and not any(role.id in excluded_roles for role in member.roles) and member.id not in excluded_members:
                    try:
                        await member.send(msg_to_send)
                        await asyncio.sleep(2)  # Pause de 2 secondes entre chaque message
                    except Exception as e:
                        print(f"Could not send message to {member}: {e}")
            await message.channel.send("Messages sent!")
        except Exception as e:
            print(e)
            await message.channel.send("An error occurred while fetching members.")

    elif message.content.startswith('!dmall '):
        args = message.content.split(' ')[1:]
        if len(args) < 1:
            await message.channel.send("Usage: `!dmall <message>`")
            return

        msg_to_send = ' '.join(args)

        try:
            for guild in client.guilds:
                async for member in guild.fetch_members(limit=None):
                    if not member.bot and not any(role.id in excluded_roles for role in member.roles) and member.id not in excluded_members:
                        try:
                            await member.send(msg_to_send)
                            await asyncio.sleep(2)  # Pause de 2 secondes entre chaque message
                        except Exception as e:
                            print(f"Could not send message to {member}: {e}")
            await message.channel.send("Messages sent to all members in all servers!")
        except Exception as e:
            print(e)
            await message.channel.send("An error occurred while fetching members.")

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
        embed = discord.Embed(title="Servers", color=0xFF69B4)  # Couleur rose

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
        embed = discord.Embed(title="Help", description=(
            "Available commands:\n\n"
            "`!dm <server_id> <message>` - Send a direct message to all members of the specified server.\n"
            "`!dmall <message>` - Send a direct message to all members of all servers.\n"
            "`!addrole <role_id>` - Add a role to the exclusion list.\n"
            "`!addmember <member_id>` - Add a member to the exclusion list.\n"
            "`!roles` - List all roles in the exclusion list.\n"
            "`!members` - List all members in the exclusion list.\n"
            "`!servers` - List all servers the bot is in.\n"
            "`!help` - Display this help message."
        ), color=0xFF69B4)  # Couleur rose
        await message.channel.send(embed=embed)

def save_config():
    with open('config.json', 'w') as config_file:
        json.dump({
            "token": TOKEN,
            "excluded_roles": excluded_roles,
            "excluded_members": excluded_members
        }, config_file, indent=2)

client.run(TOKEN)
