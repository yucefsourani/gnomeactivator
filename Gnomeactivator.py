#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Gnomeactivator.py
#  
#  Copyright 2021 yucef sourni <youssef.m.sourani@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk , GLib, Gio, GdkPixbuf
import dbus
import threading
import time

class CTextView():
    def __init__(self):
        self.sw = Gtk.ScrolledWindow()        
        self.t = Gtk.TextView()
        self.textviewbuffer          = self.t.get_buffer()
        self.t.props.editable        = False
        self.t.props.cursor_visible  = False
        self.t.props.justification   = Gtk.Justification.LEFT
        self.t.props.wrap_mode       = Gtk.WrapMode.CHAR
        self.sw.add(self.t)
        self.t.connect("size-allocate", self._autoscroll)
        
    def _autoscroll(self,widget,rec):
        adj = self.sw.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

    def insert_text(self,text):
        self.textviewbuffer.insert_at_cursor(text,len(text))
        
class GnomeShell(object):
    def __init__(self):
        self.__bus                    = dbus.SessionBus()
        self.__id                     = "org.gnome.Shell"
        self.__object                 = "/org/gnome/Shell"
        self.__interface_properties   = "org.freedesktop.DBus.Properties"
        self.__interface_extensions   = "org.gnome.Shell.Extensions"
        self.__proxy                  = self.__bus.get_object(self.__id,self.__object)
        self.__interface_p            = dbus.Interface(self.__proxy,self.__interface_properties)
        self.__interface_e            = dbus.Interface(self.__proxy,self.__interface_extensions)
        self.__settings = Gio.Settings(schema='org.gnome.shell')

    def version(self):
        return self.__interface_p.Get(self.__interface_extensions,"ShellVersion")
        
    def list_enabled_extensions(self):
        result = []
        for k,v in self.__interface_e.ListExtensions().items():
            if v["state"]==1.0:
                result.append(k)
        return result

    def disable_extensions(self,extensions):
        ex = self.__settings.get_strv("enabled-extensions")
        for extension in extensions:
            while extension  in ex:
                ex.remove(extension)
        self.__settings.set_strv("enabled-extensions", ex)
        
class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_size_request(300, 200)
        mainvbox = Gtk.VBox()
        mainvbox.props.margin = 10
        self.add(mainvbox)
        
        self.g_need_active = False
        self.gnomeshell    = GnomeShell()
        for extension in self.gnomeshell.list_enabled_extensions():
            if extension == "activate_gnome@isjerryxiao":
                self.g_need_active = True
            
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale("KMSPico1.png",100,100,True)
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        mainvbox.pack_start(image,False,False,1)

        self.button = Gtk.Button()
        self.button.get_style_context().add_class("destructive-action")
        if self.g_need_active:
            self.button.props.label = "Active Gnome!"
            
        else:
            self.button.props.label = "Gnome is activated"
        self.button.connect("clicked",self.active_gnome)
        mainvbox.pack_start(self.button,False,False,1)
        
        self.textview = CTextView()
        mainvbox.pack_start(self.textview.sw,True,True,1)

    def active_gnome(self,button):
        threading.Thread(target=self._active_gnome,args=(button,)).start()
        
    def _active_gnome(self,button):
        if not self.g_need_active:
            return
        self.g_need_active = False
        GLib.idle_add(self.textview.insert_text,"Please Wait")
        for i in range(30):
            GLib.idle_add(self.textview.insert_text,".")
            time.sleep(0.2)
        self.gnomeshell.disable_extensions(["activate_gnome@isjerryxiao"])
        GLib.idle_add(button.set_label,"Gnome is activated")
        GLib.idle_add(self.textview.insert_text,"\n\nDone.")

        
mainwindow = MainWindow()
mainwindow.connect("delete-event",Gtk.main_quit)
mainwindow.show_all()
Gtk.main()
