import io
import pygame
import tkinter as tk
import json
from tkinter import simpledialog
from gtts import gTTS
from deep_translator import GoogleTranslator
import os
import appdirs


class GoodTranslatorApp:
    CONFIG_DIR = appdirs.user_data_dir("GoodTranslator")
    CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

    def __init__(self):
        os.makedirs(self.CONFIG_DIR, exist_ok=True)

        self.languages = GoogleTranslator().get_supported_languages(as_dict=True)

        self.config = self.load_or_create_config()
        self.source_lang = self.config.get("source_lang", "fr")
        self.target_lang = self.config.get("target_lang", "ru")

        self.window = tk.Tk()
        self.target_scrolled_text = None
        self.swap_button = None
        self.source_scrolled_text = None
        self.source_lang_button = None
        self.target_lang_button = None
        self.minsize = None

        self.window_bg_color = "#2E3440"
        self.text_bg_color = "#3B4252"
        self.fg_color = "#D8DEE9"
        self.font = ("JetBrains Mono", 14)

        self.configure_window()

        self.window.mainloop()
    def language_is_correct(self, language):
        return language in self.languages.keys() or language in self.languages.values()

    def load_or_create_config(self):
        try:
            with open(self.CONFIG_PATH, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            default_config = {
                "source_lang": "fr",
                "target_lang": "ru"
            }
            self.save_config(default_config)
            return default_config

    def save_config(self, config=None):
        if not (
            config and
            type(config) == dict and
            self.language_is_correct(config["source_lang"]) and
            self.language_is_correct(config["target_lang"])
        ):
            config = {
                "source_lang": self.source_lang,
                "target_lang": self.target_lang
            }

        with open(self.CONFIG_PATH, "w") as file:
            json.dump(config, file)

    def configure_window(self):
        self.window.title("GoodTranslator")
        self.window.configure(bg=self.window_bg_color)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=0)
        self.window.grid_rowconfigure(2, weight=1)

        self.create_entry_widget()
        self.create_buttons()
        self.create_output_widget()

    def create_entry_widget(self):
        input_frame = tk.Frame(self.window, bg=self.window_bg_color)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)

        self.source_scrolled_text = tk.Text(
            input_frame,
            width=70,
            height=4,
            highlightthickness=0,
            undo=True,
            wrap=tk.WORD,
            font=self.font,
            padx=10,
            pady=10,
            bg=self.text_bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
        )
        self.source_scrolled_text.grid(row=0, column=0, sticky="nsew")
        self.source_scrolled_text.bind("<Command-KeyPress>", self.command_keypress_bind)
        self.source_scrolled_text.bind("<Option-BackSpace>", self.option_backspace_bind)
        self.source_scrolled_text.bind("<Return>", self.enter_bind)
        self.source_scrolled_text.bind("<Tab>", self.tab_bind)

    def create_buttons(self):
        button_frame = tk.Frame(self.window, bg=self.window_bg_color)
        button_frame.grid(row=1, column=0, pady=10)

        # Translate button
        translate_button = tk.Button(
            button_frame,
            text="Translate",
            command=self.translate,
            fg=self.window_bg_color,
            font=self.font,
            bd="2",
            padx=15,
            pady=5
        )
        translate_button.pack(side=tk.LEFT, padx=10)

        # Speak button
        speak_button = tk.Button(
            button_frame,
            text="Vocalize",
            command=self.speak,
            fg=self.window_bg_color,
            font=self.font,
            padx=15,
            pady=5
        )
        speak_button.pack(side=tk.LEFT, padx=10)

        # Source language selection button
        self.source_lang_button = tk.Button(
            button_frame,
            text=f"{self.source_lang}",
            command=self.select_source_language,
            fg=self.window_bg_color,
            font=self.font,
            bd="2",
            padx=15,
            pady=5
        )
        self.source_lang_button.pack(side=tk.LEFT, padx=10)

        # Swap button
        self.swap_button = tk.Button(
            button_frame,
            text="<=>",
            command=self.swap_language,
            fg=self.window_bg_color,
            font=("JetBrains Mono", 14),
            padx=0,
            pady=5
        )
        self.swap_button.pack(side=tk.LEFT, padx=10)

        # Target language selection button
        self.target_lang_button = tk.Button(
            button_frame,
            text=f"{self.target_lang}",
            command=self.select_target_language,
            fg=self.window_bg_color,
            font=self.font,
            padx=15,
            pady=5
        )
        self.target_lang_button.pack(side=tk.LEFT, padx=10)

        self.window.update()
        buttons = [translate_button, speak_button, self.source_lang_button, self.swap_button, self.target_lang_button]
        min_width = sum(button.winfo_width() for button in buttons) + 20 * (len(buttons))
        min_height = 3 * (button_frame.winfo_height() + 20)
        self.window.minsize(min_width, min_height)

    def create_output_widget(self):
        output_frame = tk.Frame(self.window, bg=self.window_bg_color)
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
            bg=self.text_bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            state="disabled"
        )
        self.target_scrolled_text.grid(row=0, column=0, sticky="nsew")

    def swap_language(self):
        self.source_lang, self.target_lang = self.target_lang, self.source_lang
        self.source_lang_button.config(text=f"{self.source_lang}")
        self.target_lang_button.config(text=f"{self.target_lang}")
        new_source_text = self.target_scrolled_text.get("1.0", "end-1c")
        new_target_text = self.source_scrolled_text.get("1.0", "end-1c")

        self.target_scrolled_text.config(state="normal")
        self.source_scrolled_text.delete("1.0", "end")
        self.target_scrolled_text.delete("1.0", "end")

        self.source_scrolled_text.insert("1.0", new_source_text)
        self.target_scrolled_text.insert("1.0", new_target_text)

        self.target_scrolled_text.config(state="disabled")

        self.save_config()

    def select_source_language(self):
        lang = simpledialog.askstring("Choose Source Language",
                                      "Enter the language code (e.g. 'en' or 'english' for English):",
                                      parent=self.window)

        if not lang:
            return

        if self.language_is_correct(lang):
            if lang in self.languages.keys():
                self.source_lang = self.languages[lang]
            else:
                self.source_lang = lang
            self.source_lang_button.config(text=f"{self.source_lang}")
            self.save_config()
        else:
            self.show_invalid_language_message()

    def select_target_language(self):
        lang = simpledialog.askstring("Choose Target Language",
                                      "Enter the language code (e.g. 'en' or 'english' for English):",
                                      parent=self.window)
        if not lang:
            return

        if self.language_is_correct(lang):
            if lang in self.languages.keys():
                self.target_lang = self.languages[lang]
            else:
                self.target_lang = lang
            self.target_lang_button.config(text=f"{self.target_lang}")
            self.save_config()
        else:
            self.show_invalid_language_message()

    @staticmethod
    def show_invalid_language_message():
        tk.messagebox.showerror("Invalid Language", "The selected language code is invalid or not supported!")

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

    def command_keypress_bind(self, event):
        if event.char == 'v':
            event.widget.event_generate("<<Paste>>")
        elif event.char == 'c':
            event.widget.event_generate("<<Copy>>")
        elif event.char == 'x':
            event.widget.event_generate("<<Cut>>")
        elif event.char == 'a':
            text = self.source_scrolled_text
            text.tag_add("sel", "1.0", f"end-1c")
        elif event.char == 'z':
            try:
                self.source_scrolled_text.edit_undo()
            except:
                pass
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
        elif event.keysym == 'BackSpace':
            current_position = self.source_scrolled_text.index(tk.INSERT)

            line, char = current_position.split(".")
            line = int(line)
            char = int(char)

            if char >= 1:
                start_of_line = f"{line}.{0}"
                self.source_scrolled_text.delete(start_of_line, current_position)
            else:
                if line > 1:
                    previous_line_end = self.source_scrolled_text.index(f"{line - 1}.end")
                    self.source_scrolled_text.delete(previous_line_end, f"{line}.0")
        return 'break'

    def option_backspace_bind(self, event=None):
        current_position = self.source_scrolled_text.index(tk.INSERT)

        line, char = [int(x) for x in current_position.split(".")]

        if char >= 1:
            start_of_word = self.find_start_of_word(current_position)
            self.source_scrolled_text.delete(start_of_word, current_position)
        else:
            if line > 1:
                previous_line_end = self.source_scrolled_text.index(f"{line - 1}.end")
                self.source_scrolled_text.delete(previous_line_end, f"{line}.0")

        return 'break'

    def find_start_of_word(self, current_position):
        while current_position.split('.')[1] != '0':
            prev_position = self.source_scrolled_text.index(f"{current_position} -1c")
            char = self.source_scrolled_text.get(prev_position, current_position)
            if char == ' ':
                return prev_position
            current_position = prev_position
        return current_position

    def enter_bind(self, event):
        if event.state == 0:    # only enter
            self.translate()
            return 'break'
        if event.state & 1:     # shift + enter
            self.source_scrolled_text.insert(tk.END, "\n")
            return 'break'
        if event.state & 8:     # command + enter
            self.speak()
            return 'break'
        return 'break'

    def tab_bind(self, event):
        self.swap_language()
        return 'break'

if __name__ == "__main__":
    app = GoodTranslatorApp()
