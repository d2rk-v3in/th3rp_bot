import discord
from discord import ui
from discord import app_commands
from discord import Intents
from discord.ext import commands
from discord.ext.commands.errors import MissingPermissions
from discord.utils import get
import datetime
import random
import csv
import asyncio
import string
from datetime import datetime, timedelta
from pathlib import Path
from discord import app_commands, utils

intents = Intents.default()
intents.message_content = True
intents.guild_messages = True
intents.members = True

# Support Server Invite: https://discord.gg/ZjBBxfVM
GuildID = 1013869213443706960 # Enter Guild ID here
Token = 'Token#' # Token for client goes here

TicketPermission = 1088986329850843186 #Replace the ID with your ticket moderator / ticket permission role (people who can access tickets)
BlacklistRoleID = 1089418835095998474
SuspensionRoleID = 1089490668881199114
CivilianRoleID = 1089433357915537512

VehicleRegChannel = 1088988321063108629
CitationLogChannel = 1088988836274634774
ArrestLogChannel = 1088988854935113758
AppealLogChannel = 1088989465114054668
ArrivalLogChannel = 1088988970999881749 
SuggestionChannel = 1088988377728159845
VerifyChannel = 1089400322314752020
SupportChannel = 1088990143014240256
RulesChannel = 1089400322314752020
GuidelinesChannel = 1089400322314752020
RoleplayBlackListChannel = 1088989145461952572
SuspensionChannel = 1088989292350668901
StartupOneChannel = 1088989616729768066
StartupTwoChannel = 1089504220266385549
EarlyAccessOne = 1088989744656040046
EarlyAccessTwo = 1089504332719870052






Folder = Path(__file__).parent.resolve()
file = Folder / "filter.txt"
file2 = Folder / "casenumber.txt"
file3 = Folder / "coneimages.txt"
file4 = Folder / "rpblacklist.csv"
file5 = Folder / "suspensionlist.csv"
with open(file, 'r') as f:
    global badwords
    words = f.read()
    bad_words = words.split()
