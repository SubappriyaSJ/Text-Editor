import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, ttk
from collections import deque
import os
import re
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
class Trie:
    def __init__(self):
        self.root = TrieNode()
    def insert(self, word):
        curr = self.root
        for char in word:
            if char not in curr.children:
                curr.children[char] = TrieNode()
            curr = curr.children[char]
        curr.is_end_of_word = True
    def search(self, word):
        curr = self.root
        for char in word:
            if char not in curr.children:
                return False
            curr = curr.children[char]
        return curr.is_end_of_word
    def find_words_with_prefix(self, prefix):
            results = []
            curr = self.root
            for char in prefix:
                char = char.lower()
                if char not in curr.children:
                    return results
                curr = curr.children[char]
            self._dfs(curr, prefix, results)
            return results

    def _dfs(self, node, prefix, results):
        if node.is_end_of_word:
            results.append(prefix)
        for char, child in node.children.items():
            self._dfs(child, prefix + char, results)
dictionary_trie = Trie()
def load_dictionary_trie():
    try:
        with open("dictionary.txt", "r") as f:
            for line in f:
                dictionary_trie.insert(line.strip().lower())
    except FileNotFoundError:
        messagebox.showerror("Error", "dictionary.txt not found. Please provide a valid dictionary.")


from string import ascii_lowercase

def suggest_similar_words(word, trie):
    suggestions = set()

    # Replace each character
    for i in range(len(word)):
        for ch in ascii_lowercase:
            new_word = word[:i] + ch + word[i+1:]
            if trie.search(new_word):
                suggestions.add(new_word)

    # Delete each character
    for i in range(len(word)):
        new_word = word[:i] + word[i+1:]
        if trie.search(new_word):
            suggestions.add(new_word)

    # Insert a character at every position
    for i in range(len(word)+1):
        for ch in ascii_lowercase:
            new_word = word[:i] + ch + word[i:]
            if trie.search(new_word):
                suggestions.add(new_word)

    return list(suggestions)


def check_spelling_with_trie():
    text_area.tag_remove("misspelled", "1.0", tk.END)
    text = text_area.get("1.0", tk.END)
    words = re.findall(r'\b\w+\b', text.lower())
    shown_words = set()  # To avoid multiple popups for the same word

    for word in words:
        if not dictionary_trie.search(word) and word not in shown_words:
            shown_words.add(word)
            start = "1.0"
            while True:
                pos = text_area.search(word, start, stopindex=tk.END, nocase=True)
                if not pos:
                    break
                end = f"{pos}+{len(word)}c"
                text_area.tag_add("misspelled", pos, end)
                start = end

            suggestions = suggest_similar_words(word, dictionary_trie)
            if suggestions:
                messagebox.showinfo("Suggestions", f"Suggestions for '{word}':\n" + ", ".join(suggestions))

    text_area.tag_config("misspelled", foreground="red", underline=True)

load_dictionary_trie()
splash = tk.Tk()
splash.title("Loading...")
splash.geometry("400x200")
splash.configure(bg="#2c3e50")
ttk.Label(splash, text="Loading Text Editor...", font=("Arial", 14), background="#2c3e50", foreground="white").pack(pady=30)
style = ttk.Style()
style.theme_use('clam')
style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
progress = ttk.Progressbar(splash, style="green.Horizontal.TProgressbar", mode='determinate', length=300)
progress.pack(pady=20)
def load():
    for i in range(0, 101, 5):
        splash.update_idletasks()
        progress['value'] = i
        splash.after(50)
    splash.destroy()
splash.after(2000, load)
splash.mainloop()

root = tk.Tk()
root.title("Text Editor")
root.state("zoomed")
current_file = None
current_font_family = "Arial"
current_font_size = 14
undo_stack = []
redo_stack = []
# Initialize dictionary trie
dictionary_trie = Trie()

# Load dictionary from file
def load_dictionary():
    try:
        with open("dictionary.txt", "r") as file:
            for line in file:
                word = line.strip()
                if word:
                    dictionary_trie.insert(word)
    except FileNotFoundError:
        messagebox.showerror("Error", "dictionary.txt not found!")
        root.destroy()

load_dictionary()

