#!/usr/bin/python3

import curses
import curses.panel
from time import sleep
from threading import Thread
RUN_UPDATE_WINDOW_THREAD = False
RUN_UPDATE_NUMBER_THREAD = False
COUNT_PER_MILLISECOND = 1
COUNT = 0


def number_window_updater():
    with open("log", "w") as logfile:
        number_window = curses.newwin(5,10,2,2)
        number_panel = curses.panel.new_panel(number_window)
        count = COUNT
        while 1:
            if RUN_UPDATE_WINDOW_THREAD:
                sleep(0.001)
                if count != COUNT:
                    count = COUNT
                    number_panel.top()
                    number_window.addstr(1,1,str(count))
                    number_window.refresh()
                    curses.panel.update_panels()
            else:
                return


def change_count(value):
    global COUNT
    COUNT += value


def number_updater():
    while 1:
        if RUN_UPDATE_NUMBER_THREAD:
            sleep(0.001)
            change_count(COUNT_PER_MILLISECOND)
        else:
            return

def run_update_window_thread(arg):
    global RUN_UPDATE_WINDOW_THREAD
    RUN_UPDATE_WINDOW_THREAD = arg


def run_update_number_thread(arg):
    global RUN_UPDATE_NUMBER_THREAD
    RUN_UPDATE_NUMBER_THREAD = arg


def main(stdscr):
    curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.cbreak()  # No need for [Return]
    curses.noecho()  # Stop keys being printed
    curses.curs_set(0)  # Invisible cursor
    stdscr.keypad(True)
    stdscr.clear()
    curses.panel.update_panels()
    
    run_update_window_thread(True)
    update_window_thread = Thread(target = number_window_updater)
    update_window_thread.start()

    run_update_number_thread(True)
    update_number_thread = Thread(target = number_updater)
    update_number_thread.start()

    stdscr.addstr(5,10,"Press Q to exit.")

    while True:
        key = stdscr.getkey()
        if key == "q":
            run_update_window_thread(False)
            run_update_number_thread(False)
            sleep(0.01)
            quit()
        elif key == " ":
            change_count(10000)


curses.wrapper(main)