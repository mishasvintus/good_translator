import io
import pygame
import tkinter as tk
from tkinter import scrolledtext, ttk
from gtts import gTTS
from deep_translator import GoogleTranslator


class GoodTranslatorApp:
    def __init__(self):
        self.source_lang = 'fr'
        self.target_lang = 'ru'

        self.window = tk.Tk()
        self.target_scrolled_text = None
        self.swap_button = None
        self.source_scrolled_text = None

        # Configure colors and fonts
        self.bg_color = "#2E3440"  # Dark background
        self.fg_color = "#D8DEE9"  # Light text
        self.accent_color = "#5E81AC"  # Accent color for buttons
        self.hover_color = "#81A1C1"  # Hover color for buttons
        self.scrollbar_bg = "#4C566A"  # Scrollbar background
        self.scrollbar_trough = "#3B4252"  # Scrollbar trough color
        self.font = ("JetBrains Mono", 14)

        self.configure_window()
        self.window.mainloop()

    def configure_window(self):
        self.window.title("GoodTranslator")
        self.window.configure(bg=self.bg_color)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=0)
        self.window.grid_rowconfigure(2, weight=1)

        self.create_entry_widget()
        self.create_buttons()
        self.create_output_widget()

    def create_entry_widget(self):
        input_frame = tk.Frame(self.window, bg=self.bg_color)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)

        self.source_scrolled_text = tk.Text(
            input_frame,
            width=70,
            height=4,
            highlightthickness=0,
            wrap=tk.WORD,
            font=self.font,
            padx=10,
            pady=10,
            bg="#3B4252",
            fg=self.fg_color,
            insertbackground=self.fg_color,  # Cursor color
        )
        self.source_scrolled_text.grid(row=0, column=0, sticky="nsew")
        self.source_scrolled_text.bind("<Command-KeyPress>", self.command_keypress)
        self.source_scrolled_text.bind("<Option-BackSpace>", self.option_keypress)

    def create_buttons(self):
        button_frame = tk.Frame(self.window, bg=self.bg_color)
        button_frame.grid(row=1, column=0, pady=10)

        translate_button = tk.Button(
            button_frame,
            text="Перевести",
            command=self.translate,
            fg=self.bg_color,
            font=self.font,
            bd="2",
            padx=15,
            pady=5
        )
        translate_button.pack(side=tk.LEFT, padx=10)

        # Speak Button
        speak_button = tk.Button(
            button_frame,
            text="Озвучить",
            command=self.speak,
            fg=self.bg_color,
            font=self.font,
            padx=15,
            pady=5
        )
        speak_button.pack(side=tk.LEFT, padx=10)

        # Swap Button
        self.swap_button = tk.Button(
            button_frame,
            text=f"{self.source_lang}->{self.target_lang}",
            command=self.swap_language,
            fg=self.bg_color,
            font=self.font,
            padx=15,
            pady=5
        )
        self.swap_button.pack(side=tk.LEFT, padx=10)

    def create_output_widget(self):
        output_frame = tk.Frame(self.window, bg=self.bg_color)
        output_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.target_scrolled_text = tk.Text(
            output_frame,
            width=70,
            height=4,
            wrap=tk.WORD,
            highlightthickness=0,
            font=self.font,
            padx=10,
            pady=10,
            bg="#3B4252",
            fg=self.fg_color,
            insertbackground=self.fg_color,
            state="disabled"
        )
        self.target_scrolled_text.grid(row=0, column=0, sticky="nsew")

    def translate(self):
        text = self.source_scrolled_text.get("1.0", tk.END).strip()

        self.target_scrolled_text.config(state="normal")
        self.target_scrolled_text.delete("1.0", tk.END)

        if text:
            translated = self.translate_text(text, self.source_lang, self.target_lang)
            self.target_scrolled_text.insert(tk.END, translated)

        self.target_scrolled_text.config(state="disabled")

    @staticmethod
    def translate_text(text, source='fr', target='ru'):
        return GoogleTranslator(source=source, target=target).translate(text)

    def speak(self):
        text = self.source_scrolled_text.get("1.0", tk.END).strip()
        if not text:
            return

        tts = gTTS(text=text, lang=self.source_lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        pygame.mixer.init()
        pygame.mixer.music.load(fp, 'mp3')
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            self.window.update()  # To prevent GUI from freezing

    def swap_language(self):
        self.source_lang, self.target_lang = self.target_lang, self.source_lang
        self.swap_button.config(text=f"{self.source_lang}->{self.target_lang}")

        new_source_text = self.target_scrolled_text.get("1.0", "end-1c")
        new_target_text = self.source_scrolled_text.get("1.0", "end-1c")

        self.target_scrolled_text.config(state="normal")
        self.source_scrolled_text.delete("1.0", "end")
        self.target_scrolled_text.delete("1.0", "end")

        self.source_scrolled_text.insert("1.0", new_source_text)
        self.target_scrolled_text.insert("1.0", new_target_text)

        self.target_scrolled_text.config(state="disabled")

    def command_keypress(self, event):
        if event.char == 'v':
            event.widget.event_generate("<<Paste>>")
        elif event.char == 'c':
            event.widget.event_generate("<<Copy>>")
        elif event.char == 'x':
            event.widget.event_generate("<<Cut>>")
        elif event.char == 'a':
            text = self.source_scrolled_text
            text.tag_add("sel", "1.0", f"end-1c")
        elif event.keysym == 'BackSpace':
            current_position = self.source_scrolled_text.index(tk.INSERT)

            line, char = current_position.split(".")
            line = int(line)
            char = int(char)

            if char >= 1:
                start_of_line = f"{line}.{0}"
                self.source_scrolled_text.delete(start_of_line, current_position)  # Delete to start of line
            else:
                if line > 1:
                    previous_line_end = self.source_scrolled_text.index(f"{line - 1}.end")
                    self.source_scrolled_text.delete(previous_line_end, f"{line}.0")  # Delete line break
        elif event.keysym == 'Left':
            cursor_position = self.source_scrolled_text.index(tk.INSERT)
            line_start = self.source_scrolled_text.index(f"{cursor_position} linestart")
            self.source_scrolled_text.mark_set(tk.INSERT, line_start)
        elif event.keysym == 'Right':
            cursor_position = self.source_scrolled_text.index(tk.INSERT)
            line_end = self.source_scrolled_text.index(f"{cursor_position} lineend")
            self.source_scrolled_text.mark_set(tk.INSERT, line_end)
        elif event.keysym == 'Up':
            self.source_scrolled_text.mark_set(tk.INSERT, "1.0")
            self.source_scrolled_text.see("1.0")
        elif event.keysym == 'Down':
            self.source_scrolled_text.mark_set(tk.INSERT, tk.END)
            self.source_scrolled_text.see(tk.END)

        return 'break'

    def option_keypress(self, event=None):
        current_position = self.source_scrolled_text.index(tk.INSERT)

        line, char = [int(x) for x in current_position.split(".")]

        if char >= 1:
            start_of_word = self.find_start_of_word(current_position)
            if start_of_word != current_position:
                self.source_scrolled_text.delete(start_of_word, current_position)
        else:
            if line > 1:
                previous_line_end = self.source_scrolled_text.index(f"{line - 1}.end")
                self.source_scrolled_text.delete(previous_line_end, f"{line}.0")

        return 'break'

    def find_start_of_word(self, current_position):
        start_of_word = current_position

        while current_position.split('.')[1] != '0':
            prev_position = self.source_scrolled_text.index(f"{current_position} -1c")
            char = self.source_scrolled_text.get(prev_position, current_position)
            if char == ' ':
                return prev_position
            current_position = prev_position
        return current_position


if __name__ == "__main__":
    app = GoodTranslatorApp()