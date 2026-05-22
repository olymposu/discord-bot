import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime


def zaman():
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


class Logger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # guild_id -> log_channel_id eşlemesi
        self.log_kanallari: dict[int, int] = {}

    def log_embed(self, baslik: str, renk: discord.Color, alanlar: list[tuple]) -> discord.Embed:
        embed = discord.Embed(title=baslik, color=renk, timestamp=datetime.utcnow())
        for ad, deger, inline in alanlar:
            embed.add_field(name=ad, value=deger, inline=inline)
        embed.set_footer(text=zaman())
        return embed

    async def log_gonder(self, guild: discord.Guild, embed: discord.Embed):
        kanal_id = self.log_kanallari.get(guild.id)
        if not kanal_id:
            return
        kanal = guild.get_channel(kanal_id)
        if kanal:
            try:
                await kanal.send(embed=embed)
            except discord.Forbidden:
                pass

    # ─── KURULUM KOMUTU ────────────────────────────────────
    @app_commands.command(name="logkanal", description="Log kanalını ayarla")
    @app_commands.describe(kanal="Log mesajlarının gönderileceği kanal")
    @app_commands.checks.has_permissions(administrator=True)
    async def logkanal(self, interaction: discord.Interaction, kanal: discord.TextChannel):
        self.log_kanallari[interaction.guild_id] = kanal.id

        embed = discord.Embed(
            title="✅ Log Kanalı Ayarlandı",
            description=f"Bundan sonra tüm log mesajları {kanal.mention} kanalına gönderilecek.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

        # Test mesajı
        test = discord.Embed(
            title="📋 Log Sistemi Aktif",
            description="Bu kanal log kanalı olarak ayarlandı.",
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow()
        )
        test.add_field(name="Ayarlayan", value=interaction.user.mention)
        await kanal.send(embed=test)

    @app_commands.command(name="logkapat", description="Log sistemini kapat")
    @app_commands.checks.has_permissions(administrator=True)
    async def logkapat(self, interaction: discord.Interaction):
        self.log_kanallari.pop(interaction.guild_id, None)
        await interaction.response.send_message("🔕 Log sistemi kapatıldı.", ephemeral=True)

    # ══════════════════════════════════════════════════════
    # MESAJ OLAYLARI
    # ══════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return
        embed = self.log_embed(
            "🗑️ Mesaj Silindi",
            discord.Color.red(),
            [
                ("Kullanıcı", message.author.mention, True),
                ("Kanal", message.channel.mention, True),
                ("İçerik", message.content[:1000] if message.content else "*Ek/Embed*", False),
            ]
        )
        embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
        await self.log_gonder(message.guild, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not before.guild or before.author.bot or before.content == after.content:
            return
        embed = self.log_embed(
            "✏️ Mesaj Düzenlendi",
            discord.Color.yellow(),
            [
                ("Kullanıcı", before.author.mention, True),
                ("Kanal", before.channel.mention, True),
                ("Önce", before.content[:500] or "*boş*", False),
                ("Sonra", after.content[:500] or "*boş*", False),
            ]
        )
        embed.set_author(name=str(before.author), icon_url=before.author.display_avatar.url)
        embed.url = after.jump_url
        await self.log_gonder(before.guild, embed)

    # ══════════════════════════════════════════════════════
    # ÜYE OLAYLARI
    # ══════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        hesap_yasi = (datetime.utcnow() - member.created_at.replace(tzinfo=None)).days
        embed = self.log_embed(
            "📥 Üye Katıldı",
            discord.Color.green(),
            [
                ("Kullanıcı", f"{member.mention} ({member})", True),
                ("ID", str(member.id), True),
                ("Hesap Yaşı", f"{hesap_yasi} gün", True),
                ("Sunucu Üye Sayısı", str(member.guild.member_count), True),
            ]
        )
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        await self.log_gonder(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        roller = [r.name for r in member.roles if r.name != "@everyone"]
        embed = self.log_embed(
            "📤 Üye Ayrıldı",
            discord.Color.orange(),
            [
                ("Kullanıcı", f"{member.mention} ({member})", True),
                ("ID", str(member.id), True),
                ("Roller", ", ".join(roller) if roller else "Yok", False),
            ]
        )
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        await self.log_gonder(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        alanlar = []

        # Nickname değişimi
        if before.nick != after.nick:
            alanlar.append(("Önceki Nick", before.nick or "*Yok*", True))
            alanlar.append(("Yeni Nick", after.nick or "*Yok*", True))

        # Rol değişimi
        eklenen = set(after.roles) - set(before.roles)
        cikarilan = set(before.roles) - set(after.roles)
        if eklenen:
            alanlar.append(("➕ Eklenen Rol", ", ".join(r.mention for r in eklenen), False))
        if cikarilan:
            alanlar.append(("➖ Alınan Rol", ", ".join(r.mention for r in cikarilan), False))

        if not alanlar:
            return

        embed = self.log_embed(
            "🔄 Üye Güncellendi",
            discord.Color.blue(),
            [("Kullanıcı", after.mention, False)] + alanlar
        )
        embed.set_author(name=str(after), icon_url=after.display_avatar.url)
        await self.log_gonder(after.guild, embed)

    # ══════════════════════════════════════════════════════
    # SES KANALI OLAYLARI
    # ══════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if before.channel == after.channel:
            return

        if before.channel is None:
            # Ses kanalına girdi
            embed = self.log_embed(
                "🔊 Ses Kanalına Girdi",
                discord.Color.green(),
                [
                    ("Kullanıcı", member.mention, True),
                    ("Kanal", after.channel.mention, True),
                ]
            )
        elif after.channel is None:
            # Ses kanalından çıktı
            embed = self.log_embed(
                "🔇 Ses Kanalından Çıktı",
                discord.Color.red(),
                [
                    ("Kullanıcı", member.mention, True),
                    ("Kanal", before.channel.mention, True),
                ]
            )
        else:
            # Kanal değiştirdi
            embed = self.log_embed(
                "🔀 Ses Kanalı Değiştirdi",
                discord.Color.yellow(),
                [
                    ("Kullanıcı", member.mention, True),
                    ("Önceki", before.channel.mention, True),
                    ("Yeni", after.channel.mention, True),
                ]
            )

        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        await self.log_gonder(member.guild, embed)

    # ══════════════════════════════════════════════════════
    # KANAL OLAYLARI
    # ══════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        embed = self.log_embed(
            "📁 Kanal Oluşturuldu",
            discord.Color.green(),
            [
                ("Kanal", channel.mention, True),
                ("Tür", str(channel.type).capitalize(), True),
            ]
        )
        await self.log_gonder(channel.guild, embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        embed = self.log_embed(
            "🗑️ Kanal Silindi",
            discord.Color.red(),
            [
                ("Kanal Adı", f"#{channel.name}", True),
                ("Tür", str(channel.type).capitalize(), True),
            ]
        )
        await self.log_gonder(channel.guild, embed)

    # ══════════════════════════════════════════════════════
    # MODERASYon OLAYLARI (ban/unban)
    # ══════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        embed = self.log_embed(
            "🔨 Kullanıcı Yasaklandı",
            discord.Color.dark_red(),
            [
                ("Kullanıcı", f"{user.mention} ({user})", True),
                ("ID", str(user.id), True),
            ]
        )
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        await self.log_gonder(guild, embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        embed = self.log_embed(
            "✅ Yasak Kaldırıldı",
            discord.Color.green(),
            [
                ("Kullanıcı", f"{user.mention} ({user})", True),
                ("ID", str(user.id), True),
            ]
        )
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        await self.log_gonder(guild, embed)

    # ─── HATA ──────────────────────────────────────────────
    @logkanal.error
    async def logkanal_hatasi(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Bu komutu sadece adminler kullanabilir!", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Logger(bot))
