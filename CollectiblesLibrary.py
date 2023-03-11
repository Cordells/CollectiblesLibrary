import tkinter.filedialog
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import json
import os
import zmq


class CollectiblesEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__


class CurrentSave:
    """Stores file save data, loads the main_save file, also saves and exits program"""

    def __init__(self):
        self.collections = {}
        self.thumbnails = []
        self.current_thumbnail = ["default"]
        self.values = {}

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

    def total_values(self):
        context = zmq.Context()

        # socket to communicate with server
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")

        # send request to TotalMicroservice
        socket.send_json(self.collections)
        values = {}
        socket.setsockopt(zmq.LINGER, 100)
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        if poller.poll(100):
            try:
                values = socket.recv_json(flags=zmq.NOBLOCK)
            except zmq.ZMQError:
                socket.close()
        self.values = values


class StartGUI(Tk):
    """Creates Tkinter root and starts the first frame which is the LaunchFrame"""

    def __init__(self):
        Tk.__init__(self)
        self._current_frame = None
        self.geometry('850x600')
        self.title('Collectibles Library')
        self.iconbitmap('crs.ico')
        self.main_save = CurrentSave()
        self.main_save.load_save()
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
        Frame.__init__(self, parent)
        Frame(parent, borderwidth=5, relief="groove")
        self.parent = parent
        self.main_save = parent.main_save

        self.show_info_1 = 'How to Info'
        self.show_info_2 = 'To add a new collection and add new items to that collection.' \
                           '\n-Select "Add Collection" from the home screen.\n-After the collection is ' \
                           'created you can select it on the home screen.\n-Once in the collection ' \
                           'view select "Add Item", this will populate the current collection with ' \
                           'a new item.\n\nTo remove an item.\n-You must select that item and once in ' \
                           'that view select the "Delete Item" button.\n\nTo remove a collection\n' \
                           '-In the chosen collection view select the "Delete Collection" button,' \
                           'this will delete the collection and all items contained within it.'

        current_category = "Your current collections: "
        Label(self, text=current_category, font=50).grid(row=1, column=2, padx=5, pady=5, columnspan=8, sticky=NW)

        # menu buttons
        menu_frame = Frame(self, borderwidth=5)
        menu_frame.grid(row=1, columns=1, rowspan=10, sticky=N)
        Button(menu_frame, text='Add Collection', width=15, background='green',
               command=lambda: parent.change_frame(AddCollectionFrame)).grid(row=1, column=1)
        Button(menu_frame, text='Load User Backup', width=15).grid(row=2, column=1)
        Button(menu_frame, text='How to Info', width=15, command=self.show_info).grid(row=3, column=1)
        Button(menu_frame, text='Values', width=15, command=self.show_values).grid(row=4, column=1)
        Button(menu_frame, text='Advanced', width=15).grid(row=5, column=1)
        Button(menu_frame, text='Save & Exit', width=15, background='red',
               command=self.main_save.save_and_exit).grid(row=6, column=1)

        # collectibles frame
        collectible_frame = Frame(self, borderwidth=5)
        collectible_frame.grid(row=2, column=2, columnspan=8, rowspan=8)
        self.main_save.thumbnails = []
        row_count = 1
        column_count = 1
        for category in self.main_save.collections:
            photos = self.main_save.thumbnails
            current_category = self.main_save.collections[category]
            photos.append(ImageTk.PhotoImage(Image.open(current_category['image_loc']).resize((100, 100))))
            Button(collectible_frame,
                   text=current_category['name'], padx=5, pady=5, wraplength=100, width=120, height=140,
                   image=photos[len(photos) - 1], compound=TOP,
                   command=lambda i=current_category:
                   parent.change_frame(CollectionFrame, i)).grid(row=row_count, column=column_count)
            if column_count == 5:
                row_count += 1
                column_count = 1
            else:
                column_count += 1

        if not self.main_save.collections:
            messagebox.showinfo('Empty Collection', 'If you have a backup save file of all your collections which you '
                                                    'would like to restore then on the launch screen you can select '
                                                    'Advanced then load backup.')

    def show_info(self):
        messagebox.showinfo(self.show_info_1, self.show_info_2)

    def show_values(self):
        self.main_save.total_values()
        message = ""
        if self.main_save.values:
            for category in self.main_save.values:
                if category != 'Total':
                    message = message + category + ' value: $' + str(self.main_save.values[category]) + '\n'
            message = message + 'Total value of collections: $' + str(self.main_save.values['Total'])
        if message == "":
            message = "Value not returned from microservice..."
        messagebox.showinfo('Collection Values', message)