clipboard_queue = deque(maxlen=5)
def copy_to_clipboard(event=None):
    try:
        text = text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
    except tk.TclError:
        messagebox.showwarning("Empty", "Nothing selected to copy!")
        return
    root.clipboard_clear()
    root.clipboard_append(text)
    clipboard_queue.append(text)
def cut_to_clipboard(event=None):
    try:
        text = text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
    except tk.TclError:
        messagebox.showwarning("Empty", "Nothing selected to cut!")
        return
    root.clipboard_clear()
    root.clipboard_append(text)
    clipboard_queue.append(text)
    text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
def paste_latest(event=None):
    if clipboard_queue:
        latest = clipboard_queue[-1]
        text_area.insert(tk.INSERT, latest)
    else:
        messagebox.showerror("Empty", "Clipboard is empty.")
def show_history(event=None):
    if not clipboard_queue:
        messagebox.showinfo("History", "Clipboard history is empty.")
        return
    history = "\n".join(f"{i+1}. {item}" for i, item in enumerate(reversed(clipboard_queue)))
    messagebox.showinfo("Clipboard History", history)
def update_title():
    name = os.path.basename(current_file) if current_file else "Untitled"
    root.title(f"{name} - Advanced Text Editor")
def new_file():
    global current_file
    if text_area.get("1.0", tk.END).strip():
        if messagebox.askyesno("Save", "Do you want to save the current file?"):
            save_as()
    text_area.delete("1.0", tk.END)
    current_file = None
    update_title()
def open_file():
    global current_file
    path = filedialog.askopenfilename(defaultextension=".txt",
                                      filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if path:
        current_file = path
        with open(path, "r") as f:
            content = f.read()
        text_area.delete("1.0", tk.END)
        text_area.insert(tk.END, content)
        update_title()
def save_file():
    global current_file
    if current_file:
        with open(current_file, "w") as f:
            f.write(text_area.get("1.0", tk.END))
    else:
        save_as()
def save_as():
    global current_file
    path = filedialog.asksaveasfilename(defaultextension=".txt",
                                        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if path:
        current_file = path
        with open(current_file, "w") as f:
            f.write(text_area.get("1.0", tk.END))
        update_title()
def choose_font_color():
    color = colorchooser.askcolor(title="Choose font color")[1]
    if color:
        text_area.config(fg=color)
def change_font_size(event=None):
    global current_font_size
    try:
        size = int(font_size_var.get())
        current_font_size = size
        text_area.config(font=(current_font_family, current_font_size))
    except:
        pass
def push_undo_stack(event=None):
    undo_stack.append(text_area.get("1.0", tk.END))
    redo_stack.clear()
def undo_action(event=None):
    if undo_stack:
        redo_stack.append(text_area.get("1.0", tk.END))
        last = undo_stack.pop()
        text_area.delete("1.0", tk.END)
        text_area.insert(tk.END, last)
def redo_action(event=None):
    if redo_stack:
        undo_stack.append(text_area.get("1.0", tk.END))
        next_text = redo_stack.pop()
        text_area.delete("1.0", tk.END)
        text_area.insert(tk.END, next_text)
def align_left():
    content = text_area.get("1.0", tk.END)
    text_area.tag_config("left", justify="left")
    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, content, "left")
def align_center():
    content = text_area.get("1.0", tk.END)
    text_area.tag_config("center", justify="center")
    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, content, "center")
def align_right():
    content = text_area.get("1.0", tk.END)
    text_area.tag_config("right", justify="right")
    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, content, "right")
def highlight_search():
    # Remove previous highlights
    text_area.tag_remove("highlight", "1.0", tk.END)
    
    search_term = search_entry.get()
    if not search_term:
        return
    
    start_pos = "1.0"
    while True:
        start_pos = text_area.search(search_term, start_pos, stopindex=tk.END, nocase=True)
        if not start_pos:
            break
        
        end_pos = f"{start_pos}+{len(search_term)}c"
        text_area.tag_add("highlight", start_pos, end_pos)
        start_pos = end_pos
    
    text_area.tag_config("highlight", background="yellow", foreground="black")
