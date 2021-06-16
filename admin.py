# global variables
ADMIN_LIST = []
USERS_IN_BAN = []


def main(id, message):
    command = message.split()[0]
    if id in ADMIN_LIST:
        if command == "/ban":
            try:
                USERS_IN_BAN.append(int(message.split()[1]))
                return "Banned"
            except IndexError:
                return "Error"
            except ValueError:
                return "Write an ID"
        elif command == "/banlist":
            list = "List:\n"
            for i in USERS_IN_BAN:
                list += str(i) + '\n'
            return list
    else:
        return "No admins!"
