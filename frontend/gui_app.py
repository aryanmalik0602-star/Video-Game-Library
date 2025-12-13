import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
import requests
import time
import threading
import random
import os
import csv

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:5000/media"

# --- THE "HYPER-NEON" PALETTE ---
C_VOID    = "#020202"
C_GRID    = "#0f1410"
C_CYAN    = "#00F0FF"
C_MAGENTA = "#FF003C"
C_YELLOW  = "#FCEE09"
C_TEXT    = "#D0D0D0"
C_DIM     = "#303030"

class NeonCanvasButton(tk.Canvas):
    """Custom Button logic"""
    def __init__(self, master, text, command, color=C_CYAN, width=160, height=40):
        super().__init__(master, width=width, height=height, bg=C_VOID, highlightthickness=0, cursor="hand2")
        self.command = command
        self.text_str = text
        self.color = color
        
        self.rect = self.create_rectangle(2, 2, width-2, height-2, outline=color, width=1)
        self.corner = self.create_polygon(width-15, height-2, width-2, height-2, width-2, height-15, fill=color)
        self.text = self.create_text(width/2, height/2, text=text, fill=color, font=("Consolas", 10, "bold"))
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.config(takefocus=0)

    def on_enter(self, e):
        self.itemconfig(self.rect, width=2, fill=self.color)
        self.itemconfig(self.text, fill=C_VOID)
        self.itemconfig(self.corner, fill=C_VOID)

    def on_leave(self, e):
        self.itemconfig(self.rect, width=1, fill="")
        self.itemconfig(self.text, fill=self.color)
        self.itemconfig(self.corner, fill=self.color)

    def on_click(self, e):
        if self.command: self.command()

class NeonLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1150x750")
        self.root.overrideredirect(True) 
        self.root.configure(bg=C_VOID)
        self.root.wm_attributes("-topmost", True) 

        self._offsetx = 0
        self._offsety = 0

        # --- BACKGROUND ---
        self.canvas = tk.Canvas(root, bg=C_VOID, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.draw_grid(1150, 750)
        
        self.canvas.create_line(20, 50, 20, 730, fill=C_DIM, width=2)
        self.canvas.create_line(1130, 50, 1130, 730, fill=C_DIM, width=2)
        self.canvas.config(takefocus=0)
        
        # --- TITLE BAR ---
        self.title_bar = tk.Frame(root, bg=C_VOID, height=40)
        self.title_bar.place(x=0, y=0, width=1150, height=40)
        self.title_bar.bind('<Button-1>', self.clickwin)
        self.title_bar.bind('<B1-Motion>', self.dragwin)
        
        lbl_title = tk.Label(self.title_bar, text="SYSTEM // SEARCH ACTIVE", bg=C_VOID, fg=C_MAGENTA, font=("Segoe UI", 12, "bold"))
        lbl_title.pack(side="left", padx=20)
        lbl_title.bind('<Button-1>', self.clickwin)
        lbl_title.bind('<B1-Motion>', self.dragwin)

        btn_close = tk.Button(self.title_bar, text="[ TERMINATE ]", bg=C_VOID, fg=C_DIM, font=("Consolas", 10), 
                              bd=0, command=root.destroy, activebackground=C_MAGENTA)
        btn_close.pack(side="right", padx=10)

        # Search Variable
        self.search_var = tk.StringVar()
        
        # --- SEARCH WIDGETS ---
        search_frame = tk.Frame(root, bg=C_VOID)
        search_frame.place(x=60, y=95, height=40, width=500) 

        self.entry_search = tk.Entry(search_frame, textvariable=self.search_var, bg=C_DIM, fg=C_CYAN, insertbackground=C_CYAN, 
                                font=("Consolas", 14), bd=0)
        self.entry_search.pack(side="left", padx=0, pady=5, fill="x", expand=False)
        self.entry_search.config(width=28, takefocus=1) # Ensure it CAN take focus

        # REMOVE KeyRelease binding from entry itself - we will bind root instead

        self.entry_search.config(state='normal')
        
        NeonCanvasButton(search_frame, "SCAN LIBRARY", self.force_search, color=C_CYAN).pack(side="left", padx=(10,0))
        
        # --- LIST SECTION ---
        self.canvas.create_line(60, 150, 400, 150, fill=C_CYAN, width=1)
        self.list_frame = tk.Frame(root, bg=C_VOID)
        self.list_frame.place(x=60, y=160, width=340, height=480)
        
        self.game_list = tk.Listbox(self.list_frame, bg=C_VOID, fg=C_TEXT, selectbackground=C_MAGENTA, 
                                    selectforeground=C_VOID, font=("Consolas", 12), bd=0, highlightthickness=0)
        self.game_list.pack(fill="both", expand=True)
        self.game_list.bind('<<ListboxSelect>>', self.show_details_animated)

        # --- DETAILS SECTION ---
        self.canvas.create_rectangle(450, 160, 1080, 640, outline=C_DIM, width=1)
        self.canvas.create_line(450, 200, 450, 160, 490, 160, fill=C_YELLOW, width=3) 
        
        self.details_text = tk.Text(root, bg=C_VOID, fg=C_CYAN, font=("Courier New", 10, "bold"), bd=0, highlightthickness=0)
        self.details_text.place(x=470, y=180, width=590, height=440)
        self.details_text.config(takefocus=0)

        # --- FOOTER ---
        NeonCanvasButton(root, "UPLOAD DATA", self.add_game, color=C_YELLOW).place(x=60, y=670)
        NeonCanvasButton(root, "PURGE DATA", self.delete_game, color=C_MAGENTA).place(x=240, y=670)
        NeonCanvasButton(root, "REFRESH ALL", self.refresh_list, color=C_TEXT).place(x=950, y=670)

        # FINAL AGGRESSIVE FOCUS SETTING & KEY HANDLER
        self.root.bind('<Key>', self.handle_keypress)
        root.after(10, self.entry_search.focus_set)
        
        self.refresh_list()

    def draw_grid(self, w, h):
        step = 40
        for x in range(0, w, step): self.canvas.create_line(x, 0, x, h, fill="#080808", width=1)
        for y in range(0, h, step): self.canvas.create_line(0, y, w, y, fill="#080808", width=1)

    def clickwin(self, event):
        self._offsetx = event.x
        self._offsety = event.y
    def dragwin(self, event):
        x = self.root.winfo_x() + event.x - self._offsetx
        y = self.root.winfo_y() + event.y - self._offsety
        self.root.geometry(f'+{x}+{y}')

    # --- KEYBOARD LOGIC HANDLERS ---
    
    def handle_keypress(self, event):
        """Manually manages key input for the search bar when the root window is focused."""
        char = event.char
        keysym = event.keysym
        entry = self.entry_search
        
        # 1. Handle regular printable characters (typing)
        if len(char) == 1 and char.isprintable():
            # Get current text, insert character at the cursor position (insertion point)
            text = entry.get()
            cursor_pos = entry.index(tk.INSERT)
            new_text = text[:cursor_pos] + char + text[cursor_pos:]
            self.search_var.set(new_text)
            entry.icursor(cursor_pos + 1) # Move cursor one position right
            self.live_search()
        
        # 2. Handle Backspace (Deletion)
        elif keysym == 'BackSpace' or keysym == 'Delete':
            text = entry.get()
            cursor_pos = entry.index(tk.INSERT)
            
            # Backspace deletes left, Delete deletes right
            if keysym == 'BackSpace' and cursor_pos > 0:
                new_text = text[:cursor_pos-1] + text[cursor_pos:]
                self.search_var.set(new_text)
                entry.icursor(cursor_pos - 1)
            elif keysym == 'Delete' and cursor_pos < len(text):
                new_text = text[:cursor_pos] + text[cursor_pos+1:]
                self.search_var.set(new_text)
                # Cursor position doesn't change for Delete
            
            self.live_search()
        
        # 3. Handle Cursor Movement (Optional, but helps user experience)
        elif keysym == 'Left':
            entry.icursor(entry.index(tk.INSERT) - 1)
        elif keysym == 'Right':
            entry.icursor(entry.index(tk.INSERT) + 1)
            
        # 4. Handle Escape (Clear)
        elif keysym == 'Escape':
            self.search_var.set("")
            self.live_search()

        return 'break' # Stop event propagation to prevent it being processed elsewhere

    # --- LOGIC ---
    
    def refresh_list(self, data=None):
        self.game_list.delete(0, tk.END)
        if data is None:
            try:
                response = requests.get(API_URL)
                if response.status_code == 200: data = response.json()
                else: data = []
            except: return
        
        sorted_items = sorted(data, key=lambda x: x['name'])
        for item in sorted_items:
            self.game_list.insert(tk.END, item['name'])

    def live_search(self, event=None):
        """Performs the search based on the current text in search_var."""
        name = self.search_var.get()
        if not name: 
            self.refresh_list()
            return

        try:
            r = requests.get(f"{API_URL}/search/{name}")
            if r.status_code == 200:
                results = r.json()
                self.game_list.delete(0, tk.END)
                for item in results:
                    self.game_list.insert(tk.END, item['name'])
            else:
                self.game_list.delete(0, tk.END)
        except: 
            pass

    def force_search(self):
        self.live_search()

    def show_details_animated(self, event, explicit_item=None):
        item = explicit_item
        if not item:
            sel = self.game_list.curselection()
            if not sel: return
            name = self.game_list.get(sel[0])
            try:
                r = requests.get(f"{API_URL}/item/{name}")
                if r.status_code == 200:
                    item = r.json()
            except: return

        if item:
            text = f"""
 // SECURE CONNECTION ESTABLISHED
 // ID: {hash(item['name'])%99999}
 
 OBJECT_NAME:
    {item.get('name').upper()}

 CATEGORY_CLASS:
    {item.get('category').upper()}

 PUBLISHER_ENTITY:
    {item.get('publisher').replace('User Rating: ', 'RATING: ')}

 RELEASE_CYCLE:
    {item.get('date')}
    
 [ END OF FILE ]
            """
            self.details_text.config(state="normal", fg=C_CYAN)
            self.details_text.delete(1.0, tk.END)
            threading.Thread(target=self.typewriter, args=(text,), daemon=True).start()

    def typewriter(self, text):
        for char in text:
            self.details_text.insert(tk.END, char)
            self.details_text.see(tk.END)
            time.sleep(0.002)
        self.details_text.config(state="disabled")

    def add_game(self):
        # Create a simple upload window
        upload_window = tk.Toplevel(self.root)
        upload_window.title("UPLOAD GAME")
        upload_window.geometry("350x200")
        upload_window.configure(bg=C_VOID)
        upload_window.resizable(False, False)
        
        # Make window stay on top
        upload_window.attributes('-topmost', True)
        
        # Title
        title_label = tk.Label(upload_window, text="ADD NEW GAME", font=("Consolas", 14, "bold"), 
                               fg=C_CYAN, bg=C_VOID)
        title_label.pack(pady=15)
        
        # Game Name Label
        name_label = tk.Label(upload_window, text="GAME NAME:", font=("Consolas", 10), 
                              fg=C_CYAN, bg=C_VOID)
        name_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        # Game Name Input
        name_entry = tk.Entry(upload_window, font=("Consolas", 10), bg=C_GRID, fg=C_TEXT, 
                              insertbackground=C_CYAN, width=30)
        name_entry.pack(pady=5, padx=20)
        name_entry.focus()
        
        def upload_game():
            game_name = name_entry.get().strip()
            if not game_name:
                messagebox.showwarning("WARNING", "Please enter a game name!", parent=upload_window)
                return
            
            try:
                # Upload game with default values
                game_data = {
                    "name": game_name,
                    "author": "Unknown",
                    "publisher": "N/A",
                    "category": "PC",
                    "date": "2025"
                }
                requests.post(API_URL, json=game_data)
                messagebox.showinfo("SUCCESS", f"Game '{game_name}' added!", parent=upload_window)
                upload_window.destroy()
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("ERROR", f"Failed to upload: {str(e)}", parent=upload_window)
        
        # Upload Button
        upload_btn = tk.Button(upload_window, text="UPLOAD", font=("Consolas", 11, "bold"), 
                               bg=C_YELLOW, fg=C_VOID, command=upload_game, cursor="hand2", 
                               activebackground=C_CYAN, activeforeground=C_VOID, bd=2)
        upload_btn.pack(pady=15, padx=20, fill="x")
        
        # Allow Enter key to upload
        name_entry.bind("<Return>", lambda e: upload_game())

    def delete_game(self):
        sel = self.game_list.curselection()
        if sel:
            name = self.game_list.get(sel[0])
            if messagebox.askyesno("CONFIRM", f"DELETE {name}?"):
                requests.delete(f"{API_URL}/{name}")
                self.refresh_list()
                self.details_text.config(state="normal"); self.details_text.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = NeonLibraryApp(root)
    root.mainloop()