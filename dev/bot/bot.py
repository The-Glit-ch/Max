import os, json, random, time
from datetime import datetime

from discord import client

#External Custom Libs
from libs.acnh_api import ACNH_Call as acnh

import discord, asyncpraw, aiohttp
from discord.ext import commands, tasks
from dotenv import load_dotenv;  load_dotenv()

#Other
__version__ = "2.2.1" #Major.Minor.BugFix.PartOfUpdate
__author__  = "Matthew A. Florenzano || The_Glit-ch#4859"
__url__     = "https://github.com/The-Glit-ch"

#global
global lockdown
global shitposted
lockdown = False
shitposted = False

#Maps
color_map = [0xedbdb0,0xf2d0b0,0xc0c77c,0x3fa0a3,0x52616e] #Main-Peach-Green-Turquoise-Grey
emoji_map = {"skull":'\U0001F480',"joy":'\U0001F602',"moyai":'\U0001F5FF',"heavy_check":'\U00002705',"x_cross":'\U0000274C',"neutral_face":'\U0001F610',"worried":'\U0001F61F',
            "hahaha":'<:hahaha:894752316975087676>',"puro_surprised":'<:puro_surprised:894752337917263883>',"puro_pathetic":'<:puro_pathetic:894752354862243881>',"puro_ping":'<:puro_ping:894752368766369802>',"wut":'<:wut:894752382813098024>',"boohoo":'<:boohoo:894752397971316776>',"pensive_clown":'<:pensive_clown:894752451452870656>',"trollface":'<:trollface:894752463691841626>',"ping":'<:ping:894758117487837194>',"cringe":'<:cringeasf:896897324624797788>',"facepalm":'<:facepalm:897678284890988614>'}
status_map = {discord.Status.online:"Online",discord.Status.idle:"Idle",discord.Status.dnd:"Do Not Disturb",discord.Status.offline:"Offline"}
json_map = {"welcome_c":"channels/welcome", "announcements_c":'channels/announcements', "shitpost": 'daily_shitpost', "b_prefix":"bot_settings/prefix", "autoreply":'bot_settings/autoreply'}

#Snipes
snipes = {}
edit_snipes = {}

#Return Bot Prefix
async def returnPrefix(bot, message):
    guildID = message.guild.id
    if guildID:
        try:
            return getJSONData(guildID,json_map['b_prefix'])
        except:
            return "$"
    else:
        return "$"

#Vars
bot_id = 893676436349673503
authorized_users = [557339295325880320]
reddit = asyncpraw.Reddit(client_id=os.environ["REDDIT_ID"], client_secret=os.environ["REDDIT_SECRET"], user_agent="Max")

bot = commands.Bot(command_prefix=returnPrefix, activity=discord.Activity(type=discord.ActivityType.playing, name="$help"),status=discord.Status.online, intents=discord.Intents.all())
print("Replacing default help command...")
bot.remove_command("help")
print("Command replaced!")

#Regular Functions
def is_dataDir():
    if os.path.exists("./data") and os.path.exists("./data/server_conf"):
        print("Data directories found!")
    else:
        print("Data directories not found\nNow making one")
        os.mkdir("./data")
        os.mkdir("./data/server_conf")
        print("Data directories made")

def getJSONData(guild_id, path):
    try:
        with open(f"./data/server_conf/{guild_id}.json","r") as File:
                data = json.load(File)
                File.close()
                paths = path.split("/")

                for i in range(0, len(paths)):
                    if i == len(paths) - 1:
                        data = data[paths[i]]
                        print(f"JSON Data returned || {guild_id} on path '{path}'")
                        return data
                    else:
                        data = data[paths[i]]
    except FileNotFoundError or KeyError as err:
        print(f"File not found OR Invalid Key/Value pair\nErr: {err}")
        return None

def setJSONData(guild_id, path, value):
    try:
        with open(f"./data/server_conf/{guild_id}.json","r") as File:
            data = json.load(File)
            File.close()
            with open(f"./data/server_conf/{guild_id}.json","w") as File: #Oh python. The pain of my existence
                paths = path.split("/")

                if len(paths) > 1: #Kinda cringe we have to hard set it
                    data[paths[0]][paths[1]] = value
                else:
                    data[paths[0]] = value
                
                File.write(json.dumps(data))
                File.close()
                print(f"New JSON data set for {guild_id} || New Value: {value}")
    except FileNotFoundError or KeyError as err:
        print(f"File not found OR Invalid Key/Value pair\nErr: {err}")

