from telethon import TelegramClient, events, types
import asyncio
import nest_asyncio
import json
nest_asyncio.apply()

with open('config.json', 'r') as configfile:
    config = json.load(configfile)
    chats_combination = config['chats']
    tg_id = config['tg_api']['id']
    tg_hash = config['tg_api']['hash']

tgclient = TelegramClient("forwarder_bot", tg_id, tg_hash).start()


async def getChannelId(text, maxdialogs):
    dialogs = await tgclient.get_dialogs(maxdialogs)
    isChannel = False
    for dialog in enumerate(dialogs):
        print(str(dialog[0])+")", dialog[1].name)
    while not isChannel:
        chat_num = int(input(text))
        if isinstance(dialogs[chat_num].message.peer_id, types.PeerChannel):
            isChannel = True
            chat_id = int(dialogs[chat_num].message.peer_id.channel_id)
        else:
            print("Введенный номер не является каналом.")
    return chat_id


@ tgclient.on(events.NewMessage(chats=list(map(int, list(chats_combination.keys())))))
async def handler(event: types.Message):
    channel_id = event.message.peer_id.channel_id
    msgText = event.message.message
    await tgclient.send_message(chats_combination[str(channel_id)], msgText)


async def main():
    print("Хотите ли вы изменить настройки пересылки?")
    doChangeSettings = int(input("1 - да, 0 - нет: "))
    if doChangeSettings == 1:
        global chats_combination, config
        chats_combination = {}
        channelNum = int(input("Введите количество каналов для пересылки: "))
        for x in range(channelNum):
            chat_from = await getChannelId(f"Введите номер {x+1} канала, откуда пересылать: ", 50)
            chat_to = await getChannelId(f"Введите номер {x+1} канала, куда пересылать: ", 50)
            chats_combination[str(chat_from)] = chat_to
        config['chats'] = chats_combination
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
    if chats_combination:
        print("Начал проверять на новые сообщения.")
        await tgclient._run_until_disconnected()
    else:
        print("Вы не ввели ни одну пару каналов для пересылки.")
        await tgclient.disconnect()

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
    finally:
        tgclient.disconnect()
