import telebot
import lichess.api
import berserk
import admin

LOGGER_ID = None

TOKEN = 'Your token'

bot = telebot.TeleBot(TOKEN)

client = berserk.Client()


def reparse(msg):
    return msg.split(" ")


def title(handle):
    try:
        return client.users.get_realtime_statuses(handle)[0]['title']
    except KeyError:
        return


def get_top_10(text):
    try:
        type = text[1]
        type = type.lower()
        n = 10
        if len(text) == 3:
            try:
                n = min(100, int(text[2]))
            except:
                return "Write type then count!"
        top10 = client.users.get_leaderboard(type, count=n)
        top = type.capitalize() + ":\n"
        # top10['perfs']['type'][position]['username']

        for i in range(0, n):
            user = top10[i]['username']
            title_ = title(user)
            if title_ == None:
                top += f"{i + 1}) {user}: {top10[i]['perfs'][type]['rating']}\n"
            else:
                top += f"{i + 1}) {title_} {user}: {top10[i]['perfs'][type]['rating']}\n"
        return top
        # print(top)

    except berserk.exceptions.ResponseError:
        return "Enter a correct type!"


def gif(handle):
    try:
        link = last_game_link(handle)
        conv = link.split(".")
        converted = conv[0] + "1.org/game/export/gif" + conv[1][3:] + ".gif"
        return converted
    except:
        return "User not found!"


def last_game_link(handle):
    try:
        import re
        pgn = last_game_pgn(handle)
        url_pattern = r'http(?:s)?://\S+'
        link = re.findall(url_pattern, pgn)
        out = link[0][:-2]
        return out
    except:
        return "User not found!"


def last_game_pgn(handle):
    from lichess.format import SINGLE_PGN
    # user = lichess.api.user(handle)
    try:
        pgn = lichess.api.user_games(handle, max=1, format=SINGLE_PGN)
        return pgn
    except:
        return "User not found!"


def online_status(handle):
    ans = "Offline"
    try:
        user = lichess.api.user(handle)
        if user['online']:
            ans = "Online"
    except lichess.api.ApiHttpError:
        ans = "User not found!"
    return ans


def all_info(handle):
    ans = ""
    try:
        user = lichess.api.user(handle)
        bullet = f"Bullet - {user['perfs']['bullet']['rating']}"
        blitz = f"Blitz - {user['perfs']['blitz']['rating']}"
        rapid = f"Rapid - {user['perfs']['rapid']['rating']}"
        classical = f"Classical - {user['perfs']['classical']['rating']}"
        online = online_status(handle)
        playing = "Not playing now"
        if user.get('playing'):
            playing = "Playing now"
        ans = f"{handle}:\n{bullet}\n{blitz}\n{rapid}\n{classical}\n{online}\n{playing}\nTitle: {title(handle)}"
    except KeyError:
        ans = "Account was closed!"
    except lichess.api.ApiHttpError:
        ans = "User not found!"
    return ans


def get_rating(handle):
    ans = ""
    try:
        user = lichess.api.user(handle)
        bullet = f"Bullet - {user['perfs']['bullet']['rating']}"
        blitz = f"Blitz - {user['perfs']['blitz']['rating']}"
        rapid = f"Rapid - {user['perfs']['rapid']['rating']}"
        classical = f"Classical - {user['perfs']['classical']['rating']}"
        ans = f"{bullet}\n{blitz}\n{rapid}\n{classical}"
    except lichess.api.ApiHttpError:
        ans = "User not found!"
    return ans



ADMIN_COMMANDS = ["/ban", "/banlist"]  # , "/stop", "/run"]


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    bot.message_handler(content_types=['text'])
    # print(message.text.split()[0])
    if message.text.split()[0] in ADMIN_COMMANDS:
        if message.from_user.id in admin.USERS_IN_BAN:
            return
        bot.send_message(
            message.from_user.id, admin.main(message.from_user.id, message.text))


    elif message.from_user.id in admin.USERS_IN_BAN:
        return
    elif message.text == "/start":
        bot.send_message(message.from_user.id, "Используйте: /help")
    elif message.text == "/iidd":
        bot.send_message(message.from_user.id, message.from_user.id)
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Использование: /command user_handle\n"
                                               "Во всех командах поддерживаются только стандартные режимы:\n"
                                               "Bullet, Blitz, Rapid, Classical\n"
                                               "/rating - выводит текущий рейтинг пользователя\n"
                                               "/game - выводит последнюю игру пользователя в PGN формате,\n"
                                               "/link - выводит ссылку на последнюю игру пользователя\n"
                                               "/status - выводит статус пользователя в сети.\n"
                                               "/top - выводит топ игроков введенного варианта игры с введенного кол-ва игроков\n"
                                               "(Максимально 100, 10 по умолчанию)\n"
                                               "Использование: /top variant count\n"
                                               "count - необязательный параметр\n"
                                               "/gif - выводит ссылку на gif последней партии\n"
                                               "/info - выводит всю информацию о пользователе")
    else:
        if len(reparse(message.text)) < 2:
            bot.send_message(message.from_user.id, "Write command in the correct form")
        else:
            command = reparse(message.text)[0]
            handle = reparse(message.text)[1]
            if command == "/rating":
                bot.send_message(message.from_user.id, get_rating(handle))
            elif command == "/game":
                bot.send_message(message.from_user.id, last_game_pgn(handle))
            elif command == "/status":
                bot.send_message(message.from_user.id, online_status(handle))
            elif command == "/link":
                bot.send_message(message.from_user.id, last_game_link(handle))
            elif command == "/gif":
                # print(type(gif(handle)))
                bot.send_message(message.from_user.id, gif(handle))
            elif command == "/info":
                bot.send_message(message.from_user.id, all_info(handle))
            elif command == "/top":
                bot.send_message(message.from_user.id, get_top_10(reparse(message.text)))
            else:
                bot.send_message(message.from_user.id, "Incorrect command!")
    text = message.from_user.first_name + ' [' + str(message.from_user.id) + ']: ' + str(message.text)
    if LOGGER_ID != None:
        bot.send_message(LOGGER_ID, text)


bot.polling(none_stop=True, interval=0)