def makeServerConf(guild_id):
    open(f"./data/server_conf/{guild_id}.json","a").close()
    with open(f"./data/server_conf/{guild_id}.json","w") as File:
        data = {
            "channels":{
                "welcome": None,
                "announcements": None
            },
            "daily_shitpost": False,
            "bot_settings": {
                "prefix":"$",
                "autoreply": False
            }
        }
        json.dump(data,File)
        File.close()

def returnRandom(x,y):
    return y[random.randint(x,len(y) - 1)]

#Async Funcs
async def getRedditPost(subbreddit:str):
    sub = await reddit.subreddit(subbreddit)
    random_list = []
    
    async for post in sub.hot(limit=100):
        random_list.append(post)
    
    for _ in random_list:
        post = returnRandom(0,random_list)
        if str(post.url).endswith(('.jpg', '.png', '.gif', '.jpeg')):
            return {"title":post.title,"author":post.author,"url":post.url}

async def showUpdateLog():
    print("Checking update logs....")
    with open("./data/update_log.json","r") as File:
        JSON = json.load(File);     File.close()
        
        if JSON["shown"] == True:
            print("No new updates")
            return
        else:
            with open("./data/update_log.json","w") as File: 
                print("New update!")
                embed = discord.Embed(title = JSON["title"], description = JSON["desc"], color = returnRandom(0,color_map), timestamp = datetime.utcnow())
                for guild in bot.guilds:
                    ID = guild.id
                    try:
                        channel = bot.get_channel(getJSONData(ID,json_map['announcements_c']))
                        await channel.send(embed=embed)
                    except:
                        for channel in guild.text_channels:
                            if channel.permissions_for(guild.me).send_messages:
                                await channel.send(embed = embed)
                                await channel.send("What this message in a specific channel? Set it in the configuration menu ($conf). Already did that? Make sure I have permissions to send and embed messages in that channel.")
                                break
            
                JSON["shown"] = True
                json.dump(JSON,File)
                File.close()
                print("Update announcment sent to servers")
                return         

#Events
@bot.event
async def on_ready():
    print(f"---Max v{__version__} starting up---")
    is_dataDir()
    #await cleanUp()
    print("Starting loops...")
    shitpost.start()
    dont_assign_one_tb_for_a_fucking_array.start()
    print("All loops started!")
    await showUpdateLog()
    print("---End---")

@bot.event
async def on_message(message):
    if lockdown == True:
        return

    if bot_id != message.author.id and message.author.bot != True and getJSONData(message.guild.id,json_map['autoreply']) == True:
        msg = message.content.lower()

        if "forgor" in msg or "fogor" in msg:
            await message.add_reaction(emoji_map["skull"])
        
        if str(bot_id) in msg and "$" not in msg:
            await message.reply(f"Ping {emoji_map['puro_ping' if random.randint(0,1) == 0 else 'ping']}")

        if "no cap" in msg:
            await message.reply(f"no kissie")
        
        if "ratio" in msg:
            await message.add_reaction(emoji_map["cringe"])
            my_msg = await message.reply(f"Did not ask + ratio")
            await my_msg.add_reaction(emoji_map["heavy_check"])

    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    if message.author.id != bot_id:
        snipes[message.channel.id] = {
            "author": message.author,
            "content": message.content,
            "createdAt": message.created_at.strftime('%d/%m/%y at %H:%M(UTC)'),
            "image": message.attachments[0].proxy_url if len(message.attachments) != 0 else None
        }
        print("New snipe added")

@bot.event
async def on_message_edit(old_msg, new_msg):
    if old_msg.author.id != bot_id:
        edit_snipes[old_msg.channel.id] = {
            "author": old_msg.author,
            "content": old_msg.content,
            "createdAt": new_msg.created_at.strftime('%d/%m/%y at %H:%M(UTC)'),
            "reply": old_msg
        }
        print("New edit snipe added")

@bot.event
async def on_guild_join(guild):
    print("Joined new server")
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send("Hi! Thank you for adding me. Type ``$help`` for a list of commands. If you are a server memeber with ``manage channels`` permisions then check out the server configuartion menu via ``$conf``")
            makeServerConf(guild.id)
            break

@bot.event
async def on_member_join(member):
    await member.send(f"Hi <@{member.id}> and welcome to the **{member.guild.name}** server. To see a list of commands type ``$help``")
    await bot.get_channel(getJSONData(member.guild.id,json_map['welcome_c'])).send(f"Welcome <@{member.id}> to the **{member.guild.name}** server")

@bot.event
async def on_member_remove(member):
    await bot.get_channel(getJSONData(member.guild.id,json_map['welcome_c'])).send(f"<@{member.id}> left the server")

