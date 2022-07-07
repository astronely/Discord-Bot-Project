import random
import sqlite3

def choose_word(level):
	with sqlite3.connect('db/DiscordBot.db') as db:
		cursor = db.cursor()

		if level == 1:
			number = random.randint(1, 524)
		elif level == 2:
			number = random.randint(525, 958)
		elif level == 3:
			number = random.randint(959, 1009)

		cursor.execute(""" SELECT name FROM first WHERE (id = %(number)d) AND (level = %(level)d) """
		               % {'number': number, 'level': level})
		return(cursor.fetchone()[0])

def find_number(message):
	for i in range(len(message)):
		if message[i][0] in '0123456789':
			return int(message[i])

def key_function(word_input, word_output, word_needed):
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

	return output_function(word_output), word_output, letters_input.intersection(letters_closed)


def output_function(word):
	word_new = ''
	for i in range(len(word)):
		if word[i] == '#':
			word_new += '⬜️'
		else:
			word_new += word[i]
	return word_new
