import io
import pygame
import tkinter as tk
from tkinter import scrolledtext
from gtts import gTTS
from deep_translator import GoogleTranslator


def translate_text(text, source='fr', target='ru'):
    return GoogleTranslator(source=source, target=target).translate(text)


def translate():
    text = text_entry.get("1.0", tk.END).strip()  # Получаем введённый текст

    translated_text.delete("1.0", tk.END)
    if not text:
        return

    translated = translate_text(text)
    translated_text.insert(tk.END, translated)


def speak():
    text = text_entry.get("1.0", tk.END).strip()  # Получаем введённый текст
    if not text:
        return  # Если пусто — ничего не делаем

    tts = gTTS(text=text, lang="fr")  # Генерируем французскую речь
    fp = io.BytesIO()  # Виртуальный файл в памяти
    tts.write_to_fp(fp)
    fp.seek(0)

    pygame.mixer.init()
    pygame.mixer.music.load(fp, 'mp3')
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        root.update()  # Чтобы GUI не зависал


# Создание окна
root = tk.Tk()
root.title("Переводчик + Синтезатор речи")

# Поле для ввода текста
text_entry = scrolledtext.ScrolledText(root, width=70, height=4, wrap=tk.WORD, font=("Arial", 14))
text_entry.pack(pady=5, padx=10)

# Создаём Frame для размещения кнопок
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

# Кнопка "Перевести"
speak_button1 = tk.Button(button_frame, text="Перевести", command=translate)
speak_button1.pack(side=tk.LEFT, padx=5)

# Кнопка "Озвучить"
speak_button2 = tk.Button(button_frame, text="Озвучить", command=speak)
speak_button2.pack(side=tk.LEFT, padx=5)

# Поле для вывода переведённого текста
translated_text = scrolledtext.ScrolledText(root, width=70, height=4, wrap=tk.WORD, state="normal", font=("Arial", 14))
translated_text.pack(pady=5, padx=10)

# Запуск GUI


root.update_idletasks()

root.geometry(f'{root.winfo_width()}x{root.winfo_height()}')

root.mainloop()