#Dev Functions
@bot.command()
async def regen_server_conf(ctx):
    global lockdown

    if ctx.author.id in authorized_users:
        
        lockdown = True
        guilds = bot.guilds
        embed = discord.Embed(title = "**NOTICE**", description = "Your server configuration file is being update. Bot will be temporarly offline", color = discord.Colour.red(), timestamp = datetime.utcnow())
        embed_ = discord.Embed(title = "**NOTICE**", description = "Your server configuration file has been updated! Bot will be back online shortly", color = discord.Colour.green(), timestamp = datetime.utcnow())

        for guild in guilds:
            guildID = guild.id
            
            try:
                channel = bot.get_channel(getJSONData(guildID,json_map['announcements_c']))
                await channel.send(embed = embed)
            except:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        await channel.send(embed = embed)
                        await channel.send("What this message in a specific channel? Set it in the configuration menu ($conf). Already did that? Make sure I have permissions to send and embed messages in that channel.")
                        break
            
            makeServerConf(guildID) if os.path.exists(f"./data/server_conf/{guildID}.json") == False else print("Server already has a data file")

            print(f"Updating config file for {guildID}({guild.name})")
            
            save_paths     =    [json_map['welcome_c'],json_map['announcements_c'],json_map['b_prefix']]
            save_data      =    [getJSONData(guildID,json_map['welcome_c']),getJSONData(guildID,json_map['announcements_c']),getJSONData(guildID,json_map['b_prefix'])] #Data to save
            temp_save_path =    {}
            
            makeServerConf(guildID)
            for i in range(0,len(save_paths)):
                if save_paths[i] in [*temp_save_path.keys()]:
                    setJSONData(guildID,temp_save_path[save_paths[i]],save_data[i])
                else:
                    setJSONData(guildID,save_paths[i],save_data[i])
            print("Config file update done")
        
        lockdown = False
        print("Done!")

        for guild in guilds:
            guildID = guild.id
            try:
                channel = bot.get_channel(getJSONData(guildID,json_map['announcements_c']))
                await channel.send(embed = embed_)
            except:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        await channel.send(embed = embed_)
                        await channel.send("What this message in a specific channel? Set it in the configuration menu ($conf). Already did that? Make sure I have permissions to send and embed messages in that channel.")
                        break
        
        print("Servers notified update is done")
        print("Shutting down...")
        await bot.close()

@bot.command()
async def update_announce(ctx):
    global lockdown

    if ctx.author.id in authorized_users:
        
        lockdown = True
        guilds = bot.guilds
        print(guilds)
        embed = discord.Embed(title = "**NOTICE**", description = "Bot is now shutting down for update/maintenance", color = discord.Colour.red(), timestamp = datetime.utcnow())

        for guild in guilds:
            guildID = guild.id
            try:
                channel = bot.get_channel(getJSONData(guildID,json_map['announcements_c']))
                await channel.send(embed = embed)
            except:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        await channel.send(embed = embed)
                        await channel.send("What this message in a specific channel? Set it in the configuration menu ($conf). Already did that? Make sure I have permissions to send and embed messages in that channel.")
                        break
        
    
        await bot.close()

#Mod Functions
@bot.command()
@commands.has_permissions(kick_members = True)
@commands.guild_only()
async def kick(ctx, user:discord.Member, *, reason = None):
    channel = bot.get_channel(getJSONData(ctx.message.guild.id,json_map['welcome_c'])) if getJSONData(ctx.message.guild.id, json_map['welcome_c']) != None else ctx
    if reason == None:
        await user.kick(reason="None")
        await channel.send(f"<@{user.id}> has been kicked")
    else:
        await user.kick(reason=reason)
        await channel.send(f"<@{user.id}> has been kicked due to **{reason}**")

@kick.error
async def kick_error(ctx, error):
    user_ping = f"<@{ctx.author.id}>"

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{user_ping}  You need **Kick Members** permission to use this command")

@bot.command()
@commands.has_permissions(ban_members = True)
@commands.guild_only()
async def ban(ctx, user:discord.Member, *, reason = None):
    channel = bot.get_channel(getJSONData(ctx.message.guild.id,json_map['welcome_c'])) if getJSONData(ctx.message.guild.id,json_map['welcome_c']) != None else ctx
    if reason == None:
        await user.ban(reason="None")
        await channel.send(f"<@{user.id}> has been kicked")
    else:
        await user.ban(reason=reason)
        await channel.send(f"<@{user.id}> has been kicked due to **{reason}**")

@ban.error
async def ban_error(ctx, error):
    user_ping = f"<@{ctx.author.id}>"

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{user_ping}  You need **Ban Members** permission to use this command")

