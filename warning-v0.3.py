# Welcome on warning bot - This is a moderation bot for your discord server.
# import module for the bot.
import asyncio  # async function
import datetime  # date and time handling
import random  # generate random numbers
from collections import defaultdict  # dictionary with default values

import discord  # Discord API
import pytz  # timezone handling
from discord import Embed  # rich content for Discord messages
from discord.ext import commands  # extension for Discord bot commands

import config  # you will need to create your config.py and add your token in it. # bot configuration settings

# Creating a Default Instance
intents = discord.Intents.all()
# Dictionary to keep track of link posts by users
link_post_count = defaultdict(int)
# Creating the client with the specified intents
client = commands.Bot(command_prefix='/', intents=intents)


@client.event
async def on_connect():
    print(f"{client.user} is connected to Discord.")

@client.event
async def on_ready():
    # Loading of slash commands.
    await client.tree.sync()
    try:
        client.start_time = datetime.datetime.now()
        print(f"{client.user} is rebooting...")
        # Booting / Rebooting mode
        await client.change_presence(status=discord.Status.idle, activity=discord.Game(name="Rebooting..."))
        await asyncio.sleep(5)
        # Initializing mode - getting ready
        await client.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Initializing..."))
        await asyncio.sleep(5)
        print(f"{client.user} is ready to operate.")
        print(f"Latency: {client.latency}ms")
        print(len(client.commands), "Commands loaded.")
        print(f"{client.guilds[1]} is connected.")

        channel_count = sum(1 for guild in client.guilds for channel in guild.channels)
        print(f"Channel Amount: {channel_count} Connected.")

        member_count = sum(1 for guild in client.guilds for member in guild.members)
        print(f"Member Amount: {member_count} Connected.")

        category_count = sum(1 for guild in client.guilds for category in guild.categories)
        print(f"Category Amount: {category_count} Connected.")
        voice_count = len(client.voice_clients)
        print(f'Voice Amount: {voice_count} Connected.')
        await change_status()
    except discord.HTTPException as http_err:
        print(f"HTTP error occurred: {http_err}")
    except discord.ClientException as client_err:
        print(f"A customer error has occurred: {client_err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command. Use `/help' to see the list of available commands.")
    else:
        await ctx.send("An error occurred while processing the command.")
        print(f"Error: {error}")


# the status system is made with random module for be able to added multiple status, switching every 3 secs.
async def change_status():
    guild = client.get_guild(1218559535145418802) # add your own guild ID.
    activity_list = [f"{len(guild.members)} Members", f"{len(client.guilds)} servers."] # add your own status

    while True:
        try:
            selected_activity = random.choice(activity_list)

            await client.change_presence(
                status=discord.Status.online,
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=selected_activity
                )
            )
            await asyncio.sleep(5)
        except Exception as e:
            print(f"An error occurred while setting presence: {e}")
            # Log or handle the error appropriately

# this function is for when user join the discord server.
@client.event
async def on_member_join(member):
    print(f'SysInfo: {member.name} has joined the server.')

    channels = [12345,67890] # add your own channel id were the message will be sent.

    # Greeting message.
    embed = discord.Embed(title=f"Welcome to the server {member.name}!", color=0x00ff00)# you can add more information as you want below.

    # Send messages in each channel
    for channel_id in channels:
        channel = client.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)

    # add the role automatic
    if member.bot:  # If the member is a bot
        role = discord.utils.get(member.guild.roles, name="Bot")  # Récupérer le rôle "Bot" can be changed.
    else:  # If the member is human
        role = discord.utils.get(member.guild.roles, name="Human")  # Récupérer le rôle "Human" can be changed.

    if role:  # Si le rôle existe
        await member.add_roles(role)  # Ajouter le rôle au membre
    else:
        print(f'SysInfo: {role} doesnt exist.')

# this function is when a user leave the guild.
@client.event
async def on_member_remove(member):
    print(f'SysInfo: {member.name} has left the server.')
    channels = [12345, 67890]  # List of channels to send messages to
    mentioned_roles = [role.mention for role in member.roles if role.name != '@everyone']
    roles_str = ", ".join(mentioned_roles)
    # Calculating the duration of the member’s presence on the server
    time_in_server = datetime.now(pytz.utc) - member.joined_at
    # Conversion of duration into days, hours, minutes
    days, remainder = divmod(time_in_server.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    # Formatage de la chaîne de temps
    time_str = f"{int(days)} Days, {int(hours)} Hours, {int(minutes)} Minutes"

    print(f"{member.display_name} left the server.")

    embed = discord.Embed(title=f"Goodbye {member.name}!", color=0xff0000)
    embed.add_field(name="We're sad to see you leave.",
                       value="If you decide to come back, you'll always be welcome!",
                       inline=False)
    embed.add_field(name="Removed Roles", value=roles_str if roles_str else "None")
    embed.set_footer(text=f"Joined at: {time_str}")

    # Send messages in each channel
    for channel_id in channels:
        channel = client.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)
        else:
            print(f'No {channel} has been added in the list.')

# this function is for when member update their roles
@client.event
async def on_member_update(before, after):
    channels = [12345, 67890]  # List of channels to send messages to

    # Check if the member's roles have been modified
    if before.roles != after.roles:
        # List of added roles
        roles_added = [role.name for role in after.roles if role not in before.roles]
        # List of removed roles
        roles_removed = [role.name for role in before.roles if role not in after.roles]

        # Create an embed for role update messages
        embed = discord.Embed(title="Roles Update", color=discord.Color.blue())
        if roles_added:
            added_roles_str = ', '.join(roles_added)
            embed.add_field(name=f"{after.name} received the following role(s):", value=added_roles_str, inline=False)
        if roles_removed:
            removed_roles_str = ', '.join(roles_removed)
            embed.add_field(name=f"{after.name} lost the following role(s):", value=removed_roles_str, inline=False)

        # Send messages to each channel with the embed
        for channel_id in channels:
            channel = client.get_channel(channel_id)
            if channel:
                await channel.send(embed=embed)

