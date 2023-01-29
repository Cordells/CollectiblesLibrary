from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import json
import os
import shutil  # shutil and os used together to copy images to image dir


class CollectiblesEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__


class CurrentSave:
    """Stores file save data, loads the main_save file, also saves and exits program"""

    def __init__(self):
        self.collections = {}
        self.thumbnails = []

    def save_and_exit(self):
        json_object = json.dumps(self.collections, indent=4, cls=CollectiblesEncoder)
        with open('main_save.json', 'w') as outfile:
            outfile.write(json_object)
        gui.destroy()

    def save(self):
        json_object = json.dumps(self.collections, indent=4, cls=CollectiblesEncoder)
        with open('main_save.json', 'w') as outfile:
            outfile.write(json_object)

    def load_save(self):
        path = 'main_save.json'
        if os.path.exists(path):
            with open('main_save.json', 'r') as openfile:
                parsed_json = json.load(openfile)
                self.collections = parsed_json
        else:
            self.save()

    def remove_item(self, category, item):
        self.collections[category].pop(item)


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
        menu_frame.grid(row=1, columns=1, rowspan=10, sticky=N)
        Button(menu_frame, text='Add Collection', width=15, background='green',
               command=lambda: parent.change_frame(AddCollectionFrame)).grid(row=1, column=1)
        Button(menu_frame, text='Load User Backup', width=15).grid(row=2, column=1)
        Button(menu_frame, text='How to Info', width=15, command=self.show_info).grid(row=3, column=1)
        Button(menu_frame, text='Advanced', width=15).grid(row=4, column=1)
        Button(menu_frame, text='Save & Exit', width=15, background='red',
               command=main_save.save_and_exit).grid(row=5, column=1)

        # collectibles frame
        collectible_frame = Frame(self, borderwidth=5)
        collectible_frame.grid(row=2, column=2, columnspan=8, rowspan=8)
        main_save.thumbnails = []
        for category in main_save.collections:
            photos = main_save.thumbnails
            current_category = main_save.collections[category]
            photos.append(ImageTk.PhotoImage(Image.open(current_category['image_loc']).resize((100, 100))))
            Button(collectible_frame,
                   text=current_category['name'], padx=5, pady=5, wraplength=100, width=120, height=140,
                   image=photos[len(photos) - 1], compound=TOP,
                   command=lambda i=current_category: parent.change_frame(CollectionFrame, i)).pack(side=RIGHT)

        if not main_save.collections:
            messagebox.showinfo('Empty Collection', 'If you have a backup save file of all your collections which you '
                                                    'would like to restore then on the launch screen you can select '
                                                    'Advanced then load backup.')

    def show_info(self):
        messagebox.showinfo('How to Info', 'To add a new collection and add new items to that collection.'
                                           '\n-Select "Add Collection" from the home screen.\n-After the collection is '
                                           'created you can select it on the home screen.\n-Once in the collection '
                                           'view select "Add Item", this will populate the current collection with '
                                           'a new item.\n\nTo remove an item.\n-You must select that item and once in '
                                           'that view select the "Delete Item" button.\n\nTo remove a collection\n'
                                           '-In the chosen collection view select the "Delete Collection" button,'
                                           'this will delete the collection and all items contained within it.')


