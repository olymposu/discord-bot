import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        # Cog'ları yükle
        cogs = ["cogs.moderasyon", "cogs.muzik", "cogs.rol", "cogs.logger"]
        for cog in cogs:
            await self.load_extension(cog)
            print(f"✅ {cog} yüklendi.")

        # Slash komutlarını senkronize et
        await self.tree.sync()
        print("✅ Slash komutları senkronize edildi.")

    async def on_ready(self):
        print(f"\n{'='*40}")
        print(f"🤖 Bot aktif: {self.user}")
        print(f"📡 Sunucu sayısı: {len(self.guilds)}")
        print(f"{'='*40}\n")

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(self.guilds)} sunucu | /yardım"
            )
        )

bot = MyBot()

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ HATA: .env dosyasına DISCORD_TOKEN ekleyin!")
        exit(1)
    bot.run(token)