class CollectionFrame(Frame):
    """Opens a view of the chosen collectibles from the launch frame."""

    def __init__(self, parent, category):
        Frame.__init__(self, parent)
        self.parent = parent
        self.main_save = parent.main_save

        current_category = "The category currently in view is: " + category['name']
        Label(self, text=current_category, font=50).grid(row=1, column=2, padx=5, pady=5, columnspan=8, sticky=NW)

        # menu buttons
        menu_frame = Frame(self, borderwidth=5)
        menu_frame.grid(row=1, columns=1, rowspan=10, sticky=NW)
        Button(menu_frame, text='Back', width=15, justify=LEFT,
               command=lambda: parent.change_frame(LaunchFrame)).grid(row=1, column=1)
        Button(menu_frame, text='Add Item', width=15, background='green',
               command=lambda: parent.change_frame(AddItemFrame, category)).grid(row=2, column=1)
        Button(menu_frame, text='Delete Collection', width=15, background='red',
               command=lambda: self.verify(category)).grid(row=6, column=1, sticky=S, pady=(100, 0))

        # items frame
        items_frame = Frame(self, borderwidth=5)
        items_frame.grid(row=2, column=2, columnspan=8, rowspan=8, sticky=NW)

        self.load_items(category, items_frame)

    def load_items(self, category, items_frame):
        index_counter = 0
        parent = self.parent
        parent.main_save.thumbnails = []

        row_count = 1
        column_count = 1
        for item in category['items']:
            photos = parent.main_save.thumbnails
            current_item = category['items'][item]
            photos.append(ImageTk.PhotoImage(Image.open(current_item['image_loc']).resize((100, 100))))
            Button(items_frame,
                   text=current_item['name'], padx=5, pady=5, wraplength=100, width=120, height=140,
                   image=photos[len(photos) - 1], compound=TOP, justify=LEFT,
                   command=lambda i=current_item:
                   parent.change_frame(ItemFrame, category, i)).grid(row=row_count, column=column_count, sticky=NW)
            index_counter += 1
            if column_count == 5:
                row_count += 1
                column_count = 1
            else:
                column_count += 1

    def delete_collection(self, category):
        self.main_save.collections.pop(category['name'])
        self.parent.change_frame(LaunchFrame)
        self.main_save.save()

    def verify(self, category):
        verify_collection = messagebox.askyesno('Delete?', 'Are you sure you want to delete this collection and all '
                                                           'items within it?')
        if verify_collection == 1:
            self.delete_collection(category)


class ItemFrame(Frame):
    """Opens a view of the chosen item from a collection."""

    def __init__(self, parent, category, item):
        Frame.__init__(self, parent)

        self.parent = parent
        self.category = category
        self.item = item
        self.main_save = parent.main_save

        current_item = "The item currently in view is: " + item['name']
        Label(self, text=current_item, font=50).grid(row=1, column=2, padx=5, pady=5, columnspan=8, sticky=NW)

        # menu buttons
        menu_frame = Frame(self, borderwidth=5)
        menu_frame.grid(row=1, columns=1, rowspan=10, sticky=NW)
        Button(menu_frame, text='Back', width=15,
               command=lambda: parent.change_frame(CollectionFrame, category)).grid(row=1, column=1)
        Button(menu_frame, text='Edit', width=15, background='green',
               command=lambda: parent.change_frame(EditItemFrame, category, item)).grid(row=2, column=1)
        Button(menu_frame, text='Delete Item', width=15, background='red',
               command=self.verify).grid(row=3, column=1, sticky=N, pady=(100, 0))

        # item info frame
        info_frame = Frame(self, borderwidth=5)
        info_frame.grid(row=2, column=2)

        photo = parent.main_save.current_thumbnail
        photo[0] = (ImageTk.PhotoImage(Image.open(item['image_loc']).resize((200, 200))))
        Label(info_frame, image=photo[0]).grid(row=1, column=1, sticky=NW)

        Label(info_frame, text='Name: ' + item['name'], font=10, wraplength=500).grid(row=2, column=1, sticky=NW)
        Label(info_frame, text='Description: ' + item['description'], wraplength=500, font=10,
              justify=LEFT).grid(row=3, column=1, sticky=NW)
        Label(info_frame, text='Value: ' + str(item['value']), font=10).grid(row=4, column=1, sticky=NW)

    def delete_item(self):
        self.category['items'].pop(self.item['name'])
        self.parent.change_frame(CollectionFrame, self.category)
        self.main_save.save()

    def verify(self):
        verify_delete = messagebox.askyesno('Delete?', 'Are you sure you want to delete this item?')
        if verify_delete == 1:
            self.delete_item()


