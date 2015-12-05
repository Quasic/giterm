#!/usr/bin/env python
# -*- coding: utf-8 -*-
import curses

import watch
from gui import GitermPanelManager


def keyloop(stdscr):
    panels = GitermPanelManager(stdscr)
    active = panels['log'].activate()
    panels.display()

    w = watch.Watcher()
    for name, panel in panels.iteritems():
        w.event_handler.subscribe(panel.handle_event)

    # Initialize contents
    w.event_handler.fire()
    panels['changes'].request_diff_in_diff_view()

    w.start()

    while True:
        c = stdscr.getch()
        if 0 < c < 256:
            c = chr(c)
            if c in ' \n':  # 'SPACE BAR' or 'ENTER' hit
                active.select()
            elif c in 'Qq':
                break
            elif c == '\t':
                active = panels.toggle()
        elif c == curses.KEY_BTAB:
            active = panels.toggle(reverse=True)
        elif c == curses.KEY_UP:
            active.move_up()
        elif c == curses.KEY_LEFT:
            active.move_left()
        elif c == curses.KEY_DOWN:
            active.move_down()
        elif c == curses.KEY_RIGHT:
            active.move_right()
        elif c == curses.KEY_RESIZE:
            pass  # TODO: handle terminal resize properly (downsize and upsize)
        else:
            pass

    w.stop()


def main(stdscr):
    keyloop(stdscr)


if __name__ == '__main__':
    curses.wrapper(main)
