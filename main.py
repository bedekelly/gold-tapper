#!/usr/bin/python3
"""
|=====================================|
| Gold Tapper -- Workin' all day long |
|=====================================|

Copyright © 2014 Bede Kelly <bedekelly@mail.com>
This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See the COPYING file for more details.

"""

import curses
import curses.panel
from time import sleep, gmtime, strftime
import threading
from threading import Thread
from collections import namedtuple
ShopItem = namedtuple("ShopItem", ["name", "price", "quantity"])



class Shop(object):
    def __init__(self, item_prices):
        pass



class Credits(object):
    def __init__(self, stdscr):
        try:
            self.text = open("credits", "r").readlines()
        except FileNotFoundError:
            file_not_found(stdscr)
        self.indent = 5  # columns
        self.start_line = 5  # rows

    def display(self, stdscr):
        stdscr.clear()
        for index, line in enumerate(self.text):
            stdscr.addstr(index + self.start_line, self.indent, line)
        stdscr.border(0)
        stdscr.refresh()
        stdscr.getkey()


class Refresher(object):
    def __init__(self):
        self.keep_updating = True
    def refresher(self):
        while self.keep_updating:
            sleep(0.01)
            curses.panel.update_panels()
    def start_refreshing(self):
        refresh_thread = Thread(target = self.refresher)
        refresh_thread.start()
    def stop_refreshing(self):
        self.keep_updating = False


class Menu(object):
    def __init__(self, headline, CENTER, indent=0):
        self.headline = headline
        self.list_items = []
        self.headline_xpos = get_horizontal_position(headline, CENTER)
        self.headline_ypos = CENTER.y_coordinate - 3
        self.indent = indent

    def print_all(self, stdscr, CENTER):
        stdscr.addstr(self.headline_ypos, self.headline_xpos,
            self.headline)
        for index, item in enumerate(self.list_items):
            item_hpos = get_horizontal_position(item.text, CENTER)
            stdscr.addstr(self.headline_ypos + index + 2, item_hpos,
                          item.text, curses.A_REVERSE if item.selected
                          else curses.A_NORMAL)
        stdscr.border(0)
        stdscr.refresh()

    class MenuItem:
        def __init__(self, text, func=None):
            self.text = text
            self.selected = False
            self.func = func
        def select(self):
            self.selected = True
        def deselect(self):
            self.selected = False
        def __call__(self, stdscr, CENTER):
            if self.func is not None:
                self.func(stdscr, CENTER)
        def __str__(self):
            return self.text


class Accumulator(object):
    def __init__(self, value=0, incr_value=0, update_interval=0.01,
    run_update=True):
        self.value = value
        self.incr_value = incr_value
        self.update_interval = update_interval
        self.run_update = run_update

    def change_incr_value(self, value):
        self.incr_value = value

    def add(self, value):
        self.value += value

    def start_updating(self, object_to_update):
        thread = Thread(target = self.updater, args=(object_to_update,))
        thread.start()


    def updater(self, object_to_update):
        while self.run_update:
            sleep(self.update_interval)
            self.value += self.incr_value
            if round(object_to_update.value) != round(self.value):
                object_to_update.update_value(self.value)

    def stop_updating(self):
        self.run_update = False

    def __cmp__(self, other):
        if self.value < other:
            return -1
        elif self.value > other:
            return 1
        elif self.value == other:
            return 0

    def __str__(self):
        return str(self.value)


class HUDPanel(object):
    def __init__(self, dimensions, init_value, unit_string, 
        incr_per_second, update_interval, accumulator, wait=0, color=0):
        self.window = curses.newwin(*dimensions)
        self.window.bkgd(' ', curses.color_pair(color))
        self.panel = curses.panel.new_panel(self.window)
        self.value = init_value
        self.unit_string = unit_string
        self.incr_per_second = incr_per_second
        self.update_interval = update_interval
        self.run_update = True
        self.needs_update = True
        self.accumulator = accumulator
        self.wait = wait
        self.window.border(0)

    def update_value(self, value):
        self.value = value
        self.needs_update = True

    def toggle_hidden(self):
        if self.panel.hidden():
            # log("attempting to show panel")
            self.panel.show()
            curses.panel.update_panels()
            curses.doupdate()
        else:
            # log("attempting to hide panel")
            self.panel.hide()
            curses.panel.update_panels()
            curses.doupdate()



    def updater(self):
        # self.window.clear()
        # self.window.addstr(2,2,"{}: {}".format(
        # self.unit_string, round(self.value)))
        # self.window.border(0)
        # self.window.refresh()
        while 1:
            if self.run_update:
                # curses.panel.update_panels()
                sleep(self.update_interval)
                if self.panel.hidden():
                    # log("Panel is hidden")
                    pass
                else:
                    # log("Panel is shown")
                    if self.needs_update:
                        sleep(self.wait)
                        self.window.clear()
                        self.window.addstr(2,2,"{}: {}".format(
                            self.unit_string, round(self.value)))
                        self.window.border(0)
                        self.window.refresh()
                        self.needs_update = False


            else:
                # log("Stopped updating window " + self.unit_string)
                return

    def start_updating(self):
        self.run_update = True
        thread = Thread(target = self.updater)
        thread.start()


    def stop_updating(self):
        self.run_update = False


