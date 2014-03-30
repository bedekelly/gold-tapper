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
import time
import threading
from threading import Thread
from collections import namedtuple
GOLD_PIECES = 0
TAPPED_ITEMS = 0
GOLD_INCREMENT_VALUE = 1
GOLD_UPDATE_INTERVAL = 1  # second(s)


class Credits:
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


class Menu:
    def __init__(self, headline, CENTER, indent=0):
        self.headline = headline
        self.list_items = []
        self.headline_xpos = get_horizontal_position(headline, CENTER)
        self.headline_ypos = CENTER.y_coordinate - 3
        self.indent = indent

    def print_all(self, stdscr, CENTER):
        stdscr.addstr(self.headline_ypos, self.headline_xpos, self.headline)
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


class TaskThread:
    """Thread that executes a task every n seconds. Thanks to 
    Itamar Shtull-Trauring"""
    def __init__(self):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self._interval = GOLD_UPDATE_INTERVAL

    def set_interval(self, interval):
        self._interval = interval
    def shutdown(self):
        self._finished.set()
    def run(self, param):
        while True:
            if self._finished.isSet():
                return
            self.task(param)
            self._finished.wait(self._interval)
    def task(self):
        """The task performed by this thread -- override in subclasses."""
        pass


class GoldUpdater(TaskThread):
    def task(self, gold_panel):
        if not gold_panel.hidden():
            gold_window = gold_panel.window()
            gold_window.clear()
            gold_window.addstr(2, 3, "Gold pieces: {}".format(GOLD_PIECES))
            gold_window.refresh() 


def file_not_found(stdscr):
    stdscr.clear()
    stdscr.addstr(5, 5, "A critical file is missing. "
                        "Please reinstall the game.")
    stdscr.getkey()
    quit()


def print_credits(stdscr, _):
    credits = Credits(stdscr)
    credits.display(stdscr)


def get_dimensions(item, stdscr):
    if item == "gold":
        lines = 5
        columns = 20
        _, H_MAX = stdscr.getmaxyx()
        y = 1
        x = H_MAX - columns - 2

    elif item == "tapped":
        lines = 5
        columns = 21
        y = 1
        x = 2

    return lines, columns, y, x


def display_gold_window(gold_window, gold_panel):
    gold_panel.show()
    gold_window.bkgd(' ', curses.color_pair(2))
    gold_window.clear()
    gold_window.addstr(2, 3, "Gold pieces: {}".format(GOLD_PIECES))
    gold_window.border(0)
    gold_window.refresh()


def display_tapped_window(tapped_window, tapped_panel):
    tapped_panel.show()
    tapped_window.bkgd(' ', curses.color_pair(1))
    tapped_window.clear()
    tapped_window.addstr(2, 3, "Total tapped: {}".format(TAPPED_ITEMS))
    tapped_window.border(0)
    tapped_window.refresh()


def display_hud(stdscr, stdscr_panel, tapped_panel, gold_panel,
display_gold, display_tapped):
    gold_window = gold_panel.window()
    tapped_window = tapped_panel.window()
    if display_gold:
        display_gold_window(gold_window, gold_panel)
    else:
        gold_panel.hide()
    if display_tapped:
        display_tapped_window(tapped_window, tapped_panel)
    else:
        tapped_panel.hide()
    curses.panel.update_panels()
    stdscr.refresh()


# def update_gold_window(gold_window):
#     while True:
#         if not KILL_GOLD_UPDATE:
#             time.sleep(GOLD_UPDATE_INTERVAL)
#             gold_window.clear()
#             gold_window.addstr(2, 3, "Gold pieces: {}".format(GOLD_PIECES))
#             gold_window.refresh()
#         else:
#             return


def play_game(stdscr, CENTER):
    # Setup main screen
    stdscr.clear()
    stdscr.border(0)
    # Setup screen items
    gold_window = curses.newwin(*get_dimensions("gold", stdscr))
    gold_panel = curses.panel.new_panel(gold_window)
    tapped_window = curses.newwin(*get_dimensions("tapped", stdscr))
    tapped_panel = curses.panel.new_panel(tapped_window)
    stdscr_panel = curses.panel.new_panel(stdscr)
    # Panels hidden by default
    display_gold = False
    display_tapped = False

    # Setup gold to update every GOLD_UPDATE_INTERVAL seconds
    gold_window_updater = GoldUpdater()
    gold_window_updater.run(gold_panel)
    # Main input loop
    while True:
        hud_data = (stdscr_panel, tapped_panel, gold_panel,
                        display_gold, display_tapped)
        display_hud(stdscr, *hud_data)


        key = stdscr.getkey()
        if key == "g":
            display_gold = not display_gold  # toggle
        elif key == "t":
            display_tapped = not display_tapped  # toggle
        elif key == "p":
            GOLD_PIECES += 1
        elif key == "q":
            KILL_GOLD_UPDATE = True
            return


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
    stdscr, CENTER = setup_stdscr(stdscr)
    # Execute
    while True:
        choice = startup_menu(stdscr, CENTER)
        if choice.func is not None:
            if choice.func != quit:
                choice(stdscr, CENTER)
            else:
                quit()
        else:
            quit()

if __name__ == "__main__":
    curses.wrapper(main)
    # General error trapping, won't destroy terminal if errors occur