def clear_highlight():
    # Remove the highlight tag from the entire text
    text_area.tag_remove("highlight", "1.0", tk.END)
    search_entry.delete(0, tk.END)
def get_completions(prefix, trie):
    node = trie.root
    for char in prefix:
        if char not in node.children:
            return []  # no completions
        node = node.children[char]

    completions = []
    queue = deque([(node, prefix)])
    while queue:
        curr_node, curr_word = queue.popleft()
        if curr_node.is_end_of_word:
            completions.append(curr_word)
        for ch, child in curr_node.children.items():
            queue.append((child, curr_word + ch))
    return completions

toolbar = ttk.Notebook(root)
toolbar.pack(side=tk.TOP, fill=tk.X)
home_tab = ttk.Frame(toolbar)
toolbar.add(home_tab, text="Home")
ttk.Button(home_tab, text="New", command=new_file).pack(side=tk.LEFT, padx=2)
ttk.Button(home_tab, text="Open", command=open_file).pack(side=tk.LEFT, padx=2)
ttk.Button(home_tab, text="Save", command=save_file).pack(side=tk.LEFT, padx=2)
ttk.Button(home_tab, text="Save As", command=save_as).pack(side=tk.LEFT, padx=2)
ttk.Separator(home_tab, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=4)
ttk.Button(home_tab, text="Cut (Ctrl+X)", command=cut_to_clipboard).pack(side=tk.LEFT, padx=2)
ttk.Button(home_tab, text="Copy (Ctrl+C)", command=copy_to_clipboard).pack(side=tk.LEFT, padx=2)
ttk.Button(home_tab, text="Paste (Ctrl+V)", command=paste_latest).pack(side=tk.LEFT, padx=2)
ttk.Separator(home_tab, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=4)
ttk.Button(home_tab, text="Undo (Ctrl+Z)", command=undo_action).pack(side=tk.LEFT, padx=2)
ttk.Button(home_tab, text="Redo (Ctrl+Y)", command=redo_action).pack(side=tk.LEFT, padx=2)
ttk.Button(home_tab, text="Spell Check", command=check_spelling_with_trie).pack(side=tk.LEFT, padx=2)
format_tab = ttk.Frame(toolbar)
toolbar.add(format_tab, text="Format")
ttk.Label(format_tab, text="Font Size:").pack(side=tk.LEFT, padx=5)
font_size_var = tk.StringVar(value=str(current_font_size))
font_box = ttk.Combobox(format_tab, textvariable=font_size_var,
                        values=[8, 10, 12, 14, 16, 18, 20, 24, 28, 32], width=5, state='readonly')
font_box.pack(side=tk.LEFT, padx=5)
font_box.bind("<<ComboboxSelected>>", change_font_size)
ttk.Button(format_tab, text="Font Color", command=choose_font_color).pack(side=tk.LEFT, padx=5)
ttk.Button(format_tab, text="Align Left", command=align_left).pack(side=tk.LEFT, padx=2)
ttk.Button(format_tab, text="Align Center", command=align_center).pack(side=tk.LEFT, padx=2)
ttk.Button(format_tab, text="Align Right", command=align_right).pack(side=tk.LEFT, padx=2)
view_tab = ttk.Frame(toolbar)
toolbar.add(view_tab, text="View")
ttk.Button(view_tab, text="Zoom In", command=lambda: font_size_var.set(str(int(font_size_var.get()) + 2))).pack(side=tk.LEFT, padx=5)
ttk.Button(view_tab, text="Zoom Out", command=lambda: font_size_var.set(str(int(font_size_var.get()) - 2))).pack(side=tk.LEFT, padx=5)
font_box.bind("<FocusOut>", change_font_size)
help_tab = ttk.Frame(toolbar)
toolbar.add(help_tab, text="Help")
ttk.Button(help_tab, text="About", command=lambda: messagebox.showinfo("About", "Advanced Text Editor by Jana")).pack(padx=10, pady=10)
text_area = tk.Text(root, wrap=tk.WORD, font=(current_font_family, current_font_size), undo=False)
text_area.pack(expand=True, fill=tk.BOTH)
text_area.bind("<KeyRelease>", push_undo_stack)
root.bind("<Control-z>", undo_action)
root.bind("<Control-y>", redo_action)
root.bind("<Control-c>", copy_to_clipboard)
root.bind("<Control-x>", cut_to_clipboard)
root.bind("<Control-v>", paste_latest)
root.bind("<Control-h>", show_history)
search_tab = ttk.Frame(toolbar)
toolbar.add(search_tab, text="Search")

