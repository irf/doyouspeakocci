#!/usr/bin/python
# -*- coding: utf-8 -*-

# 
# Copyright (C) 2011 Platform Computing
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# 

from tests import test_occi
import logging

try:
    from Tkinter import Toplevel, Frame, LabelFrame, Label, StringVar, IntVar, Button, Entry, Checkbutton, \
    N, E, W, S, Tk, LEFT, FALSE
except ImportError:
    logging.warn("TK GUI will not be available...")
    exit(1)

'''
A GUI test runner...

Created on Apr 4, 2011

@author: tmetsch
'''
class GUIRunner(Toplevel):

    #===========================================================================
    # fields to set in the GUI
    #===========================================================================

    info_text = None
    paddingArgs = {'padx':3, 'pady':3}

    def __init__(self, parent):
        '''
        Constructor.
        '''
        Toplevel.__init__(self, parent)
        self.wm_withdraw()
        self.resizable(height = FALSE, width = FALSE)
        #self.wm_deiconify()

        self.url = StringVar()
        self.login = IntVar()
        self.user = StringVar()
        self.password = StringVar()

        self.master = parent
        self.configure(borderwidth = 5)
        self.init_gui()

    def init_gui(self):
        '''
        Initialize a simple gui.
        '''
        top = Frame(self.master)
        top.grid(**self.paddingArgs)

        frame = Frame(top)
        frame.grid(column = 0, row = 0, columnspan = 2)

        text = Label(frame, text = 'OCCI service URL:')
        text.grid(column = 0, row = 0, **self.paddingArgs)

        # self.url.set('http://fjjutraa.joyent.us:8888')
        self.url.set('http://localhost:8888')
        entry = Entry(frame, width = 25, textvariable = self.url)
        entry.grid(column = 1, row = 0, **self.paddingArgs)

        go = Button(frame, text = 'Go', command = self.run_tests)
        go.grid(column = 2, row = 0, **self.paddingArgs)

        reset = Button(frame, text = 'Reset', command = self.reset)
        reset.grid(column = 3, row = 0, **self.paddingArgs)

        login_frame = LabelFrame(top, borderwidth = 2, relief = 'groove', text = 'Session information')
        login_frame.grid(column = 0, row = 1, sticky = W + E + N + S,
                         padx = 2, pady = 2)

        self.login.set(1)

        login_switch = Checkbutton(login_frame, text = 'Login required?',
                                   variable = self.login)
        login_switch.grid(column = 0, row = 0, columnspan = 2, **self.paddingArgs)

        self.user.set('foo')
        self.password.set('bar')

        user_text = Label(login_frame, text = 'Username:')
        user_text.grid(column = 0, row = 1, sticky = W, **self.paddingArgs)
        user_entry = Entry(login_frame, textvariable = self.user, width = 15)
        user_entry.grid(column = 1, row = 1, **self.paddingArgs)

        text = Label(login_frame, text = 'Password:')
        text.grid(column = 0, row = 2, sticky = W, **self.paddingArgs)
        entry = Entry(login_frame, textvariable = self.password, width = 15,
                      show = "*")
        entry.grid(column = 1, row = 2, **self.paddingArgs)

        info_frame = LabelFrame(top, borderwidth = 2, relief = 'groove', text = 'Service information')
        info_frame.grid(column = 1, row = 1, sticky = W + E + N + S, **self.paddingArgs)

        self.info_text = Label(info_frame, text = 'Please press "GO"')
        self.info_text.pack(side = 'top')

        test_frame = LabelFrame(top, borderwidth = 2, relief = 'groove', text = 'Tests')
        test_frame.grid(column = 0, row = 2, columnspan = 2, **self.paddingArgs)

        label = Label(test_frame, text = 'Checking for correct version information:')
        label.grid(column = 0, row = 0, sticky = W, **self.paddingArgs)

        self.version_test_label = Label(test_frame, text = '...')
        self.version_test_label.grid(column = 1, row = 0, sticky = W, **self.paddingArgs)

        label = Label(test_frame, text = 'Checking completeness of infrastructure model:')
        label.grid(column = 0, row = 1, sticky = W, **self.paddingArgs)

        self.infra_model_test_label = Label(test_frame, text = '...')
        self.infra_model_test_label.grid(column = 1, row = 1, sticky = W, **self.paddingArgs)

        label = Label(test_frame, text = 'Checking correct handling of Content-type/Accept headers:')
        label.grid(column = 0, row = 2, sticky = W, **self.paddingArgs)

        self.accept_header_test_label = Label(test_frame, text = '...')
        self.accept_header_test_label.grid(column = 1, row = 2, sticky = W, **self.paddingArgs)

        label = Label(test_frame, text = 'Testing instantiation of compute/storage/network kinds:')
        label.grid(column = 0, row = 3, sticky = W, **self.paddingArgs)

        self.creational_test_label = Label(test_frame, text = '...')
        self.creational_test_label.grid(column = 1, row = 3, sticky = W, **self.paddingArgs)

        label = Label(test_frame, text = 'Testing correct handling of user-defined mixins (tagging/grouping):')
        label.grid(column = 0, row = 4, sticky = W, **self.paddingArgs)

        self.mixin_test_label = Label(test_frame, text = '...')
        self.mixin_test_label.grid(column = 1, row = 4, sticky = W, **self.paddingArgs)

        label = Label(test_frame, text = 'Testing links between compute/storage compute/network:')
        label.grid(column = 0, row = 5, sticky = W, **self.paddingArgs)

        self.link_test_label = Label(test_frame, text = '...')
        self.link_test_label.grid(column = 1, row = 5, sticky = W, **self.paddingArgs)

        label = Label(test_frame, text = 'Triggering actions on compute/network/storage kinds:')
        label.grid(column = 0, row = 6, sticky = W, **self.paddingArgs)

        self.action_test_label = Label(test_frame, text = '...')
        self.action_test_label.grid(column = 1, row = 6, sticky = W, **self.paddingArgs)

        label = Label(test_frame, text = 'Testing filter mechanisms using Categories:')
        label.grid(column = 0, row = 7, sticky = W, **self.paddingArgs)

        self.filter_test_label = Label(test_frame, text = '...')
        self.filter_test_label.grid(column = 1, row = 7, sticky = W, **self.paddingArgs)

        label = Label(test_frame, text = 'Testing correct behaviour on location and "normal" paths:')
        label.grid(column = 0, row = 8, sticky = W, **self.paddingArgs)

        self.location_path_label = Label(test_frame, text = '...')
        self.location_path_label.grid(column = 1, row = 8, sticky = W, **self.paddingArgs)

        label = Label(test_frame, text = 'Simple syntax checks:')
        label.grid(column = 0, row = 9, sticky = W, **self.paddingArgs)

        self.syntax_test_label = Label(test_frame, text = '...')
        self.syntax_test_label.grid(column = 1, row = 9, sticky = W, **self.paddingArgs)

        label = Label(top, text = 'NOTE: Passing all tests only indicates that the service\nyou are testing is OCCI compliant - IT DOES NOT GUARANTE IT!')
        label.grid(column = 0, row = 4, columnspan = 2, **self.paddingArgs)

        quit_button = Button(top, text = 'Quit', command = self.quit)
        quit_button.grid(column = 1, row = 5, sticky = E, **self.paddingArgs)

    def run_tests(self):
        '''
        run a set of tests.
        '''
        url = self.url.get()
        if self.login.get() is 1:
            cookie = test_occi.get_session_cookie(self.url.get(), self.user.get(),
                                        self.password.get())
            heads = {'Cookie': cookie}
        else:
            heads = {}

        # display basic information
        self.info_text.configure(text = 'Server version:\n'
                                    + test_occi.get_version(url, heads)
                                    + '\nNumber of registered categories:\n'
                                    + str(len(test_occi.get_categories(url, heads))),
                                    anchor = W, justify = LEFT)

        # run the tests...
        self.run_single_test(test_occi.test_version_information, url, heads, self.version_test_label)
        self.run_single_test(test_occi.test_infrastructure_model_for_completness, url, heads, self.infra_model_test_label)
        self.run_single_test(test_occi.test_accept_header, url, heads, self.accept_header_test_label)
        self.run_single_test(test_occi.test_create_kinds, url, heads, self.creational_test_label)
        self.run_single_test(test_occi.test_mixins, url, heads, self.mixin_test_label)
        self.run_single_test(test_occi.test_links, url, heads, self.link_test_label)
        self.run_single_test(test_occi.test_actions, url, heads, self.action_test_label)
        self.run_single_test(test_occi.test_filter, url, heads, self.filter_test_label)
        self.run_single_test(test_occi.test_location, url, heads, self.location_path_label)
        self.run_single_test(test_occi.test_syntax, url, heads, self.syntax_test_label)

    def run_single_test(self, test, url, heads, label):
        '''
        Run a single test and display the outcome.
        '''
        try:
            test(url, heads)
        except Exception as ae:
            logging.warn(str(ae))
            label.configure(text = 'Failed', background = 'red')
        else:
            label.configure(text = 'OK')

    def reset(self):
        '''
        Reset the gui...
        '''
        self.info_text.configure(text = 'Please press "GO"')
        self.version_test_label.configure(text = '...')
        self.infra_model_test_label.configure(text = '...')
        self.accept_header_test_label.configure(text = '...')
        self.creational_test_label.configure(text = '...')
        self.mixin_test_label.configure(text = '...')
        self.link_test_label.configure(text = '...')
        self.action_test_label.configure(text = '...')
        self.filter_test_label.configure(text = '...')
        self.location_path_label.configure(text = '...')
        self.syntax_test_label.configure(text = '...')

    def quit(self):
        '''
        Quit the master loop.
        '''
        self.master.quit()

if __name__ == '__main__':
    root = Tk()
    root.title('OCCI compliance test')
    gui = GUIRunner(root)
    root.mainloop()
