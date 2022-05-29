import discord
from discord.ext import commands

class UserData(object):
	def __init__(self, state, word, message_input, message_output, attempt):
		self.state = state
		self.word = word
		self.message_input = message_input
		self.message_output = message_output
		self.attempt = attempt

	def logs_print(self):
		return f"Введенное слово: {self.message_input}\nПопытка: {self.attempt}"


game_process = UserData(False, '', '', '', 0)

bot_token = 'OTY0NzMxODg3ODQxMDY3MDY5.Ylo6lQ.EaO456sfByr6EX81goCMLLWIasc'
client = commands.Bot(command_prefix='.')