@bot.command()
@commands.has_permissions(manage_channels = True)
@commands.guild_only()
async def conf(ctx, setting = None, value = None):
    guildID = ctx.message.guild.id
    guildName = ctx.message.guild.name

    setting = str.lower(setting) if setting != None else None
    value = str.lower(value) if value != None else None
    
    true_list = ["true","t","yes","y","enable","yeah"]
    false_list = ["false","f","no","n","disable","nah"]

    if setting == None:
        Info = {"Channels":f"**Welcome**: <#{getJSONData(guildID,json_map['welcome_c'])}>\n**Announcements**: <#{getJSONData(guildID,json_map['announcements_c'])}>",
                "BotSettings":f"**Prefix**: ``{getJSONData(guildID,json_map['b_prefix'])}``\n**Autoreply**: ``{getJSONData(guildID,json_map['autoreply'])}``",
                "Misc": f"Daily **Shitpost**: ``{getJSONData(guildID,json_map['shitpost'])}``"}
        
        embed = discord.Embed(title = f"Server Settings for **{guildName}**",color = color_map[0], timestamp = datetime.utcnow())

        embed.add_field(name = "Channels", value = Info["Channels"], inline = True)
        embed.add_field(name = "Bot Settings", value = Info["BotSettings"], inline = True)
        embed.add_field(name = "Misc", value = Info["Misc"], inline = False)

        embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
        embed.set_thumbnail(url = ctx.guild.icon_url)
        embed.set_footer(text="|| Ex: $conf shitpost true ||")
        
        await ctx.send(embed=embed)
    
    elif setting == "welcome" and value != None and value.startswith("<#") == True:
        value = int(value.replace("<#","").replace(">",""))
        channel = bot.get_channel(value)
        if channel != None and channel.permissions_for(ctx.message.guild.me).send_messages:
            old_value = getJSONData(guildID,json_map['welcome_c'])
            setJSONData(guildID,json_map['welcome_c'],value)
            await ctx.send(f"**Welcome Channel** has been updated || <#{old_value}> --> <#{value}>")
        else:
            await ctx.send("Please enter in a valid channel and make sure I have permission to send and embed messages")
    
    elif setting == "announcements" and value != None and value.startswith("<#") == True:
        value = int(value.replace("<#","").replace(">",""))
        channel = bot.get_channel(value)
        if channel != None and channel.permissions_for(ctx.message.guild.me).send_messages:
            old_value = getJSONData(guildID,json_map['announcements_c'])
            setJSONData(guildID,json_map['announcements_c'],value)
            await ctx.send(f"**Announcements Channel** has been updated || <#{old_value}> --> <#{value}>")
        else:
            await ctx.send("Please enter in a valid channel and make sure I have permission to send and embed messages")
    
    elif setting == "shitpost" and value != None:
        if getJSONData(guildID,json_map['announcements_c']) != None:
            if value in true_list:
                old_value = getJSONData(guildID,json_map['shitpost'])
                value = True
                setJSONData(guildID,json_map['shitpost'],value)
                await ctx.send(f"**Daily Shitpost** has been updated || **{old_value}** --> **{value}**")
            
            elif value in false_list:
                old_value = getJSONData(guildID,json_map['shitpost'])
                value = False
                setJSONData(guildID,json_map['shitpost'],value)
                await ctx.send(f"**Daily Shitpost** has been updated || **{old_value}** --> **{value}**")
            
            else:
                await ctx.send("Please enter in a True/False value")
        else:
            await ctx.send("You must set an announcements channel before enabling this setting")
    
    elif setting == "prefix" and value != None:
        old_value = getJSONData(guildID, json_map['b_prefix'])
        value = value.lower()
        setJSONData(guildID,json_map['b_prefix'],value)
        await ctx.send(f"**Bot Prefix** has been updated || **{old_value}** --> **{value}**")

    elif setting == "autoreply" and value != None:
        if value in true_list:
            old_value = getJSONData(guildID,json_map['autoreply'])
            value = True
            setJSONData(guildID,json_map['autoreply'],value)
            await ctx.send(f"**Autoreply** has been updated || **{old_value}** --> **{value}**")
        
        elif value in false_list:
            old_value = getJSONData(guildID,json_map['autoreply'])
            value = False
            setJSONData(guildID,json_map['autoreply'],value)
            await ctx.send(f"**Autoreply** has been updated || **{old_value}** --> **{value}**")
        
        else:
            await ctx.send("Please enter in a True/False value")

@conf.error
async def conf_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"<@{ctx.author.id}> You need **Manage Channels** permission to use this command")

