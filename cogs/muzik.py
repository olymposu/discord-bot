import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp
from collections import deque

# yt-dlp ayarları
YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
    "extract_flat": False,
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn -filter:a 'volume=0.5'",
}


class MuzikKuyruk:
    def __init__(self):
        self.kuyruk: deque = deque()
        self.simdi_caliniyor: dict | None = None
        self.ses_seviyesi: float = 0.5
        self.tekrar: bool = False


class Muzik(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sunucu_kuyruk: dict[int, MuzikKuyruk] = {}

    def get_kuyruk(self, guild_id: int) -> MuzikKuyruk:
        if guild_id not in self.sunucu_kuyruk:
            self.sunucu_kuyruk[guild_id] = MuzikKuyruk()
        return self.sunucu_kuyruk[guild_id]

    async def ara_ve_getir(self, sorgu: str) -> dict | None:
        """YouTube'da arama yap ve ses URL'i döndür"""
        loop = asyncio.get_event_loop()

        # URL mi yoksa arama mı?
        if not sorgu.startswith("http"):
            sorgu = f"ytsearch:{sorgu}"

        def _ara():
            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ytdl:
                info = ytdl.extract_info(sorgu, download=False)
                if "entries" in info:
                    info = info["entries"][0]
                return {
                    "url": info["url"],
                    "baslik": info.get("title", "Bilinmiyor"),
                    "sure": info.get("duration", 0),
                    "kanal": info.get("uploader", "Bilinmiyor"),
                    "thumbnail": info.get("thumbnail", ""),
                    "webpage_url": info.get("webpage_url", ""),
                }

        try:
            return await loop.run_in_executor(None, _ara)
        except Exception as e:
            print(f"Arama hatası: {e}")
            return None

    def sonraki_sarki(self, guild_id: int, voice_client: discord.VoiceClient):
        """Sıradaki şarkıyı çal"""
        kuyruk = self.get_kuyruk(guild_id)

        if kuyruk.tekrar and kuyruk.simdi_caliniyor:
            sarki = kuyruk.simdi_caliniyor
        elif kuyruk.kuyruk:
            sarki = kuyruk.kuyruk.popleft()
            kuyruk.simdi_caliniyor = sarki
        else:
            kuyruk.simdi_caliniyor = None
            return

        source = discord.FFmpegPCMAudio(sarki["url"], **FFMPEG_OPTIONS)
        source = discord.PCMVolumeTransformer(source, volume=kuyruk.ses_seviyesi)

        def after(error):
            if error:
                print(f"Oynatıcı hatası: {error}")
            asyncio.run_coroutine_threadsafe(
                asyncio.sleep(0.5), self.bot.loop
            ).result()
            self.sonraki_sarki(guild_id, voice_client)

        voice_client.play(source, after=after)

    # ─── ÇALINACAK ─────────────────────────────────────────
    @app_commands.command(name="cal", description="Müzik çal (URL veya isim)")
    @app_commands.describe(sorgu="YouTube URL veya şarkı adı")
    async def cal(self, interaction: discord.Interaction, sorgu: str):
        if not interaction.user.voice:
            return await interaction.response.send_message("❌ Önce bir ses kanalına girin!", ephemeral=True)

        await interaction.response.defer()

        kanal = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        if not vc:
            vc = await kanal.connect()
        elif vc.channel != kanal:
            await vc.move_to(kanal)

        sarki = await self.ara_ve_getir(sorgu)
        if not sarki:
            return await interaction.followup.send("❌ Şarkı bulunamadı!")

        kuyruk = self.get_kuyruk(interaction.guild_id)

        if vc.is_playing():
            kuyruk.kuyruk.append(sarki)
            dakika, saniye = divmod(sarki["sure"], 60)
            embed = discord.Embed(
                title="📋 Kuyruğa Eklendi",
                description=f"**[{sarki['baslik']}]({sarki['webpage_url']})**",
                color=discord.Color.blue()
            )
            embed.add_field(name="Süre", value=f"{dakika:02d}:{saniye:02d}", inline=True)
            embed.add_field(name="Kanal", value=sarki["kanal"], inline=True)
            embed.add_field(name="Sıra", value=f"#{len(kuyruk.kuyruk)}", inline=True)
            if sarki["thumbnail"]:
                embed.set_thumbnail(url=sarki["thumbnail"])
        else:
            kuyruk.simdi_caliniyor = sarki
            source = discord.FFmpegPCMAudio(sarki["url"], **FFMPEG_OPTIONS)
            source = discord.PCMVolumeTransformer(source, volume=kuyruk.ses_seviyesi)

            def after(error):
                if error:
                    print(f"Oynatıcı hatası: {error}")
                self.sonraki_sarki(interaction.guild_id, vc)

            vc.play(source, after=after)

            dakika, saniye = divmod(sarki["sure"], 60)
            embed = discord.Embed(
                title="🎵 Şimdi Çalınıyor",
                description=f"**[{sarki['baslik']}]({sarki['webpage_url']})**",
                color=discord.Color.green()
            )
            embed.add_field(name="Süre", value=f"{dakika:02d}:{saniye:02d}", inline=True)
            embed.add_field(name="Kanal", value=sarki["kanal"], inline=True)
            if sarki["thumbnail"]:
                embed.set_thumbnail(url=sarki["thumbnail"])

        await interaction.followup.send(embed=embed)

    # ─── DUR ───────────────────────────────────────────────
    @app_commands.command(name="dur", description="Müziği durdur/devam ettir")
    async def dur(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc:
            return await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)

        if vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Müzik duraklatıldı.")
        elif vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Müzik devam ediyor.")
        else:
            await interaction.response.send_message("❌ Şu an çalan bir şarkı yok.", ephemeral=True)

    # ─── GEÇ ───────────────────────────────────────────────
    @app_commands.command(name="gec", description="Sıradaki şarkıya geç")
    async def gec(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_playing():
            return await interaction.response.send_message("❌ Şu an çalan şarkı yok.", ephemeral=True)

        vc.stop()
        await interaction.response.send_message("⏭️ Sonraki şarkıya geçildi.")

    # ─── KUYRUK ────────────────────────────────────────────
    @app_commands.command(name="kuyruk", description="Müzik kuyruğunu göster")
    async def kuyruk(self, interaction: discord.Interaction):
        kuyruk = self.get_kuyruk(interaction.guild_id)

        embed = discord.Embed(title="🎶 Müzik Kuyruğu", color=discord.Color.purple())

        if kuyruk.simdi_caliniyor:
            embed.add_field(
                name="▶️ Şimdi Çalınıyor",
                value=f"**{kuyruk.simdi_caliniyor['baslik']}**",
                inline=False
            )

        if kuyruk.kuyruk:
            liste = "\n".join(
                [f"`{i+1}.` {s['baslik']}" for i, s in enumerate(kuyruk.kuyruk)]
            )
            embed.add_field(name=f"📋 Sıradakiler ({len(kuyruk.kuyruk)})", value=liste[:1024], inline=False)
        else:
            embed.add_field(name="📋 Kuyruk", value="Kuyruk boş", inline=False)

        await interaction.response.send_message(embed=embed)

    # ─── SES ───────────────────────────────────────────────
    @app_commands.command(name="ses", description="Ses seviyesini ayarla (1-100)")
    @app_commands.describe(seviye="Ses seviyesi (1-100)")
    async def ses(self, interaction: discord.Interaction, seviye: int):
        if seviye < 1 or seviye > 100:
            return await interaction.response.send_message("❌ Ses 1-100 arası olmalı!", ephemeral=True)

        kuyruk = self.get_kuyruk(interaction.guild_id)
        kuyruk.ses_seviyesi = seviye / 100

        vc = interaction.guild.voice_client
        if vc and vc.source:
            vc.source.volume = kuyruk.ses_seviyesi

        await interaction.response.send_message(f"🔊 Ses seviyesi: **{seviye}%**")

    # ─── TEKRAR ────────────────────────────────────────────
    @app_commands.command(name="tekrar", description="Mevcut şarkıyı tekrarla")
    async def tekrar(self, interaction: discord.Interaction):
        kuyruk = self.get_kuyruk(interaction.guild_id)
        kuyruk.tekrar = not kuyruk.tekrar
        durum = "açık 🔁" if kuyruk.tekrar else "kapalı"
        await interaction.response.send_message(f"Tekrar modu: **{durum}**")

    # ─── ÇIKIS ─────────────────────────────────────────────
    @app_commands.command(name="cik", description="Botu ses kanalından çıkar")
    async def cik(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc:
            return await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)

        kuyruk = self.get_kuyruk(interaction.guild_id)
        kuyruk.kuyruk.clear()
        kuyruk.simdi_caliniyor = None
        await vc.disconnect()
        await interaction.response.send_message("👋 Ses kanalından çıkıldı.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Muzik(bot))
