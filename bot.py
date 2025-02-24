# Gerekli kütühaneleri içe aktarmak 📕📗📘📙
import discord
from discord.ext import commands
from config import TOKEN
from modal import ProjectView

# Discord izinlerini vermek 👇
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yapıldı")

@bot.command()
async def start(ctx):
    await ctx.send("Aşağıdaki butonları kullanarak işlemleri gerçekleştirebilirsiniz:", view=ProjectView())

bot.run(TOKEN)