#Utility
@bot.command()
@commands.guild_only()
async def profile(ctx, user:discord.Member = None):
    user = ctx.author if user == None else user
    status = status_map[user.desktop_status] if user.is_on_mobile() != True else "Mobile Online"

    embed = discord.Embed(title=f"User Info",color=returnRandom(0,color_map), timestamp = datetime.utcnow())
    embed.set_author(name=ctx.author,url=ctx.author.avatar_url,icon_url=ctx.author.avatar_url)
    embed.add_field(name="Info",value=f"Joined on: **{user.joined_at.strftime('%d/%m/%y at %H:%M')}**\nNickname: **{user.nick}**\nStatus: **{status}**",inline=False)
    embed.add_field(name=f"Roles[{len(user.roles) - 1}]",value=f"{', '.join([r.mention for r in user.roles if r != ctx.guild.default_role])}",inline=False)
    embed.set_thumbnail(url=user.avatar_url)
    embed.set_footer(text=f"Requested by: {ctx.author}")
    
    await ctx.send(embed=embed)

@bot.command()
async def info(ctx):
    embed = discord.Embed(title = "Hi! My name is Max.", description = f"Hi! My name is Max.\nI am just your ordinary discord bot that ***cough cough*** replaced another bot ***cough cough*** Linda ***cough***.\nIf you want to see all my commands then type ``$help``.\nWant to invite me to your server? Then click the title!\nWell that is all for now. Cya later {ctx.author}!",color = returnRandom(0,color_map),url = "https://discord.com/api/oauth2/authorize?client_id=893676436349673503&permissions=533582965878&scope=bot" ,timestamp = datetime.utcnow())
    embed.set_author(name = bot.get_user(bot_id).name, icon_url = bot.get_user(bot_id).avatar_url, url = "https://discord.com/api/oauth2/authorize?client_id=893676436349673503&permissions=533582965878&scope=bot")
    embed.set_thumbnail(url = bot.get_user(bot_id).avatar_url)
    embed.set_footer(text=f"Requested by: {ctx.author}")

    await ctx.send(embed = embed)