class CollectionFrame(Frame):
    """Opens a view of the chosen collectibles from the launch frame."""

    def __init__(self, parent, category):
        # Collection frame
        Frame.__init__(self, parent)

        current_category = "The category currently in view is: " + category['name']
        Label(self, text=current_category, font=50).grid(row=1, column=2, padx=5, pady=5, columnspan=8, sticky=EW)

        # menu buttons
        menu_frame = Frame(self, borderwidth=5)
        menu_frame.grid(row=1, columns=1, rowspan=10, sticky=NW)
        Button(menu_frame, text='Back', width=15,
               command=lambda: parent.change_frame(LaunchFrame)).grid(row=1, column=1)
        Button(menu_frame, text='Add Item', width=15, background='green',
               command=lambda: parent.change_frame(AddItemFrame, category)).grid(row=2, column=1)
        Button(menu_frame, text='Delete Collection', width=15, background='red',
               command=lambda: self.verify(parent, category)).grid(row=6, column=1, sticky=S, pady=(100, 0))

        # items frame
        items_frame = Frame(self, borderwidth=5)
        items_frame.grid(row=2, column=2, columnspan=8, rowspan=8)

        self.load_items(category, parent, items_frame)

    def load_items(self, category, parent, items_frame):
        index_counter = 0
        main_save.thumbnails = []

        for item in category['items']:
            photos = main_save.thumbnails
            current_item = category['items'][item]
            photos.append(ImageTk.PhotoImage(Image.open(current_item['image_loc']).resize((100, 100))))
            Button(items_frame,
                   text=current_item['name'], padx=5, pady=5, wraplength=100, width=120, height=140,
                   image=photos[len(photos) - 1], compound=TOP,
                   command=lambda i=current_item: parent.change_frame(ItemFrame, category, i)).pack(side=RIGHT)
            index_counter += 1

    def delete_collection(self, parent, category):
        main_save.collections.pop(category['name'])
        parent.change_frame(LaunchFrame)
        main_save.save()

    def verify(self, parent, category):
        verify_collection = messagebox.askyesno('Delete?', 'Are you sure you want to delete this collection and all '
                                                           'items within it?')
        if verify_collection == 1:
            self.delete_collection(parent, category)


class ItemFrame(Frame):
    """Opens a view of the chosen collectibles from the launch frame."""

    def __init__(self, parent, category, item):
        # Collection frame
        Frame.__init__(self, parent)

        self.parent = parent
        self.category = category
        self.item = item

        current_item = "The item currently in view is: " + item['name']
        Label(self, text=current_item, font=50).grid(row=1, column=2, padx=5, pady=5, columnspan=8, sticky=EW)

        # menu buttons
        menu_frame = Frame(self, borderwidth=5)
        menu_frame.grid(row=1, columns=1, rowspan=10, sticky=NW)
        Button(menu_frame, text='Back', width=15,
               command=lambda: parent.change_frame(CollectionFrame, category)).grid(row=1, column=1)
        Button(menu_frame, text='Save Changes', background='green', width=15).grid(row=2, column=1)
        Button(menu_frame, text='Delete Item', width=15, background='red',
               command=self.verify).grid(row=3, column=1, sticky=N, pady=(100, 0))

        # item info frame
        info_frame = Frame(self, borderwidth=5)
        info_frame.grid(row=2, column=2)

        Label(info_frame, text=item['name'], font=10).grid(row=1, column=1, sticky=NW)
        Label(info_frame, text=item['description'], wraplength=500, font=10).grid(row=2, column=1, sticky=NW)
        Label(info_frame, text=item['value'], font=10).grid(row=3, column=1, sticky=NW)
        photos = main_save.thumbnails
        photos.append(ImageTk.PhotoImage(Image.open(item['image_loc']).resize((50, 50))))  # TODO: fix this image sizing
        Label(info_frame, image=photos[0]).grid(row=2, column=2, sticky=NW)

    def delete_item(self):
        self.category['items'].pop(self.item['name'])
        self.parent.change_frame(CollectionFrame, self.category)
        main_save.save()

    def verify(self):
        verify_delete = messagebox.askyesno('Delete?', 'Are you sure you want to delete this item?')
        if verify_delete == 1:
            self.delete_item()


