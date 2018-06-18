import asyncio
import datetime
import json
import logging
from pathlib import Path
import re

import discord
from discord.ext import commands

help_str = "GENFORCER HELP:\n" \
           "The Genforcer will remove any messages that have non-g alphanumeric (a-z,0-9) characters or more than 25% special characters in \"the-g-channel\"\n" \
           "The Genforcer will always delete your message upon recieving your command.\n" \
           "COMMANDS:\n" \
           "`!g suppress <seconds>` suppresses the Genforcer for a time\n" \
           "`!g gbinary <text>` converts your text to binary\n" \
           "`!g help` DMs you this"

def config_load():
    with open('data/config.json', 'r', encoding='utf-8') as doc:
        #  Please make sure encoding is correct, especially after editing the config file
        return json.load(doc)

config = config_load()

async def run():
    bot = Bot(config=config,
              description=config['description'])
    try:
        await bot.start(config['token'])
    except KeyboardInterrupt:
        await bot.logout()


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix="!",
            description=kwargs.pop('description')
        )
        self.start_time = None
        self.app_info = None

        self.suppressed_until = datetime.datetime.now()

        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())

    async def track_start(self):
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()

    async def load_all_extensions(self):
        await self.wait_until_ready()
        await asyncio.sleep(1)  # ensure that on_ready has completed and finished printing
        cogs = [x.stem for x in Path('cogs').glob('*.py')]
        for extension in cogs:
            try:
                self.load_extension(f'cogs.{extension}')
                print(f'loaded {extension}')
            except Exception as e:
                error = f'{extension}\n {type(e).__name__} : {e}'
                print(f'failed to load extension {error}')
            print('-' * 10)

    async def on_ready(self):
        print('-' * 10)
        self.app_info = await self.application_info()
        print(f'Logged in as: {self.user.name}\n'
              f'Using discord.py version: {discord.__version__}\n'
              f'Owner: {self.app_info.owner}\n'
              f'Template Maker: SourSpoon / Spoon#7805')
        print('-' * 10)

    async def process_commands(self, message):
        if message.content.lower().lstrip().startswith("!g "):
            await self.delete_message(message) # Do this first in case there's an exception
            fragments = message.content.lower().lstrip().split(" ")
            if fragments[1] == "suppress":
                if fragments[2]:
                    s = int(fragments[2])
                    self.suppressed_until = datetime.datetime.now() + datetime.timedelta(seconds=s)
            if fragments[1] == "gbinary":
                sbuild = ""
                for fragment in fragments[2:]:
                    sbuild += fragment + " "
                newstr = ''
                for char in sbuild:
                    newstr += bin(ord(char)).replace('0b', '').replace('0', 'g').replace('1', 'G')
                for sendable in [newstr[i:i+1920] for i in range(0, len(newstr), 1920)]:
                    await self.send_message(message.channel, content=sendable)
            if fragments[1] == "help":
                await self.send_message(message.author, content=help_str)

    async def on_message(self, message):
        #print(message.content + " in: " + str(message.channel) + " by: " + str(message.author))
        if message.author.bot:
            return  # ignore all bots
        else:
            await self.process_commands(message)
            if message.content.lower().lstrip().startswith("!g "):
                return
            part_we_care_about = message.content.replace(" ", "").replace("\n","").replace("\r","").lower()
            g_ratio = float(part_we_care_about.count('g')) / float(len(part_we_care_about))
            if datetime.datetime.now() > self.suppressed_until:
                if str(message.channel) == "the-g-channel" or str(message.channel) == "g-channel":
                    for character in part_we_care_about.lower():
                        if re.match("[a-f]|[h-z]|[0-9]", character) is not None:
                            print(str(message.author) + " sent an illegal message!")
                            await self.delete_message(message)
                            return
                    if g_ratio < float(config['character_ratio']):
                        print (str(message.author) + " sent an illegal message!")
                        await self.delete_message(message)
                        return

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())