ttk.Label(search_tab, text="Find:").pack(side=tk.LEFT, padx=5)
search_entry = ttk.Entry(search_tab, width=30)
search_entry.pack(side=tk.LEFT, padx=5)

ttk.Button(search_tab, text="Search", command=highlight_search).pack(side=tk.LEFT, padx=5)
ttk.Button(search_tab, text="Cancel", command=clear_highlight).pack(side=tk.LEFT, padx=5)
suggestion_box = None  # global variable to hold the popup

def show_suggestions(event=None):
    global suggestion_box

    # Remove previous suggestion box
    if suggestion_box:
        suggestion_box.destroy()
        suggestion_box = None

    cursor_pos = text_area.index(tk.INSERT)
    start = f"{cursor_pos} wordstart"
    word = text_area.get(start, cursor_pos)

    if not word:
        return

    completions = get_completions(word.lower(), dictionary_trie)
    if not completions:
        return

    # Create a Listbox popup
    suggestion_box = tk.Toplevel(root)
    suggestion_box.wm_overrideredirect(True)

    try:
        x, y, _, _ = text_area.bbox(tk.INSERT)
        x += text_area.winfo_rootx()
        y += text_area.winfo_rooty() + 20
        suggestion_box.geometry(f"+{x}+{y}")
    except TypeError:
        # cursor not visible
        suggestion_box.destroy()
        return

    listbox = tk.Listbox(suggestion_box, width=30)
    listbox.pack()

    for item in completions[:10]:  # show top 10 suggestions
        listbox.insert(tk.END, item)

    def select_completion(event):
        selection = listbox.get(tk.ACTIVE)
        text_area.delete(start, cursor_pos)
        text_area.insert(start, selection)
        suggestion_box.destroy()

    listbox.bind("<Double-Button-1>", select_completion)
    listbox.bind("<Return>", select_completion)
def load_dictionary():
    try:
        with open("dictionary.txt", "r") as file:
            for line in file:
                word = line.strip()
                if word:
                    dictionary_trie.insert(word)
    except FileNotFoundError:
        messagebox.showerror("Error", "dictionary.txt not found!")
        root.destroy()
autocomplete_listbox = None

def show_autocomplete(event=None):
    global autocomplete_listbox
    if autocomplete_listbox:
        autocomplete_listbox.destroy()

    cursor_pos = text_area.index(tk.INSERT)
    line, column = map(int, cursor_pos.split('.'))
    start = f"{line}.{column}"

    content = text_area.get("1.0", start)
    match = re.search(r'(\b\w+)$', content)
    if not match:
        return
    prefix = match.group(1)

    suggestions = dictionary_trie.find_words_with_prefix(prefix)
    if not suggestions:
        return

    autocomplete_listbox = tk.Listbox(root, height=min(5, len(suggestions)))
    x = text_area.winfo_rootx() + 5
    y = text_area.winfo_rooty() + 25
    autocomplete_listbox.place(x=x, y=y)

    for suggestion in suggestions:
        autocomplete_listbox.insert(tk.END, suggestion)

    autocomplete_listbox.bind("<<ListboxSelect>>", lambda e: insert_autocomplete(prefix))

def insert_autocomplete(prefix):
    global autocomplete_listbox
    if not autocomplete_listbox:
        return
    selection = autocomplete_listbox.curselection()
    if selection:
        chosen_word = autocomplete_listbox.get(selection[0])
        cursor_pos = text_area.index(tk.INSERT)
        line, column = map(int, cursor_pos.split('.'))
        start = f"{line}.{column - len(prefix)}"
        end = f"{line}.{column}"
        text_area.delete(start, end)
        text_area.insert(start, chosen_word)
    autocomplete_listbox.destroy()
    autocomplete_listbox = None

# ---------- Bindings ----------
text_area.bind("<KeyRelease>", show_autocomplete)

root.mainloop()
