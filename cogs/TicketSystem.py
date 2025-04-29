import discord
from discord.ext import commands
from discord.commands import slash_command
import ezcord

class Ticket(ezcord.Cog, emoji="🎫"):

    default_color = 0x57F287
    staff_role_id = 1363896903141429482
    ticket_category_id = 1361360637359554611

    @slash_command()
    @discord.default_permissions(administrator=True)
    async def ticket(self, ctx):
        embed = discord.Embed(
            title="🎫 YOUR_SERVER_NAME × Ticket-Support",
            description="Hey, danke, dass du unseren Support nutzt!\n\n> Wir bitten dich, dein Problem möglichst genau zu beschreiben, damit unsere Supporter dir so schnell wie möglich helfen können.\n\n> **Bitte habe ein wenig Geduld, da unser Support auch ein Privatleben hat**!",
            color=self.default_color,
        )

        await ctx.send(embed=embed, view=TicketDropdownView())
        await ctx.respond("Ticket-Embed wurde erstellt.", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketDropdownView())
        self.bot.add_view(TicketActionView())

class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support", description="Erstelle ein Support-Ticket", emoji="🛠️"),
            discord.SelectOption(label="Team-Bewerbung", description="Erstelle ein Team-Bewerbung-Ticket", emoji="📄"),
            discord.SelectOption(label="Partnerschafts-Bewerbung", description="Werde HEUTE Partner von uns!", emoji="🤝"),
        ]
        super().__init__(placeholder="📝 Erstelle ein Ticket...", min_values=1, max_values=1, options=options, custom_id="ticket_dropdown")

    async def callback(self, interaction: discord.Interaction):
        staff_role = interaction.guild.get_role(self.staff_role_id)
        username = interaction.user.name

        category_id = self.ticket_category_id
        category = interaction.guild.get_channel(category_id)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        ticket_channel = await interaction.guild.create_text_channel(
            f"🎫〡{username}", category=category, overwrites=overwrites, topic=f"{self.values[0]}", reason=f"Ticket erstellt, {interaction.user.name} ({interaction.user.id}) hat ein Ticket erstellt."
        )
        embed = discord.Embed(
            title=f"BambooSMP | {self.values[0]} Ticket",
            description=f"{interaction.user.mention} bitte beschreibe dein Anliegen oder Problem detailliert, damit unser Team dir bestmöglich helfen kann.",
            color=0x57F287,
        )
        embed.set_footer(text="Bitte warte, bis sich ein Teammitglied meldet.")
        message = await ticket_channel.send(embed=embed, view=TicketActionView(), content=f"{staff_role.mention}")

        confirmation_embed = discord.Embed(
            title=f"BambooSMP | {self.values[0]} Ticket",
            description=f"Dein Ticket wurde erfolgreich erstellt: {ticket_channel.mention}",
            color=0x57F287,
        )

        await interaction.response.send_message(embed=confirmation_embed, ephemeral=True)
        await message.pin()
        await ticket_channel.purge(limit=1)

class TicketDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

class TicketActionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket übernehmen", style=discord.ButtonStyle.success, emoji="✅", custom_id="claimticketidyeah")
    async def claim_button(self, button, interaction: discord.Interaction):
        staff_role = interaction.guild.get_role(self.staff_role_id)
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message("Du hast keine Berechtigung, um dieses Ticket zu übernehmen.", ephemeral=True)
            return

        button.disabled = True
        await interaction.message.edit(view=self)
        embed = discord.Embed(
            title="YOUR_SERVER_NAME | Ticket-Support",
            description=f"Dieses Ticket wird nun von {interaction.user.mention} bearbeitet.",
            color=0x57F287,
        )
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Ticket schließen", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="closeticketidyeah")
    async def close_button(self, button, interaction: discord.Interaction):
        staff_role = interaction.guild.get_role(self.staff_role_id)
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message("Du hast keine Berechtigung, um dieses Ticket zu schließen.", ephemeral=True)
            return

        await interaction.channel.delete()
        embed = discord.Embed(
            title="YOUR_SERVER_NAME | Ticket-Support",
            description="Das Ticket wurde geschlossen.",
            color=0x57F287,
        )

        try:
            await interaction.user.send(embed=embed)
        except discord.Forbidden:
            pass

def setup(bot: discord.Bot):
    bot.add_cog(Ticket(bot))
