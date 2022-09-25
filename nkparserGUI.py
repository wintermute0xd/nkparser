import tkinter as tk
import tkinter.messagebox
import pyperclip
import os
import subprocess

from nkparser import MyParser


class MainWindow:
    def __init__(self, root):
        # create main window
        self.root = root
        self.root.title('NK news parser')
        #self.root.geometry('660x720+500+200')
        self.root.resizable(False, True)
        # create 2 frames in main window
        self.topframe = tk.Frame(root)
        self.topframe.pack(side=tk.TOP, fill=tk.X)
        self.bottomframe = tk.Frame(root)
        self.bottomframe.pack(fill=tk.X)
        
        # topframe
        # start field
        self.start_label = tk.Label(self.topframe, text='Start', width=5, padx=3, pady=5, anchor='w',
                                    font=('Helvetica', 12))
        self.start_label.grid(row=0, column=0, sticky=tk.W)
        # set default value for start field
        self.def_start_value = tk.StringVar()
        self.def_start_value.set('1')
        self.start_entry = tk.Entry(self.topframe, width=3, font=('Helvetica', 11), textvariable=self.def_start_value)
        self.start_entry.grid(row=0, column=1, sticky=tk.W)
        self.start_entry.focus_set()

        # main img size field
        self.m_imgsize_label = tk.Label(self.topframe, text='Main Img Size:', width=10, anchor='w',
                                    font=('Helvetica', 11))
        self.m_imgsize_label.grid(row=0, column=1, sticky=tk.W, padx=(35, 0))
        # set default value for main img size field
        self.def_m_imgsize_value = tk.StringVar()
        self.def_m_imgsize_value.set('500')
        self.m_imgsize_entry = tk.Entry(self.topframe, width=5, font=('Helvetica', 11), textvariable=self.def_m_imgsize_value)
        self.m_imgsize_entry.grid(row=0, column=1, sticky=tk.W, padx=(135,0))

        # img size field
        self.imgsize_label = tk.Label(self.topframe, text='Img Size:', width=8, anchor='w',
                                    font=('Helvetica', 11))
        self.imgsize_label.grid(row=0, column=1, sticky=tk.W, padx=(190, 0))
        # set default value for img size field
        self.def_imgsize_value = tk.StringVar()
        self.def_imgsize_value.set('800')
        self.imgsize_entry = tk.Entry(self.topframe, width=5, font=('Helvetica', 11), textvariable=self.def_imgsize_value)
        self.imgsize_entry.grid(row=0, column=1, sticky=tk.W, padx=(255,0))

        # radiobutton
        self.source_rb_var = tk.IntVar()
        self.source_rb_var.set(0)
        self.source_rb_nko = tk.Radiobutton(self.topframe, text='nk-online', variable=self.source_rb_var, value=0,
                                            font=('Helvetica', 12))
        self.source_rb_nko.grid(row=0, column=1, sticky=tk.E, padx=(0, 60))
        # self.source_rb_rad = tk.Radiobutton(self.topframe, text='radio', variable=self.source_rb_var, value=1,
        #                                     font=('Helvetica', 12))
        # self.source_rb_rad.grid(row=0, column=1, sticky=tk.W, padx=(170, 0))

        # newsite checkbox
        self.chbx_var = tk.IntVar()
        self.chbx_new = tk.Checkbutton(self.topframe, text='New', variable=self.chbx_var, onvalue=1, offvalue=0,
                                       font=('Helvetica', 12))
        self.chbx_new.grid(row=0, column=1, sticky=tk.E)
        self.chbx_new.select()

        # url field
        self.url_label = tk.Label(self.topframe, text='URL', padx=3, pady=5, anchor='w', font=('Helvetica', 12))
        self.url_label.grid(row=1, column=0, sticky=tk.W)
        self.url_entry = tk.Entry(self.topframe, width=73, font=('Helvetica', 11))
        self.url_entry.grid(row=1, column=1, sticky=tk.W)
        # button
        self.get_button = tk.Button(self.topframe, text='Get', command=self.do_pars, width=10,
                                    font=('Helvetica', 12))
        self.get_button.grid(row=2, column=1, pady=(5, 5))

        # bottomframe
        # Title textfield
        self.title_label = tk.Label(self.bottomframe, text='Title', width=5, padx=3, anchor='w',
                                    font=('Helvetica', 12))
        self.title_label.grid(row=0, column=0, sticky=tk.W)
        self.title_text_field = tk.Text(self.bottomframe, wrap=tk.WORD, height=3, width=73, font=('Helvetica', 11))
        self.title_text_field.grid(row=0, column=1, sticky=tk.W)

        # Main textfield with scrollbars
        self.main_text_label = tk.Label(self.bottomframe, text='Text', width=5, padx=3, anchor='w',
                                        font=('Helvetica', 12))
        self.main_text_label.grid(row=2, column=0, sticky=tk.W)
        self.v_scroll = tk.Scrollbar(self.bottomframe)
        self.v_scroll.grid(row=2, column=2, sticky=tk.N + tk.S + tk.W)
        self.main_text_field = tk.Text(self.bottomframe, wrap=tk.WORD, height=30, width=73, font=('Helvetica', 11),
                                       yscrollcommand=self.v_scroll.set)
        self.main_text_field.grid(row=2, column=1, sticky=tk.W)
        self.v_scroll.config(command=self.main_text_field.yview)
        # buttons
        self.copy_title_button = tk.Button(self.bottomframe, text='Copy Title', command=self.title_to_clipboard,
                                           width=10, font=('Helvetica', 12))
        self.copy_title_button.grid(row=1, column=1, pady=(5, 5))

        self.copy_text_button = tk.Button(self.bottomframe, text='Copy Text', command=self.text_to_clipboard,
                                          width=10, font=('Helvetica', 12))
        self.copy_text_button.grid(row=3, column=1, pady=(5, 0))

        self.quit_button = tk.Button(self.bottomframe, text='Exit', command=self.quit, width=10, font=('Helvetica', 12))
        self.quit_button.grid(row=4, column=1, sticky=tk.W, pady=(5, 5))

        self.open_dir_button = tk.Button(self.bottomframe, text='Open images dir', command=self.open_img_dir,
                                         width=15, font=('Helvetica', 12))
        self.open_dir_button.grid(row=4, column=1, sticky=tk.E, pady=(5, 5))
        # init menu bar
        self.init_menubar()

    # menu bar
    def init_menubar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0, font=('Helvetica', 10))
        file_menu.add_command(label='Exit', command=self.quit)
        menubar.add_cascade(label='File', menu=file_menu)

        command_menu = tk.Menu(menubar, tearoff=0, font=('Helvetica', 10))
        command_menu.add_command(label='Get', command=self.do_pars)
        command_menu.add_command(label='Copy Title', command=self.title_to_clipboard)
        command_menu.add_command(label='Copy Text', command=self.text_to_clipboard)
        command_menu.add_command(label='Open images dir', command=self.open_img_dir)
        command_menu.add_command(label='Paste in URL', command=lambda:self.url_entry.insert(tk.END,pyperclip.paste()))
        menubar.add_cascade(label='Commands', menu=command_menu)

    # button's functions
    def do_pars(self):
        try:
            start_value = int(self.start_entry.get())
            assert(start_value >= 1), '"Start" must be >= 1'
        except ValueError as e:
            tk.messagebox.showerror('Value Error', str(e)+'\n\n"Start" must be a number')
        except AssertionError as e:
            tk.messagebox.showerror('Value Error', str(e))
            # dirty hack to make program stop
            raise Exception

        try:
            m_imgsize_value = int(self.m_imgsize_entry.get())
            assert(m_imgsize_value >= 0), '"Main Img Size" must be >= 0'
        except ValueError as e:
            tk.messagebox.showerror('Value Error', str(e)+'\n\n"Main Img Size" must be a number')
        except AssertionError as e:
            tk.messagebox.showerror('Value Error', str(e))
            raise Exception

        try:
            imgsize_value = int(self.imgsize_entry.get())
            assert(imgsize_value >= 0), '"Img Size" must be >= 0'
        except ValueError as e:
            tk.messagebox.showerror('Value Error', str(e)+'\n\n"Img Size" must be a number')
        except AssertionError as e:
            tk.messagebox.showerror('Value Error', str(e))
            raise Exception

        url_value = self.url_entry.get()
        source_rb_value = self.source_rb_var.get()
        chbx_value = self.chbx_var.get()
        parser = MyParser(url_value, start_value, source_rb_value, chbx_value, imgsize_value, m_imgsize_value)

        title = parser.get_title()
        article = parser.get_article()
        img_links = parser.get_images()
        author = parser.get_author()
        videos = parser.get_video()

        self.main_text_field.delete('1.0', tk.END)
        self.main_text_field.insert(tk.END, article + videos + author)  # + img_links
        self.title_text_field.delete('1.0', tk.END)
        self.title_text_field.insert(tk.END, title)

    def title_to_clipboard(self):
        text = self.title_text_field.get('1.0', tk.END)
        pyperclip.copy(text)

    def text_to_clipboard(self):
        pyperclip.copy(self.main_text_field.get('1.0', tk.END))

    def quit(self):
        self.root.destroy()

    def open_img_dir(self):
        img_dir = os.getcwd() + '\\downloads'
        if not os.path.exists(img_dir):
            tk.messagebox.showerror('Directory does not exist',
                                    'Directory ' + img_dir + ' does not exist.'
                                    'Run parsing process and it will be created automatically')
        else:
            command = 'explorer ' + '"' + img_dir + '"'
            subprocess.Popen(command)

