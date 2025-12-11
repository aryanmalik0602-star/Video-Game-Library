import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import requests
import time
import threading
import random

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

        self._offsetx = 0
        self._offsety = 0

        # --- BACKGROUND ---
        self.canvas = tk.Canvas(root, bg=C_VOID, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.draw_grid(1150, 750)
        
        self.canvas.create_line(20, 50, 20, 730, fill=C_DIM, width=2)
        self.canvas.create_line(1130, 50, 1130, 730, fill=C_DIM, width=2)
        
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

        # --- SEARCH SECTION ---
        self.canvas.create_text(60, 80, text="DATABASE SCAN", fill=C_CYAN, anchor="w", font=("Consolas", 11))
        self.search_var = tk.StringVar()
        
        # KEY CHANGE: Bind the KeyRelease event
        self.entry_search = tk.Entry(root, textvariable=self.search_var, bg=C_DIM, fg=C_CYAN, insertbackground=C_CYAN, 
                                font=("Consolas", 14), bd=0)
        self.entry_search.place(x=60, y=100, width=300, height=30)
        self.entry_search.bind('<KeyRelease>', self.live_search)
        
        NeonCanvasButton(root, "SCAN LIBRARY", self.force_search, color=C_CYAN).place(x=380, y=95)

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

        # --- FOOTER ---
        NeonCanvasButton(root, "UPLOAD DATA", self.add_game, color=C_YELLOW).place(x=60, y=670)
        NeonCanvasButton(root, "PURGE DATA", self.delete_game, color=C_MAGENTA).place(x=240, y=670)
        NeonCanvasButton(root, "REFRESH ALL", self.refresh_list, color=C_TEXT).place(x=950, y=670)

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

    # NEW: Triggers on every keypress
    def live_search(self, event=None):
        name = self.search_var.get()
        if not name: 
            # If empty, show everything again
            self.refresh_list()
            return

        try:
            # Backend now returns a list of matches!
            r = requests.get(f"{API_URL}/search/{name}")
            if r.status_code == 200:
                results = r.json()
                self.game_list.delete(0, tk.END)
                # Populate list with all matches
                for item in results:
                    self.game_list.insert(tk.END, item['name'])
            else:
                # If backend returns empty list or error (e.g. 404 in old version), clear list
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
                # Need to find the exact item details. 
                # Since we might have filtered the list, we fetch by unique name ID from backend.
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
        name = simpledialog.askstring("INPUT", "NAME:")
        if name:
            requests.post(API_URL, json={"name":name, "author":"Manual", "publisher":"N/A", "category":"PC", "date":"2025"})
            self.refresh_list()

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