import sqlite3
import re

conn = sqlite3.connect('ships.db')
c = conn.cursor()

# TODO: in the future if the database is larger (about 50 entries), replace linear search with binary search


def create_tables():    # should only run once, run this manually if initializing database
    c.execute("CREATE TABLE IF NOT EXISTS shipTable(name TEXT, faction TEXT, score TEXT, cost TEXT, user TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS factionAccount(name TEXT, balance TEXT, ceo TEXT, score INTEGER)")


def data_entry(name, faction, score, cost, user):
    cost = re.sub('[^0-9]', '', cost)   # use regex to remove non-numerical characters from string

    c.execute('INSERT INTO shipTable(name, faction, score, cost, user) VALUES (?, ?, ?, ?, ?)',
              (name, faction, score, cost, user))
    conn.commit()


def new_faction(faction_name, ceo_id):
    STARTING_BALANCE = 10000
    c.execute('INSERT INTO factionAccount(name, balance, ceo, score) VALUES (?, ?, ?, ?)',
              (faction_name, STARTING_BALANCE, ceo_id, 0))
    conn.commit


def get_factions():
    c.execute("SELECT * FROM factionAccount")
    menu = ":crossed_swords:  **All factions (use `c!faction [faction]` to see more): **\n\n"
    menulist = list()
    count = 1

    for row in c.fetchall():
        menulist.append(f"{count}. {row[0]}\n")     # travel through database and add each ship to the menu
        count = count + 1

    for i in menulist:
        menu = menu + i

    return menu


def get_faction(name):
    c.execute("SELECT * FROM factionAccount")
    faction = "Not Found"       # TODO: actually do stuff when "Not Found" is returned (error message)

    for row in c.fetchall():
        if name.lower() == row[0].lower():
            faction = [row[0], row[1], row[2], row[3]]     # return faction tuple of [name, balance, ceo, battle_score]
    return faction


def update_balance(faction, amount):
    c.execute('SELECT * FROM factionAccount')
    search = "Not Found"
    for row in c.fetchall():
        name = row[0]

        if faction == name.lower():
            faction = row
            search = ""

    if search == "Not Found":
        return "Not Found"

    balance = int(faction[1]) + int(amount)
    balance = str(balance)
    c.execute('UPDATE factionAccount SET balance = (?) WHERE name = (?)', (balance, faction[0]))
    conn.commit()


def get_menu():
    c.execute("SELECT * FROM shipTable")
    menu = ":sailboat: **All ships (Use `c!ship [ship]` to learn more on a ship)**: \n\n"
    menulist = list()
    count = 1
    for row in c.fetchall():
        menulist.append(f"{count}. {row[0]}\n")
        count = count + 1

    for i in menulist:
        menu = menu + i

    return menu


def get_ship(name):
    c.execute('SELECT * FROM shipTable')
    ship = "Not found"
    for row in c.fetchall():
        if name.lower() == row[0].lower():
            ship = [row[0], row[1], row[2], row[3]]
    return ship


def get_edit_list(id):
    c.execute('SELECT * FROM shipTable')
    # all_ids = c.fetchall()
    editlist = list()
    editmenu = ""
    count = 1

    for row in c.fetchall():
        if id == int(row[4]):
            editlist.append(f"{count}. {row[0]}\n")

    for i in editlist:
        editmenu = editmenu + i
    if editmenu == "":
        return "You have no entries!"
    else:
        return editmenu


def edit_ship(user_id, ship, operation, new_part):
    c.execute('SELECT * FROM shipTable')

    entry = "Not Found"

    for row in c.fetchall():
        name = row[0]
        id = row[4]
        if ship.lower() == name.lower():
            if user_id == int(id):
                entry = row

    if entry == "Not Found":
        print("Not found")
        return "Not Found"

    if operation.lower() == "name":
        c.execute('UPDATE shipTable SET name = (?) WHERE name = (?)', (new_part, entry[0]))
    elif operation.lower() == "faction":
        c.execute('UPDATE shipTable SET faction = (?) WHERE name = (?)', (new_part, entry[0]))
    elif operation.lower() == "score":
        new_part = re.sub('[^0-9]', '', new_part)  # use regex to remove non-numerical characters from string

        if new_part == '':
            return "error"

        c.execute('UPDATE shipTable SET score = (?) WHERE name = (?)', (new_part, entry[0]))
    elif operation.lower() == "cost":
        new_part = re.sub('[^0-9]', '', new_part)

        if new_part == '':
            return "error"

        c.execute('UPDATE shipTable SET cost = (?) WHERE name = (?)', (new_part, entry[0]))

    conn.commit()


def delete_ship(ship, user_id):
    c.execute('SELECT * FROM shipTable')
    entry = "Not found"
    for row in c.fetchall():
        # print(row)
        id = row[4]
        if ship == row[0] and user_id == int(id):
            entry = row
    if entry == "Not found":
        return "Not found"
    else:
        name = entry[0]
        c.execute('DELETE FROM shipTable WHERE name = (?)', (name,))

    conn.commit()


def update_score(faction, amount):
    c.execute('SELECT * FROM factionAccount')
    search = "Not Found"
    for row in c.fetchall():
        name = row[0]
        # print(f"faction:{faction} name:{row[0]}")
        if faction == name.lower():
            faction = row
            search = ""

    if search == "Not Found":
        # print("Not found")
        return "Not Found"

    new_score = faction[3] + int(amount)
    # new_score = str(new_score)
    c.execute('UPDATE factionAccount SET score = (?) WHERE name = (?)', (new_score, faction[0]))
    conn.commit()


def reset_score():
    c.execute('SELECT * FROM factionAccount')
    c.execute('UPDATE factionAccount SET score = (?)', (0, ))
