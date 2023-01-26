from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import json


class CollectiblesEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__


class CurrentSave:
    """Stores file save data, loads the main_save file, also saves and exits program"""

    def __init__(self):
        self.collections = []
        self.thumbnails = []

    def save_and_exit(self):
        json_object = json.dumps(self.collections, indent=4, cls=CollectiblesEncoder)
        with open('main_save.json', 'w') as outfile:
            outfile.write(json_object)
        gui.destroy()

    def load_save(self):
        with open('main_save.json', 'r') as openfile:
            parsed_json = json.load(openfile)
            self.collections = parsed_json


class Collectible:
    def __init__(self, name, image_loc):
        self.name = name
        self.image_loc = image_loc
        self.items = []


class Item:
    def __init__(self, name, description, value=0, image_loc='/images/default.jpg'):
        self.name = name
        self.description = description
        self.value = value
        self.image_loc = image_loc


class StartGUI(Tk):
    """Creates Tkinter root and starts the first frame which is the LaunchFrame"""

    def __init__(self):
        Tk.__init__(self)
        self._current_frame = None
        self.geometry('800x600')
        self.title('Collectibles Library')
        self.iconbitmap('crs.ico')
        self.change_frame(LaunchFrame)

    def change_frame(self, frame_class, *args):
        """Changes to the passed frame and hides the current frame."""
        next_frame = frame_class(self, *args)
        if self._current_frame is not None:
            self._current_frame.destroy()
        self._current_frame = next_frame
        self._current_frame.grid()


class LaunchFrame(Frame):
    """frame which program starts with to present all available collections"""

    def __init__(self, parent):
        # Launch frame
        Frame.__init__(self, parent)
        Frame(parent, borderwidth=5, relief="groove")

        current_category = "Your current collections: "
        Label(self, text=current_category, font=50).grid(row=1, column=2, padx=5, pady=5, columnspan=8, sticky=EW)

        # menu buttons
        menu_frame = Frame(self, borderwidth=5)
        menu_frame.grid(row=1, columns=1, rowspan=10)
        Button(menu_frame, text='Add Collection', width=15).grid(row=1, column=1)
        Button(menu_frame, text='Load User Backup', width=15).grid(row=2, column=1)
        Button(menu_frame, text='How to Info', width=15).grid(row=3, column=1)
        Button(menu_frame, text='Advanced', width=15).grid(row=4, column=1)
        Button(menu_frame, text='Save & Exit', width=15, command=main_save.save_and_exit).grid(row=5, column=1)

        # collectibles frame
        collectible_frame = Frame(self, borderwidth=5)
        collectible_frame.grid(row=2, column=2, columnspan=8, rowspan=8)
        index_counter = 0
        main_save.thumbnails = []
        for collectible in main_save.collections:
            photos = main_save.thumbnails
            photos.append(ImageTk.PhotoImage(Image.open(collectible['image_loc']).resize((100, 100))))
            Button(collectible_frame,
                   text=collectible['name'], padx=5, pady=5, wraplength=100, width=120, height=140,
                   image=photos[len(photos) - 1], compound=TOP,
                   command=lambda index=index_counter: parent.change_frame(CollectionFrame, index)).pack(side=RIGHT)
            index_counter += 1


class CollectionFrame(Frame):
    """Opens a view of the chosen collectibles from the launch frame."""

    def __init__(self, parent, category):
        # Collection frame
        Frame.__init__(self, parent)

        current_category = "The category currently in view is: " + main_save.collections[category]['name']
        Label(self, text=current_category, font=50).grid(row=1, column=2, padx=5, pady=5, columnspan=8, sticky=EW)

        # menu buttons
        menu_frame = Frame(self, borderwidth=5)
        menu_frame.grid(row=1, columns=1, rowspan=10)
        Button(menu_frame, text='Back', width=15,
               command=lambda: parent.change_frame(LaunchFrame)).grid(row=1, column=1)
        Button(menu_frame, text='Add Item', width=15).grid(row=2, column=1)
        Button(menu_frame, text='Delete Collection', width=15).grid(row=6, column=1, sticky=S, pady=(100, 0))

        # items frame
        items_frame = Frame(self, borderwidth=5)
        items_frame.grid(row=2, column=2, columnspan=8, rowspan=8)

        index_counter = 0
        main_save.thumbnails = []
        for item in main_save.collections[category]['items']:
            photos = main_save.thumbnails
            photos.append(ImageTk.PhotoImage(Image.open(item['image_loc']).resize((100, 100))))
            Button(items_frame,
                   text=item['name'], padx=5, pady=5, wraplength=100, width=120, height=140,
                   image=photos[len(photos) - 1], compound=TOP,
                   command=lambda index=index_counter:
                   parent.change_frame(CollectionFrame, category, index)).pack(side=RIGHT)
            index_counter += 1


# class ItemFrame(Frame):
#     """Opens a view of the chosen collectibles from the launch frame."""
#     def __init__(self, parent, item):
#         # Collection frame
#         Frame.__init__(self, parent)
#
#         current_category = "The category currently in view is: " + main_save.collections[category][item]
#         Label(self, text=current_category).grid(row=1, column=2, padx=5, pady=5, columnspan=8, sticky=EW)
#
#         # menu buttons
#         menu_frame = Frame(self)
#         menu_frame.grid(row=1, columns=1, rowspan=10)
#         Button(menu_frame, text='Back', width=15,
#                command=lambda: parent.change_frame(LaunchFrame)).grid(row=1, column=1)
#         Button(menu_frame, text='Add Item', width=15).grid(row=2, column=1)
#         Button(menu_frame, text='Delete Collection', width=15).grid(row=6, column=1, sticky=S, pady=(100, 0))
#
#         # collectibles frame
#         collectible_frame = Frame(self, borderwidth=5)
#         collectible_frame.grid(row=2, column=2, columnspan=8, rowspan=8)
#         index_counter = 0
#         for item in main_save.collections[category]:
#             photos = main_save.thumbnails
#             photos.append(ImageTk.PhotoImage(Image.open(item['image_loc']).resize((100, 100))))
#             Button(collectible_frame,
#                    text=item['name'],
#                    command=lambda index=index_counter: parent.change_frame(CollectionFrame, index)).pack(side=RIGHT)
#             index_counter += 1


if __name__ == '__main__':
    main_save = CurrentSave()
    main_save.load_save()
    gui = StartGUI()
    # main_save.collections.append(Collectible('DVDs', 'images/dvd.jpg'))
    # main_save.collections.append(Collectible('Board Games', 'images/catan.jpg'))
    # main_save.collections.append(Collectible('Beanie Babies', 'images/beanie.jpg'))
    # main_save.collections.append(Collectible('Dinosaurs', 'images/dino.png'))
    # main_save.collections[0]['items'].append(Item('Matrix', 'Not today Mr.Anderson', 400))
    # main_save.collections[0]['items'].append(Item('Short Circuit', 'Johnny Five is alive!', 375))
    # main_save.collections[0]['items'].append(Item('First Blood', 'I could have killed \'em all, I could\'ve killed'
    #                                                              ' you. In town you\'re the law, out here it\'s me. '
    #                                                              'Don\'t push it! Don\'t push it or I\'ll give you a '
    #                                                              'war you won\'t believe.', 689))

    gui.mainloop()