class AddCollectionFrame(Frame):
    """Opens a view to add a collection to the launch frame."""

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent
        self.main_save = parent.main_save

        text_to_label = "You are currently adding a new collection"
        Label(self, text=text_to_label, font=50).grid(row=1, column=2, padx=5, pady=5, columnspan=8, sticky=NW)

        # menu buttons
        menu_frame = Frame(self, borderwidth=5)
        menu_frame.grid(row=1, columns=1, rowspan=10, sticky=NW)
        Button(menu_frame, text='Back', width=15,
               command=lambda: parent.change_frame(LaunchFrame)).grid(row=1, column=1)
        Button(menu_frame, text='Save Changes', width=15, background='green',
               command=lambda: self.save_back()).grid(row=2, column=1)

        # creation frame
        self.creation_frame = Frame(self, borderwidth=5)
        creation_frame = self.creation_frame
        creation_frame.grid(row=2, column=2, columnspan=8, rowspan=8, sticky=NW)

        Label(creation_frame, text='Please enter the category name:').grid(row=1, column=1, sticky=NW)
        self.inp_name = Entry(creation_frame)
        self.inp_name.grid(row=2, column=1, padx=5, pady=5, sticky=NW)

        Button(creation_frame, text='Select Image', width=15, command=lambda: self.get_image()).grid(row=3, column=1,
                                                                                                     sticky=NW)
        self.image_location = ""

    def get_image(self):
        self.image_location = tkinter.filedialog.askopenfilename(initialdir=os.getcwd() + "/images/",
                                                                 title="Select an image",
                                                                 filetypes=[(".png/.jpg", "*.png *.jpg")])
        Label(self.creation_frame, text=self.image_location, wraplength=600, justify=LEFT).grid(row=4, column=1,
                                                                                                columnspan=8, sticky=NW)

    def save_back(self):
        item_name = self.inp_name.get()
        item_image = self.image_location
        if item_image == "":
            item_image = 'images/default.png'
        item = {
            'name': item_name,
            'image_loc': item_image,
            'items': {}
        }
        self.main_save.collections[item['name']] = item
        self.main_save.save()
        self.parent.change_frame(LaunchFrame)


class AddItemFrame(Frame):
    """Opens a view to add an item to the current category."""

    def __init__(self, parent, category):
        Frame.__init__(self, parent)

        self.parent = parent
        self.category = category
        self.main_save = parent.main_save

        current_category = "You are currently adding a new item to: " + category['name']
        Label(self, text=current_category, font=50).grid(row=1, column=2, padx=5, pady=5, columnspan=8, sticky=NW)

        # menu buttons
        menu_frame = Frame(self, borderwidth=5)
        menu_frame.grid(row=1, columns=1, rowspan=10, sticky=NW)
        Button(menu_frame, text='Back', width=15,
               command=lambda: parent.change_frame(CollectionFrame, category)).grid(row=1, column=1)
        Button(menu_frame, text='Save Changes', width=15, background='green',
               command=lambda: self.verify_entry()).grid(row=2, column=1)

        # creation frame
        self.creation_frame = Frame(self, borderwidth=5)
        creation_frame = self.creation_frame
        creation_frame.grid(row=2, column=2, columnspan=8, rowspan=8, sticky=NW)

        Label(creation_frame, text='Please enter the item name:').grid(row=1, column=1, sticky=NW)
        self.inp_name = Entry(creation_frame)
        self.inp_name.grid(row=2, column=1, padx=5, pady=5, sticky=NW)

        Label(creation_frame, text='Please enter the item description:').grid(row=3, column=1, sticky=NW)
        self.inp_description = Entry(creation_frame)
        self.inp_description.grid(row=4, column=1, padx=5, pady=5, sticky=NW)

        Label(creation_frame, text='Please enter the item value:').grid(row=5, column=1, sticky=NW)
        self.inp_value = Entry(creation_frame)
        self.inp_value.grid(row=6, column=1, padx=5, pady=5, sticky=NW)

        Button(creation_frame, text='Select Image', width=15, command=lambda: self.get_image()).grid(row=7, column=1,
                                                                                                     sticky=NW)
        self.image_location = ""

    def get_image(self):
        self.image_location = tkinter.filedialog.askopenfilename(initialdir=os.getcwd() + "/images/",
                                                                 title="Select an image",
                                                                 filetypes=[(".png/.jpg", "*.png *.jpg")])
        Label(self.creation_frame, text=self.image_location, wraplength=600, justify=LEFT).grid(row=8, column=1,
                                                                                                columnspan=8, sticky=NW)

    def verify_entry(self):
        item_name = self.inp_name.get()
        item_value = self.inp_value.get()

        if item_value == "":
            item_value = "0"
        if item_name == "":
            messagebox.showinfo('Invalid Name', 'Please enter an item name.')
        elif not (str.isnumeric(item_value)):
            messagebox.showinfo('Invalid Item Value', 'Please enter only a number for the item value')
        else:
            if self.image_location != "":
                if not os.path.exists(self.image_location):
                    messagebox.showinfo('Invalid image location', 'Please select a valid image.')
                else:
                    self.save_back()
            else:
                self.save_back()

    def save_back(self):
        item_name = self.inp_name.get()
        item_description = self.inp_description.get()
        item_value = self.inp_value.get()
        if item_value == "":
            item_value = 0
        item_image = self.image_location
        if item_image == "":
            item_image = 'images/default.png'
        item = {
            'name': item_name,
            'description': item_description,
            'value': int(item_value),
            'image_loc': item_image
        }
        self.category['items'][item['name']] = item
        self.main_save.save()
        self.parent.change_frame(CollectionFrame, self.category)


