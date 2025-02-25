# Gerekli kütühaneleri içe aktarmak 📕📗📘📙
import discord
from discord.ext import commands
from config import TOKEN
from modal import ProjectView

# Discord izinlerini vermek 👇
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True 

# Botun ön ekini belirler
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yapıldı")

@bot.command()
async def proje(ctx):
    await ctx.send("Aşağıdaki butonları kullanarak işlemleri gerçekleştirebilirsiniz:", view=ProjectView())

if __name__ == "__main__":
    bot.run(TOKEN)