with open(file2, 'r') as f:
    current_case_number = int(f.read().strip())
    
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.synced = False
        self.added = False
        self.mod = TicketPermission
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        client.loop.create_task(expired_blacklist())
        client.loop.create_task(expired_suspension())
        if not self.synced:
            await tree.sync(guild = discord.Object(id = GuildID))
            self.synced = True
        if not self.added:
            self.add_view(TicketLaunch())
            self.add_view(main())
            self.added=True
    async def on_member_join(self, member):
        logs_channel = self.get_channel(ArrivalLogChannel)
        verify_channel = self.get_channel(VerifyChannel)
        support_channel = self.get_channel(SupportChannel)
        rules_channel = self.get_channel(RulesChannel)
        guidelines_channel = self.get_channel(GuidelinesChannel)

        embed=discord.Embed(
            title=f"Welcome to TH3RP, {member.display_name}!",
            description=f"Please go to {verify_channel.mention} and verify. If you need help, go to {support_channel.mention} for verifying instructions and {guidelines_channel.mention} for RP guidelines and {rules_channel.mention} for server rules. Happy roleplaying!",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
    
        embed.set_thumbnail(url=member.display_avatar)
        
        member_count = len(member.guild.members)
        embed.set_author(name=f"Member #{member_count}")

        # Send the embed to the logs channel
        await logs_channel.send(embed=embed)
        await logs_channel.send(member.mention)

        with open(file4, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if member.id == int(row[0]):
                    blrole = member.guild.get_role(BlacklistRoleID)
                    await member.add_roles(blrole)
        with open(file5, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if member.id == int(row[0]):
                    srole = member.guild.get_role(SuspensionRoleID)
                    await member.add_roles(srole)
    async def on_message(self, message):
        for embed in message.embeds:
            for field in embed.fields:
                if field.value is not None:
                    if isinstance(field.value, str):
                        for word in bad_words:
                            if word in field.value.lower():
                                await message.delete()
                                return
                if embed.title is not None:
                    for word in bad_words:
                        if word in embed.title.lower():
                            await message.delete()
                            return
                if embed.description is not None:
                    for word in bad_words:
                        if word in embed.description.lower():
                            await message.delete()
                            return
                if embed.footer is not None and embed.footer.text is not None:
                    for word in bad_words:
                        if word in embed.footer.text.lower():
                            await message.delete()
                            return
                if embed.author is not None and embed.author.name is not None:
                    for word in bad_words:
                        if word in embed.author.name.lower():
                            await message.delete()
                            return
           
client = MyClient()
tree = app_commands.CommandTree(client)


def add_blacklist(user_id, duration):
    with open(file4, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        blacklist_time = datetime.now() + timedelta(minutes=duration)
        writer.writerow([user_id, duration, blacklist_time])

def remove_blacklist(user_id):
    rows = []
    with open(file4, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if int(row[0]) != user_id:
                rows.append(row)
    with open(file4, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

def load_blacklists():
    blacklists = []
    with open(file4, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if datetime.now() < datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f'):
                blacklists.append(row)
    return blacklists

async def expired_blacklist():
    while True:
        with open(file4, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if datetime.now() >= datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f'):
                    guild = client.get_guild(GuildID)
                    member = guild.get_member(int(row[0]))
                    blacklist_role = guild.get_role(BlacklistRoleID)
                    await member.remove_roles(blacklist_role)
                    remove_blacklist(int(row[0]))
        await asyncio.sleep(60)



# new 
def add_suspension(user_id, duration):
    with open(file5, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        suspension_time = datetime.now() + timedelta(minutes=duration)
        writer.writerow([user_id, duration, suspension_time])

def remove_suspension(user_id):
    rows = []
    with open(file5, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if int(row[0]) != user_id:
                rows.append(row)
    with open(file5, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

def load_suspension():
    suspensions = []
    with open(file5, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if datetime.now() < datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f'):
                suspensions.append(row)
    return suspensions

async def expired_suspension():
    while True:
        with open(file5, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if datetime.now() >= datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f'):
                    guild = client.get_guild(GuildID)
                    member = guild.get_member(int(row[0]))
                    suspension_role = guild.get_role(SuspensionRoleID)
                    await member.remove_roles(suspension_role)
                    remove_suspension(int(row[0]))
        await asyncio.sleep(60)


# This class is for vehicle registration
class VehicleRegModal(discord.ui.Modal, title="Vehicle Registration"):
    RBXName = ui.TextInput(label="Roblox Username", placeholder="Roblox Username | Ex: d2rkv3in", style=discord.TextStyle.short,required=True)
    VehicleBrandModel = ui.TextInput(label="Vehicle Brand and Model", placeholder="Brand and Model of the Vehicle | Ex: Bullhorn Prancer", style=discord.TextStyle.short,required=True)
    VehicleYear = ui.TextInput(label="Vehicle Year", placeholder="Year of the Vehicle | Ex: 1969", style=discord.TextStyle.short, required=True)
    VehicleColor = ui.TextInput(label="Vehicle Color", placeholder="Color of the Vehicle | Ex: Pink", style=discord.TextStyle.short, required=True)
    PlateNumber = ui.TextInput(label="Plate Number", placeholder="Plate Number of the Vehicle | Ex: LOL-420", style=discord.TextStyle.short, required=True)
    

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Vehicle registration form submitted!", ephemeral=True) 
        embed= discord.Embed(title="Vehicle Registration", description="",color=0x206694, timestamp=datetime.now())
        embed.set_author(name=(f"{interaction.user.display_name}"), icon_url=(f"{interaction.user.display_avatar}"))
        embed.add_field(name="Discord Username", value=(f"{interaction.user.mention}"), inline=True)
        embed.add_field(name="Roblox Username", value=(f"{self.RBXName}"), inline=True)
        embed.add_field(name="Vehicle Brand and Model", value=(f"{self.VehicleBrandModel}"), inline=False)
        embed.add_field(name="Vehicle Year", value=(f"{self.VehicleYear}"), inline=True)
        embed.add_field(name="Vehicle Color", value=(f"{self.VehicleColor}"), inline=True)
        embed.add_field(name="Plate Number", value=(f"{self.PlateNumber}"), inline=True)
        channel = client.get_channel(VehicleRegChannel) 
        await channel.send(embed=embed)

# This class is for a citation log system
class CitationLogs(discord.ui.Modal, title="Citation Log Form"):
    CitationReceiver = ui.TextInput(label="Discord ID of Citation Receiver", placeholder="ONLY put the ID of the receiver | Ex: 194887110199607296", style=discord.TextStyle.short,required=True)
    CitationLocation = ui.TextInput(label="Citation Location", placeholder="Location | Ex: Six Houses", style=discord.TextStyle.short,required=True)
    PlateNumber = ui.TextInput(label="Plate Number", placeholder="Plate Number of the Vehicle | Ex: LOL-420", style=discord.TextStyle.short, required=True)
    PenalCode = ui.TextInput(label="Penal Code(s) / Infraction Name(s)", placeholder="Penal Code / Infraction Name | Ex: §7.32", style=discord.TextStyle.short, required=True)
    FineInput = ui.TextInput(label="Fine", placeholder="Fine | Ex: $500", style=discord.TextStyle.short, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        global current_case_number 
        await interaction.response.send_message(f"Citation log form submitted!", ephemeral=True)
        embed= discord.Embed(title="Citation Log", description="",color=0x206694, timestamp=datetime.now())
        embed.set_author(name=(f"Case Number: {current_case_number}"), icon_url=(f"{interaction.user.display_avatar}"))
        embed.add_field(name="Citation Giver", value=(f"{interaction.user.mention}"), inline=True) 
        embed.add_field(name="Citation Receiver", value=(f"<@{self.CitationReceiver}>"), inline=True)
        embed.add_field(name="Citation Location", value=(f"{self.CitationLocation}"), inline=False)
        embed.add_field(name="Vehicle Plate", value=(f"{self.PlateNumber}"), inline=False)
        embed.add_field(name="Penal Code(s) And Infraction Name(s)", value=(f"{self.PenalCode}"), inline=False)
        embed.add_field(name="Fine", value=(f"{self.FineInput}"), inline=True)
        embed.add_field(name="Signature", value=(f"<@{self.CitationReceiver}>"), inline=True)

        channel = client.get_channel(CitationLogChannel)
        await channel.send(embed=embed)
       
        current_case_number += 1 

        with open(file2, 'w') as f:
            f.write(str(current_case_number))

# This class is for a arrest log system
class ArrestLogs(discord.ui.Modal, title="Arrest Log Form"):
    UnitNames = ui.TextInput(label="Discord ID of additional unit(s) [Opt.]", placeholder="Format: <@ID>, <@ID2> | Ex: <@194887110199607296>", style=discord.TextStyle.short,required=False)
    UserArrested = ui.TextInput(label="Discord ID of user arrested", placeholder="ONLY put the ID of the user | Ex: 194887110199607296", style=discord.TextStyle.short,required=True)
    Charges = ui.TextInput(label="Charges", placeholder="Charge | Ex:  §2.1, 7.8", style=discord.TextStyle.short,required=True)
    FineInput = ui.TextInput(label="Fine and Jail Time(If applicable)", placeholder="Fine and Jail Time | Ex: $650 & 2 Minutes Jail", style=discord.TextStyle.short, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        global current_case_number 
        await interaction.response.send_message(f"Arrest log form submitted!", ephemeral=True)
        embed= discord.Embed(title="Arrest Log", description="",color=0x206694, timestamp=datetime.now()) # 301438306909159434 , # 776150745183158275
        embed.set_author(name=(f"Case Number: {current_case_number}"), icon_url=(f"{interaction.user.display_avatar}"))
        embed.add_field(name="Unit(s)", value=(f"{interaction.user.mention}, {self.UnitNames}"), inline=False) 
        embed.add_field(name="User Arrested", value=(f"<@{self.UserArrested}>"), inline=True)
        embed.add_field(name="Charges", value=(f"{self.Charges}"), inline=True)
        embed.add_field(name="Fine and Jail Time(If applicable)", value=(f"{self.FineInput}"), inline=False)
            

        channel = client.get_channel(ArrestLogChannel)
        await channel.send(embed=embed)
       
        current_case_number += 1

        
        with open(file2, 'w') as f:
            f.write(str(current_case_number))


# This class is for roleplay blacklist system
class BlacklistModal(discord.ui.Modal, title="Roleplay Blacklist"):
    CivilianUser = ui.TextInput(label="Civilian Discord ID", placeholder="Only put the ID! | Ex: 194887110199607296", style=discord.TextStyle.short,required=True)
    Reason = ui.TextInput(label="Reason for Blacklist", placeholder="Reason | Ex: x3 Infractions", style=discord.TextStyle.short, required=True)
    Duration = ui.TextInput(label="Duration in minutes", placeholder="Integer only! | Ex: 20160", style=discord.TextStyle.short, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        global current_case_number 
        
        ID = {self.CivilianUser.value}
        newID = str(ID).strip("{}").replace("'", "")
        
        duration_minutes = str(self.Duration)

        if not duration_minutes.isdigit:
            channel = client.get_channel(RoleplayBlackListChannel)
            await interaction.response.send_message(f"{interaction.user.mention} Only integers are accepeted! Please resubmit your roleplay blacklist form.", ephemeral=True)
            return
        

        duration_minutes = int(duration_minutes)

        hours, remaining_minutes = divmod(duration_minutes, 60)
        if duration_minutes >= 1440:
            weeks, days = divmod(duration_minutes, 60 * 24 * 7)
            if weeks > 0:
                duration_str = f"{weeks} week(s)"
                if days > 0:
                    duration_str += f" and {days} day(s)"
            else:
                duration_str = f"{days} day(s)"
        elif duration_minutes >= 60:
            duration_str = f"{hours} hour(s)"
        else:
            duration_str = f"{duration_minutes} minute(s)"

        add_role = interaction.guild.get_role(BlacklistRoleID)
        remove_role = interaction.guild.get_role(CivilianRoleID)
        BlacklistedUser = interaction.guild.get_member(int(newID))
        if BlacklistedUser is None:
            await interaction.response.send_message(f"{interaction.user.mention} No user found! Please resubmit your roleplay blacklist form.", ephemeral=True)
            return
        with open(file4, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if BlacklistedUser.id == int(row[0]):
                    await interaction.response.send_message(f"{interaction.user.mention} User is already roleplay blacklisted!", ephemeral=True)
                    return

        await BlacklistedUser.add_roles(add_role)
        await BlacklistedUser.remove_roles(remove_role)
        add_blacklist(BlacklistedUser.id, duration_minutes)

        await interaction.response.send_message(f"Blacklist submitted!", ephemeral=True)
        embed= discord.Embed(title="Roleplay Blacklist", description="",color=0x206694, timestamp=datetime.now())
        embed.set_author(name=(f"Case Number: {current_case_number}"), icon_url=(f"{interaction.user.display_avatar}"))
        embed.add_field(name="Blacklisted by", value=f"{interaction.user.mention}", inline=False) 
        embed.add_field(name="Civilian", value=f"<@{self.CivilianUser}>", inline=False) 
        embed.add_field(name="Duration", value=f"{duration_str}", inline=True) 
        embed.add_field(name="Reason", value=f"{self.Reason}", inline=True) 
        channel = client.get_channel(RoleplayBlackListChannel)
        await channel.send(embed=embed)

        current_case_number += 1 

        with open(file2, 'w') as f:
            f.write(str(current_case_number))


# This class is for license suspension system
class SuspensionModal(discord.ui.Modal, title="License Suspension"):
    OfficerUser = ui.TextInput(label="Officer's Discord ID (Opt.)", placeholder="Only put the ID! | Ex: 194887110199607296", style=discord.TextStyle.short,required=False)
    CivilianUser = ui.TextInput(label="Offender's Discord ID", placeholder="Only put the ID! | Ex: 194887110199607296", style=discord.TextStyle.short,required=True)
    Reason = ui.TextInput(label="Reason for Suspension", placeholder="Reason | Ex: Unpaid Tickets", style=discord.TextStyle.short, required=True)
    Duration = ui.TextInput(label="Duration in minutes", placeholder="Integer only! | Ex: 20160", style=discord.TextStyle.short, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        global current_case_number 
        
        ID = {self.CivilianUser.value}
        newID = str(ID).strip("{}").replace("'", "")
        
        duration_minutes = str(self.Duration)

        if not duration_minutes.isdigit:
            channel = client.get_channel(SuspensionChannel)
            await interaction.response.send_message(f"{interaction.user.mention} Only integers are accepeted! Please resubmit your license suspension form.", ephemeral=True)
            return
        

        duration_minutes = int(duration_minutes)

        hours, remaining_minutes = divmod(duration_minutes, 60)
        if duration_minutes >= 1440:
            weeks, days = divmod(duration_minutes, 60 * 24 * 7)
            if weeks > 0:
                duration_str = f"{weeks} week(s)"
                if days > 0:
                    duration_str += f" and {days} day(s)"
            else:
                duration_str = f"{days} day(s)"
        elif duration_minutes >= 60:
            duration_str = f"{hours} hour(s)"
        else:
            duration_str = f"{duration_minutes} minute(s)"

        add_role = interaction.guild.get_role(SuspensionRoleID)
        OffenderUser = interaction.guild.get_member(int(newID))

        if OffenderUser is None:
            await interaction.response.send_message(f"{interaction.user.mention} No user found! Please resubmit your license suspension form.", ephemeral=True)
            return
        with open(file5, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if OffenderUser.id == int(row[0]):
                    await interaction.response.send_message(f"{interaction.user.mention} User already has a suspended license!", ephemeral=True)
                    return

        await OffenderUser.add_roles(add_role)
        add_suspension(OffenderUser.id, duration_minutes)

        await interaction.response.send_message(f"Suspension submitted!", ephemeral=True)
        embed= discord.Embed(title="License Suspension", description="",color=0x206694, timestamp=datetime.now())
        embed.set_author(name=(f"Case Number: {current_case_number}"), icon_url=(f"{interaction.user.display_avatar}"))
        embed.add_field(name="Filed by", value=f"{interaction.user.mention}", inline=True) 
        if self.OfficerUser.value != "":
            embed.add_field(name="Officer", value=f"<@{self.OfficerUser}>", inline=True) 
        embed.add_field(name="Offender", value=f"<@{self.CivilianUser}>", inline=True) 
        embed.add_field(name="Duration", value=f"{duration_str}", inline=False) 
        embed.add_field(name="Reason", value=f"{self.Reason}", inline=False) 
        channel = client.get_channel(SuspensionChannel)
        await channel.send(embed=embed)

        current_case_number += 1 

        with open(file2, 'w') as f:
            f.write(str(current_case_number))


# This class is for a appeal log system
class AppealLog(discord.ui.Modal, title="Appeal Log Form"):
    UserAppealing = ui.TextInput(label="Discord ID of user appealing", placeholder="Only put the ID! | Ex: 194887110199607296", style=discord.TextStyle.short,required=True)
    AppCaseNumber = ui.TextInput(label="Case Number of the Appeal", placeholder="Case Number | Ex: #1337", style=discord.TextStyle.short,required=True)
    Result = ui.TextInput(label="Verdict", placeholder="Accepted or Denied", style=discord.TextStyle.short,required=True)
    ResultReason = ui.TextInput(label="Reason", placeholder="Reason for verdict", style=discord.TextStyle.paragraph,required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Arrest log form submitted!", ephemeral=True)
        embed= discord.Embed(title="Arrest Log", description="",color=0x206694, timestamp=datetime.now()) # 301438306909159434 , # 776150745183158275
        embed.set_author(name=(f"{interaction.user.display_name}"), icon_url=(f"{interaction.user.display_avatar}"))
        embed.add_field(name="User Appealing", value=(f"<@{self.UserAppealing}>"), inline=True)
        embed.add_field(name="Case Number", value=(f"{self.AppCaseNumber}"), inline=True)
        embed.add_field(name="Verdict", value=(f"{self.Result}"), inline=True)
        embed.add_field(name="Reason", value=(f"{self.ResultReason}"), inline=False)

        channel = client.get_channel(AppealLogChannel)
        await channel.send(embed=embed)
        await channel.send(f"<@{self.UserAppealing}>")

# This class is for suggestions system
class SuggestionModal(discord.ui.Modal, title="Suggestion"):
    Suggestion = ui.TextInput(label="Suggestion", placeholder="Type a title for your suggestion", style=discord.TextStyle.short,required=True)
    SuggestionDetails = ui.TextInput(label="Describe your suggestion", placeholder="Elaborate on your suggestion (Optional)", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Thank you for submitting a suggestion!", ephemeral=True)
        embed= discord.Embed(title=(f"{self.Suggestion}"), description=(f"{self.SuggestionDetails}"),color=0x206694, timestamp=datetime.now())
        embed.add_field(name="Suggested by", value=f"{interaction.user.mention}", inline=False) 
        channel = client.get_channel(SuggestionChannel)
        await channel.send(embed=embed)

class StartupModal(discord.ui.Modal, title="Starup Launch Form"):
    Game = ui.TextInput(label="Game", placeholder="What game will the session be in?", style=discord.TextStyle.short,required=True)
    StartupNum = ui.TextInput(label="Startup Channel", placeholder="1 or 2 (Number Only)| Ex: 1", style=discord.TextStyle.short,required=True)



    async def on_submit(self, interaction: discord.Interaction):
        Startup1_In_Use = False
        Startup2_In_Use = False
        Released = False
        if int(self.StartupNum.value) not in [1, 2]:
            await interaction.response.send_message("Startup Channel Entry must be '1' or '2'! Resubmit the form with the correct format.", ephemeral=True)
            print(self.StartupNum.value)
            return
        if Startup1_In_Use !=False:
            await interaction.response.send_message("Startup 1 is in use! Resubmit the form and try startup 2.", ephemeral=True)
            return
        if Startup2_In_Use !=False:
            await interaction.response.send_message("Startup 2 is in use! Resubmit the form and try startup 1.", ephemeral=True)
            return
        await interaction.response.send_message("Launching session!", ephemeral=True)
        if int(self.StartupNum.value) == 1:
            Startup1_In_Use = True
        elif int(self.StartupNum.value) == 2:
            Startup2_In_Use = True
        vehicle_registration = client.get_channel(VehicleRegChannel)
        rules_channel = client.get_channel(RulesChannel)
        guidelines_channel = client.get_channel(GuidelinesChannel)


        emojith3rp = discord.PartialEmoji(name='TH3RPLogo', id='870536562788679720')
        emojisesh = discord.PartialEmoji(name='sesh3', id='854564582034636870')

        embed = discord.Embed(title=(f"{emojith3rp}__**TH3RP | Session Startup!**__{emojisesh}"),
                            url="https://th3rp.com",
                            description=(f"Before you join a session you must:\n\n> ~ Make sure your vehicle is registered in {vehicle_registration.mention}\n> ~ Review all regulations and civilian rules in {guidelines_channel.mention} and {rules_channel.mention}\n\nTo get invited to the session with manual invite:\n\n> 1. You need to go to \" https://www.roblox.com/my/account#!/privacy \"\n> 2. Change \" Contact Settings \" to \" Custom \"\n> 3. Go down to \" Other Settings \" and where it says \" Who can invite me to private servers? \" Select \" Everyone \" ( https://gyazo.com/75d8e70bd53b213cbd40b4f6badb9297 )\n> 4. When I startup the server, I should be able to add you and you'll see the server after I announce it.\n\nDo not DM or Ping the Host to add you to the session.\n\n> To join the session with link:\n> 1. A link will be released.\n> 2. Don't ask the host for the link.\n> 3. When it is released, follow verification rules from the host.\n\n**This session will be hosted in {self.Game}**\n\n15+ Reactions are required for this session to start!"),
                            colour=0x00b0f4,
                            timestamp=datetime.now())
        embed.set_author(name=(f"Hosted by: {interaction.user.display_name}"),
                        icon_url=(f"{interaction.user.display_avatar}"))
        embed.set_image(url="https://media.discordapp.net/attachments/1089408032699584542/1089511572067582003/dinkdoink.png?width=1920&height=1080")

        channel = client.get_channel(StartupOneChannel)
        await channel.send(embed=embed)

# This is for the ticket system 
class TicketLaunch(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Create a Ticket", style=discord.ButtonStyle.blurple, custom_id="ticket_button")
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        ticket = utils.get(interaction.guild.text_channels, name=f"ticket-{interaction.user.name}-{interaction.user.discriminator}")
        if ticket is not None: await interaction.response.send_message(f"You already have a ticket open at {ticket.mention}!", ephemeral=True)
        else:
            if type(client.mod) is not discord.Role:
                client.mod = interaction.guild.get_role(TicketPermission) 
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
                interaction.user: discord.PermissionOverwrite(view_channel = True, send_messages = True, attach_files = True, embed_links = True),
                interaction.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True),
                client.mod: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
            }
            channel = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}-{interaction.user.discriminator}", overwrites = overwrites, reason=f"Ticket for {interaction.user}")
            await channel.send(f"{interaction.user.mention} created a ticket!", view=main())
            await interaction.response.send_message(f"Your ticket has been created! {channel.mention}!", ephemeral=True)

class confirm(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm", style= discord.ButtonStyle.red, custom_id="confirm")
    async def confirm_button(self, interaction, button):
        try: await interaction.channel.delete()
        except: await interaction.response.send_message("Channel deletion failed! Insufficent permissions.")

class main(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Close Ticket", style= discord.ButtonStyle.red, custom_id="close")
    async def close(self, interaction, button):
        embed = discord.Embed(title="Are you sure you want to close this ticket?", color = discord.Color.blurple())
        await interaction.response.send_message(embed=embed, view=confirm(), ephemeral = True)





@tree.command(name="vehicle-registration", description="File your vehicle registration.", guild=discord.Object(id = GuildID)) 
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
async def modal(interaction: discord.Interaction):
    await interaction.response.send_modal(VehicleRegModal())
@tree.command(name="citation-log", description="File a citation log.", guild=discord.Object(id = GuildID)) 
async def modal(interaction: discord.Interaction):
    await interaction.response.send_modal(CitationLogs())
@tree.command(name="arrest-log", description="File an arrest log.", guild=discord.Object(id = GuildID)) 
async def modal(interaction: discord.Interaction):
    await interaction.response.send_modal(ArrestLogs())
@tree.command(name="appeal-log", description="File an appeal log.", guild=discord.Object(id = GuildID)) 
async def modal(interaction: discord.Interaction):
    await interaction.response.send_modal(AppealLog())
@tree.command(name="roleplay-blacklist", description="Roleplay Blacklist a user.", guild=discord.Object(id = GuildID)) 
async def modal(interaction: discord.Interaction):
    await interaction.response.send_modal(BlacklistModal())
@tree.command(name="license-suspension", description="Suspend a user's license.", guild=discord.Object(id = GuildID)) 
async def modal(interaction: discord.Interaction):
    await interaction.response.send_modal(SuspensionModal())
@tree.command(name="suggestion", description="Create a suggestion for the server.", guild=discord.Object(id = GuildID)) 
async def modal(interaction: discord.Interaction):
    await interaction.response.send_modal(SuggestionModal())
@tree.command(name="startup", description="Host a session.", guild=discord.Object(id = GuildID)) 
async def modal(interaction: discord.Interaction):
    await interaction.response.send_modal(StartupModal())
@tree.command(name="cone", description="C O N E", guild=discord.Object(id = GuildID)) 
async def cone_command(interaction):
    with open(file3, 'r') as file:
        lines = file.readlines()
        img_url = random.choice(lines).strip()   
    await interaction.response.send_message(img_url)
@tree.command(name="ticket", description="Creates a ticket for support or questions", guild=discord.Object(id = GuildID)) 
@app_commands.default_permissions(manage_guild=True)
async def ticketing(interaction: discord.Interaction):
    embed = discord.Embed(title="If you need support, click the button below and create a ticket!", color = discord.Color.blue())
    await interaction.channel.send(embed=embed, view=TicketLaunch())
    await interaction.response.send_message("Creating ticket!", ephemeral=True)
@tree.command(name="close-ticket", description="Closes the ticket", guild=discord.Object(id = GuildID)) 
@app_commands.default_permissions(manage_guild=True)
async def close(interaction: discord.Interaction):
    if "ticket-" in interaction.channel.name:
        embed = discord.Embed(title="Are you sure you want to close this ticket?", color = discord.Color.blurple())
        await interaction.channel.send(embed=embed, view=confirm())
    else: await interaction.response.send_message("No ticket found!", ephemeral=True)
@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"Error Message: {error}", ephemeral = True)
    else: raise error



client.run(Token)