@bot.command()
async def help(ctx, cmd = None):
    cmd = cmd.lower() if cmd != None else None

    help_dict = {"kick":{"usage":'$kick <user> <reason || optional>',
                        "ex":f'$kick <@{ctx.author.id}>\n$kick <@{ctx.author.id}> Short Reason\n$kick <@{ctx.author.id}> Really super dupper long reason',
                        "notes":'Kick a user from the server',
                        "alias":'None',
                        'cat':'mod'},
                "ban":{"usage":'$ban <user> <reason || optional>',
                        "ex":f'$ban <@{ctx.author.id}>\n$ban <@{ctx.author.id}> Short Reason\n$ban <@{ctx.author.id}> Really super dupper long reason',
                        "notes":'Ban a user from the server',
                        "alias":'None',
                        'cat':'mod'},
                "conf":{"usage":'$conf <setting> <value>',
                        "ex":'$conf announcements #announcements-channel\n$conf prefix !\n$conf shitpost true\n$conf autoreply nah',
                        "notes":'View and manage your server configuration settings',
                        "alias":'None',
                        'cat':'mod'},
                "profile":{"usage":'$profile <user || optional>',
                        "ex":f'$profile\n$profile <@{ctx.author.id}>',
                        "notes":'See your or another users discord profile',
                        "alias":'None',
                        'cat':'util'},
                "info":{"usage":'$info',
                        "ex":'$info',
                        "notes":'See bot information',
                        "alias":'None',
                        'cat':'util'},
                "help":{"usage":'$help <command>',
                        "ex":'$help\n$help kick\n$help conf',
                        "notes":'Shows the help menu',
                        "alias":'None',
                        'cat':'util'},
                "serverstats":{"usage":'$serverstats',
                        "ex":'$serverstats',
                        "notes":'Shows the server stats',
                        "alias":'None',
                        'cat':'util'},
                "snipe":{"usage":'$snipe',
                        "ex":'$snipe',
                        "notes":'Snipe a deleted message',
                        "alias":'None',
                        'cat':'fun'},
                "editsnipe":{"usage":'$editsnipe',
                        "ex":'$snipe\n$es',
                        "notes":'Snipe a edited message',
                        "alias":'$es',
                        'cat':'fun'},
                "magicball":{"usage":'$magicball <question>',
                        "ex":'$magicball does he love me?\n$magicball is he gay????',
                        "notes":'Ask the magic ball a question',
                        "alias":'None',
                        'cat':'fun'},
                "minecraft":{"usage":'$minecraft <top text,,bottom text>',
                        "ex":'$minecraft hello,,world\n$minecraft dont put to much text or,,it goes out of bounds',
                        "notes":'Make a Minecraft achievement with custom text\nTop and bottom text must be seperate by two ",,"',
                        "alias":'None',
                        'cat':'fun'},
                "urban":{"usage":'$urban <word>',
                        "ex":'$urban hello world\n$urban netflix and chill\n',
                        "notes":'Return a defnition of the word on Urban Dictionary',
                        "alias":'None',
                        'cat':'fun'},
                "kill":{"usage":'$kill <user>',
                        "ex":f'$kill\n$kill <@{ctx.author.id}>',
                        "notes":'Kill a user..or the user kills you',
                        "alias":'None',
                        'cat':'fun'},
                "insult":{"usage":'$insult <user || optional>',
                        "ex":f'$insult\n$insult <@{ctx.author.id}>',
                        "notes":'Insult yourself or a user',
                        "alias":'None',
                        'cat':'fun'},
                "critterpedia":{"usage":'$critterpedia <item type> <item name/item index>',
                        "ex":'$critterpedia fish pale chub\n$critterpedia sea 40',
                        "notes":'Get item data from the Animal Crossing: New Horizons API\nCurrent Item Types: Fish \|| Sea \|| Bug \|| Fossil',
                        "alias":'None',
                        'cat':'fun'}
    }
    
    cmd_list = [key for key in help_dict]

    if cmd == None:
        embed = discord.Embed(title = "Help Menu", color = returnRandom(0,color_map), timestamp = datetime.utcnow())
        _temp = {}

        def add_value(cat,i):
            try:
                _temp[cat] = _temp[cat] + str(f"``{i}``\n")
            except Exception:
                _temp[cat] = str(f"``{i}``\n")

        for i in cmd_list:
            print(i)
            cat = help_dict[i]['cat']

            if cat == "mod":
                add_value(cat,i)
            elif cat == "util":
                add_value(cat,i)
            elif cat == "fun":
                add_value(cat,i)

        embed.add_field(name = "Mod Commands", value = _temp["mod"], inline = True).video
        embed.add_field(name = "Utility Commands", value = _temp["util"], inline = True)
        embed.add_field(name = "Fun Commands", value = _temp["fun"], inline = True)
        embed.set_footer(text = "|| Ex: $help kick ||")
        
        await ctx.send(embed=embed)
    
    elif cmd in cmd_list:
        data = help_dict[cmd]
        
        embed = discord.Embed(title = f"Help for __{cmd}__ command", color = returnRandom(0,color_map), timestamp = datetime.utcnow())
        embed.add_field(name = "Usage", value = data["usage"], inline = False)
        embed.add_field(name = "Example(s)", value = data["ex"], inline = False)
        embed.add_field(name = "Notes", value = data["notes"], inline = False)
        embed.add_field(name = "Alias", value = data["alias"], inline = False)
        
        await ctx.send(embed=embed)

@bot.command()
@commands.guild_only()
async def serverstats(ctx):
    g = ctx.guild
    
    #Member Count
    all_count   = len(g.members)
    user_count  = len([m for m in g.members if not m.bot])
    bot_count   = len([m for m in g.members if m.bot])

    #Parse DateTime
    t = g.created_at
    create_date = f"{t.day}/{t.month}/{t.year} at {t.hour}:{f'0{t.minute}' if t.minute < 10 else t.minute}(UTC)" #Ik what you might say, but now is not the time

    #Server Boosters
    server_boosters = len(g.premium_subscribers) if len(g.premium_subscribers) != 0 else "None"

    embed = discord.Embed(title = f"Server Stats for __{g.name}__", color = returnRandom(0,color_map))
    embed.set_thumbnail(url = g.icon_url)
    embed.add_field(name = "Member Stats", value = f"All Members: **{all_count}**\nUsers: **{user_count}**\nBots: **{bot_count}**", inline = False)
    embed.add_field(name = "Server Info", value = f"Created On: **{create_date}**\nServer Boosters: **{server_boosters}**\nServer Owner: <@{g.owner.id}>", inline = False)

    await ctx.send(embed=embed)

#<@579786439269810196> is pissed :TrollFace:
@bot.command()
@commands.guild_only()
async def snipe(ctx):
    try:
        if snipes[ctx.message.channel.id] == None:
            pass
    except KeyError:
        await ctx.send("No one has been caught lacking...*yet*")
        return #Best way of checking lol

    author = snipes[ctx.message.channel.id]['author']
    content = snipes[ctx.message.channel.id]['content']
    sentAt = snipes[ctx.message.channel.id]['createdAt']
    image = snipes[ctx.message.channel.id]['image']


    embed = discord.Embed(title = f"{author} Caught lacking \U0001F4F8",description = content,color = returnRandom(0,color_map))
    embed.set_image(url = image) if image != None else None
    embed.set_footer(text = f"Sent on {sentAt}")
    
    
    await ctx.send(f"<@{author.id}>",embed=embed)

