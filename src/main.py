import io
import pygame
import customtkinter
import json
from tkinter import simpledialog, messagebox
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

        self.window = customtkinter.CTk()
        self.target_scrolled_text = None
        self.swap_button = None
        self.source_scrolled_text = None
        self.source_lang_button = None
        self.target_lang_button = None

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
                isinstance(config, dict) and
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
        self.window.configure(fg_color=self.window_bg_color)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=0)
        self.window.grid_rowconfigure(2, weight=1)

        self.create_entry_widget()
        self.create_buttons()
        self.create_output_widget()

    def create_entry_widget(self):
        input_frame = customtkinter.CTkFrame(self.window, fg_color=self.window_bg_color)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)

        self.source_scrolled_text = customtkinter.CTkTextbox(
            input_frame,
            width=600,
            height=100,
            wrap="word",
            font=self.font,
            fg_color=self.text_bg_color,
            text_color=self.fg_color,
            border_width=0,
            # cursor_color=self.fg_color,
        )
        self.source_scrolled_text.grid(row=0, column=0, sticky="nsew")

        # Bind to underlying Text widget
        self.source_scrolled_text._textbox.bind("<Command-KeyPress>", self.command_keypress_bind)
        self.source_scrolled_text._textbox.bind("<Option-BackSpace>", self.option_backspace_bind)
        self.source_scrolled_text._textbox.bind("<Return>", self.enter_bind)

    def create_buttons(self):
        button_frame = customtkinter.CTkFrame(self.window, fg_color=self.window_bg_color)
        button_frame.grid(row=1, column=0, pady=10)

        # Translate button
        translate_button = customtkinter.CTkButton(
            button_frame,
            text="Translate",
            command=self.translate,
            text_color=self.window_bg_color,
            fg_color=self.fg_color,
            font=self.font,
            border_width=2,
            # padding=(15, 5),
        )
        translate_button.pack(side="left", padx=10)

        # Speak button
        speak_button = customtkinter.CTkButton(
            button_frame,
            text="Vocalize",
            command=self.speak,
            text_color=self.window_bg_color,
            fg_color=self.fg_color,
            font=self.font,
            # padding=(15, 5),
        )
        speak_button.pack(side="left", padx=10)

        # Source language selection button
        self.source_lang_button = customtkinter.CTkButton(
            button_frame,
            text=f"{self.source_lang}",
            command=self.select_source_language,
            text_color=self.window_bg_color,
            fg_color=self.fg_color,
            font=self.font,
            border_width=2,
            # padding=(15, 5),
        )
        self.source_lang_button.pack(side="left", padx=10)

        # Swap button
        self.swap_button = customtkinter.CTkButton(
            button_frame,
            text="<=>",
            command=self.swap_language,
            text_color=self.window_bg_color,
            fg_color=self.fg_color,
            font=("JetBrains Mono", 14),
            width=40,
            # padding=(0, 5),
        )
        self.swap_button.pack(side="left", padx=10)

        # Target language selection button
        self.target_lang_button = customtkinter.CTkButton(
            button_frame,
            text=f"{self.target_lang}",
            command=self.select_target_language,
            text_color=self.window_bg_color,
            fg_color=self.fg_color,
            font=self.font,
            # padding=(15, 5),
        )
        self.target_lang_button.pack(side="left", padx=10)

    def create_output_widget(self):
        output_frame = customtkinter.CTkFrame(self.window, fg_color=self.window_bg_color)
        output_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.target_scrolled_text = customtkinter.CTkTextbox(
            output_frame,
            width=600,
            height=100,
            wrap="word",
            font=self.font,
            fg_color=self.text_bg_color,
            text_color=self.fg_color,
            border_width=0,
            # cursor_color=self.fg_color,
            state="disabled"
        )
        self.target_scrolled_text.grid(row=0, column=0, sticky="nsew")

    def swap_language(self):
        self.source_lang, self.target_lang = self.target_lang, self.source_lang
        self.source_lang_button.configure(text=f"{self.source_lang}")
        self.target_lang_button.configure(text=f"{self.target_lang}")
        new_source_text = self.target_scrolled_text.get("1.0", "end-1c")
        new_target_text = self.source_scrolled_text.get("1.0", "end-1c")

        self.target_scrolled_text.configure(state="normal")
        self.source_scrolled_text.delete("1.0", "end")
        self.target_scrolled_text.delete("1.0", "end")

        self.source_scrolled_text.insert("1.0", new_source_text)
        self.target_scrolled_text.insert("1.0", new_target_text)

        self.target_scrolled_text.configure(state="disabled")
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
            self.source_lang_button.configure(text=f"{self.source_lang}")
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
            self.target_lang_button.configure(text=f"{self.target_lang}")
            self.save_config()
        else:
            self.show_invalid_language_message()

    @staticmethod
    def show_invalid_language_message():
        messagebox.showerror("Invalid Language", "The selected language code is invalid or not supported!")

    def translate(self):
        text = self.source_scrolled_text.get("1.0", "end").strip()

        self.target_scrolled_text.configure(state="normal")
        self.target_scrolled_text.delete("1.0", "end")

        if text:
            translated = self.translate_text(text, self.source_lang, self.target_lang)
            self.target_scrolled_text.insert("end", translated)

        self.target_scrolled_text.configure(state="disabled")

    @staticmethod
    def translate_text(text, source='fr', target='ru'):
        return GoogleTranslator(source=source, target=target).translate(text)

    def speak(self):
        text = self.source_scrolled_text.get("1.0", "end").strip()
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
            self.window.update()

    def command_keypress_bind(self, event):
        if event.char == 'v':
            event.widget.event_generate("<<Paste>>")
        elif event.char == 'c':
            event.widget.event_generate("<<Copy>>")
        elif event.char == 'x':
            event.widget.event_generate("<<Cut>>")
        elif event.char == 'a':
            text = self.source_scrolled_text.textbox
            text.tag_add("sel", "1.0", "end-1c")
        elif event.keysym == 'Left':
            cursor_position = event.widget.index("insert")
            line_start = event.widget.index(f"{cursor_position} linestart")
            event.widget.mark_set("insert", line_start)
        elif event.keysym == 'Right':
            cursor_position = event.widget.index("insert")
            line_end = event.widget.index(f"{cursor_position} lineend")
            event.widget.mark_set("insert", line_end)
        elif event.keysym == 'Up':
            event.widget.mark_set("insert", "1.0")
            event.widget.see("1.0")
        elif event.keysym == 'Down':
            event.widget.mark_set("insert", "end")
            event.widget.see("end")
        elif event.keysym == 'BackSpace':
            current_position = event.widget.index("insert")
            line, char = current_position.split(".")
            line = int(line)
            char = int(char)

            if char >= 1:
                start_of_line = f"{line}.0"
                event.widget.delete(start_of_line, current_position)
            else:
                if line > 1:
                    previous_line_end = event.widget.index(f"{line - 1}.end")
                    event.widget.delete(previous_line_end, f"{line}.0")
        return 'break'

    def option_backspace_bind(self, event=None):
        current_position = event.widget.index("insert")
        line, char = [int(x) for x in current_position.split(".")]

        if char >= 1:
            start_of_word = self.find_start_of_word(current_position, event)
            event.widget.delete(start_of_word, current_position)
        else:
            if line > 1:
                previous_line_end = event.widget.index(f"{line - 1}.end")
                event.widget.delete(previous_line_end, f"{line}.0")

        return 'break'

    def find_start_of_word(self, current_position, event):
        while current_position.split('.')[1] != '0':
            prev_position = event.widget.index(f"{current_position} -1c")
            char = event.widget.get(prev_position, current_position)
            if char == ' ':
                return prev_position
            current_position = prev_position
        return current_position

    def enter_bind(self, event):
        if event.state & 0x0001:
            return
        self.translate()
        return 'break'


if __name__ == "__main__":
    app = GoodTranslatorApp()