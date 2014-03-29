#!/usr/bin/python3
"""
|================================|
| Gold Clicker -- Text Edition   |
|================================|

Copyright © 2014 Bede Kelly <bedekelly@mail.com>
This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See the COPYING file for more details.

"""


import curses
import curses.panel
import time
from collections import namedtuple
GOLD_PIECES = 0
TAPPED_ITEMS = 0

class Credits:
    def __init__(self, screen):
        try:
            self.text = open("credits", "r").readlines()
        except FileNotFoundError:
            file_not_found(screen)
        self.indent = 5  # columns
        self.start_line = 5  # rows

    def display(self, screen):
        screen.clear()
        for index, line in enumerate(self.text):
            screen.addstr(index + self.start_line, self.indent, line)
        screen.border(0)
        screen.refresh()
        screen.getkey()


class Menu:
    def __init__(self, headline, CENTER, indent=0):
        self.headline = headline
        self.list_items = []
        self.headline_xpos = get_horizontal_position(headline, CENTER)
        self.headline_ypos = CENTER.y_coordinate - 3
        self.indent = indent

    def print_all(self, screen):
        screen.addstr(self.headline_ypos, self.headline_xpos, self.headline)
        for index, item in enumerate(self.list_items):
            screen.addstr(self.headline_ypos + index + 2, self.indent,
                          item.text, curses.A_REVERSE if item.selected
                          else curses.A_NORMAL)
        screen.border(0)
        screen.refresh()

    class MenuItem:
        def __init__(self, text, func=None):
            self.text = text
            self.selected = False
            self.func = func
        def select(self):
            self.selected = True
        def deselect(self):
            self.selected = False
        def __call__(self, screen, CENTER):
            if self.func is not None:
                self.func(screen, CENTER)
        def __str__(self):
            return self.text


def file_not_found(screen):
    screen.clear()
    screen.addstr(5, 5, "A critical file is missing. Please reinstall the "
                        "game.")
    screen.getkey()
    quit()


def print_credits(screen, _):
    credits = Credits(screen)
    credits.display(screen)


def get_dimensions(item, screen):
    if item == "gold":
        lines = 5
        columns = 20
        _, H_MAX = screen.getmaxyx()
        y = 1
        x = H_MAX - columns - 2

    elif item == "stats":
        lines = 10
        columns = 20
        y = 1
        x = 1

    return lines, columns, y, x

def display_gold_window(gold_window, gold_panel):
    gold_panel.show()
    gold_window.bkgd(' ', curses.color_pair(2))
    gold_window.clear()
    gold_window.addstr(1, 1, "Gold pieces: {}".format(GOLD_PIECES))
    gold_window.border(0)
    gold_window.refresh()


def display_stats_window(stats_window, stats_panel):
    stats_panel.show()
    stats_window.bkgd(' ', curses.color_pair(1))
    stats_window.clear()
    stats_window.addstr(1, 1, "Total tapped: {}".format(TAPPED_ITEMS))
    stats_window.border(0)
    stats_window.refresh()


def play_game(screen, CENTER):
    screen.clear()
    gold_window = curses.newwin(*get_dimensions("gold", screen))
    gold_panel = curses.panel.new_panel(gold_window)

    stats_window = curses.newwin(*get_dimensions("stats", screen))
    stats_panel = curses.panel.new_panel(stats_window)

    screen_panel = curses.panel.new_panel(screen)
    display_gold = False
    display_stats = False
    while True:
        screen_panel.bottom()
        if display_gold:
            display_gold_window(gold_window, gold_panel)
            # gold_panel.show()
            # gold_window.border(0)
            # gold_window.addstr(0,0,"Test gold window")
            # gold_window.refresh()
        else:
            gold_panel.hide()

        if display_stats:
            display_stats_window(stats_window, stats_panel)
            # stats_panel.show()
            # stats_window.border(0)
            # stats_window.addstr(0,0,"Test stats window")
            # stats_window.refresh()
        else:
            stats_panel.hide()
        curses.panel.update_panels()
        screen.refresh()
        key = screen.getkey()
        if key == "g":
            display_gold = not display_gold  # toggle
        elif key == "s":
            display_stats = not display_stats  # toggle
        elif key == "q":
            return


def get_horizontal_position(text, CENTER):
    # Halfway across the screen, minus half the length of the text
    return CENTER.x_coordinate - len(text) // 2


def get_pos_consts(screen):
    """Make positional constants"""
    # Get maximum vertical and horizontal coords
    V_MAX, H_MAX = screen.getmaxyx()
    # Get halfway coords
    V_CENTER, H_CENTER = int(V_MAX // 2), int(H_MAX // 2)
    Coords = namedtuple("Center", ["y_coordinate", "x_coordinate"])
    CENTER = Coords(y_coordinate=V_CENTER, x_coordinate=H_CENTER)
    return CENTER


def startup_menu(screen, CENTER):
    headline = "Cookie Clicker -- The REAL Text Version"

    # Generate menu options
    menu = Menu(headline, CENTER, indent=4)
    menu.playgame = menu.MenuItem("Play Game", func=play_game)
    menu.credits = menu.MenuItem("Credits", func=print_credits)
    menu.list_items = [menu.playgame, menu.credits]

    # Select initial values
    current_item = 0
    menu.playgame.select()

    # Main menu loop
    while True:
        screen.clear()
        menu.print_all(screen)
        given_key = screen.getkey()  # Get key input
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


def setup_screen(screen):
    # Setup a window object, misc
    curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.cbreak()  # No need for [Return]
    curses.noecho()  # Stop keys being printed
    curses.curs_set(0)  # Invisible cursor
    screen.keypad(True)
    screen.clear()
    screen.border(0)

    # Setup color pairs
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    # Setup background
    screen.bkgd(' ', curses.color_pair(1))

    # Setup constants
    CENTER = get_pos_consts(screen)
    return screen, CENTER

def main(screen):
    screen, CENTER = setup_screen(screen)
    # Execute
    while True:
        choice = startup_menu(screen, CENTER)
        if choice.func is not None:
            choice(screen, CENTER)


if __name__ == "__main__":
    curses.wrapper(main)
    # General error trapping, won't destroy terminal if errors occur
