import io
import pygame
import tkinter as tk
from tkinter import scrolledtext
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

        self.configure_window()

        self.window.mainloop()

    def configure_window(self):
        self.window.title("GoodTranslator")
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=0)
        self.window.grid_rowconfigure(2, weight=1)

        self.create_entry_widget()
        self.create_buttons()
        self.create_output_widget()

    def create_entry_widget(self):
        input_frame = tk.Frame(self.window)
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)

        self.source_scrolled_text = scrolledtext.ScrolledText(input_frame,
                                                              # width=70,
                                                              height=4,
                                                              # bg="white",
                                                              highlightthickness=0,
                                                              wrap=tk.WORD,
                                                              font=("JetBrains Mono", 14),
                                                              padx=5,
                                                              pady=5)
        self.source_scrolled_text.grid(row=0, column=0, sticky="nsew")
        self.source_scrolled_text.bind("<Command-KeyPress>", self.command_keypress)

    def create_buttons(self):
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=1, column=0)

        translate_button = tk.Button(button_frame, text="Перевести", command=self.translate)
        translate_button.pack(side=tk.LEFT, padx=10)

        speak_button = tk.Button(button_frame, text="Озвучить", command=self.speak)
        speak_button.pack(side=tk.LEFT, padx=10)

        swap_button = tk.Button(button_frame, text=f"{self.source_lang}->{self.target_lang}",
                                command=self.swap_language)
        swap_button.pack(side=tk.LEFT, padx=10)

    def create_output_widget(self):
        output_frame = tk.Frame(self.window)
        output_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.target_scrolled_text = scrolledtext.ScrolledText(output_frame,
                                                              # width=70,
                                                              height=4,
                                                              wrap=tk.WORD,
                                                              # bg="white",
                                                              highlightthickness=0,
                                                              font=("JetBrains Mono", 14),
                                                              padx=5,
                                                              pady=5,
                                                              state="disabled")
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
            self.window.update()  # Чтобы GUI не зависал

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
        return 'break'


if __name__ == "__main__":
    app = GoodTranslatorApp()