class AddItemFrame(Frame):
    """Opens a view to add an item to the passed category."""

    def __init__(self, parent, category):
        # Collection frame
        Frame.__init__(self, parent)

        self.parent = parent
        self.category = category

        current_category = "You are currently adding a new item to: " + category['name']
        Label(self, text=current_category).grid(row=1, column=2, padx=5, pady=5, columnspan=8, sticky=EW)

        # menu buttons
        menu_frame = Frame(self, borderwidth=5)
        menu_frame.grid(row=1, columns=1, rowspan=10, sticky=NW)
        Button(menu_frame, text='Back', width=15,
               command=lambda: parent.change_frame(CollectionFrame, category)).grid(row=1, column=1)
        Button(menu_frame, text='Save Changes', width=15, background='green',
               command=lambda: self.save_back(parent, category)).grid(row=2, column=1)

        # creation frame
        creation_frame = Frame(self, borderwidth=5)
        creation_frame.grid(row=2, column=2, columnspan=8, rowspan=8)

        Label(creation_frame, text='Please enter the item name:').grid(row=1, column=1)
        self.inp_name = Entry(creation_frame)
        self.inp_name.grid(row=2, column=1, padx=5, pady=5)

        Label(creation_frame, text='Please enter the item description:').grid(row=3, column=1)
        self.inp_description = Entry(creation_frame)
        self.inp_description.grid(row=4, column=1, padx=5, pady=5)

        Label(creation_frame, text='Please enter the item value:').grid(row=5, column=1)
        self.inp_value = Entry(creation_frame)
        self.inp_value.grid(row=6, column=1, padx=5, pady=5)

        Label(creation_frame, text='Please enter the image location:').grid(row=7, column=1)
        self.inp_image = Entry(creation_frame)
        self.inp_image.grid(row=8, column=1, padx=5, pady=5)

    def save_back(self, parent, category):
        item_name = self.inp_name.get()
        item_description = self.inp_description.get()
        item_value = self.inp_value.get()
        item_image = self.inp_image.get()
        if item_image == "":
            item_image = 'images/default.png'
        item = {
            'name': item_name,
            'description': item_description,
            'value': int(item_value),
            'image_loc': item_image
        }
        category['items'][item['name']] = item
        main_save.save()
        parent.change_frame(CollectionFrame, category)


class AddCollectionFrame(Frame):
    """Opens a view to add a collectible to the launch frame."""

    def __init__(self, parent):
        # Collection frame
        Frame.__init__(self, parent)

        self.parent = parent

        text_to_label = "You are currently adding a new collection"
        Label(self, text=text_to_label, font=50).grid(row=1, column=2, padx=5, pady=5, columnspan=8, sticky=EW)

        # menu buttons
        menu_frame = Frame(self, borderwidth=5)
        menu_frame.grid(row=1, columns=1, rowspan=10, sticky=NW)
        Button(menu_frame, text='Back', width=15,
               command=lambda: parent.change_frame(LaunchFrame)).grid(row=1, column=1)
        Button(menu_frame, text='Save Changes', width=15, background='green',
               command=lambda: self.save_back(parent)).grid(row=2, column=1)

        # creation frame
        creation_frame = Frame(self, borderwidth=5)
        creation_frame.grid(row=2, column=2, columnspan=8, rowspan=8)

        Label(creation_frame, text='Please enter the category name:').grid(row=1, column=1)
        self.inp_name = Entry(creation_frame)
        self.inp_name.grid(row=2, column=1, padx=5, pady=5)

        Label(creation_frame, text='Please enter the image location:').grid(row=3, column=1)
        self.inp_image = Entry(creation_frame)
        self.inp_image.grid(row=4, column=1, padx=5, pady=5)

    def save_back(self, parent):
        item_name = self.inp_name.get()
        item_image = self.inp_image.get()
        if item_image == "":
            item_image = 'images/default.png'
        item = {
            'name': item_name,
            'image_loc': item_image,
            'items': {}
        }
        main_save.collections[item['name']] = item
        main_save.save()
        parent.change_frame(LaunchFrame)


if __name__ == '__main__':
    main_save = CurrentSave()
    main_save.load_save()
    gui = StartGUI()
    gui.mainloop()
