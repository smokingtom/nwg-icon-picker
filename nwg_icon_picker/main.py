#!/usr/bin/env python

"""
nwg-icon-picker is a simple GTK icon chooser with textual search capability.
Project: https://github.com/nwg-piotr/nwg-icon-chooser
Author's email: nwg.piotr@gmail.com
Copyright (c) 2022 Piotr Miller
Copyright (c) 2026 smokingtom
License: MIT


"""

import argparse
import sys

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk, GLib

from nwg_icon_picker.__about__ import __version__

gtk_theme_name = ""
gtk_icon_theme = None
search_entry = None
icon_info = None
btn_height = 0

result_wrapper_box = None
icon_names = []
result_scrolled_window = None

icon_path = ""


def choose_icon(btn):
    if icon_path:
        print(icon_path, flush=True)

    Gtk.main_quit()


def cancel_picker(btn):
    Gtk.main_quit()


def on_search_changed(sb):
    global result_scrolled_window

    phrase = sb.get_text()

    if phrase and len(phrase) > 2:
        if result_scrolled_window:
            result_scrolled_window.destroy()

        scrolled_window = Gtk.ScrolledWindow.new(None, None)
        scrolled_window.set_propagate_natural_width(True)
        scrolled_window.set_propagate_natural_height(True)

        result_scrolled_window = scrolled_window
        result_wrapper_box.pack_start(scrolled_window, True, True, 0)

        lb = Gtk.ListBox.new()
        scrolled_window.add(lb)

        for name in icon_names:
            if phrase in name:
                row = IconListRow(name)
                lb.add(row)

        result_wrapper_box.show_all()
    else:
        if result_scrolled_window:
            result_scrolled_window.destroy()


class IconListRow(Gtk.ListBoxRow):
    def __init__(self, name):
        super().__init__()

        self.connect("focus-in-event", update_info, name)
        self.connect("activate", on_row_activate, name)

        eb = Gtk.EventBox.new()
        self.add(eb)

        eb.connect("button-press-event", update_info, name)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        eb.add(box)

        pixbuf = gtk_icon_theme.load_icon(
            name,
            24,
            Gtk.IconLookupFlags.FORCE_SIZE |
            Gtk.IconLookupFlags.GENERIC_FALLBACK |
            Gtk.IconLookupFlags.USE_BUILTIN
        )

        img = Gtk.Image.new_from_pixbuf(pixbuf)
        box.pack_start(img, False, False, 6)

        lbl = Gtk.Label.new(name)
        box.pack_start(lbl, False, False, 0)


def update_info(ebox, ebtn, name):
    global icon_info
    icon_info.update(name)


class IconInfo(Gtk.Box):
    def __init__(self, name):
        super().__init__()

        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.name = name

        self.button = Gtk.Button()
        self.button.set_always_show_image(True)
        self.button.set_image_position(Gtk.PositionType.TOP)
        self.button.set_label(name)
        self.button.set_tooltip_text("Click to choose this icon")
        self.pack_start(self.button, False, False, 0)

        self.button.connect("clicked", choose_icon)

        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        self.pack_start(hbox, False, False, 6)

        self.lbl_filename = Gtk.Label()
        self.lbl_filename.set_line_wrap(True)
        self.lbl_filename.set_selectable(True)
        hbox.pack_start(self.lbl_filename, True, False, 0)

        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        self.pack_start(button_box, False, False, 6)

        self.btn_choose = Gtk.Button.new_with_label("Choose")
        self.btn_choose.set_tooltip_text("Choose this icon")
        self.btn_choose.connect("clicked", choose_icon)
        button_box.pack_start(self.btn_choose, True, True, 0)

        self.btn_cancel = Gtk.Button.new_with_label("Cancel")
        self.btn_cancel.set_tooltip_text("Cancel icon selection")
        self.btn_cancel.connect("clicked", cancel_picker)
        button_box.pack_start(self.btn_cancel, True, True, 0)

        self.update(name)

    def update(self, name):
        info = gtk_icon_theme.lookup_icon(name, 96, 0)

        global icon_path

        if info:
            icon_path = info.get_filename()
            self.lbl_filename.set_text(icon_path)
        else:
            icon_path = ""
            self.lbl_filename.set_text("")

        img = Gtk.Image.new_from_icon_name(name, Gtk.IconSize.DIALOG)
        self.button.set_image(img)
        self.button.set_label(name)

        global btn_height

        if btn_height > 0:
            self.button.set_size_request(0, btn_height)


def on_row_activate(row, name):
    icon_info.update(name)


def handle_keyboard(window, event):
    if event.type == Gdk.EventType.KEY_RELEASE:
        phrase = search_entry.get_text()

        if event.keyval == Gdk.KEY_Escape:
            if len(phrase) > 0:
                search_entry.grab_focus()
                search_entry.set_text("")
            else:
                Gtk.main_quit()

        elif event.keyval == Gdk.KEY_BackSpace and not search_entry.is_focus():
            search_entry.set_text(phrase[:-1])
            search_entry.grab_focus_without_selecting()
            search_entry.set_position(len(phrase) - 1)


def main():
    GLib.set_prgname('Choose Icon')

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s version {}".format(__version__),
        help="display version information"
    )

    parser.parse_args()

    global gtk_theme_name
    global gtk_icon_theme
    global icon_names
    global icon_info
    global search_entry
    global result_wrapper_box

    window = Gtk.Window()
    window.connect("destroy", Gtk.main_quit)
    window.connect("key-release-event", handle_keyboard)

    gtk_settings = Gtk.Settings.get_default()

    gtk_theme_name = gtk_settings.get_property("gtk-icon-theme-name")
    gtk_icon_theme = Gtk.IconTheme.get_default()

    icon_names = gtk_icon_theme.list_icons()

    print(
        "Found {} icons".format(len(icon_names)),
        file=sys.stderr
    )

    icon_names.sort(key=str.casefold)

    hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
    hbox.set_property("margin", 6)
    window.add(hbox)
    window.set_resizable(False)

    vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
    hbox.pack_start(vbox, True, True, 0)

    icon_info = IconInfo("nwg-icon-picker")
    vbox.pack_start(icon_info, False, False, 0)

    search_entry = Gtk.SearchEntry()
    search_entry.connect("search-changed", on_search_changed)
    vbox.pack_start(search_entry, False, False, 0)

    result_wrapper_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
    vbox.pack_start(result_wrapper_box, False, False, 0)

    window.show_all()

    search_entry.grab_focus()

    global btn_height
    btn_height = icon_info.button.get_allocated_height()

    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
