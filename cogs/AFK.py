###################################
# AUTHOR: @Larrox | @copyandbuild #
###################################

import discord
from discord.ext import commands
from discord.commands import slash_command
import sqlite3
import datetime
import asyncio
import os

if not os.path.exists("db"):
    os.makedirs("db")

database = sqlite3.connect("db/afk.db")
cursor = database.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS afk_system (
        user INTEGER PRIMARY KEY,
        seid_wann INTEGER,
        warum TEXT
    )
""")
database.commit()

class AFKMain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Melde dich ab!")
    async def afk(self, ctx: discord.ApplicationContext, grund: str):
        cursor.execute("SELECT user FROM afk_system WHERE user = ?", (ctx.author.id,))
        check_entry = cursor.fetchone()

        if check_entry is None:
            momentane_zeit_timestamp = int(datetime.datetime.now().timestamp())
            cursor.execute("INSERT INTO afk_system(user, seid_wann, warum) VALUES (?, ?, ?)",
                           (ctx.author.id, momentane_zeit_timestamp, grund))
            database.commit()

            await ctx.respond(
                content=f"<:info:1295457691443138591>  › {ctx.author.mention} ist nun **AFK** gemeldet! \n**Grund:** {grund}"
            )
            try:
                await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
            except discord.Forbidden:
                pass
            await asyncio.sleep(60)
            await ctx.delete()
        else:
            await ctx.respond(content="Du bist bereits im AFK!", view=Deaktivieren(ctx), ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return

        cursor.execute("SELECT user FROM afk_system WHERE user = ?", (msg.author.id,))
        check = cursor.fetchone()
        if check is not None:
            cursor.execute("DELETE FROM afk_system WHERE user = ?", (msg.author.id,))
            database.commit()
            nachricht = await msg.channel.send(
                content=f"<:info:1295457691443138591> › {msg.author.mention} ist nun nicht mehr **AFK** gemeldet!"
            )
            try:
                await msg.author.edit(nick=msg.author.display_name.replace("[AFK] ", ""))
            except discord.Forbidden:
                pass
            await asyncio.sleep(60)
            await nachricht.delete()

        if msg.mentions:
            for m in msg.mentions:
                if m == msg.author or m.bot:
                    continue

                cursor.execute("SELECT warum, seid_wann FROM afk_system WHERE user = ?", (m.id,))
                reason_data = cursor.fetchone()
                if reason_data:
                    nachricht = await msg.reply(
                        content=f"›  {m.display_name} hat sich <t:{reason_data[1]}:R> **AFK** gemeldet!\n **Grund:** {reason_data[0]}"
                    )
                    await asyncio.sleep(60)
                    await nachricht.delete()


class Deaktivieren(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    @discord.ui.button(label="Aus dem AFK gehen", style=discord.ButtonStyle.red)
    async def deaktivieren_button(self, button, interaction):
        cursor.execute("DELETE FROM afk_system WHERE user = ?", (interaction.user.id,))
        database.commit()
        await interaction.response.send_message(content="Du bist nun nicht mehr im AFK!", ephemeral=True)
        await interaction.channel.send(
            content=f"<:info:1295457691443138591> › {interaction.user.mention} ist nun nicht mehr **AFK** gemeldet!"
        )
        try:
            display_name = interaction.user.display_name
            if display_name.startswith("[AFK] "):
                new_display_name = display_name[len("[AFK] "):]
                await interaction.user.edit(nick=new_display_name)
        except discord.Forbidden:
            pass

def setup(bot):
    bot.add_cog(AFKMain(bot))
