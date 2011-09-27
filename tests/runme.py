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

import getopt
import logging
import sys
import test_occi_11

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

        frame = Frame(top)
        frame.grid(column=0, row=0, columnspan=2)

        text = Label(frame, text='OCCI service URL:')
        text.grid(column=0, row=0, **self.paddingArgs)

        # self.url.set('http://fjjutraa.joyent.us:8888')
        self.url.set('http://localhost:8888')
        entry = Entry(frame, width=25, textvariable=self.url)
        entry.grid(column=1, row=0, **self.paddingArgs)

        go = Button(frame, text='Go', command=self.run_tests)
        go.grid(column=2, row=0, **self.paddingArgs)

        reset = Button(frame, text='Reset', command=self.reset)
        reset.grid(column=3, row=0, **self.paddingArgs)

        #======================================================================
        # Test frame
        #======================================================================

        self.test_frame = LabelFrame(top, borderwidth=2, relief='groove',
                                     text='Tests')
        self.test_frame.grid(column=0, row=1, columnspan=2, **self.paddingArgs)

        i = 0
        for item in self._get_tests().keys():
            label = Label(self.test_frame, text=item)
            label.grid(column=0, row=i, sticky=W, **self.paddingArgs)

            label2 = Label(self.test_frame, text='...')
            label2.grid(column=1, row=i, sticky=N + E + W + S,
                        **self.paddingArgs)

            i += 1

        #======================================================================
        # Bottom
        #======================================================================

        note = 'NOTE: Passing all tests only indicates that the service\n \
                you are testing is OCCI compliant - IT DOES NOT GUARANTE IT!'

        label = Label(top, text=note)
        label.grid(column=0, row=2, columnspan=2, **self.paddingArgs)

        quit_button = Button(top, text='Quit', command=self.quit)
        quit_button.grid(column=1, row=3, sticky=E, **self.paddingArgs)

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
            except AttributeError as error:
                logging.error(error)
                label2 = Label(self.test_frame, text='Failed',
                               background='red')
                label2.grid(column=1, row=i, sticky=N + E + W + S,
                            **self.paddingArgs)

            i += 1

    def reset(self):
        self.test_frame.grid_columnconfigure(1, {'uniform': 100})

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
        print('you are testing is OCCI compliant - IT DOES NOT GUARANTE IT!\n')

        self.run_tests(url)

    def run_tests(self, url):
        '''
        Run all the tests.
        '''
        for item in dir(test_occi_11):
            if item.find('test_') != -1:
                # func = locals()[item]
                func = getattr(test_occi_11, item)

                try:
                    print("{0:80s} {1:6s}".format(func.__doc__.strip(),
                                                  func(url)))
                except AttributeError as error:
                    logging.error(error)
                    print("{0:80s} {1:6s}".format(func.__doc__.strip(),
                                                  'FAILED'))

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
            print ('Usage: test_occi.py url=<URL> or test_occi.py --gui')
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