# this function is for when user update their data as profile picture.
@client.event
async def on_user_update(before, after):
    channels = [1200785223458238594, 1196487382292238457]  # List of channels to send messages to

    # Check if the avatar has changed
    if before.avatar != after.avatar:
        # Create an embed message
        embed = discord.Embed(title="Profile Picture Update", color=0x00ff00)
        embed.set_author(name=after.name, icon_url=after.avatar.url if after.avatar else None)

        # Old Avatar
        if before.avatar:
            embed.add_field(name="Old Avatar", value=" ", inline=False)
            embed.set_image(url=before.avatar.url)
        else:
            embed.add_field(name="Old Avatar", value="No Avatar", inline=False)

        # New Avatar
        if after.avatar:
            embed.add_field(name="New Avatar", value=" ", inline=False)
            embed.set_thumbnail(url=after.avatar.url)
        else:
            embed.add_field(name="New Avatar", value="No Avatar", inline=False)

        # Send messages to each channel with the embed
        for channel_id in channels:
            channel = client.get_channel(channel_id)
            if channel:
                await channel.send(embed=embed)



@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # Your message log details
    print(
        f"Time: {message.created_at.strftime('%Y-%m-%d %H:%M:%S')}, "
        f"Message: {message.content}, Username: {message.author.name}, "
        f"Channel: {message.channel}, Discord: {message.guild.name}"
    )
    # Anti-Link system.
    links = ["http://", "https://", "www", "discord.gg"]  # links to detect
    # Whitelist role and server below.
    allowed_role_ids = [12345, 67890,2468]  # list of allowed role IDs (role1, role2,role3)
    allowed_server_ids = [12345]  # list of servers excluded from the anti-link system
    mute_threshold = 3  # Number of offenses (link unauthorized) before a user is muted
    link_post_count = {}  # Dictionary to store message counts per user

    # Check for unauthorized link sharing
    if any(link in message.content for link in links):
        user_roles_ids = [role.id for role in message.author.roles]
        if not any(role_id in user_roles_ids for role_id in
                   allowed_role_ids) and message.guild.id not in allowed_server_ids:
            # Increment the count of offenses
            user_id = message.author.id
            link_post_count[user_id] = link_post_count.get(user_id, 0) + 1

            # Check if the mute threshold has been reached
            if link_post_count[user_id] >= mute_threshold:
                muted_role = discord.utils.get(message.guild.roles, name="Muted")
                if muted_role:
                    await message.author.add_roles(muted_role, reason="Posting unauthorized links multiple times.")
                    print(f"{message.author} has been muted for posting unauthorized links repeatedly.")
                else:
                    print("Muted role not found.")
                print(f"{message.author} has been muted for posting unauthorized links repeatedly.")
                # Retrieving the infraction logs channel
                infraction_logs_channel_id = 12345  # Replace with your infraction logs channel ID
                infraction_logs_channel = client.get_channel(infraction_logs_channel_id)

                if infraction_logs_channel:  # Check if the channel was found
                    # Create an embed to record the infraction
                    embed = discord.Embed(
                        title="User Infraction",
                        description=(
                            f"**Member:** {message.author.mention} (`{message.author}`)"
                            f"\n**Action:** Muted"
                            f"\n**Reason:** Repeated unauthorized link posting"
                        ),
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Offense Count", value=str(link_post_count[user_id]))
                    embed.set_footer(text=f"User ID: {message.author.id}")
                    embed.set_thumbnail(url=message.author.avatar)
                    embed.timestamp = message.created_at

                    # Send the embed to the infraction logs channel
                    await infraction_logs_channel.send(embed=embed)
                else:
                    print(f"Could not find the infraction logs channel with ID: {infraction_logs_channel_id}")

                # Optionally reset their count, however the user has been banned
                del link_post_count[user_id]
                # Optionally reset their count, however, the user has been banned
                link_post_count[user_id] = 0
            else:
                # If not at the ban threshold, just delete the message and inform the user
                await message.delete()
                warning_message = await message.channel.send(
                    f"{message.author.mention}, you are not allowed to post links here without the proper role.")
                # Optionally delete the warning message after some time
                await asyncio.sleep(5)
                await warning_message.delete()

                print(
                    f"Unauthorized link removed. User {message.author} does not have the required role to post links.")
        else:
            print("User has the authorized role to post links or belongs to a whitelisted server.")



@client.hybrid_command(description="Displays information about the server.")
async def serverinfo(ctx: commands.Context):
    print("Command '/serverinfo' detected.")
    server = ctx.guild
    text_channels = len(server.text_channels)
    voice_channels = len(server.voice_channels)
    categories = len(server.categories)

    embed = discord.Embed(title="Server Information", color=discord.Color.blue())
    embed.add_field(name="Server Name", value=server.name, inline=False)
    embed.add_field(name="Member Count", value=server.member_count, inline=False)
    embed.add_field(name="Text Channels", value=text_channels, inline=False)
    embed.add_field(name="Voice Channels", value=voice_channels, inline=False)
    embed.add_field(name="Categories", value=categories, inline=False)
    await ctx.send(embed=embed)

# Delete function who make you delete a certain number of message or everything in the channel.
@client.hybrid_command(description="Deletes messages in the current channel.")
async def delete_msg(ctx: commands.Context):
    print("Command '/delete_msg' detected.")

    # Prompt for user input
    embed = discord.Embed(title="Delete Messages",
                          description="Please enter the number of messages to delete or type 'all' to delete all messages.",
                          color=discord.Color.blue())
    await ctx.send(embed=embed)

    # Define check function for wait_for
    def check(m):
        return m.author == ctx.message.author and m.channel == ctx.message.channel

    try:
        reply = await client.wait_for('message', check=check, timeout=30.0)

        if reply.content.lower() == 'all':
            # Delete all messages
            deleted_messages = await ctx.message.channel.purge()
            print('SysInfo: Deleting messages...')
        else:
            msg_count = int(reply.content)
            await reply.delete()

            # Delete messages
            deleted_messages = await ctx.message.channel.purge(limit=msg_count + 1)  # Also removes the initial command

        # Confirmation message
        embed = discord.Embed(title="Message Deletion Confirmation", color=discord.Color.green())
        embed.add_field(name="Action", value="Messages deleted", inline=False)
        embed.add_field(name="Messages Deleted", value=len(deleted_messages), inline=False)
        await ctx.send(embed=embed)
        print(f'SysInfo: Messages deleted: **{len(deleted_messages)}**')

    except asyncio.TimeoutError:
        embed = discord.Embed(title="Error", description="Sorry Pal, You took too long to respond.",
                              color=discord.Color.red())
        await ctx.message.channel.send(embed=embed)
    except ValueError:
        embed = discord.Embed(title="Error", description="Please enter a valid number.", color=discord.Color.red())
        await ctx.message.channel.send(embed=embed)

# Command to create a role
@client.hybrid_command(description="Creates a role.")
async def create_role(ctx: commands.Context, role_name):
    print("Command '/create_role' detected.")
    channels = [12345, 67890]  # List of channels to send messages to

    # Check if the user has permission to manage roles
    if ctx.author.guild_permissions.manage_roles:
        guild = ctx.guild

        # Check if the role already exists
        if any(role.name == role_name for role in guild.roles):
            embed = discord.Embed(title="Error", description="A role with this name already exists.",
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        # Create the role with the specified name
        new_role = await guild.create_role(name=role_name)
        print(f'SysInfo: {role_name} has been created.')
        # Add permissions to the role
        permissions = discord.Permissions(send_messages=True, read_messages=True)  # Set permissions as needed
        await new_role.edit(permissions=permissions)
        print(f'SysInfo: Adding permissions to {role_name}.')

        # Send a confirmation message that the role was successfully created
        embed = discord.Embed(title="Role Created",
                              description=f"The role '{role_name}' has been successfully created!",
                              color=discord.Color.green())
        for channel_id in channels:
            channel = client.get_channel(channel_id)
            if channel:
                await channel.send(embed=embed)  # Envoyer le message dans chaque canal
        print(f"SysInfo: The role {role_name} has been successfully created!")
    else:
        embed = discord.Embed(title="Error", description="You do not have the necessary permissions to create a role.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)


# this function make you delete a role with his role_name.
@client.hybrid_command(description="Deletes a role.")
async def delete_role(ctx: commands.Context, role_name):
    print("Command '/delete_role' detected.")

    # Check if the user has permission to manage roles
    if ctx.author.guild_permissions.manage_roles:
        print('SysInfo: Permission check.')
        guild = ctx.guild

        # Retrieve channels for confirmation messages
        channels = [12345, 67890]

        # Find role by name
        role = discord.utils.get(guild.roles, name=role_name)
        print(f'SysInfo: Searching for role by name {role_name}.')

        if role:
            # Delete the role
            await role.delete()

            embed = discord.Embed(title="Role Deleted",
                                  description=f"The role {role_name} has been successfully deleted!",
                                  color=discord.Color.green())

            for channel_id in channels:
                channel = client.get_channel(channel_id)
                if channel:
                    await channel.send(embed=embed)  # Envoyer le message dans chaque canal
            print(f'The role {role_name} has been successfully deleted!')
        else:
            embed = discord.Embed(title="Error", description=f"The role {role_name} was not found.",
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            print(f'SysError: The role {role_name} was not found!')
    else:
        embed = discord.Embed(title="Error",
                              description=f"Sorry, {ctx.author.mention}, you do not have permission to delete roles.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)
        print("Sorry, you do not have permission to delete roles.")


# Command to add a role to a user
@client.hybrid_command(description="Adds a role to a user.")
async def add_role(ctx: commands.Context, member: discord.Member, *, role_name):
    print("Command '/add_role' detected.")
    await ctx.defer()

    # Check if the user has permission
    if ctx.author.guild_permissions.manage_roles:
        print('SysInfo: Permission check.')
        guild = ctx.guild

        # Retrieve channels for confirmation messages
        channels = [12345, 67890] # add your own id
        print("SysInfo: Channel retrieval.")

        # Find role by name
        role = discord.utils.get(guild.roles, name=role_name)
        print(f'SysInfo: Searching for role by name {role_name}.')

        if role:
            # Add role to user
            await member.add_roles(role)
            embed = discord.Embed(title="Role Added",
                                  description=f"The role {role_name} has been successfully added to {member.mention}!",
                                  color=discord.Color.green())
            for channel_id in channels:
                channel = client.get_channel(channel_id)
                if channel:
                    await channel.send(embed=embed)  # Envoyer le message dans chaque canal
            print(f"The role {role_name} has been successfully added to {member.mention}!")
        else:
            embed = discord.Embed(title="Error", description=f"The role {role_name} was not found.",
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            print(f'The role {role_name} was not found.')
    else:
        embed = discord.Embed(title="Error", description="Sorry, you do not have permission to add roles.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)
        print("Sorry, you do not have permission to add roles.")


# Command to remove a role from a user
@client.hybrid_command(description="Removes a role from a user.")
async def remove_role(ctx: commands.Context, member: discord.Member, role_name: str):
    print("Command '/remove_role' detected.")

    # Check if the user has permission
    if ctx.author.guild_permissions.manage_roles:
        print('SysInfo: Permission check.')
        guild = ctx.guild

        # Retrieve channel IDs for confirmation messages
        channel_ids = [12345, 67890] # add your own id
        print('SysInfo: Channel retrieval.')

        # Find role by name
        role = discord.utils.get(guild.roles, name=role_name)
        print(f'SysInfo: Searching for role by name {role_name}.')

        if role:
            # Remove role from user
            await member.remove_roles(role)
            embed = discord.Embed(
                title="Role Removed",
                description=f"The role {role_name} has been successfully removed from {member.mention}!",
                color=discord.Color.green()
            )
            for channel_id in channel_ids:
                channel = client.get_channel(channel_id)
                if channel:
                    await channel.send(embed=embed)
            print(f"SysInfo: The role {role_name} has been successfully removed from {member.mention}!")
        else:
            embed = discord.Embed(
                title="Error",
                description=f"The role {role_name} was not found.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            print(f'SysInfo: The role {role_name} was not found.')
    else:
        embed = discord.Embed(
            title="Error",
            description="Sorry, you do not have permission to remove roles.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        print('SysError: Sorry, you do not have permission to remove roles.')


# this function able you to create a custom invitation with max_use and duration in minutes.
@client.hybrid_command(description="Creates an invitation link with specified settings.")
async def create_invit(ctx: commands.Context, max_uses: int, duration: int):
    print("Commande '/create_invit' détectée.")

    # Vérifier les permissions de l'utilisateur
    if not ctx.author.guild_permissions.create_instant_invite:
        await ctx.send("Vous n'avez pas la permission de créer des invitations.")
        return

    # Vérifier si les arguments sont corrects
    if max_uses <= 0 or duration <= 0:
        await ctx.send("Les utilisations maximales et la durée doivent être des entiers positifs.")
        return

    # Convertir la durée en secondes
    duration_seconds = duration * 60

    # Créer une invitation
    invite = await ctx.channel.create_invite(max_uses=max_uses, max_age=duration_seconds)

    # Envoyer l'invitation générée
    await ctx.send(
        f"Here is your invitation with {max_uses} maximum uses and a validity of {duration} minutes : {invite.url}")
    print(
        f"Here is your invitation with {max_uses} maximum uses and a validity of {duration} minutes : {invite.url}")



# this function give you the latency of the bot.
@client.hybrid_command(description="Check the bot's latency.")
async def ping(ctx: commands.Context):
    print('Commande /Ping détecté.')
    await ctx.defer()
    bot_latency = round(client.latency * 1000)
    embed = Embed(title="Bot Latency", description=f"{client.user.name} Latency: {bot_latency}ms.",
                  color=0x3498db)
    await ctx.message.channel.send(embed=embed)
    print(f"{bot_latency}ms")


@client.hybrid_command(description="Displays the total number of members in the server.")
async def member_count(ctx: commands.Context):
    total_members = ctx.message.guild.member_count
    embed = Embed(title="Total Server Members",
                  description=f"Total Members: {total_members} Members.", color=0x3498db)
    await ctx.message.channel.send(embed=embed)

@client.hybrid_command(description="Creates a channel with the specified name and type (text or voice).")
async def create_channel(ctx: commands.Context, channel_name, channel_type):
    print('Command /create_channel detected.')

    # Check if channel name and type are specified
    if channel_name and channel_type:
        guild = ctx.guild
        # Check if a channel with the same name already exists
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if existing_channel:
            # Check if the existing channel is of the same type as requested
            if (channel_type.lower() == "text" and isinstance(existing_channel, discord.TextChannel)) or \
               (channel_type.lower() == "voice" and isinstance(existing_channel, discord.VoiceChannel)):
                await ctx.send(f"The {channel_type} channel '{channel_name}' already exists.")
                return

        # Create the channel with the specified name and type
        if channel_type.lower() == "text":
            new_channel = await guild.create_text_channel(channel_name)
        elif channel_type.lower() == "voice":
            new_channel = await guild.create_voice_channel(channel_name)
        else:
            await ctx.send("Invalid channel type. Please specify 'text' or 'voice'.")
            return

        await ctx.send(f"Channel '{new_channel.name}' of type '{channel_type}' has been successfully created.")
    else:
        await ctx.send("Please specify both the name and type of the channel to create.")



@client.hybrid_command(description="Deletes a channel with the specified name and type (text or voice).")
async def delete_channel(ctx, channel_name, channel_type):
    print('Command /delete_channel detected.')

    # Check if channel name and type are specified
    if channel_name and channel_type:
        guild = ctx.guild
        # Retrieve the channel with the specified name
        if channel_type.lower() == "text":
            channel = discord.utils.get(guild.text_channels, name=channel_name)
        elif channel_type.lower() == "voice":
            channel = discord.utils.get(guild.voice_channels, name=channel_name)
        else:
            await ctx.send("Invalid channel type. Please specify 'text' or 'voice'.")
            return

        if channel:
            # Delete the channel
            await channel.delete()
            await ctx.send(f"The channel '{channel_name}' has been deleted.")
        else:
            await ctx.send(f"The channel '{channel_name}' was not found.")
    else:
        await ctx.send("Please specify both the name and type of the channel to delete.")


# RAID-Protect System
@client.hybrid_command(description="Activates raid protection for the specified duration.")
async def raid_protect(ctx: commands.Context, duration: int):
    print(f'Command /raid_protect detected.')
    await ctx.defer()
    message = ctx.message
    logs_channel_ids = [12345, 67890]
    print('SysInfo: Collecting logs channel.')
    # Récupérer les objets de canal à partir des IDs
    logs_channels = [message.guild.get_channel(channel_id) for channel_id in logs_channel_ids if message.guild.get_channel(channel_id)]
    if not logs_channels:
        await ctx.send("Couldn't find the logs channel.")
        print('SysError: Cannot find the logs channel.')
        return

    role = message.guild.default_role  # Get the default role
    print('SysInfo: Modifying perms...')
    # Modify each channel with or without category
    for channel in message.guild.channels:
        await process_overwrites(channel)
    print('SysInfo: Locking down channels...')
    # Set permissions for each logs channel
    for logs_channel in logs_channels:
        await logs_channel.set_permissions(role, send_messages=False)
        print(f"SysInfo: {logs_channel.name} has been locked.")  # Print the name of the locked channel
        # Lock all other text channels outside categories
        for channel in filter(lambda chan: chan.type == discord.ChannelType.text and not chan.category,
                              message.guild.text_channels):
            await channel.set_permissions(role, send_messages=False)
            print(f"SysInfo: {channel.name} has been locked.")  # Print the name of the locked channel

    # Send messages about raid protect status
    for logs_channel in logs_channels:
        await logs_channel.send(
            f"@everyone\n**Raid protect enabled.**\n**The server is now under system protection.**\nAll channels without "
            f"explicit exceptions are locked for **{duration}** minutes.")

    await asyncio.sleep(duration * 60)
    print('SysInfo: Restoring permissions...')
    # Restore permissions for channels without category
    for channel in message.guild.channels:
        if not channel.category:
            await process_overwrites(channel, allow=True, deny=False)
            print(
                f"SysInfo: Permissions restored for channel: {channel.name}")  # Print the name of the restored channel
    for logs_channel in logs_channels:
        await logs_channel.send(
            "@everyone\n**Raid protect disabled.**\nChannels without category are restored back to normal.")


async def process_overwrites(channel, allow=None, deny=None):
    for target, permissions in channel.overwrites.items():
        if isinstance(target, discord.Role) and target.id:
            if allow is not None and deny is not None:
                await channel.set_permissions(target, read_messages=allow, send_messages=deny)
            elif allow is not None:
                await channel.set_permissions(target, read_messages=allow)
            else:
                await channel.set_permissions(target, send_messages=deny)
        elif isinstance(target, discord.Member):
            await process_overwrites(target.voice.channel, allow, deny)

# Submit a suggestion for your discord server.
@client.hybrid_command(description="Submit a suggestion.")
async def suggest(ctx: commands.Context, suggestion_content):
    print("Commande '/suggest' détectée.")
    # Check if the suggestion is not empty
    if suggestion_content:
        # Create an embed to display the suggestion
        embed = discord.Embed(
            title="New suggestion:",
            description=suggestion_content,
            color=discord.Color.blue()
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

        # Envoyer la suggestion dans le canal dédié
        suggestion_channel = client.get_channel(1211826350042644510)  # Remplacer CHANNEL_ID par l'ID du canal dédié
        suggestion_message = await suggestion_channel.send(embed=embed)

        # Ajouter les réactions pour voter
        await suggestion_message.add_reaction('👍')
        await suggestion_message.add_reaction('👎')

        # Avertir le rôle "Humain"
        human_role = ctx.guild.get_role(1200797745322139658)  # Remplacer ROLE_ID par l'ID du rôle "Humain"
        await suggestion_channel.send(
            f"{human_role.mention}, A new suggestion has been added by {ctx.author.mention}.")
    else:
        await ctx.send("SysInfo: You must provide a non-empty suggestion.")


@client.hybrid_command(description="Restart the bot.")
async def reboot(ctx: commands.Context):
    print(f'SysInfo: Reboot detected.')
    if ctx.author.guild_permissions.administrator:
        print('SysInfo: This user is authorized with ADMIN perms.')
        # Creating the embed
        embed = discord.Embed(
            title="Bot Restart",
            description="The bot will restart in a few seconds... Please wait.",
            color=discord.Color.orange()
        )
        # Sending the embed
        print(f"SysInfo: Restarting {client.user.name}...")
        await ctx.send(embed=embed)
        try:
            # Closing HTTP connections if they exist
            if client.http and client.http.connector:
                await client.http.connector.close()
            else:
                await ctx.send("No HTTP connection to close.")
                print('SysInfo: No HTTP connection to close.')

            # Closing the Discord client
            print('SysInfo: Closing the client.')
            await client.change_presence(activity=discord.Status.idle)
            await asyncio.sleep(5)  # Wait for 5 seconds instead of 10
            await client.close()
            await asyncio.sleep(5)  # Wait for 5 seconds instead of 10

            # Restarting the Discord client
            await client.start(config.warning_pass)
        except Exception as e:
            await ctx.send(f"An error occurred while restarting the bot: {e}")
            print(f"SysError: An error occurred while restarting the bot: {e}")
    else:
        # If the user doesn't have the permission, send an error message
        await ctx.send("You don't have permission to execute this command.")
        print("SysInfo: The member doesn't have permission to execute this command.")


# commande de désactivation du bot (Utilisation restreinte)
@client.hybrid_command(description="shutting down the bot")
async def shutdown(ctx: commands.Context):
    # Checking if the user has admin permissions
    if ctx.author.guild_permissions.administrator:
        await ctx.send("Shutting down the bot... Goodbye!")
        await client.close()
    else:
        print(f'SysError: {ctx.author} doesnt have enough permissions.')
        await ctx.send(f"{ctx.author.mention}, you need to be an ADMIN to use this command.")

# ID du rôle requis pour démarrer un giveaway
REQUIRED_ROLE_ID = 12345  # Remplace par l'ID du membre
# Stockage des messages de giveaway
giveaway_messages = {}

# Commande pour démarrer un giveaway
@client.hybrid_command(description="start a giveaway")
async def start_giveaways(ctx: commands.Context):
    # Vérification du rôle
    role = discord.utils.get(ctx.guild.roles, id=REQUIRED_ROLE_ID)
    if role not in ctx.author.roles:
        await ctx.send("You don't have the required role to start a giveaway.")
        return

    # Fonction de vérification de l'auteur
    def check_author(m):
        return m.author == ctx.author

    await ctx.send("Please enter the reward for the giveaway:")
    reward_message = await client.wait_for('message', check=check_author)
    reward = reward_message.content

    await ctx.send("Please enter the duration of the giveaway in days:")
    duration_message = await client.wait_for('message', check=check_author)
    duration_days = int(duration_message.content)
    duration_seconds = duration_days * 24 * 60 * 60  # Conversion en secondes

    await ctx.send("Please enter the channel ID where the giveaway should be posted:")
    channel_message = await client.wait_for('message', check=check_author)
    channel_id = int(channel_message.content)

    giveaway_channel = client.get_channel(channel_id)

    if giveaway_channel is None:
        await ctx.send(f"Channel with ID {channel_id} not found.")
        return

    giveaway_embed = Embed(
        title="🎉 Giveaway! 🎉",
        description=f"React with 🎉 to enter!\n**Reward:** {reward}\n**Duration:** {duration_days} days",
        color=0x00ff00
    )
    giveaway_message = await giveaway_channel.send(embed=giveaway_embed)

    await giveaway_message.add_reaction("🎉")

    await asyncio.sleep(duration_seconds)

    giveaway_message = await giveaway_channel.fetch_message(giveaway_message.id)
    reaction = discord.utils.get(giveaway_message.reactions, emoji="🎉")

    users = await reaction.users().flatten()
    users = [user for user in users if not user.bot]

    if len(users) == 0:
        await ctx.send("No one participated in the giveaway.")
        return

    winner = random.choice(users)

    await ctx.send(f"Congratulations {winner.mention}! You won the giveaway for **{reward}**!")


# Commande pour reroll un giveaway
@client.hybrid_command(description="reroll a giveaway")
async def reroll_giveaways(ctx: commands.Context):
    # Vérification du rôle
    role = discord.utils.get(ctx.guild.roles, id=REQUIRED_ROLE_ID)
    if role not in ctx.author.roles:
        await ctx.send("You don't have the required role to reroll a giveaway.")
        return

    # Vérifier si un message de giveaway existe pour le serveur
    if ctx.guild.id not in giveaway_messages:
        await ctx.send("No ongoing giveaway found to reroll.")
        return

    # Récupérer le message de giveaway
    giveaway_message_id = giveaway_messages[ctx.guild.id]
    giveaway_message = await ctx.channel.fetch_message(giveaway_message_id)
    reaction = discord.utils.get(giveaway_message.reactions, emoji="🎉")

    users = await reaction.users().flatten()
    users = [user for user in users if not user.bot]

    if len(users) == 0:
        await ctx.send("No one participated in the giveaway.")
        return

    # Sélection d'un nouveau gagnant
    winner = random.choice(users)

    await ctx.send(f"Congratulations {winner.mention}! You are the new winner of the rerolled giveaway!")


@client.hybrid_command(description="Creates a new category with the specified name.")
async def create_cc(ctx: commands.Context, category_name):
    print(f'Command /create_cc detected.')
    guild = ctx.guild
    # Check if the user has the necessary permissions to create categories
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("You do not have the necessary permissions to create categories")
        return
    try:
        category = await guild.create_category(name=category_name)
        await ctx.send(f"Category '{category_name}' created successfully!")
    except discord.HTTPException:
        await ctx.send("SysError: An error occurred while creating the category. Please try again.")


@client.hybrid_command(description="Deletes a category with the specified name.")
async def delete_cc(ctx: commands.Context, category_name):
    print(f'Command /delete_cc detected.')
    guild = ctx.guild
    # Check if the user has the necessary permissions to delete categories
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("You do not have the necessary permissions to delete categories.")
        print('SysError: You do not have the necessary permissions to delete categories.')
        return
    print('SysInfo: Searching for category to delete.')
    # Search for the category to delete
    category = discord.utils.get(guild.categories, name=category_name)
    if category is None:
        await ctx.send("Category not found.")
        print('SysInfo: Category not found.')
        return
    try:
        await category.delete()
        await ctx.send(f"Category '{category_name}' deleted successfully!")
    except discord.HTTPException:
        await ctx.send(
            "SysError: An error occurred while deleting the category. Please try again.")


@client.hybrid_command(description="Change the name of a channel.")
async def change_channel_name(ctx: commands.Context, channel_name: str, channel_type: str):
    print("Command '/change_channel_name' detected.")
    print('SysInfo: Checking permissions.')
    # Check if the user has permission to manage channels
    if ctx.author.guild_permissions.manage_channels:
        print('SysInfo: This user has MANAGE_CHANNELS perms.')
        print('SysInfo: Retrieving the channel.')
        # Get the guild object
        guild = ctx.guild
        # Determine the channel type
        if channel_type.lower() == "text":
            # Find the text channel by name
            channel = discord.utils.get(guild.text_channels, name=channel_name)
        elif channel_type.lower() == "voice":
            # Find the voice channel by name
            channel = discord.utils.get(guild.voice_channels, name=channel_name)
        else:
            await ctx.send("Invalid channel type. Please specify 'text' or 'voice'.")
            return
        if channel is None:
            await ctx.send("Channel not found.")
            return
        print('SysInfo: Channel found.')
        try:
            # Change the channel name
            await channel.edit(name=channel_name)
            print('SysInfo: Channel name modified.')
            # Send a confirmation message
            await ctx.send(f"The channel name has been successfully changed to '{channel_name}'.")
            print(f"Channel name successfully changed to '{channel_name}'.")
        except Exception as e:
            # In case of error, send an error message
            await ctx.send(f"An error occurred while changing the channel name: {e}")
            print(f"Error occurred: {e}")
    else:
        # If the user doesn't have the required permissions, send an error message
        await ctx.send("You don't have the necessary permissions to manage channels.")
        print("Insufficient permissions to manage channels.")


@client.hybrid_command(description="Change the name of a category.")
async def change_name_cc(ctx: commands.Context, category_name: str, new_name: str):
    """
    Change the name of a category.

    Parameters:
        ctx (commands.Context): The context of the command.
        category_name (str): The current name of the category.
        new_name (str): The new name to be set for the category.
    """
    category = discord.utils.get(ctx.guild.categories, name=category_name)
    if category:
        await category.edit(name=new_name)
        await ctx.send(f"The name of the category has been changed to {new_name}.")
    else:
        await ctx.send("Category not found.")


@client.hybrid_command(description='Change the name of a role')
async def change_role_name(ctx, before: str, after: str):
    print("Command '/change_role_name' detected.")

    # Check if the user has permission to manage roles
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("You do not have permission to manage roles.")
        return

    guild = ctx.guild

    # Find the role by its current name
    role = discord.utils.get(guild.roles, name=before)
    print(f'SysInfo: Searching for role by name {before}.')

    if role is None:
        await ctx.send(f"Role '{before}' not found.")
        print(f'SysError: Role {before} not found.')
    else:
        try:
            # Change the role name
            await role.edit(name=after)
            await ctx.send(f"Role '{before}' has been successfully renamed to '{after}'.")
            print(f"SysInfo: Role '{before}' has been renamed to '{after}'.")
        except Exception as e:
            await ctx.send(f"An error occurred while renaming the role: {e}")
            print(f'SysError: An error occurred while renaming the role: {e}')

@client.hybrid_command(description="Check the uptime of the bot.")
async def uptime(ctx: commands.Context):
    print('Command /uptime détected.')
    # Get the time when the bot started
    start_time = client.start_time

    # Calculate the uptime
    uptime_delta = datetime.datetime.now() - start_time
    print('SysInfo: Calculate the uptime.')
    # Format the uptime message
    uptime_message = f"{client.user.name} has been online for {uptime_delta.days} days, {uptime_delta.seconds // 3600} hours, {uptime_delta.seconds // 60 % 60} minutes, and {uptime_delta.seconds % 60} seconds."

    # Create an embed for the uptime message
    embed = discord.Embed(title="Bot Uptime", description=uptime_message, color=discord.Color.blue())

    # Send the embed to the channel where the command was invoked
    await ctx.send(embed=embed)


@client.hybrid_command(description="Kick a user from the server.")
async def kick(ctx: commands.Context, member: discord.Member, *, reason: str):
    channel_ids = [12345, 67890] # add your own id

    # Check if the user has permission to kick members
    if not ctx.author.guild_permissions.kick_members:
        embed = discord.Embed(title="Error", description="You don't have permission to kick members.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    # Check if the bot has permission to kick members
    if not ctx.guild.me.guild_permissions.kick_members:
        embed = discord.Embed(title="Error", description="I don't have permission to kick members.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    # Check if the user specifies a reason
    if not reason:
        embed = discord.Embed(title="Error", description="Please provide a reason for the kick.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    try:
        # Kick the user with the specified reason
        await member.kick(reason=reason)
        embed = discord.Embed(title="Kick Success",
                              description=f"{member.mention} has been kicked from the server. Reason: {reason}",
                              color=discord.Color.green())

        # Send the embed to each channel in the list
        for channel_id in channel_ids:
            channel = client.get_channel(channel_id)
            if channel:
                await channel.send(embed=embed)

        # Send a private message to the user to inform them they have been kicked with the reason
        private_message = f"You have been kicked from the server. Reason: {reason}"
        await member.send(private_message)

    except discord.Forbidden:
        embed = discord.Embed(title="Error", description="I don't have permission to kick that member.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)
    except discord.HTTPException:
        embed = discord.Embed(title="Error",
                              description="An error occurred while trying to kick the member. Please try again later.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)

@client.hybrid_command(description="Ban a user from the server.")
async def ban(ctx: commands.Context, member: discord.Member, *, reason: str):
    channel = [12345,67890]# add your own id

    # Check if the user has permission to ban members
    if not ctx.author.guild_permissions.ban_members:
        embed = discord.Embed(title="Error", description="You don't have permission to ban members.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    # Check if the bot has permission to ban members
    if not ctx.guild.me.guild_permissions.ban_members:
        embed = discord.Embed(title="Error", description="I don't have permission to ban members.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    # Check if the user specifies a reason
    if not reason:
        embed = discord.Embed(title="Error", description="Please provide a reason for the ban.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    try:
        # Ban the user with the specified reason
        await member.ban(reason=reason)
        embed = discord.Embed(title="Ban Success",
                              description=f"{member.mention} has been banned from the server. Reason: {reason}",
                              color=discord.Color.green())
        await ctx.channel.send(embed=embed)

        # Envoi d'un message privé à l'utilisateur pour l'informer qu'il a été banni avec la raison
        private_message = f"You have been banned from the server. Reason: {reason}"
        await member.send(private_message)

    except discord.Forbidden:
        embed = discord.Embed(title="Error", description="I don't have permission to ban that member.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)
    except discord.HTTPException:
        embed = discord.Embed(title="Error",
                              description="An error occurred while trying to ban the member. Please try again later.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)

@client.hybrid_command(description="Unban a user with the bot.")
async def unban(ctx: commands.Context, user_id: int, *, reason: str):
    # Retrieve the channel where you want to send follow-up messages
    channel = [12345,67890]

    # Check permissions needed to perform unban action
    if ctx.author.guild_permissions.ban_members:
        try:
            # Convert the user ID into a discord object.
            user = await client.fetch_user(user_id)

            # Remove user ban
            await ctx.guild.unban(user, reason=reason)

            # Send a confirmation message in the designated channel
            await ctx.channel.send(
                f"The user: {user.name} with the {user_id} ID was unbanned by {ctx.author.name} for the following reason: {reason}")
            # Send a confirmation message in the channel where the command was executed
            await ctx.send(f"The user: {user.name} with ID {user_id} has been successfully unbanned.")
        except discord.NotFound:
            # If the user is not banned
            await ctx.send(f"The user: {user.name} with the {user_id} ID is not banned.")
        except discord.HTTPException:
            # En cas d'erreur de requête HTTP
            await ctx.send("An error occurred while trying to debug the user.")
    else:
        # Si l'utilisateur n'a pas les permissions nécessaires
        await ctx.send("You do not have the necessary permissions to perform this action.")



@client.hybrid_command(description="List all available commands.")
async def help_cmd(ctx: commands.Context):
    embed = discord.Embed(title="List of Available Commands", description="Here are the commands you can use:",
                          color=discord.Color.blue())

    commands_info = [
        ("serverinfo", "Displays information about the server."),
        ("delete_msg", "Deletes messages in the current channel."),
        ("create_role", "Creates a role."),
        ("delete_role", "Deletes a role."),
        ("add_role", "Adds a role to a user."),
        ("remove_role", "Removes a role from a user."),
        ("create_invit", "Creates an invitation link with specified settings."),
        ("ping", "Check the bot's latency."),
        ("member_count", "Displays the total number of members in the server."),
        ("create_tc", "Creates a text channel with the specified name."),
        ("delete_tc", "Deletes a text channel with the specified name."),
        ("raid_protect", "Activates raid protection for the specified duration."),
        ("suggest", "Submit a suggestion."),
        ("reboot", "Restart the bot."),
        ("create_cc", "Creates a new category with the specified name."),
        ("delete_cc", "Deletes a category with the specified name."),
        ("uptime", "Check the uptime of the bot."),
        ("kick", "Kick a user from the server."),
        ("ban", "Ban a user from the server."),
        ("unban","Unban a user from the server."),
        ("open_ticket", "Create an ticket for support request."),
        ("change_name", "Change the name of an member."),
        ("warn_user", "Warn an user."),
        ("change_name_tc", "Change the name of a channel."),
        ("change_name_cc", "Change the name of a category."),
        ("change_name_vc", "Change the name of a voice channel.")
    ]

    # Splitting commands into pages
    pages = [commands_info[i:i + 25] for i in range(0, len(commands_info), 25)]

    for page in pages:
        embed = discord.Embed(title="List of Available Commands", description="Here are the commands you can use:",
                              color=discord.Color.blue())
        for cmd, desc in page:
            embed.add_field(name=f"!{cmd}", value=desc, inline=False)
        await ctx.send(embed=embed)


@client.hybrid_command(description="Create an ticket for request services.")
async def open_ticket(ctx: commands.Context):
    print('Commande open_ticket détecté.')
    # Create a new ticket channel in the category specified.
    print('SysInfo: Create a ticket channel.')
    category = discord.utils.get(ctx.guild.categories, name="Support_name.category") # add your own category name
    ticket_channel = await ctx.guild.create_text_channel(f'ticket-{ctx.author.name}', category=category)

    # Set permissions for the ticket channel
    role_id = 12345  # Replace with the desired role ID
    role = ctx.guild.get_role(role_id)

    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    await ticket_channel.edit(overwrites=overwrites)
    print('SysInfo: Sends message in ticket channel.')

    # Send message to the ticket channel
    embed = discord.Embed(title='New Ticket has been created.', color=0x0099ff)
    embed.add_field(name='Description of Request', value='Please be specific and detailed about what you want.',
                    inline=False)
    embed.add_field(name='Request:', value='Please indicate your request.', inline=False)
    embed.timestamp = ctx.message.created_at

    await ticket_channel.send(embed=embed)

    # Notification to administrators or support team
    support_channel = discord.utils.get(ctx.guild.channels,
                                        name='test')  # Replace 'test' with your support channel name
    if support_channel is not None:
        await support_channel.send(f"A new ticket has been opened by {ctx.author.mention}.")
        print(f"SysInfo: A new ticket has been opened by {ctx.author.mention}.")

    # If no support team member is available, notify the developer
    if not role.members:
        developer = discord.utils.get(ctx.guild.members,
                                      name='test')  # Replace 'test' with your developer's username
        if developer is not None:
            await developer.send("Alert: A request is awaiting processing as no support team member is available.")
            print("SysInfo: A request is awaiting processing as no support team member is available.")

    # Confirmation message to the client
    await ctx.send(
        f"{ctx.author.mention}, your request has been received. A support team member will process it shortly.")


@client.hybrid_command(description="Change the name of a specified player.")
async def change_name(ctx: commands.Context, member: discord.Member, new_name: str):
    # Récupérer le canal où vous voulez envoyer des messages de suivi
    channel = [12345, 67890] # add your own id
    try:
        # Check if the user has the necessary permissions to change member nicknames
        if ctx.author.guild_permissions.manage_nicknames:
            # Modify the nickname of the specified member
            await member.edit(nick=new_name)
            embed = discord.Embed(title="Nickname Changed",
                                  description=f"The name of {member.display_name} has been changed to {new_name}.",
                                  color=discord.Color.green())
            await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(title="Permission Error",
                                  description="You don't have permission to change member nicknames.",
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(title="Permission Error",
                              description="I don't have permission to change member nicknames.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="Error", description=f"An error occurred: {e}", color=discord.Color.red())
        await ctx.send(embed=embed)


@client.hybrid_command(description="Warn a user.")
async def warn_user(ctx: commands.Context, member: discord.Member, reason: str):
    print('Warn command detected.')

    # Check if the user has permission to give a warning
    print('SysInfo: Checking permissions.')
    if ctx.author.guild_permissions.kick_members:
        print('SysInfo: User has kick permissions.')

        # List of channel IDs where you want to send the follow-up messages
        channel_ids = [12345, 67890]

        # Create the embed
        embed = discord.Embed(
            title=f"{member} has been warned",
            description=f"Reason: {reason}",
            color=discord.Color.orange()
        )

        # Add footer with context author's avatar
        embed.set_footer(text=f"Warning by {ctx.author}",
                         icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)

        # Send the embed to each channel in the list
        for channel_id in channel_ids:
            channel = client.get_channel(channel_id)
            if channel:
                await channel.send(embed=embed)

        # Send a DM to the warned user
        try:
            await member.send(f"You have been warned in {ctx.guild.name}. Reason: {reason}")
        except discord.errors.Forbidden:
            print("SysInfo: Unable to send DM to the user.")

        print(f'SysInfo: {member.name} has been warned for the following reason: {reason}')

    else:
        # If the user doesn't have permission, send an error message
        embed = discord.Embed(
            title="Error",
            description="You don't have permission to give a warning.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        print(f'SysInfo: {ctx.author.name}, you do not have permission to give a warning.')


@client.hybrid_command(description="Temporarily restricts a user from sending messages.")
async def timeout(ctx: commands.Context, member: discord.Member, duration: int, reason: str):
    # Retrieve the channel where you want to send follow-up messages
    channel = [12345, 67890]
    # Check if the author has the necessary permissions to timeout members
    if not ctx.author.guild_permissions.manage_roles:
        embed = discord.Embed(title="Error", description="You don't have permission to use this command.",
                              color=discord.Color.red())
        await ctx.channel.send(embed=embed)
        return

    # Get the muted role
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

    # If the muted role doesn't exist, create it
    if not muted_role:
        try:
            muted_role = await ctx.guild.create_role(name="Muted")
            # Apply permissions to the muted role to prevent sending messages
            muted_permissions = discord.PermissionOverwrite(send_messages=False)
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, overwrite=muted_permissions)
        except discord.Forbidden:
            embed = discord.Embed(title="Error",
                                  description="I don't have permission to create roles. Please create a role called 'Muted' with appropriate permissions.",
                                  color=discord.Color.red())
            await channel.send(embed=embed)
            return

    # Assign the muted role to the member
    try:
        await member.add_roles(muted_role, reason=reason)
        embed = discord.Embed(title="Timeout",
                              description=f"{member.mention} has been temporarily muted for {duration} minutes.",
                              color=discord.Color.orange())
        embed.add_field(name="Reason:", value=reason, inline=False)
        await channel.send(embed=embed)

        # Schedule the removal of the muted role after the specified duration
        await asyncio.sleep(duration * 60)  # Convert minutes to seconds
        await member.remove_roles(muted_role, reason="Timeout duration expired.")
    except discord.Forbidden:
        embed = discord.Embed(title="Error", description="I don't have permission to mute members.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)
    except discord.HTTPException:
        embed = discord.Embed(title="Error",
                              description="An error occurred while trying to mute the member. Please try again later.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)

client.run(config.warning_pass)