@bot.command(aliases = ["es"])
@commands.guild_only()
async def editsnipe(ctx):
    try:
        if edit_snipes[ctx.message.channel.id] == None:
            pass
    except KeyError:
        await ctx.send("No one has been caught lacking...*yet*")
        return #Best way of checking lol
    
    author = edit_snipes[ctx.message.channel.id]['author']
    content = edit_snipes[ctx.message.channel.id]['content']
    sentAt = edit_snipes[ctx.message.channel.id]['createdAt']
    reply = edit_snipes[ctx.message.channel.id]['reply']


    embed = discord.Embed(title = f"{author} thought they were slick \U0001F4F8",description = content,color = returnRandom(0,color_map))
    embed.set_footer(text = f"Sent on {sentAt}")
    
    
    await reply.reply(embed=embed)

@bot.command()
async def critterpedia(ctx, index:str = None,*_item):
    def check(reaction,user):
        return user == ctx.message.author and str(reaction.emoji) == '\U0001F50D'

    index = index if index != None else index
    item = '_'.join(_item).lower() if _item != "" else None

    item = item.replace("t._rex","trex").replace("t_rex","trex")

    embed = discord.Embed(title="Critterpedia", color = returnRandom(0,color_map), timestamp = datetime.utcnow())
    embed.set_footer(text = "Data provided by the ACNH API: http://acnhapi.com/")
    
    if index == "fish":
        try:
            data = await acnh(index,item)
        except Exception:
            await ctx.send("Invalid item name/index")
            return

        embed.add_field(name = "General Info", value = f"Name: **{data['name']['name-USen'].capitalize()}**\nRarity: **{data['availability']['rarity']}**\nLocation: **{data['availability']['location']}**\nShadow: **{data['shadow']}**", inline = False)
        embed.add_field(name = "Other Info", value = f"Normal Sell Price: **{data['price']}**\nC.J Sell Price: **{data['price-cj']}**")
        embed.add_field(name = "-", value = f"*{data['catch-phrase']}*\n\n*{data['museum-phrase']}*", inline = False)
        embed.set_thumbnail(url = data['icon_uri'])

    elif index == "sea":
        try:
            data = await acnh(index,item)
        except Exception:
            await ctx.send("Invalid item name/index")
            return

        embed.add_field(name = "General Info", value = f"Name: **{data['name']['name-USen'].capitalize()}**\nSpeed: **{data['speed']}**\nShadow: **{data['shadow']}**\nSell Price: **{data['price']}**", inline = False)
        embed.add_field(name = "-", value = f"*{data['catch-phrase']}*\n\n*{data['museum-phrase']}*", inline = False)
        embed.set_thumbnail(url = data['icon_uri'])
    
    elif index == "bug":
        try:
            data = await acnh(index,item)
        except Exception:
            await ctx.send("Invalid item name/index")
            return

        embed.add_field(name = "General Info", value = f"Name: **{data['name']['name-USen'].capitalize()}**\nRarity: **{data['availability']['rarity']}**\nLocation: **{data['availability']['location']}**", inline = False)
        embed.add_field(name = "Other Info", value = f"Spotted around: **{data['availability']['time'] if data['availability']['time'] != '' else 'All Day'}**\nSell Price: **{data['price']}**\nFlick Sell Price: **{data['price-flick']}**", inline = False)
        embed.add_field(name = "-", value = f"*{data['catch-phrase']}*\n\n*{data['museum-phrase']}*", inline = False)
        embed.set_thumbnail(url = data['icon_uri'])

    elif index == "fossil":
        try:
            data = await acnh(index,item)
        except Exception:
            await ctx.send("Invalid item name/index")
            return

        embed.add_field(name = "General Info", value = f"Name: **{data['name']['name-USen'].capitalize()}**\nPrice: **{data['price']}**\nCollection: **{data['part-of']}**", inline = False)
        embed.add_field(name = "-", value = f"*{data['museum-phrase']}*", inline = False)
        embed.set_thumbnail(url = data['image_uri'])


    msg = await ctx.send(embed=embed)
    await msg.add_reaction('\U0001F50D')

    try:
        await bot.wait_for('reaction_add', timeout=60, check=check)
    except TimeoutError:
        print("Embed Time Out")
    else:
        _t = await acnh(index,item)

        embed = discord.Embed()
        embed.title = f"__{_t['name']['name-USen'].capitalize()}__"
        embed.set_image(url = _t['image_uri'])
        await msg.edit(embed=embed)

