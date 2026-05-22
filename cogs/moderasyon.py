import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import timedelta

class Moderasyon(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ─── BAN ───────────────────────────────────────────────
    @app_commands.command(name="ban", description="Bir üyeyi sunucudan yasakla")
    @app_commands.describe(
        uye="Yasaklanacak üye",
        sebep="Yasaklama sebebi"
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, uye: discord.Member, sebep: str = "Sebep belirtilmedi"):
        if uye == interaction.user:
            return await interaction.response.send_message("❌ Kendinizi yasaklayamazsınız!", ephemeral=True)
        if uye.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Bu üyeyi yasaklamak için yetkiniz yok!", ephemeral=True)

        try:
            await uye.send(
                f"🔨 **{interaction.guild.name}** sunucusundan yasaklandınız.\n"
                f"📝 Sebep: {sebep}"
            )
        except discord.Forbidden:
            pass

        await uye.ban(reason=f"{interaction.user} tarafından: {sebep}")

        embed = discord.Embed(
            title="🔨 Kullanıcı Yasaklandı",
            color=discord.Color.red()
        )
        embed.add_field(name="Kullanıcı", value=uye.mention, inline=True)
        embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
        embed.add_field(name="Sebep", value=sebep, inline=False)
        embed.set_thumbnail(url=uye.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ─── KICK ──────────────────────────────────────────────
    @app_commands.command(name="kick", description="Bir üyeyi sunucudan at")
    @app_commands.describe(
        uye="Atılacak üye",
        sebep="Atma sebebi"
    )
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, uye: discord.Member, sebep: str = "Sebep belirtilmedi"):
        if uye == interaction.user:
            return await interaction.response.send_message("❌ Kendinizi atamazsınız!", ephemeral=True)
        if uye.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Bu üyeyi atmak için yetkiniz yok!", ephemeral=True)

        try:
            await uye.send(
                f"👢 **{interaction.guild.name}** sunucusundan atıldınız.\n"
                f"📝 Sebep: {sebep}"
            )
        except discord.Forbidden:
            pass

        await uye.kick(reason=f"{interaction.user} tarafından: {sebep}")

        embed = discord.Embed(
            title="👢 Kullanıcı Atıldı",
            color=discord.Color.orange()
        )
        embed.add_field(name="Kullanıcı", value=uye.mention, inline=True)
        embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
        embed.add_field(name="Sebep", value=sebep, inline=False)
        embed.set_thumbnail(url=uye.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ─── MUTE (Timeout) ────────────────────────────────────
    @app_commands.command(name="mute", description="Bir üyeyi sustur")
    @app_commands.describe(
        uye="Susturulacak üye",
        sure="Süre dakika olarak (max 40320 = 28 gün)",
        sebep="Susturma sebebi"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, uye: discord.Member, sure: int = 10, sebep: str = "Sebep belirtilmedi"):
        if uye == interaction.user:
            return await interaction.response.send_message("❌ Kendinizi susturamazsınız!", ephemeral=True)
        if sure > 40320:
            return await interaction.response.send_message("❌ Maksimum süre 40320 dakika (28 gün)!", ephemeral=True)

        bitis = discord.utils.utcnow() + timedelta(minutes=sure)
        await uye.timeout(bitis, reason=f"{interaction.user} tarafından: {sebep}")

        embed = discord.Embed(
            title="🔇 Kullanıcı Susturuldu",
            color=discord.Color.yellow()
        )
        embed.add_field(name="Kullanıcı", value=uye.mention, inline=True)
        embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
        embed.add_field(name="Süre", value=f"{sure} dakika", inline=True)
        embed.add_field(name="Sebep", value=sebep, inline=False)
        embed.set_thumbnail(url=uye.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ─── UNMUTE ────────────────────────────────────────────
    @app_commands.command(name="unmute", description="Bir üyenin susturmasını kaldır")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, uye: discord.Member):
        await uye.timeout(None)
        embed = discord.Embed(
            title="🔊 Susturma Kaldırıldı",
            description=f"{uye.mention} artık konuşabilir.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    # ─── TEMIZLE ───────────────────────────────────────────
    @app_commands.command(name="temizle", description="Kanaldan mesajları sil")
    @app_commands.describe(adet="Silinecek mesaj sayısı (max 100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def temizle(self, interaction: discord.Interaction, adet: int = 10):
        if adet < 1 or adet > 100:
            return await interaction.response.send_message("❌ 1-100 arası bir sayı girin!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        silinen = await interaction.channel.purge(limit=adet)
        await interaction.followup.send(f"🗑️ {len(silinen)} mesaj silindi.", ephemeral=True)

    # ─── UNBAN ─────────────────────────────────────────────
    @app_commands.command(name="unban", description="Yasaklı kullanıcının yasağını kaldır")
    @app_commands.describe(kullanici_id="Kullanıcının ID'si")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, kullanici_id: str):
        try:
            user = await self.bot.fetch_user(int(kullanici_id))
            await interaction.guild.unban(user)
            embed = discord.Embed(
                title="✅ Yasak Kaldırıldı",
                description=f"**{user}** kullanıcısının yasağı kaldırıldı.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        except discord.NotFound:
            await interaction.response.send_message("❌ Bu ID ile yasaklı kullanıcı bulunamadı.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Geçersiz ID formatı.", ephemeral=True)

    # ─── HATA YÖNETİMİ ─────────────────────────────────────
    @ban.error
    @kick.error
    @mute.error
    @temizle.error
    async def moderasyon_hatasi(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Bu komutu kullanmak için yetkiniz yok!", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Hata: {error}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderasyon(bot))
