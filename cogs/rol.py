import discord
from discord.ext import commands
from discord import app_commands


class Rol(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ─── ROL VER ───────────────────────────────────────────
    @app_commands.command(name="rolver", description="Bir üyeye rol ver")
    @app_commands.describe(
        uye="Rol verilecek üye",
        rol="Verilecek rol"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rolver(self, interaction: discord.Interaction, uye: discord.Member, rol: discord.Role):
        if rol >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                "❌ Bu rol botun rolünden yüksek, atayamam!", ephemeral=True
            )
        if rol in uye.roles:
            return await interaction.response.send_message(
                f"❌ {uye.mention} zaten **{rol.name}** rolüne sahip!", ephemeral=True
            )

        await uye.add_roles(rol, reason=f"{interaction.user} tarafından atandı")

        embed = discord.Embed(
            title="✅ Rol Verildi",
            color=rol.color if rol.color.value else discord.Color.green()
        )
        embed.add_field(name="Üye", value=uye.mention, inline=True)
        embed.add_field(name="Rol", value=rol.mention, inline=True)
        embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)

    # ─── ROL AL ────────────────────────────────────────────
    @app_commands.command(name="rolal", description="Bir üyeden rol al")
    @app_commands.describe(
        uye="Rolü alınacak üye",
        rol="Alınacak rol"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rolal(self, interaction: discord.Interaction, uye: discord.Member, rol: discord.Role):
        if rol not in uye.roles:
            return await interaction.response.send_message(
                f"❌ {uye.mention} zaten **{rol.name}** rolüne sahip değil!", ephemeral=True
            )

        await uye.remove_roles(rol, reason=f"{interaction.user} tarafından alındı")

        embed = discord.Embed(
            title="🗑️ Rol Alındı",
            color=discord.Color.red()
        )
        embed.add_field(name="Üye", value=uye.mention, inline=True)
        embed.add_field(name="Rol", value=rol.mention, inline=True)
        embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)

    # ─── ROL BİLGİSİ ───────────────────────────────────────
    @app_commands.command(name="rolbilgi", description="Bir rol hakkında bilgi göster")
    @app_commands.describe(rol="Bilgi alınacak rol")
    async def rolbilgi(self, interaction: discord.Interaction, rol: discord.Role):
        embed = discord.Embed(
            title=f"🏷️ {rol.name} Rolü",
            color=rol.color if rol.color.value else discord.Color.blurple()
        )
        embed.add_field(name="ID", value=rol.id, inline=True)
        embed.add_field(name="Renk", value=str(rol.color), inline=True)
        embed.add_field(name="Üye Sayısı", value=len(rol.members), inline=True)
        embed.add_field(name="Mentionlanabilir", value="✅" if rol.mentionable else "❌", inline=True)
        embed.add_field(name="Ayrı Gösterim", value="✅" if rol.hoist else "❌", inline=True)
        embed.add_field(name="Konum", value=rol.position, inline=True)

        # İzinler
        izinler = [
            perm.replace("_", " ").title()
            for perm, value in rol.permissions
            if value
        ]
        if izinler:
            embed.add_field(
                name="İzinler",
                value=", ".join(izinler[:10]) + ("..." if len(izinler) > 10 else ""),
                inline=False
            )

        embed.set_footer(text=f"Oluşturulma: {rol.created_at.strftime('%d.%m.%Y')}")
        await interaction.response.send_message(embed=embed)

    # ─── ROL OLUŞTUR ───────────────────────────────────────
    @app_commands.command(name="rolekle", description="Yeni bir rol oluştur")
    @app_commands.describe(
        isim="Rolün adı",
        renk="Hex renk kodu (örn: ff0000)",
        mentionlanabilir="Bu rol mentionlanabilir mi?"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rolekle(
        self,
        interaction: discord.Interaction,
        isim: str,
        renk: str = "000000",
        mentionlanabilir: bool = False
    ):
        try:
            renk_obj = discord.Color(int(renk.replace("#", ""), 16))
        except ValueError:
            return await interaction.response.send_message("❌ Geçersiz renk kodu! (örn: ff0000)", ephemeral=True)

        rol = await interaction.guild.create_role(
            name=isim,
            color=renk_obj,
            mentionable=mentionlanabilir,
            reason=f"{interaction.user} tarafından oluşturuldu"
        )

        embed = discord.Embed(
            title="✅ Rol Oluşturuldu",
            color=renk_obj
        )
        embed.add_field(name="Rol", value=rol.mention, inline=True)
        embed.add_field(name="Renk", value=f"#{renk.upper()}", inline=True)
        embed.add_field(name="Mentionlanabilir", value="✅" if mentionlanabilir else "❌", inline=True)
        await interaction.response.send_message(embed=embed)

    # ─── ROL SİL ───────────────────────────────────────────
    @app_commands.command(name="rolsil", description="Bir rolü sil")
    @app_commands.describe(rol="Silinecek rol")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rolsil(self, interaction: discord.Interaction, rol: discord.Role):
        if rol >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                "❌ Bu rolü silemem, rolüm bu rolden düşük!", ephemeral=True
            )

        rol_adi = rol.name
        await rol.delete(reason=f"{interaction.user} tarafından silindi")

        embed = discord.Embed(
            title="🗑️ Rol Silindi",
            description=f"**{rol_adi}** rolü silindi.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

    # ─── ROLÜM ─────────────────────────────────────────────
    @app_commands.command(name="rollerim", description="Rollerini listele")
    async def rollerim(self, interaction: discord.Interaction):
        roller = [r.mention for r in interaction.user.roles if r.name != "@everyone"]

        embed = discord.Embed(
            title=f"🏷️ {interaction.user.display_name} Rolleri",
            color=interaction.user.top_role.color
        )
        embed.description = " ".join(roller) if roller else "Hiç rol yok."
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ─── HATA YÖNETİMİ ─────────────────────────────────────
    @rolver.error
    @rolal.error
    @rolekle.error
    @rolsil.error
    async def rol_hatasi(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Rol yönetimi için yetkiniz yok!", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Hata: {error}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Rol(bot))
