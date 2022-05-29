import os
from config import *


for filename in os.listdir("./cogs"):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')

if __name__ == '__main__':
	@client.event
	async def on_ready():
		print('We have logged in as {0.user}'.format(client))
	client.run(bot_token)

