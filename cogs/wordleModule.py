import discord
from game_functions import *
from config import *

class WordleModule(commands.Cog):
	@commands.command()
	async def easy(self, ctx):
		"""Легкий режим, простые слова"""
		game_process.state = True
		game_process.word = choose_word(1)
		game_process.message_output = ['#' for _ in range(len(game_process.word))]

		print(f"Загаданное слово: {game_process.word}\n")

		await ctx.send(f"Слово длиной в {len(game_process.word)} букв успешно загадано, удачи!")
		return

	@commands.command()
	async def medium(self, ctx):
		"""Средний режим, слова посложнее"""
		game_process.state = True
		game_process.word = choose_word(2)
		game_process.message_output = ['#' for _ in range(len(game_process.word))]

		print(f"Загаданное слово: {game_process.word}\n")

		await ctx.send(f"Слово длиной в {len(game_process.word)} букв успешно загадано, удачи!")
		return

	@commands.command()
	async def hard(self, ctx):
		"""Сложный режим, самые сложные слова вплоть до 20 букв"""
		game_process.state = True
		game_process.word = choose_word(3)
		game_process.message_output = ['#' for _ in range(len(game_process.word))]

		print(f"Загаданное слово: {game_process.word}\n")
		await ctx.send(f"Для победы тебе понадобятся:\nA)Талант\nB)Трудолюбие\nC)ЭнтузиАзм")
		await ctx.send(f"Слово длиной в {len(game_process.word)} букв уже успешно загадано, удачи!")
		return

	@commands.command(aliases=['c'])
	async def choose_(self, ctx, word):
		"""Ручное загадывание слова, сообщение с словом самоудалится через секунду после написания"""
		game_process.state = True
		game_process.word = word
		game_process.message_output = ['#' for _ in range(len(game_process.word))]

		print(game_process.logs_print())

		await ctx.message.channel.purge(limit=2)
		await ctx.send(f"Слово длиной в {len(game_process.word)} букв успешно загадано!")
		return

	@commands.command()
	async def stopGame(self, ctx):
		"""Заканчивает текущую игру"""
		await ctx.send(f"Закончили упражнение\nИскомое слово - {game_process.word}")
		game_process.state = False
		game_process.word = ''
		game_process.attempt = 0
		return

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if message.content.startswith('.'):
		await client.process_commands(message)
		return

	if game_process.state is True:
		game_process.message_input = message.content
		print(game_process.logs_print())

		word = str(game_process.message_input)
		for i in range(len(word) - 2):
			if word[i] == word[i + 1] == word[i + 2]:
				return await message.channel.send("На сервере запрещено: \nа) читы,\nб)макросы")

		if game_process.message_input == game_process.word:
			await message.channel.send(f"Вы успешно отгадали слово за {game_process.attempt + 1} попыток")

			game_process.state = False
			game_process.word = ''
			game_process.attempt = 0
		else:
			game_process.attempt += 1
			word_image, game_process.message_output, needed_letters = key_function(game_process.message_input,
			                                                                       game_process.message_output,
			                                                                       game_process.word)
			output_message = ''
			if len(needed_letters) != 0:
				output_message = 'Содержащиеся буквы: '
				for s in needed_letters:
					output_message += f"{s}; "
			await message.channel.send(f"{word_image}\n{output_message}")
	else:
		await client.process_commands(message)

def setup(client):
	client.add_cog(WordleModule(client))
