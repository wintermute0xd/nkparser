import tkinter as tk

import nkparserGUI as gui


def main():
    root = tk.Tk()
    app = gui.MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
