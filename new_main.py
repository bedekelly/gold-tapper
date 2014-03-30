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


class HUDPanel:
    def __init__(self, dimensions, init_value, unit_string, incr_per_second,
    update_interval, hidden=True):
        self.window = curses.newwin(*dimensions)
        self.panel = curses.panel.new_panel(self.window)
        self.value = init_value
        self.unit_string = unit
        self.incr_per_second = incr_per_second
        self.update_interval = update_interval
        self.hidden = hidden
        self.window.border(0)

    def update_value(self, value):
        self.value += value
        self.needs_update = True

    def toggle_hidden(self):
        if self.panel.hidden:
            self.show()
        else:
            self.hide()

    def hide(self):
        self.panel.hide()

    def show(self):
        self.panel.show()

    def updater(self):
        while 1:
            if self.run_update:
                sleep(self.update_interval)
                if self.needs_update and not self.hidden:
                    self.window.clear()
                    self.window.addstr(2,2,self.unit 
                        + ": {}".format(self.value))
                    self.window.refresh()
                    self.needs_update = False
            else:
                return

    def start_updating(self):
        thread = Thread(target = self.updater)
        thread.start()

    def stop_updating(self):
        self.run_update = False



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


def setup_panels():
    tapped_panel_data = {dimensions: get_dimensions("tapped", stdscr),
                         init_value: 0,
                         unit_string: "Total Tapped",
                         incr_per_second: 0,
                         update_interval: 0.01,
                         hidden: False}
    gold_panel_data = {dimensions: get_dimensions("gold", stdscr),
                       init_value: 0,
                       unit_string: "Gold Pieces",
                       incr_per_second: 1,
                       update_interval: 0.01,
                       hidden: False}

    gold_panel = HUDPanel(**gold_panel_data)
    tapped_panel = HUDPanel(**tapped_panel_data)  
    tapped_panel.start_updating()
    gold_panel.start_updating()
    return tapped_panel, gold_panel


def play_game(stdscr):
    tapped_panel, gold_panel = setup_panels()
    while True:
        key = stdscr.getkey()
        if key == "q":
            gold_panel.stop_updating()
            tapped_panel.stop_updating()
            sleep(0.1)
            return
        elif key == "g":
            gold_panel.toggle_hidden()
        elif key == "t":
            tapped_panel.toggle_hidden()


def startup_menu(stdscr, CENTER):
    headline = "Gold Tapper --- Mining for Shineys"

    # Generate menu options
    menu = Menu(headline, CENTER, indent=4)
    menu.playgame = menu.MenuItem("Play Game", func=play_game)
    menu.credits = menu.MenuItem("Credits", func=self.display)
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
