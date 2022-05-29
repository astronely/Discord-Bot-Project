import discord
from config import *
from game_functions import *
import random
import time
from words_dict import dict_easy, dict_medium, dict_hard

@client.event
async def on_message(message):
	if message.author != client.user and not message.content.startswith('.'):
		if str(message.author) == "Silica Animus 🤖#1222" and not game_process.state:

			if not message.content.startswith('.') and message.content.startswith('Слово длиной'):
				number = find_number(str(message.content).split())
				if 2 <= number <= 6:
					game_process.dictionary = sort_dict(dict_easy, number)
				elif 7 <= number <= 11:
					game_process.dictionary = sort_dict(dict_medium, number)
				elif 12 <= number <= 16:
					game_process.dictionary = sort_dict(dict_hard, number)

				game_process.dictionary = sorted(game_process.dictionary)
				game_process.state = True
				game_process.word = game_process.dictionary[random.randint(0, len(game_process.dictionary))]

				await message.channel.send(game_process.word)

		elif str(message.author) == "Silica Animus 🤖#1222" and game_process.state:

			if not message.content.startswith('Вы успнешно'):
				time.sleep(2)
				game_process.dictionary.pop(game_process.dictionary.index(game_process.word))
				game_process.word = game_process.dictionary[random.randint(0, len(game_process.dictionary)-1)]
				print(len(game_process.dictionary))
				await message.channel.send(game_process.word)

			else:
				game_process.word = ''
				game_process.dictionary = []
				game_process.state = False

	await client.process_commands(message)
