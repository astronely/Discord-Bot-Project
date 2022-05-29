import discord
import datetime
from config import *
import asyncio
from discord.ext import commands, timers

class TimeManager(commands.Cog):
	@commands.command(name='remind_longtime',aliases=['rl'])
	async def remind_longtime(self, ctx, time, *, text):
		""" Напоминает о чем-либо в конкретную дату
			Вводить дату в виде Y/M/D, Y - год, M - месяц, D - день"""
		date = datetime.datetime(*map(int, time.split("/")))
		timers.Timer(client, "reminder", date, args=(ctx.channel.id, ctx.author.id, text)).start()

	@commands.command(name='remind')
	async def remind_(self, ctx, time, *, text):
		""" Напоминает сделать что-либо через заданное время
			Использовать время в виде NUMBERs/m/h, где NUMBER - количество единиц,
			s - секунды, m - минуты, h - часы"""
		user = ctx.message.author
		embed = discord.Embed()
		embed.set_footer(
			text=f"{client.user.name}",
			icon_url=f"{client.user.avatar_url}")
		seconds = 0
		if text is None:
			embed.add_field(name='Warning',
			                value='Please specify what do you want me to remind you about.')  # Error message
		if time.lower().endswith('h'):
			seconds += int(time[:-1]) * 60 * 60
		elif time.lower().endswith('m'):
			seconds += int(time[:-1])*60
		elif time.lower().endswith("s"):
			seconds += int(time[:-1])
		if seconds == 0:
			embed.add_field(name='Warning',
			                value='Please, enter time!')
		elif seconds > 86400:
			embed.add_field(name='Warning',
			                value='Please, enter time < 24 hours.')
		else:
			embed.add_field(name='',
			                value='Reminder successfully created!.')
			await ctx.send(embed=embed)
			await asyncio.sleep(seconds)
			await ctx.send(f"Hey, {user.mention}, you asked to remind about: {text}")
			return
		await ctx.send(embed=embed, delete_after=20)

async def on_reminder(channel_id, author_id, text):
	channel = client.get_channel(channel_id)

	await channel.send(f'Hey, <@{author_id}>, you asked to remind about: {text}')
	await client.process_commands(text)

def setup(client):
	client.add_cog(TimeManager(client))
