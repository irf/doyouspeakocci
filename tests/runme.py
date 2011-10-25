#!/usr/bin/env python
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

import getopt
import logging
import sys
import test_occi_11
from test_occi_11 import TestFailure
import textwrap

try:
    from Tkinter import Toplevel, Frame, LabelFrame, Label, StringVar, \
    IntVar, Button, Entry, Checkbutton, N, E, W, S, Tk, LEFT, FALSE
except ImportError:
    logging.warn("TK GUI will not be available...")

    class Toplevel(object):
        pass

'''
GUI and Text test runners...

Created on Apr 4, 2011

@author: tmetsch
'''


class TkRunner(Toplevel):

    info_text = None
    paddingArgs = {'padx': 3, 'pady': 3}

    def __init__(self, parent):
        '''
        Constructor.
        '''

        FORMAT = '%(message)s'
        logging.basicConfig(format=FORMAT, level=logging.DEBUG)

        Toplevel.__init__(self, parent)
        self.wm_withdraw()
        self.resizable(height=FALSE, width=FALSE)
        #self.wm_deiconify()

        self.url = StringVar()

        self.master = parent
        self.configure(borderwidth=5)
        self.init_gui()

    def init_gui(self):
        '''
        Initialize a simple gui.
        '''
        top = Frame(self.master)
        top.grid(**self.paddingArgs)

        #======================================================================
        # Top frame
        #======================================================================

        info_frame = Frame(top)
        info_frame.grid(column=0, row=0)

        text = Label(info_frame, text='OCCI service URL:')
        text.grid(column=0, row=0, **self.paddingArgs)

        # self.url.set('http://fjjutraa.joyent.us:8888')
        self.url.set('http://localhost:8888')
        entry = Entry(info_frame, width=25, textvariable=self.url)
        entry.grid(column=1, row=0, **self.paddingArgs)

        go = Button(info_frame, text='Go', command=self.run_tests)
        go.grid(column=2, row=0, **self.paddingArgs)

        reset = Button(info_frame, text='Reset', command=self.reset)
        reset.grid(column=3, row=0, **self.paddingArgs)

        #======================================================================
        # Test frame
        #======================================================================

        self.test_frame = LabelFrame(top, borderwidth=2, relief='groove',
                                     text='Tests')
        self.test_frame.grid(row=1, **self.paddingArgs)

        i = 0
        for item in self._get_tests().keys():
            label = Label(self.test_frame, text=item)
            label.grid(row=i, sticky=W, **self.paddingArgs)

            label2 = Label(self.test_frame, text='...')
            label2.grid(column=1, row=i, sticky=N + E + W + S,
                        **self.paddingArgs)

            i += 1

        #======================================================================
        # Bottom
        #======================================================================

        note = 'NOTE: Passing all tests only indicates that the service\n'
        note += 'you are testing is OCCI compliant - IT DOES NOT GUARANTEE IT!'

        label = Label(top, text=note)
        label.grid(row=2, **self.paddingArgs)

        quit_button = Button(top, text='Quit', command=self.quit)
        quit_button.grid(row=3, sticky=E, **self.paddingArgs)

    def run_tests(self):
        url = self.url.get()

        i = 0
        tests = self._get_tests()
        for item in tests.keys():
            func = tests[item]

            label = Label(self.test_frame, text=item)
            label.grid(column=0, row=i, sticky=W, **self.paddingArgs)

            try:
                label2 = Label(self.test_frame, text=func(url),
                               background='green')
                label2.grid(column=1, row=i, sticky=N + E + W + S,
                            **self.paddingArgs)
            except TestFailure as error:
                logging.error(error)
                label2 = Label(self.test_frame, text='Failed',
                               background='red')
                label2.grid(column=1, row=i, sticky=N + E + W + S,
                            **self.paddingArgs)

            i += 1

    def reset(self):
        i = 0
        for item in self._get_tests().keys():
            label = Label(self.test_frame, text=item)
            label.grid(column=0, row=i, sticky=W, **self.paddingArgs)

            label2 = Label(self.test_frame, text='...')
            label2.grid(column=1, row=i, sticky=N + E + W + S,
                        **self.paddingArgs)

            i += 1

    def _get_tests(self):
        '''
        Return with dict with test description and func
        '''
        res = {}
        for item in dir(test_occi_11):
            if item.find('test_') != -1:
                func = getattr(test_occi_11, item)
                desc = func.__doc__.strip()
                res[desc] = func
        return res


class TextRunner(object):

    def __init__(self, url):

        FORMAT = '%(message)s'
        logging.basicConfig(format=FORMAT, level=logging.DEBUG)

        print('\nExamining OCCI service at URL: ' + url)
        print('\nNOTE: Passing all tests only indicates that the service')
        print('you are testing is OCCI compliant - IT DOES NOT GUARANTEE IT!\n')

        self.run_tests(url)

        print('\n')

    def run_tests(self, url):
        '''
        Run all the tests.
        '''

        for item in dir(test_occi_11):
            if item.find('test_') != -1:
                func = getattr(test_occi_11, item)
                desc = textwrap.wrap(func.__doc__.strip(), width=90)

                try:
                    if len(desc) > 1:
                        for item in desc[0:len(desc) - 1]:
                            print item
                    result = func(url)
                    print('{0:90s} {1:6s}'.format(desc.pop(), result))
                except TestFailure as e:
                    if len(desc) > 1:
                        for item in desc[0:len(desc) - 1]:
                            print item
                    logging.error(e)
                    print("{0:90s} {1:6s}".format(desc.pop(), 'FAILED'))

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:v", ["help", "url=",
                                                          "gui"])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    use_gui = False
    url = 'http://localhost:8888'

    for o, a in opts:
        if o in ("-h", "--help"):
            print ('Usage: test_occi.py [--url=<URL>] or test_occi.py --gui')
            sys.exit()
        elif o in ("-u", "--url"):
            url = a
        elif o in ("--gui"):
            use_gui = True
        else:
            assert False, "unhandled option"

    if use_gui == False:
        TextRunner(url)
    else:
        root = Tk()
        root.title('OCCI compliance test')
        gui = TkRunner(root)
        root.mainloop()
