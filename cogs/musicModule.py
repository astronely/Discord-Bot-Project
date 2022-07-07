import discord
import itertools
from functools import partial
import asyncio
from async_timeout import timeout
from config import *
import youtube_dl
from discord.ext import commands

youtube_dl.utils.bug_reports_message = lambda: ''
ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
	'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdlopts)

class VoiceConnectionError(commands.CommandError):
	"""Custom Exception class for connection errors."""

class InvalidVoiceChannel(VoiceConnectionError):
	"""Exception for cases of invalid Voice Channels."""

class YTDLSource(discord.PCMVolumeTransformer):
	def __init__(self, source, *, data, volume=0.5):
		super().__init__(source, volume)

		self.data = data

		self.title = data.get('title')
		self.url = data.get('url')

	def __getitem__(self, item: str):
		"""Allows us to access attributes similar to a dict.
		This is only useful when you are NOT downloading.
		"""
		return self.__getattribute__(item)

	@classmethod
	async def from_url(cls, ctx, search: str, *, loop, download=False):
		loop = loop or asyncio.get_event_loop()

		to_run = partial(ytdl.extract_info, url=search, download=download)
		data = await loop.run_in_executor(None, to_run)

		if 'entries' in data:
			# Выбирает первый url из очереди
			data = data['entries'][0]

		await ctx.send(f'`[Added {data["title"]} to the Queue.]\n`', delete_after=15)

		if download:
			source = ytdl.prepare_filename(data)
		else:
			return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

		return cls(discord.FFmpegPCMAudio(source), data=data)

	@classmethod
	async def regather_stream(cls, data, *, loop):
		loop = loop or asyncio.get_event_loop()

		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url=data['webpage_url'], download=False))

		return cls(discord.FFmpegPCMAudio(data['url']), data=data)

class MusicPlayer:
	def __init__(self, ctx):
		self.client = ctx.bot

		self._guild = ctx.guild
		self._channel = ctx.channel
		self._cog = ctx.cog

		self.queue = asyncio.Queue()
		self.next = asyncio.Event()
		self.current = None
		self.volume = .5

		self.np = None
		ctx.bot.loop.create_task(self.player_loop())

	async def player_loop(self):
		await self.client.wait_until_ready()

		while not self.client.is_closed():
			self.next.clear()

			try:
				async with timeout(10000):
					source = await self.queue.get()
			except asyncio.TimeoutError:
				return self.destroy(self._guild)

			if not isinstance(source, YTDLSource):
				try:
					source = await YTDLSource.regather_stream(source, loop=self.client.loop)
				except Exception as e:
					await self._channel.send(f"There was an error processing your song.\n it was: {e}", delete_after=20)
					continue

			self.current = source
			self.volume = self.volume
			self._guild.voice_client.play(source, after=lambda _: self.client.loop.call_soon_threadsafe(self.next.set))
			self.np = await self._channel.send(f'**Now Playing:** **`{source.title}`**')

			await self.next.wait()

			source.cleanup()
			self.current = None

			try:
				await self.np.delete()
			except discord.HTTPException:
				pass

	async def destroy(self, guild):
		return self.client.loop.create_task(self._cog.cleanup(guild))

