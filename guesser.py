import discord
from config import *
from game_functions import *
import random
import time
from database import dict_easy, dict_medium, dict_hard

@client.event
async def on_message(message):
	if message.author != client.user and not message.content.startswith('.'):
		if str(message.author) == "Silica Animus 🤖#1222" and not player.state:

			if not message.content.startswith('.') and message.content.startswith('Слово длиной'):
				number = find_number(str(message.content).split())
				if 2 <= number <= 6:
					player.dictionary = sort_dict(dict_easy, number)
				elif 7 <= number <= 11:
					player.dictionary = sort_dict(dict_medium, number)
				elif 12 <= number <= 16:
					player.dictionary = sort_dict(dict_hard, number)

				player.dictionary = sorted(player.dictionary)
				player.state = True
				player.word = player.dictionary[random.randint(0, len(player.dictionary))]

				await message.channel.send(player.word)

		elif str(message.author) == "Silica Animus 🤖#1222" and player.state:

			if not message.content.startswith('Вы успнешно'):
				time.sleep(2)
				player.dictionary.pop(player.dictionary.index(player.word))
				player.word = player.dictionary[random.randint(0, len(player.dictionary)-1)]
				print(len(player.dictionary))
				await message.channel.send(player.word)

			else:
				player.word = ''
				player.dictionary = []
				player.state = False

	await client.process_commands(message)