class MainPanel(object):
    def __init__(self, text, header, window):
        self.text = text
        self.window = window
        self.header = header
        self.window.border(0)
        self.window.bkgd(0)
        self.window.refresh()
    def update_text(text):
        self.text = text
        self.window.refresh()
    def display(self):
        for line in self.header:
            self.window.addstr(line)
        self.window.refresh()


def log(message):
    with open("log", "a") as logfile:
        logfile.write(str(message) + "\n")


def get_dimensions(item, stdscr, CENTER):
    if item == "gold":
        lines = 5
        columns = 25
        _, H_MAX = stdscr.getmaxyx()
        y = 1
        x = H_MAX - columns - 2

    elif item == "tapped":
        lines = 5
        columns = 25
        y = 1
        x = 2

    elif item == "shop":
        lines = 10
        columns = 30
        y = 1
        x = 1

    return lines, columns, y, x


def get_horizontal_position(text, CENTER):
    # Halfway across the stdscr, minus half the length of the text
    return CENTER.x_coordinate - len(text) // 2


def get_pos_consts(stdscr):
    """Make positional constants"""
    # Get maximum vertical and horizontal coords
    V_MAX, H_MAX = stdscr.getmaxyx()
    # Get halfway coords
    V_CENTER, H_CENTER = int(V_MAX // 2), int(H_MAX // 2)
    Coords = namedtuple("Center", ["y_coordinate", "x_coordinate"])
    CENTER = Coords(y_coordinate=V_CENTER, x_coordinate=H_CENTER)
    return CENTER


def setup_panels(stdscr, CENTER):
    panels_refresher = Refresher()
    panels_refresher.start_refreshing()
    gold = Accumulator(incr_value=0)
    tapped = Accumulator(incr_value=0)
    tapped_panel_data = {'dimensions': get_dimensions("tapped", stdscr, CENTER),
                         'init_value': 0,
                         'unit_string': "Total Tapped",
                         'incr_per_second': 0,
                         'update_interval': 0.01,
                         'accumulator': tapped,
                         'color': 1}
    gold_panel_data = {'dimensions': get_dimensions("gold", stdscr, CENTER),
                       'init_value': 0,
                       'unit_string': "Gold Nuggets",
                       'incr_per_second': 1,
                       'update_interval': 0.01,
                       'accumulator': gold,
                       'wait': 0.04,  # Stops curses having a cow
                       'color': 2}

    gold_panel = HUDPanel(**gold_panel_data)
    tapped_panel = HUDPanel(**tapped_panel_data)  
    tapped_panel.start_updating()
    gold_panel.start_updating()
    gold.start_updating(gold_panel)
    tapped.start_updating(tapped_panel)
    return tapped, gold, tapped_panel, gold_panel, panels_refresher


def buy_item(shop_items, menu_id, gold, current_items):
    menu_id -= 1  # Adjust for zero-indexed list.
    try:
        item = shop_items[menu_id]
    except IndexError:
        return shop_items, gold, current_items
    


    return shop_items, gold, current_items


def play_game(stdscr, CENTER):
    stdscr.clear()

    # Setup panels etc. 
    data = tuple(setup_panels(stdscr, CENTER))
    tapped, gold, tapped_panel, gold_panel, panels_refresher = data
    current_items = []  # list of strings for display

    # Setup shop
    shop_header = ["|------------------------------------------------|",
                   "|                      SHOP                      |",
                   "|------------------------------------------------|",
                   "|          Item          |         Price         |",
                   "|------------------------|-----------------------|"]
    x_coord = 0
    shop_items = [ShopItem("Newbie Dwarf", 50, 1)]
    for index, line in enumerate(shop_header):
        # Print centred header for shop
        stdscr.addstr(8 + index, CENTER.x_coordinate - len(line)//2, line)
        new_y = 8 + index
        if CENTER.x_coordinate - len(line) // 2 > x_coord:
            x_coord = CENTER.x_coordinate - len(line) // 2

    for index, item in enumerate(shop_items):
        # Ugly, but formats correctly for decent screen sizes.
        stdscr.addstr(new_y + index + len(shop_items), x_coord,
            "|     " 
            + (item.name + " ({})".format(item.quantity)).ljust(19)
            + "|"
            + str(item.price).center(23)
            + "|"
            )

    stdscr.border(0)
    stdscr.refresh()

    # Main input loop
    while True:
        key = stdscr.getkey()
        if key == "q":
            # Stop everything and quit
            gold_panel.stop_updating()
            gold_panel.panel.hide()
            tapped_panel.stop_updating()
            tapped_panel.panel.hide()
            gold.stop_updating()
            tapped.stop_updating()
            panels_refresher.stop_refreshing()
            stdscr.clear()
            sleep(.1)
            return
        elif key == "g":
            # Show/hide gold panel
            gold_panel.toggle_hidden()
            curses.panel.update_panels()
        elif key == "t":
            # Show/hide gold panel
            tapped_panel.toggle_hidden()
            curses.panel.update_panels()
        elif key == " ":
            # Increment gold on spacebar tap
            gold.add(1)
            tapped.add(1)
        # elif key == "b":
        #     if gold.value >= 10:
        #         gold.incr_value += 0.01
        #         gold.value -= 10
        elif key in "123456789":
            # Buy item from shop if player has gold
            shop_items, gold, current_items = buy_item(shop_items, int(key), gold, current_items)

        # Log current items each cycle
        try:
            log("Current items: [{}]".format(", ".join(current_items)))
        except TypeError:
            log("Current items: Empty")


def print_credits(stdscr):
    credits = Credits(stdscr)
    credits.display(stdscr)


def startup_menu(stdscr, CENTER):
    headline = "Gold Tapper --- Mining for Shineys"

    # Generate menu options
    menu = Menu(headline, CENTER, indent=4)
    menu.playgame = menu.MenuItem("Play Game", func=play_game)
    menu.credits = menu.MenuItem("Credits", func=print_credits)
    menu.exit = menu.MenuItem("Exit", func=quit)
    menu.list_items = [menu.playgame, menu.credits, menu.exit]

    # Select initial values
    current_item = 0
    menu.playgame.select()

    # Main menu loop
    while True:
        stdscr.clear()
        menu.print_all(stdscr, CENTER)
        given_key = stdscr.getkey()  # Get key input
        if given_key == "q":
            break  # Quit
        elif given_key == "KEY_DOWN":
            if current_item < len(menu.list_items) - 1:
                # Go down one item if you're not already at the bottom
                menu.list_items[current_item].deselect()
                current_item += 1
                menu.list_items[current_item].select()
        elif given_key == "KEY_UP":
            if current_item != 0:
                # Go up one item if you're not already at the top
                menu.list_items[current_item].deselect()
                current_item -= 1
                menu.list_items[current_item].select()
        elif given_key == "\n":
            # Menu item chosen by hitting Enter
            return menu.list_items[current_item]
    quit()


def setup_stdscr(stdscr):
    # Setup a window object, misc
    curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.cbreak()  # No need for [Return]
    curses.noecho()  # Stop keys being printed
    curses.curs_set(0)  # Invisible cursor
    stdscr.keypad(True)
    stdscr.clear()
    stdscr.border(0)

    # Setup color pairs
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    # Setup background
    stdscr.bkgd(' ', curses.color_pair(1))

    # Setup constants
    CENTER = get_pos_consts(stdscr)
    return stdscr, CENTER


def main(stdscr):
    log("\n===== Log from {} =====\n".format(
        strftime("%Y-%m-%d %H:%M:%S", gmtime())))

    # Get formatting right, and set up panels etc
    stdscr, CENTER = setup_stdscr(stdscr)
    while True:
        choice = startup_menu(stdscr, CENTER)
        if choice.func is not None:
            if choice.func == quit:
                quit()
            elif choice.func == print_credits:
                print_credits(stdscr)
            elif choice.func == play_game:
                play_game(stdscr, CENTER)
                stdscr.clear()
        else:
            quit()

if __name__ == "__main__":
    curses.wrapper(main)
    # General error trapping, won't destroy terminal if errors occur
    # (Apparently some errors still break everything, meh)
