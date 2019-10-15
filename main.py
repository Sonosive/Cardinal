# Cardinal Bot created by Sonosive

import discord
import dbOperations
import re
import json
from discord.ext import commands

# https://discordapp.com/api/oauth2/authorize?client_id=613181852177530919&permissions=2080898257&scope=bot

# TODO: add Cogs for commands. Basically organizes the commands, and allows command groups to be enabled/disabled

with open('config.json') as config_file:    # using hidden config json for token
    data = json.load(config_file)

token = data["token"]

client = commands.Bot(command_prefix='c!')


class Ship:     # doesn't do anything actually lol
    def __init__(self, name, ship_class, score, cost):
        self.name = name
        self.ship_class = ship_class
        self.score = score
        self.cost = cost


# Events

@client.event
async def on_ready():
    dbOperations.create_tables()

    game = discord.Game("c!info or c!help")
    await client.change_presence(status=discord.Status.online, activity=game)
    print("Cardinal is ready")


@client.event
async def on_member_join(member):   # function for member joining the Meridian Server
    GENERAL_ID = 614954401404157955
    WELCOME_CHANNEL_ID = 615019804738191393
    welcome_channel = await client.fetch_channel(WELCOME_CHANNEL_ID)
    general_channel = await client.fetch_channel(GENERAL_ID)

    await general_channel.send(f"**Welcome {member.mention} to Meridian!**")
    reactions = ['🅱', "⚛", '🏜', '🌐', "⚙", '🅰']
    welcome_message = await welcome_channel.send(
        f"**Welcome {member.mention} to the Meridian Trading Server! "
        f"To get started, react to this message with your corresponding faction"
        f" to join its role. "
        f"If you do not see your faction, please contact the Meridian Chairman\n\n"
        f"B-Sec: 🅱 \n\nDIDAO: ⚛ \n\nSahara: 🏜\n\nGlobal United: 🌐\n\neDEN: ⚙\n\nAlterra: 🅰 **")

    for emoji_id in reactions:
        await welcome_message.add_reaction(emoji=emoji_id)

    def react_check(reaction, user):
        return user == member and (
                    str(reaction.emoji) == '🅱' or str(reaction.emoji) == "⚛" or str(reaction.emoji) == '🏜' or str(
                reaction.emoji) == '🌐' or str(reaction.emoji) == "⚙" or str(reaction.emoji) == '🅰')

    reaction, user = await client.wait_for('reaction_add', check=react_check)

    if str(reaction.emoji) == '🅱':
        role = discord.utils.get(member.guild.roles, name="BSEC")
        await member.add_roles(role)
    elif str(reaction.emoji) == "⚛":
        print("fired")
        role = discord.utils.get(member.guild.roles, name="DIDAO")
        await member.add_roles(role)
    elif str(reaction.emoji) == '🏜':
        role = discord.utils.get(member.guild.roles, name="Sahara")
        await member.add_roles(role)
    elif str(reaction.emoji) == '🌐':
        role = discord.utils.get(member.guild.roles, name="Global United")
        await member.add_roles(role)
    elif str(reaction.emoji) == "⚙":
        role = discord.utils.get(member.guild.roles, name="eDEN")
        await member.add_roles(role)
    elif str(reaction.emoji) == '🅰':
        role = discord.utils.get(member.guild.roels, name="Alterra")
        await member.add_roles(role)

    client.delete_message(welcome_message)


@client.event
async def on_command_error(ctx, error):     # TODO: command-specific error messages (i.e incorrect parameters)
    await ctx.send(f"Error: **{error}**")   # send error message to channel


# Commands

