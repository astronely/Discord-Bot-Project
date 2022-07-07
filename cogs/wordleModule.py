import sqlite3
import random
from config import *

class WordlePlayer:
	def __init__(self, state, word, message_input, message_output, attempt):
		self.state = state
		self.word = word
		self.message_input = message_input
		self.message_output = message_output
		self.attempt = attempt

	def logs_print(self):
		return f"Введенное слово: {self.message_input}, Попытка: {self.attempt}"

class Wordle(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.players = {}

	def get_player_(self, ctx):
		try:
			player = self.players[ctx.guild.id]
		except KeyError:
			player = WordlePlayer(False, '', '', '', 0)
			self.players[ctx.guild.id] = player
		return player

	def key_function(self, word_input, word_output, word_needed):
		"""
	        word_input - your text message from chat
	        word_output - array form of message that will be send
	        word_needed - your guessed word
	    """
		if len(word_input) < len(word_needed):
			word_input += ' ' * (len(word_needed) - len(word_input))

		for i in range(len(word_needed)):
			if word_input[i] == word_needed[i]:
				word_output[i] = word_needed[i]

		letters_input = set()
		letters_closed = set()

		for i in range(len(word_output)):
			if word_output[i] == '#':
				letters_input.add(word_input[i])
				letters_closed.add(word_needed[i])

		return self.output_function(word_output), word_output, letters_input.intersection(letters_closed)

	@staticmethod
	def output_function(word):
		word_new = ''
		for i in range(len(word)):
			if word[i] == '#':
				word_new += '⬜️'
			else:
				word_new += word[i]
		return word_new

	@staticmethod
	def choose_word(level):
		with sqlite3.connect('db/DiscordBot.db') as db:
			cursor = db.cursor()

			if level == 1:
				number = random.randint(1, 524)
			elif level == 2:
				number = random.randint(525, 958)
			elif level == 3:
				number = random.randint(959, 1009)

			cursor.execute(""" SELECT name FROM words WHERE (id = %(number)d) AND (level = %(level)d) """
						   % {'number': number, 'level': level})
			return (cursor.fetchone()[0])

	@staticmethod
	def is_exists_(channel_id):
		with sqlite3.connect(f'db/DiscordBot.db') as db:
			cursor = db.cursor()
			info = cursor.execute(f" SELECT id FROM chats WHERE id=? ", (channel_id,))

			if info.fetchone() is None:
				return False
			return True

	@commands.command()
	async def easy(self, ctx):
		"""Легкий режим, простые слова"""
		if not self.is_exists_(ctx.channel.id):
			return

		player = self.get_player_(ctx)
		if player.state:
			await ctx.send(f"Слово уже загадано!")
			return

		player.state = True
		player.word = self.choose_word(1)
		player.message_output = ['#' for _ in range(len(player.word))]

		print(f"Загаданное слово: {player.word}")

		await ctx.send(f"Слово длиной в {len(player.word)} букв успешно загадано, удачи!")
		return

	@commands.command()
	async def medium(self, ctx):
		"""Средний режим, слова посложнее"""
		if not self.is_exists_(ctx.channel.id):
			return

		player = self.get_player_(ctx)
		if player.state:
			await ctx.send(f"Слово уже загадано!")
			return

		player.state = True
		player.word = self.choose_word(2)
		player.message_output = ['#' for _ in range(len(player.word))]

		print(f"Загаданное слово: {player.word}")

		await ctx.send(f"Слово длиной в {len(player.word)} букв успешно загадано, удачи!")
		return

	@commands.command()
	async def hard(self, ctx):
		"""Сложный режим, самые сложные слова вплоть до 20 букв"""
		if not self.is_exists_(ctx.channel.id):
			return

		player = self.get_player_(ctx)
		if player.state:
			await ctx.send(f"Слово уже загадано!")
			return

		player.state = True
		player.word = self.choose_word(3)
		player.message_output = ['#' for _ in range(len(player.word))]

		print(f"Загаданное слово: {player.word}")
		await ctx.send(f"Слово длиной в {len(player.word)} букв уже успешно загадано, удачи!")
		return

	@commands.command(aliases=['c'])
	async def choose_(self, ctx, word):
		"""Ручное загадывание слова, сообщение с словом самоудалится через секунду после написания"""
		if not self.is_exists_(ctx.channel.id):
			return

		player = self.get_player_(ctx)
		if player.state:
			await ctx.send(f"Слово уже загадано!")
			return

		player.state = True
		player.word = word
		player.message_output = ['#' for _ in range(len(player.word))]
		print(f"Загаданное слово: {player.word}")

		await ctx.message.channel.purge(limit=2)
		await ctx.send(f"Слово длиной в {len(player.word)} букв успешно загадано!")
		return

	@commands.command(aliases=['stopgame'])
	async def stopGame_(self, ctx):
		"""Заканчивает текущую игру"""
		player = self.get_player_(ctx)
		await ctx.send(f"Закончили упражнение\nИскомое слово - {player.word}")
		player.state = False
		player.word = ''
		player.attempt = 0
		return

	@commands.Cog.listener()
	async def on_message(self, message):

		if message.author == client.user:
			return
		if not self.is_exists_(message.channel.id):
			return

		try:
			player = self.players[message.guild.id]
		except KeyError:
			return

		if player.state is True and not message.content.startswith('.'):
			player.message_input = message.content
			print(f"Сервер:{message.guild.name}, {player.logs_print()}")

			if player.message_input == player.word:
				await message.channel.send(f"Вы успешно отгадали слово за {player.attempt + 1} попыток")

				player.state = False
				player.word = ''
				player.attempt = 0
			else:
				player.attempt += 1
				word_image, player.message_output, needed_letters = self.key_function(player.message_input,
																				 player.message_output, player.word)
				output_message = ''
				if len(needed_letters) != 0:
					output_message = 'Содержащиеся буквы: '
					for s in needed_letters:
						output_message += f"{s}; "
				await message.channel.send(f"{word_image}\n{output_message}")


def setup(client):
	client.add_cog(Wordle(client))