class EditItemFrame(Frame):
    """Opens a view to edit an item from said item frame."""

    def __init__(self, parent, category, item):
        Frame.__init__(self, parent)

        self.parent = parent
        self.category = category
        self.item = item
        self.main_save = parent.main_save

        current_category = "You are currently editing item in: " + category['name']
        Label(self, text=current_category, font=50).grid(row=1, column=2, padx=5, pady=5, columnspan=8, sticky=NW)

        # menu buttons
        menu_frame = Frame(self, borderwidth=5)
        menu_frame.grid(row=1, columns=1, rowspan=10, sticky=NW)
        Button(menu_frame, text='Back', width=15,
               command=lambda: parent.change_frame(CollectionFrame, category)).grid(row=1, column=1)
        Button(menu_frame, text='Save Changes', width=15, background='green',
               command=lambda: self.verify_entry()).grid(row=2, column=1)

        # creation frame
        self.creation_frame = Frame(self, borderwidth=5)
        creation_frame = self.creation_frame
        creation_frame.grid(row=2, column=2, columnspan=8, rowspan=8, sticky=NW)

        Label(creation_frame, text='Please enter the item name:').grid(row=1, column=1, sticky=NW)
        self.inp_name = Entry(creation_frame)
        self.inp_name.insert(0, item['name'])
        self.inp_name.grid(row=2, column=1, padx=5, pady=5, sticky=NW)

        Label(creation_frame, text='Please enter the item description:').grid(row=3, column=1, sticky=NW)
        self.inp_description = Entry(creation_frame)
        self.inp_description.insert(0, item['description'])
        self.inp_description.grid(row=4, column=1, padx=5, pady=5, sticky=NW)

        Label(creation_frame, text='Please enter the item value:').grid(row=5, column=1, sticky=NW)
        self.inp_value = Entry(creation_frame)
        self.inp_value.insert(0, item['value'])
        self.inp_value.grid(row=6, column=1, padx=5, pady=5, sticky=NW)

        Button(creation_frame, text='Select Image', width=15, command=lambda: self.get_image()).grid(row=7, column=1,
                                                                                                     sticky=NW)
        self.image_location = item['image_loc']
        Label(self.creation_frame, text=self.image_location, wraplength=600, justify=LEFT).grid(row=8, column=1,
                                                                                                columnspan=8, sticky=NW)

    def get_image(self):
        self.image_location = tkinter.filedialog.askopenfilename(initialdir=os.getcwd() + "/images/",
                                                                 title="Select an image",
                                                                 filetypes=[(".png/.jpg", "*.png *.jpg")])
        Label(self.creation_frame, text=self.image_location, wraplength=600, justify=LEFT).grid(row=8, column=1,
                                                                                                columnspan=8, sticky=NW)

    def verify_entry(self):
        item_name = self.inp_name.get()
        item_value = self.inp_value.get()

        if item_value == "":
            item_value = "0"
        if item_name == "":
            messagebox.showinfo('Invalid Name', 'Please enter an item name.')
        elif not (str.isnumeric(item_value)):
            messagebox.showinfo('Invalid Item Value', 'Please enter only a number for the item value')
        else:
            if self.image_location != "":
                if not os.path.exists(self.image_location):
                    messagebox.showinfo('Invalid image location', 'Please select a valid image.')
                else:
                    self.save_back()
            else:
                self.save_back()

    def save_back(self):
        item_name = self.inp_name.get()
        item_description = self.inp_description.get()
        item_value = self.inp_value.get()
        if item_value == "":
            item_value = 0
        item_image = self.image_location
        if item_image == "":
            item_image = 'images/default.png'
        item = {
            'name': item_name,
            'description': item_description,
            'value': int(item_value),
            'image_loc': item_image
        }
        self.category['items'][item['name']] = item
        self.main_save.save()
        self.parent.change_frame(CollectionFrame, self.category)


if __name__ == '__main__':
    gui = StartGUI()
    gui.mainloop()