#Fun
@bot.command()
async def magicball(ctx, *question):
    question = ' '.join(question)
    
    if question == "":
        await ctx.send("You forgot the question")
        return

    ResponseList = ["It is certain","Without a doubt","You may rely on it","Yes definitely","It is decidedly so","As I see it, yes","Most likely","Yes","Outlook good","Signs point to yes","Reply hazy try again","Better not tell you now","Ask again later","Cannot predict now","Concentrate and ask again","Don’t count on it","Outlook not so good","My sources say no","Very doubtful","My reply is no"]
    embed = discord.Embed(title=question,description=returnRandom(0,ResponseList),color=returnRandom(0,color_map))
    await ctx.send(embed=embed)

@bot.command()
async def minecraft(ctx, *text):
    text = "+".join(text)
    if text == "":
        await ctx.send("https://minecraftskinstealer.com/achievement/11/Smart+Ass/You+forgot+the+text")
    else:
        texts = str(text).split(",,") if ",," in text else None
        if texts != None:
            await ctx.send(f"https://minecraftskinstealer.com/achievement/11/{texts[0].capitalize()}/{texts[1].capitalize()}")
        else:
            await ctx.send("https://minecraftskinstealer.com/achievement/11/Use+Two+Commas/To+split+the+text")

@bot.command()
async def urban(ctx, *word):
    word = '+'.join(word)
    if word == "":
        await ctx.send(f"You have to enter in a word to define dum dum {emoji_map['facepalm']}")
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.urbandictionary.com/v0/define?term={word}") as resp:
                json_ = await resp.json()
                json_ = json_['list']

                definition = json_[0]['definition'].replace("[","").replace("]","")
                example = json_[0]['example'].replace("[","").replace("]","")
                permalink = json_[0]['permalink']

                #A little messy but gets the job done
                embed = discord.Embed(title=f'Define: "**{word.replace("+"," ")}**"',description=definition,color=returnRandom(0,color_map))
                embed.set_author(name = ctx.author,icon_url = ctx.author.avatar_url)
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/UD_logo-01.svg/1920px-UD_logo-01.svg.png")
                embed.add_field(name = f"Example:",value = example,inline = False)
                embed.set_footer(text=f"View on website: {permalink}")
                
                await ctx.send(embed=embed)

@bot.command()
async def kill(ctx, user:discord.Member = None):
    auth    = f"<@{ctx.author.id}>"
    usr     = f"<@{user.id}>" if user != None else None

    death_messages = [f"{usr} installed League of Legends", f"{usr} found out the true meaning of ***watersports***", f"{usr} attended the wrong Khan Academy", f"{usr} got choked a little too hard...kinky", f"{usr} got his balls kicked in, ha no more kids", #User Death
                    f"{auth} fucked {usr} a little too hard", #Auth kills User
                    f"{usr} made {auth} listen to 100 gecs",f"{auth} suffocated in {usr} thighs \U0001F633" #User kills Author
                    ]

    if user == None:
        await ctx.send("**Bam**! You're dead. Now this time give me a user")
        return
    else:
        await ctx.send(returnRandom(0,death_messages))

@bot.command()
async def insult(ctx, user:discord.Member = None):
    user = ctx.author if user == None else user

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://evilinsult.com/generate_insult.php?lang=en&type=json") as resp:
            json_ = await resp.json()
            await ctx.send(f"{json_['insult']} <@{user.id}>")

#Loops
@tasks.loop(seconds=1)
async def shitpost():
    global shitposted

    if shitposted == False and time.strftime("%H:%M",time.localtime()) == "00:00":
        for guild in bot.guilds:
            ID = guild.id
            if getJSONData(ID,json_map['shitpost']) == True:
                
                post = await getRedditPost("shitposting+196+gayspiderbrothel")
                embed = discord.Embed(title="Daily Shitpost",color=returnRandom(0,color_map)).set_image(url=post['url']).set_footer(text=f"Post: {post['url']}")
                
                await bot.get_channel(getJSONData(ID,json_map['announcements_c'])).send(embed=embed)
                print("Shitpost sent") #send shitpost
        
        shitposted = True
        print("Shitposted now True")
    
    elif shitposted == True and time.strftime("%H:%M",time.localtime()) == "00:01":
        shitposted = False
        print("Shitposted now False")
    
@tasks.loop(seconds=90)
async def dont_assign_one_tb_for_a_fucking_array():
    print("\n--Attempting snipe clearing--")
    snipes.clear()
    print("Snipes cleared!")
    edit_snipes.clear()
    print("Edit snipes cleared!")
    print("--All done!--")

bot.run(os.environ["TOKEN"])