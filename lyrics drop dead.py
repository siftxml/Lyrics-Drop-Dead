import tkinter as tk
import time
import random

try:
    import pygame
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False


AUDIO_FILE = "" 

LYRICS = [
    (1.2, "'CUZ I ALWAYS HAD A VISION OF US STANDING LIKE THIS", 300),
    (4.5, "ALL PRESSED UP IN THE BATHROOM LINE", 350),
    (7.8, "YOU'RE LOOKING LIKE AN ANGEL ON THE WALLS OF VERSAILLES", 250),
    (11.8, "THE MOST ALIVE I'VE EVER BEEN", 350),
    (15, "BUT KISS ME AND I MIGHT", 300),
    (18.8, "KISS ME AND I MIGHT", 350),
    (22.8, "KISS ME AND I MIGHT", 350),
    (24.8, "DROP DEAD", 500),  
]
 

BOX_W, BOX_H = 300, 250
FONT = ("Helvetica", 22, "bold")
FONT_FULLSCREEN = ("Helvetica", 80, "bold")  
BG_COLOR = "#fdfdf5"
FG_COLOR = "#111111"

ALT_BG_COLOR = "#111111"
ALT_FG_COLOR = "#fdfdf5"
FLASH_SPEED = 400         

RISE_SPEED = 90          
BOTTOM_SPAWN_OFFSET = 150  


class LyricBox:
    """Kotak lirik tunggal yang memunculkan teks kata demi kata dan meluncur naik."""

    def __init__(self, master, text, x, y, word_delay, initial_alt=False, is_fullscreen=False):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)   
        self.win.attributes("-topmost", True)
        self.is_fullscreen = is_fullscreen
        self.word_delay = word_delay  
        
        
        if self.is_fullscreen:
            
            current_bg = ALT_BG_COLOR
            current_fg = ALT_FG_COLOR
        else:
            current_bg = ALT_BG_COLOR if initial_alt else BG_COLOR
            current_fg = ALT_FG_COLOR if initial_alt else FG_COLOR
        
        self.win.configure(bg=current_bg)
        
        if self.is_fullscreen:
            self.win.state('zoomed') 
            font_to_use = FONT_FULLSCREEN
            wraplen = self.win.winfo_screenwidth() - 100
        else:
            self.win.geometry(f"{BOX_W}x{BOX_H}+{int(x)}+{int(y)}")
            font_to_use = FONT
            wraplen = BOX_W - 30
            
        self.win.resizable(False, False)

        self.words = text.split()
        self.current_word_count = 0

        self.label = tk.Label(
            self.win,
            text="",
            font=font_to_use,
            bg=current_bg,
            fg=current_fg,
            wraplength=wraplen,
            justify="center"
        )
        self.label.pack(expand=True, fill="both", padx=15, pady=15)

        self.reveal_word_by_word()

        self.x = x
        self.y = float(y)

    def rise(self, dy):
        if self.is_fullscreen:
            return
        self.y -= dy
        self.win.geometry(f"{BOX_W}x{BOX_H}+{int(self.x)}+{int(self.y)}")

    def is_offscreen(self):
        if self.is_fullscreen:
            return False  
        return self.y + BOX_H < -50
    
    def reveal_word_by_word(self):
        """Memunculkan kata penuh satu per satu mengikuti ketukan jeda musik."""
        if self.current_word_count <= len(self.words):
            displayed_text = " ".join(self.words[:self.current_word_count])
            self.label.config(text=displayed_text)
            self.current_word_count += 1
            
            self.win.after(self.word_delay, self.reveal_word_by_word)

    def set_colors(self, use_alt):
        """Mengubah warna kotak secara instan mengikuti komando aplikasi utama."""

        if self.is_fullscreen:
            return
            
        try:
            bg = ALT_BG_COLOR if use_alt else BG_COLOR
            fg = ALT_FG_COLOR if use_alt else FG_COLOR
            self.win.configure(bg=bg)
            self.label.configure(bg=bg, fg=fg)
        except tk.TclError:
            pass


class LyricFloatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lyrics by siftxml")
        self.root.geometry(f"{BOX_W}x{BOX_H}")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.start_btn = tk.Button(
            root, text="Start", font=FONT, bg=BG_COLOR, fg=FG_COLOR,
            relief="flat", command=self.start
        )
        self.start_btn.pack(expand=True, fill="both", padx=15, pady=15)

        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()

        self.next_lyric_idx = 0
        self.boxes = []
        self.last_frame_time = None
        self.current_side = "left"  
        self.global_alt_color = False 

    def random_safe_x(self):
        """Alternate between left and right positions only."""
        center_x = self.screen_w // 2
        spacing = BOX_W + 60  
        left_x = center_x - spacing
        right_x = center_x + 60
        
        if self.current_side == "left":
            self.current_side = "right"
            return left_x
        else:
            self.current_side = "left"
            return right_x

    def start(self):
        self.start_btn.pack_forget()
        self.root.iconify()  
        self.start_time = time.time()
        self.last_frame_time = self.start_time

        if HAS_AUDIO and AUDIO_FILE:
            try:
                pygame.mixer.init()
                pygame.mixer.music.load(AUDIO_FILE)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Audio failed to load: {e}")

        self.tick()
        self.flash_all_boxes()

    def flash_all_boxes(self):
        """Mengubah warna seluruh kotak secara bersamaan."""
        self.global_alt_color = not self.global_alt_color
        for box in self.boxes:
            box.set_colors(self.global_alt_color)
            
        if self.next_lyric_idx < len(LYRICS) or self.boxes:
            self.root.after(FLASH_SPEED, self.flash_all_boxes)

    def tick(self):
        now = time.time()
        elapsed = now - self.start_time
        dt = now - self.last_frame_time
        self.last_frame_time = now

        while (self.next_lyric_idx < len(LYRICS) and
               LYRICS[self.next_lyric_idx][0] <= elapsed):
            t, text, word_delay = LYRICS[self.next_lyric_idx]
            
            is_drop_dead = (text == "DROP DEAD")
            x = self.random_safe_x()
            y = self.screen_h - BOX_H - BOTTOM_SPAWN_OFFSET
            
            box = LyricBox(
                self.root, 
                text, 
                x, 
                y, 
                word_delay=word_delay, 
                initial_alt=self.global_alt_color, 
                is_fullscreen=is_drop_dead
            )
            self.boxes.append(box)
            self.next_lyric_idx += 1

        dy = RISE_SPEED * dt
        for box in self.boxes:
            box.rise(dy)

        still_visible = []
        for box in self.boxes:
            if box.is_offscreen():
                try:
                    box.win.destroy()
                except tk.TclError:
                    pass
            else:
                still_visible.append(box)
        self.boxes = still_visible

        if self.next_lyric_idx < len(LYRICS) or self.boxes:
            self.root.after(16, self.tick) 


if __name__ == "__main__":
    root = tk.Tk()
    app = LyricFloatApp(root)
    root.mainloop()


#siftxml