class Music(commands.Cog):

	def __init__(self, client):
		self.client = client
		self.players = {}

	def get_player(self, ctx):
		try:
			player = self.players[ctx.guild.id]
		except KeyError:
			player = MusicPlayer(ctx)
			self.players[ctx.guild.id] = player

		return player

	async def cleanup(self, guild):
		try:
			await guild.voice_client.connected()
		except AttributeError:
			pass

		try:
			del self.players[guild.id]
		except KeyError:
			pass

	@staticmethod
	async def __error(ctx, error):
		if isinstance(error, commands.NoPrivateMessage):
			try:
				return await ctx.send('Данная команда не может использоваться в личных сообщениях', delete_after=20)
			except discord.HTTPException:
				pass
		elif isinstance(error, InvalidVoiceChannel):
			await ctx.send('Не удалось подключиться к голосовому каналу. '
						   'Убедитесь что вы находитесь в доступном голосовом канале.', delete_after=20)

	@commands.command(name="leave", aliases=['l'])
	async def leave_(self,ctx):
		"""Выгоняет бота из войс чата"""

		await ctx.voice_client.disconnect()

	@commands.command(name="connect", aliases=['j','join'])
	async def connect_(self, ctx, *, channel: discord.VoiceChannel = None):
		"""Подключает бота к войс-чату в котором вы находитесь"""

		if not channel:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				await ctx.send("Подключитесь к голосовому каналу.", delete_after=20)

		if ctx.voice_client:
			if ctx.voice_client.channel.id == channel.id:
				return
			try:
				await ctx.voice_client.move_to(channel)
			except asyncio.TimeoutError:
				return
		else:
			try:
				await channel.connect()
			except asyncio.TimeoutError:
				return

	@commands.command(name="play", aliases=['p'])
	async def play_(self, ctx, *, url):
		"""Включает звук видео из YouTube, если уже что-то запущенно, добавляет в очередь"""
		if ctx.author.voice is None:
			await ctx.send("Подключитесь к голосовому каналу.", delete_after=20)
		if ctx.voice_client is None:
			await ctx.author.voice.channel.connect()
		else:
			await ctx.voice_client.move_to(ctx.author.voice.channel)

		await ctx.trigger_typing()

		player = self.get_player(ctx)
		print(url)
		source = await YTDLSource.from_url(ctx, url, loop=self.client.loop, download=False)

		await player.queue.put(source)

	@commands.command(name="skip",aliases=['s'])
	async def skip_(self, ctx):
		"""Пропускает текущую песню"""

		if not ctx.voice_client or not ctx.voice_client.is_connected():
			return await ctx.send(f"Ничего не включено.", delete_after=20)
		elif ctx.voice_client.is_paused():
			return
		if ctx.voice_client.is_paused():
			return
		elif not ctx.voice_client.is_playing():
			return

		ctx.voice_client.stop()
		await ctx.send(f"Song skipped", delete_after=20)

	@commands.command(name="pause")
	async def pause_(self, ctx):
		"""Ставит на паузу"""

		if not ctx.voice_client or not ctx.voice_client.is_playing:
			return await ctx.send("Ничего не включено", delete_after=20)
		elif ctx.voice_client.is_paused():
			return

		ctx.voice_client.pause()

		await ctx.send("Song is paused", delete_after=20)

	@commands.command(name='resume')
	async def resume_(self, ctx):
		"""Возобновляет из паузы"""
		if not ctx.voice_client or not ctx.voice_client.is_connected():
			return await ctx.send("Ничего не включено", delete_after=20)
		elif not ctx.voice_client.is_paused():
			return

		ctx.voice_client.resume()
		await ctx.send("resume", delete_after=20)

	@commands.command(name='queue', aliases=['q', 'playlist'])
	async def queue_info(self, ctx):
		"""Информация об очереди"""

		if not ctx.voice_client or not ctx.voice_client.is_connected():
			return await ctx.send('Я не подключен к голосовому каналу.', delete_after=20)

		player = self.get_player(ctx)
		if player.queue.empty():
			return await ctx.send('Очередь пустует', delete_after=20)

		queue_list = list(itertools.islice(player.queue._queue, 0, player.queue.qsize()))

		info = '\n'.join(f'**`{queue_list.index(_)+1}`** **{_["title"]}**' for _ in queue_list)
		embed = discord.Embed(title=f'Current queue:', description=info)

		await ctx.send(embed=embed, delete_after=20)

	@commands.command(name="clean")
	async def clean_(self, ctx):
		"""Очищает всю очередь"""

		if not ctx.voice_client or not ctx.voice_client.is_connected:
			return await ctx.send("Я ничего не играю", delete_after=20)

		await self.cleanup(ctx.guild)

	@commands.command(name='clean_messages', aliases=['clear'])
	async def clean_messages(self, ctx, x):
		"""Удаляет заданное колчество сообщений"""
		await ctx.message.channel.purge(limit=int(x)+1)

def setup(client):
	client.add_cog(Music(client))
