import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@bot.command()
async def Hi(ctx):
    await ctx.send('hello')

# استبدل 'TOKEN' بتوكن البوت الخاص بك
bot.run('MTM1MDEwNjM5MTc3NTQxMjI0NQ.GocPNd.Vm7fZjuEjt4AxHTOWq0o3QFz3Eza6A3eEqwXnI')
