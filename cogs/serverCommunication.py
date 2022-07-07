from config import *
from peewee import *
import sqlite3

class Channels(commands.Cog):
    @staticmethod
    def is_exists_(channel_id, db_name):
        with sqlite3.connect(f'db/DiscordBot.db') as db:
            cursor = db.cursor()
            info = cursor.execute(f" SELECT id FROM {db_name} WHERE id=? ", (channel_id,))

            if info.fetchone() is None:
                return False
            return True

    @staticmethod
    def get_channels(db_name):
        with sqlite3.connect(f'db/DiscordBot.db') as db:
            cursor = db.cursor()
            channels = cursor.execute(f" SELECT chat FROM chats")
        return channels

    @commands.command()
    async def get_cd(self, message):
        print(message.channel)

    @commands.command(aliases=["add"])
    async def add_channel_(self, ctx):
        """Добавляет текстовый канал в базу данных и позволяет в нем играть в wordle"""
        if not self.is_exists_(int(ctx.channel.id), 'chats'):
            with sqlite3.connect('db/DiscordBot.db') as db:
                cursor = db.cursor()
                cursor.execute("""INSERT INTO chats VALUES (?, ?)""", (str(ctx.channel), int(ctx.channel.id)))

            channels = list(self.get_channels("chats"))
            info = '\n'.join(f"`{channels.index(name) + 1}`** **`{name[0]}`** **" for name in channels)
            embed = discord.Embed(title='Channel list has been updated', description=info)

            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=discord.Embed(title='This channel is already in database!'))
        return

    @commands.command(aliases=["delete"])
    async def delete_channel_(self, ctx):
        """Удаляет текстовый канал из базы данных, что запрещает играть в нем в wordle"""
        if self.is_exists_(int(ctx.channel.id), 'chats'):
            with sqlite3.connect('db/DiscordBot.db') as db:
                cursor = db.cursor()
                cursor.execute(f" DELETE FROM chats WHERE id=? ", (str(ctx.channel.id),))

            channels = list(self.get_channels("chats"))
            info = '\n'.join(f"`{channels.index(name) + 1}`** **`{name[0]}`** **" for name in channels)
            embed = discord.Embed(title='Channel list has been updated', description=info)

            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=discord.Embed(title="This channel isn't in database!"))
        return

    @commands.command(aliases=['set'])
    async def set_logs_directory_(self, ctx):
        """Устанавливает текстовый канал, в котором будут логи"""
        if not self.is_exists_(int(ctx.channel.id), "logs"):
            with sqlite3.connect('db/DiscordBot.db') as db:
                cursor = db.cursor()
                cursor.execute(f" INSERT INTO logs VALUES (?, ?, ?)",
                               (str(ctx.guild.name), str(ctx.channel.name), int(ctx.channel.id)))
            await ctx.send(embed=discord.Embed(title='Now this channel is actual logs directory!'))
        return

def setup(client):
    client.add_cog(Channels(client))