class Utilities(commands.Cog):  # Cog for basic, generic commands, like help, ping, etc.

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Pong!")
    async def ping(self, ctx):
        await ctx.send(f"Pong! **{round(client.latency * 1000)}**ms")

    @commands.command(brief="More information")
    async def info(self, ctx):
        await ctx.send(f"**Welcome to Cardinal, the Ship and Trade manager for factions!**\n\n"
                       f"Cardinal was made to facilitate trade and economy between factions\n"
                       f"To see all the ships currently in the database, use `c!ships`\n"
                       f"To view a list of the factions, use `c!factions`\n"
                       f"For faction CEOS, register ships with `c!register`. "
                       f" followed by the *name, class, cost,* and *Battle Score* of the ship.\n"
                       f"Please note that ship names must be 1 word! Use underscores and dashes if necessary.\n"
                       f"Make sure to hold a vote first regarding the cost and Battle Score!\n\n\n"
                       f"For a list of all the other commands, use `c!help`\n"
                       f"If an error message comes up, feel free to report it to Sono")

    @commands.command(brief="Planned updates")
    async def updates(self, ctx):
        await ctx.send(f"**Planned Updates:** (With no particular deadline)\n"
                       f"**1. Add support for changes in CEO roles \n"
                       f"2. Improve help menu, error messages, and other UX \n"
                       f"3. Plan out implementation for personal trading accounts, stocks, and investments**")

    @commands.command()
    async def commit(self, ctx):
        dbOperations.conn_commit()  # when the bot is acting whack, run this before closing to commit db changes


class FactionCommands(commands.Cog):    # Cog for faction related commands

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="For CEOs to create their faction")
    async def createFaction(self, ctx, name):

        def check(m):
            return m.author == ctx.author

        role = discord.utils.get(ctx.guild.roles, name="CEO")
        if role in ctx.author.roles:
            await ctx.send(f"**Are you sure you want to name your faction {name}? "
                           f"This action cannot be undone. Reply with `Yes` or `No` **")
            reply = await client.wait_for('message', check=check)

            if reply.content.lower() == "yes":
                dbOperations.new_faction(name, ctx.author.id)
                await ctx.send(f"**{name} has been created!**")
            elif reply.content.lower() == "no":
                await ctx.send(f"**Faction creation cancelled**")
            else:
                await ctx.send(f"**Unknown input, cancelling**")
        else:
            await ctx.send(
                f"**Only CEOs can create their faction! Talk to a supervisor if you wish to create a faction!**"
            )

    @commands.command()
    async def factions(self, ctx):
        menu = dbOperations.get_factions()
        await ctx.send(menu)

    @commands.command()
    async def faction(self, ctx, query):
        fct = dbOperations.get_faction(query.lower())

        if fct == "Not Found":
            await ctx.send(f"**{query} not found!**")
            return

        ceo = discord.utils.get(client.get_all_members(), id=int(fct[2]))

        embed = discord.Embed(
            title=fct[0],
            colour=discord.Color.gold()
        )
        embed.set_author(name=f"\n")
        embed.add_field(name="CEO", value=ceo)
        embed.add_field(name="Balance", value=fct[1])
        embed.add_field(name="Current Score", value=fct[3])
        await ctx.send(embed=embed)


class ShipCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="For CEO's to register their member's ship",
                      desc="Register a ship for use. Note that names MUST be 1 word!")
    async def register(self, ctx, name, faction_name, score, cost):

        role = discord.utils.get(ctx.guild.roles, name="CEO")

        score = re.sub('[^0-9]', '', score)
        cost = re.sub('[^0-9]', '', cost)

        if cost == '' or score == '':
            await ctx.send(f"**You must enter a number for the score and cost values!**")
            return

        if role in ctx.author.roles:
            dbOperations.data_entry(name, faction_name, score, cost, ctx.author.id)

            await ctx.send(f"**Ship {name} created! "
                           f"Use `c!ships` to view all ships, or use `c!editList` to view your registers**")
        else:
            await ctx.send(f"**Only CEOs are allowed to register ships**")

    @commands.command()
    async def editList(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name = "CEO")
        if role in ctx.author.roles:
            edit_list = dbOperations.get_edit_list(ctx.author.id)
            await ctx.send(f"**Showing all your registers, "
                           f"use `c!edit [name]` to edit an entry, or `c!delete [name]` to delete one!**")
            await ctx.send(edit_list)
        else:
            await ctx.send(f"**Only CEOs can edit ships!**")

    @commands.command()
    async def edit(self, ctx, ship_name, section, change):
        result = dbOperations.edit_ship(ctx.author.id, ship_name, section, change)
        if result == "Not Found":
            await ctx.send(f"**{ship_name} not found**")
        elif result == "error":
            await ctx.send(f"**You must enter a number for cost or score!**")
        else:
            await ctx.send(f"**You have successfully changed the {section} of {ship_name}!**")

    @commands.command()
    async def delete(self, ctx, ship_name):   # TODO: add confirmation message
        result = dbOperations.delete_ship(ship_name, ctx.author.id)
        if result == "Not found":
            await ctx.send(f"**{ship_name} not found**")
        elif result == "Wrong ID":
            await ctx.send(f"**{ship_name} does not belong to you!**")
        else:
            await ctx.send(f"**You deleted {ship_name}!**")

    @commands.command()
    async def ships(self, ctx):
        menu = dbOperations.get_menu()
        await ctx.send(menu)

    @commands.command()
    async def ship(self, ctx, query):
        ship_info = dbOperations.get_ship(query.lower())
        if ship_info == "Not found":
            await ctx.send(f"**{query} not found**")
        else:
            embed = discord.Embed(
                title=ship_info[0],
                colour=discord.Color.gold()
            )
            embed.set_author(name=f"\n")
            embed.add_field(name="Faction", value=ship_info[1])
            embed.add_field(name="Battle Score", value=ship_info[2])
            embed.add_field(name="Cost", value=ship_info[3], inline=True)
            await ctx.send(embed=embed)


class BattleCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Buy a ship to use in a battle")
    async def buy(self, ctx, ship_name):
        role = discord.utils.get(ctx.guild.roles, name="CEO")

        ship_info = dbOperations.get_ship(ship_name)

        if ship_info == "Not found":
            await ctx.send(f"**{ship_name} not found!**")
            return

        faction_info = dbOperations.get_faction(ship_info[1])

        if faction_info == "Not Found":
            await ctx.send(f"**{ship_name} does not belong to a faction!**")
            return

        cost = 0 - int(ship_info[3])
        battle_score = ship_info[2]

        if role in ctx.author.roles:
            if discord.utils.get(ctx.guild.roles, name=ship_info[1]) in ctx.author.roles:
                dbOperations.update_balance(faction_info[0].lower(), cost)
                dbOperations.update_score(faction_info[0].lower(), battle_score)
                await ctx.send(f"**Purchase Complete! You bought {ship_info[0]} for {ship_info[3]}!**")
            else:
                await ctx.send(f"**You can only purchase ships from your own faction**")
        else:
            await ctx.send(f"**Only CEOs are allowed to buy from ships**")

    @commands.command(brief="For admins to add money to faction")
    async def add(self, ctx, faction_name, amount):
        faction_info = dbOperations.get_faction(faction_name)
        role = discord.utils.get(ctx.guild.roles, name="Cardinal Admin")

        if role in ctx.author.roles:
            dbOperations.update_balance(faction_info[0].lower(), amount)
            await ctx.send(f"**You have successfully added {amount} to {faction_info[0]}'s balance!**")
        else:
            await ctx.send(f"**Only Cardinal Admins can add to a faction's balance!**")

    @commands.command(brief="For admins to start a new battle")
    async def newBattle(self, ctx):   # TODO: add confirmation message

        role = discord.utils.get(ctx.guild.roles, name="CEO")

        if role in ctx.author.roles:

            dbOperations.reset_score()

            await ctx.send(f"**New Battle started! The battle score for all factions is currently 0. "
                           f"Use `c!buy[ship]` to add ships to this battle"
                           f" and `c!faction [faction]` to view a faction's current battle score**")


# add cogs
client.add_cog(BattleCommands(client))
client.add_cog(Utilities(client))
client.add_cog(FactionCommands(client))
client.add_cog(ShipCommands(client))


client.run(token)
