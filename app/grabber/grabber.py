import configparser
import json
import sys
from telethon.sync import TelegramClient
from telethon import connection
from datetime import date, datetime
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.functions.messages import GetHistoryRequest

config = configparser.ConfigParser()
config.read("config.ini")

api_id   = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

proxy = (config['Telegram']['proxy_server'],config['Telegram']['proxy_port'],config['Telegram']['proxy_key'])

client = TelegramClient(username, api_id, api_hash)
client.start()

async def dump_all_participants(channel, username):
        output = False
        async for user in client.iter_participants(channel, search=username):
                if user.username.lower() == username:
                        return True
        return output

async def main():
        url = str(sys.argv[1])
        username = str(sys.argv[2])
        # url = 'https://t.me/inst_yt_tt'
        channel = await client.get_entity(url)
        status = await dump_all_participants(channel, username)
        return status


with client:
        print(client.loop.run_until_complete(main()))