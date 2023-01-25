from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import json

collections = []


def save_collections():
    json_object = json.dumps(collections)
    with open('main_save.json', 'w') as outfile:
        outfile.write(json_object)


class Collectible:
    def __init__(self, name, image_loc):
        self.name = name
        self.image_loc = image_loc
        self.photo = None
        self.items = []


class Item:
    def __init__(self, name, description, value=0):
        self.name = name
        self.description = description
        self.value = value


class StartGUI(Tk):
    def __init__(self):
        Tk.__init__(self)
        self._current_frame = None
        self.geometry('800x600')
        self.change_frame(Launch)

    def change_frame(self, frame_class):
        """Changes to the passed frame and hides the current frame."""
        next_frame = frame_class(self)
        if self._current_frame is not None:
            self._current_frame.destroy()
        self._current_frame = next_frame
        self._current_frame.grid()


class Launch(Frame):
    def __init__(self, parent):
        # Launch frame
        Frame.__init__(self, parent)
        Frame(parent, borderwidth=5, relief="groove", width=800, height=600)

        Label(self, text='This is the home screen').grid(row=0, column=1, padx=5, pady=5)
        # Button(self, text='View Collections', command=lambda: parent.change_frame(Collection)).grid(row=0, column=0)
        Button(self, text='Exit', command=parent.destroy).grid(row=9, column=0)
        collectible_frame = Frame(self, borderwidth=5, relief='flat')
        collectible_frame.grid(row=1, column=2, columnspan=8)
        for collectible in collections:
            collectible.photo = ImageTk.PhotoImage(Image.open(collectible.image_loc).resize((100, 100)))
            Button(collectible_frame, text=collections[0].name, image=collectible.photo, compound=TOP,
                   command=lambda: parent.change_frame(Collection)).pack(side=RIGHT)


class Collection(Frame):
    def __init__(self, parent, ):
        # Collection frame
        Frame.__init__(self, parent)

        Label(self, text='This is the collection view').grid(row=0, column=1, padx=5, pady=5)
        Button(self, text='Go to launch page', command=lambda: parent.change_frame(Launch)).grid(row=0, column=0)


if __name__ == '__main__':
    collections.append(Collectible('DVDs', 'images/dvd.jpg'))
    collections.append(Collectible('Board Games', 'images/catan.jpg'))
    collections.append(Collectible('Beanie Babies', 'images/beanie.jpg'))
    gui = StartGUI()

    gui.mainloop()
