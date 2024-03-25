import tkinter as tk
import tkinter.simpledialog
import tkinter.colorchooser
import json
import os

class StickyNote(tk.Toplevel):
    def __init__(self, master, folder=None, note_data=None):
        super().__init__(master)
        self.master = master
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.header = tk.Frame(self, bg="lightgray", height=25)
        self.header.pack(fill=tk.X)
        self.header.bind("<ButtonPress-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.move_window)

        self.close_button = tk.Button(self.header, text="X", command=self.close_note, bg="lightgray", fg="red", bd=0, padx=5, pady=2, activebackground="red", activeforeground="white")
        self.close_button.pack(side=tk.RIGHT, padx=(0, 5))
        self.close_button.bind("<Enter>", lambda e: self.close_button.config(bg="red"))
        self.close_button.bind("<Leave>", lambda e: self.close_button.config(bg="lightgray"))

        self.maximize_button = tk.Button(self.header, text="□", command=self.toggle_maximize, bg="lightgray", fg="black", bd=0, padx=5, pady=2, activebackground="lightgray", activeforeground="black")
        self.maximize_button.pack(side=tk.RIGHT)
        self.maximize_button.bind("<Enter>", lambda e: self.maximize_button.config(bg="gray"))
        self.maximize_button.bind("<Leave>", lambda e: self.maximize_button.config(bg="lightgray"))

        self.minimize_button = tk.Button(self.header, text="_", command=self.minimize_note, bg="lightgray", fg="black", bd=0, padx=5, pady=2, activebackground="lightgray", activeforeground="black")
        self.minimize_button.pack(side=tk.RIGHT)
        self.minimize_button.bind("<Enter>", lambda e: self.minimize_button.config(bg="gray"))
        self.minimize_button.bind("<Leave>", lambda e: self.minimize_button.config(bg="lightgray"))

        self.folder_label = tk.Label(self.header, text="", bg="lightgray", font=("Arial", 10))
        self.folder_label.pack(side=tk.LEFT, padx=(5, 0))

        self.text = tk.Text(self, wrap=tk.WORD, font=("Arial", 12))
        self.text.pack(expand=True, fill=tk.BOTH)

        self.text.configure(pady=20)
        self.text.window_create("1.0", window=tk.Label(self.text, text="\n", font=("Arial", 12)))

        self.folder = folder

        if note_data:
            self.geometry(note_data["geometry"])
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", note_data["content"])
        else:
            self.geometry("200x200")

        if folder:
            self.folder_label.configure(text=folder.name, bg=folder.color)
            self.header.configure(bg=folder.color)

        self.bind("<ButtonPress-1>", self.start_resize)
        self.bind("<B1-Motion>", self.resize_window)
        self.bind("<ButtonRelease-1>", self.end_resize)

    def start_move(self, event):
        if not self.is_maximized():
            self.x = event.x
            self.y = event.y

    def move_window(self, event):
        if hasattr(self, "x"):
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        if not self.is_maximized():
            self.resize_pos = self.get_resize_position(event)
            if self.resize_pos:
                self.resize_x = event.x
                self.resize_y = event.y
                self.orig_width = self.winfo_width()
                self.orig_height = self.winfo_height()


    def resize_window(self, event):
        if hasattr(self, "resize_pos") and self.resize_pos:
            deltax = event.x - self.resize_x
            deltay = event.y - self.resize_y
            width = max(200, self.orig_width)
            height = max(200, self.orig_height)
            if "left" in self.resize_pos:
                width -= deltax
                self.geometry(f"{width}x{height}+{self.winfo_x() + deltax}+{self.winfo_y()}")
            elif "right" in self.resize_pos:
                width += deltax
                self.geometry(f"{width}x{height}")
            if "top" in self.resize_pos:
                height -= deltay
                self.geometry(f"{width}x{height}+{self.winfo_x()}+{self.winfo_y() + deltay}")
            elif "bottom" in self.resize_pos:
                height += deltay
                self.geometry(f"{width}x{height}")
    
    def end_resize(self, event):
        if hasattr(self, "resize_pos"):
            del self.resize_pos
        if hasattr(self, "resize_x"):
            del self.resize_x
        if hasattr(self, "resize_y"):
            del self.resize_y
        if hasattr(self, "orig_width"):
            del self.orig_width
        if hasattr(self, "orig_height"):
            del self.orig_height


    def get_resize_position(self, event):
        if event.x < 5 and event.y < 5:
            return "top_left"
        elif event.x > self.winfo_width() - 5 and event.y < 5:
            return "top_right"
        elif event.x < 5 and event.y > self.winfo_height() - 5:
            return "bottom_left"
        elif event.x > self.winfo_width() - 5 and event.y > self.winfo_height() - 5:
            return "bottom_right"
        elif event.x < 5:
            return "left"
        elif event.x > self.winfo_width() - 5:
            return "right"
        elif event.y < 5:
            return "top"
        elif event.y > self.winfo_height() - 5:
            return "bottom"
        else:
            return None

    def save_note(self, event=None):
        note_data = {
            "geometry": self.geometry(),
            "content": self.text.get("1.0", tk.END)
        }
        self.master.save_notes()

    def close_note(self):
        if self.folder:
            self.folder.remove_note(self)
        self.master.save_notes()
        self.destroy()

    def minimize_note(self):
        self.update_idletasks()
        self.overrideredirect(False)
        self.state("iconic")

    def toggle_maximize(self):
        if self.state() == "zoomed":
            self.state("normal")
        else:
            self.state("zoomed")

    def is_maximized(self):
        return self.state() == "zoomed"

class Folder:
    def __init__(self, name, color="lightgray"):
        self.name = name
        self.color = color
        self.notes = []

    def add_note(self, note):
        self.notes.append(note)

    def remove_note(self, note):
        self.notes.remove(note)

class StickyNoteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sticky Note App")
        self.folders = []
        self.current_folder = None


        self.folder_frame = tk.Frame(self)
        self.folder_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.create_folder_button = tk.Button(self.folder_frame, text="Create Folder", command=self.create_folder)
        self.create_folder_button.pack(pady=5)

        self.open_notes_button = tk.Button(self.folder_frame, text="Open Notes", command=self.open_notes)
        self.open_notes_button.pack(pady=5)

        self.save_notes_button = tk.Button(self.folder_frame, text="Save Notes", command=self.save_notes)
        self.save_notes_button.pack(pady=5)

        self.close_notes_button = tk.Button(self.folder_frame, text="Close Notes", command=self.close_notes)
        self.close_notes_button.pack(pady=5)

        self.folder_listbox = tk.Listbox(self.folder_frame)
        self.folder_listbox.pack(pady=5)
        self.folder_listbox.bind("<<ListboxSelect>>", self.open_folder)

        self.note_frame = tk.Frame(self)
        self.note_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.create_note_button = tk.Button(self.note_frame, text="Create Sticky Note", command=self.create_sticky_note)
        self.create_note_button.pack(pady=5)

        self.status_label = tk.Label(self, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.load_folders()

    def create_folder(self):
        folder_name = tk.simpledialog.askstring("Create Folder", "Enter folder name:")
        if folder_name:
            folder_color = tk.colorchooser.askcolor(title="Select Folder Color")[1]
            if folder_color:
                folder = Folder(folder_name, color=folder_color)
                self.folders.append(folder)
                self.folder_listbox.insert(tk.END, folder_name)
                self.save_folders()
                self.set_status(f"Folder '{folder_name}' created successfully.")

    def open_folder(self, event):
        selection = self.folder_listbox.curselection()
        if selection:
            folder_index = selection[0]
            folder = self.folders[folder_index]
            self.current_folder = folder
            self.set_status(f"Folder '{folder.name}' selected.")

    def create_sticky_note(self):
        if self.current_folder:
            sticky_note = StickyNote(self, folder=self.current_folder)
            self.current_folder.add_note(sticky_note)
            self.save_notes()
            self.set_status("Sticky note created successfully.")
        else:
            self.set_status("Please select a folder first.")

    def open_notes(self):
        if self.current_folder:
            self.load_notes()
            self.set_status(f"Notes from folder '{self.current_folder.name}' opened.")
        else:
            self.set_status("Please select a folder first.")

    def close_notes(self):
        if self.current_folder:
            for note in self.current_folder.notes:
                if isinstance(note, StickyNote) and note.winfo_exists():
                    note.destroy()
            self.current_folder.notes.clear()
            self.set_status(f"Notes from folder '{self.current_folder.name}' closed.")
        else:
            self.set_status("Please select a folder first.")

    def load_notes(self):
        if self.current_folder:
            self.close_notes()
            for note_data in self.current_folder.notes_data:
                sticky_note = StickyNote(self, folder=self.current_folder, note_data=note_data)
                self.current_folder.add_note(sticky_note)

    def save_notes(self):
        if self.current_folder:
            self.current_folder.notes_data = []
            for note in self.current_folder.notes:
                if isinstance(note, StickyNote) and note.winfo_exists():
                    note_data = {
                        "geometry": note.geometry(),
                        "content": note.text.get("1.0", tk.END)
                    }
                    self.current_folder.notes_data.append(note_data)
            self.save_folders()
            self.set_status(f"Notes from folder '{self.current_folder.name}' saved successfully.")
        else:
            self.set_status("Please select a folder first.")

    def save_folders(self):
        folders_data = []
        for folder in self.folders:
            folder_data = {
                "name": folder.name,
                "color": folder.color,
                "notes": folder.notes_data if hasattr(folder, "notes_data") else []
            }
            folders_data.append(folder_data)
        with open("folders.json", "w") as file:
            json.dump(folders_data, file)

    def load_folders(self):
        if os.path.exists("folders.json"):
            with open("folders.json", "r") as file:
                folders_data = json.load(file)
            for folder_data in folders_data:
                folder_color = folder_data.get("color", "lightgray")  # Use default color if not present
                folder = Folder(folder_data["name"], color=folder_color)
                folder.notes_data = folder_data.get("notes", [])  # Use empty list if notes not present
                self.folders.append(folder)
                self.folder_listbox.insert(tk.END, folder.name)

    def set_status(self, message):
        self.status_label.config(text=message)

    def on_close(self):
        self.save_folders()
        self.destroy()

if __name__ == "__main__":
    app = StickyNoteApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()