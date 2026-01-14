#!/usr/bin/env python3
# Python 3.8+
import os
import sys
import time
import secrets
from pathlib import Path

CONFIG_FILE = "config.txt"
WORDLIST_FILE = "wordlist.txt"
ASCII_DIR = "ascii"
DEFAULT_CONFIG = {
    "count_files": "1",
    "words_per_key": "3",
    "output_path": "results"
}

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def read_ascii(name: str) -> str:
    path = Path(ASCII_DIR) / name
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def print_ascii(name: str):
    path = Path(ASCII_DIR) / name
    try:
        with open(path, "r", encoding="utf-8") as f:
            print(f.read())
    except Exception:
        pass

def print_with_ascii(ascii_name: str, text: str = ""):
    art = read_ascii(ascii_name)
    if art:
        print(art)
    if text:
        print(text)

def print_ascii_no_clear(ascii_name: str, text: str = ""):
    """
    Print ASCII + text without automatic cleaning (use before input).
    """
    art = read_ascii(ascii_name)
    if art:
        print(art)
    if text:
        print(text)

def print_timed(*args, sep=" ", end="\n", delay=2, ascii_name: str = None):
    """
    Prints a string (and optionaly ASCII-art), waits `delay` seconds and cleaning the console.
    Made for informational messages, after which theres no input.
    """
    if ascii_name:
        art = read_ascii(ascii_name)
        if art:
            print(art)
    if args:
        print(*args, sep=sep, end=end)
    try:
        time.sleep(delay)
    except KeyboardInterrupt:
        # allow user to interrupt the wait
        pass
    clear_console()

def print_fin():
    fin = read_ascii("fin.txt")
    if fin:
        print(fin)

def write_config(cfg: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        for k, v in cfg.items():
            f.write(f"{k}={v}\n")

def read_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        write_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    cfg = {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    for k, v in DEFAULT_CONFIG.items():
        if not cfg.get(k):
            cfg[k] = v
    return cfg

def sanitize_word(word: str) -> str:
    w = word.strip().replace(" ", "").lower()
    if not w:
        return ""
    allowed = set("abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя-'")
    for ch in w:
        if ch not in allowed:
            return ""
    return w

def load_and_clean_wordlist(path: str) -> list:
    if not os.path.exists(path):
        print_timed(f"Error: wordlist {path} is not found.", ascii_name="0.txt")
        print_fin()
        return []
    cleaned = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            s = sanitize_word(raw)
            if s:
                cleaned.append(s)
    return list(dict.fromkeys(cleaned))

def is_positive_int_str(s: str) -> bool:
    return s.isdigit() and int(s) > 0

def prompt_positive_int(prompt_text: str, default: int, ascii_name: str = "0.txt") -> int:
    resp = input(f"{prompt_text} [{default}]: ").strip()
    clear_console()
    if resp == "":
        return int(default)
    if is_positive_int_str(resp):
        return int(resp)
    print_timed("Invalid value — using defaults.", ascii_name=ascii_name)
    print_fin()
    return int(default)

def ensure_output_path(path: str):
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print_timed(f"Unable to create a directory {path}: {e}", ascii_name="0.txt")
        print_fin()
        sys.exit(1)

def generate_keys(wordlist: list, count_files: int, words_per_key: int, output_path: str):
    total_words = len(wordlist)
    if total_words == 0:
        print_timed("Wordlist is empty after cleaning — generation impossible.", ascii_name="1.txt")
        print_fin()
        return
    ensure_output_path(output_path)
    for file_idx in range(1, count_files + 1):
        selected = [wordlist[secrets.randbelow(total_words)] for _ in range(words_per_key)]
        out_file = Path(output_path) / f"key_{file_idx}.txt"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(" ".join(selected))
    print_timed(f"Generation ended: {count_files} file(s) in {output_path}",)
    print_fin()

def settings_menu(cfg: dict):
    curr_count = cfg.get("count_files", DEFAULT_CONFIG["count_files"])
    curr_words = cfg.get("words_per_key", DEFAULT_CONFIG["words_per_key"])
    curr_path = cfg.get("output_path", DEFAULT_CONFIG["output_path"])

    print_ascii_no_clear("2.txt", "Settings (leave empty, to save the current value):")
    new_count = input(f"Amount of key files [{curr_count}]: ").strip()
    clear_console()
    if new_count:
        if is_positive_int_str(new_count):
            cfg["count_files"] = new_count
        else:
            print_timed("Invalid value — taking previous one.", ascii_name="2.txt")
            print_fin()

    print_ascii_no_clear("2.txt", "Settings (continuation):")
    new_words = input(f"Length of a key — amount of words inside the key [{curr_words}]: ").strip()
    clear_console()
    if new_words:
        if is_positive_int_str(new_words):
            cfg["words_per_key"] = new_words
        else:
            print_timed("Invalid value — taking previous one.", ascii_name="2.txt")
            print_fin()

    print_ascii_no_clear("2.txt", "Settings (continuation):")
    new_path = input(f"Path to save files [{curr_path}]: ").strip()
    clear_console()
    if new_path:
        cfg["output_path"] = new_path

    for k, v in DEFAULT_CONFIG.items():
        if not cfg.get(k):
            cfg[k] = v
    write_config(cfg)
    print_timed("Settings saved.", ascii_name="saved.txt")
    print_fin()

def main_menu():
    cfg = read_config()
    first_run = not os.path.exists(CONFIG_FILE) or cfg == DEFAULT_CONFIG
    while True:
        clear_console()
        print_ascii_no_clear("0.txt", "Main menu:")
        print("1) Generate keys")
        print("2) Settings")
        print("3) Exit")
        choice = input("Choose the section (1/2/3): ").strip()
        clear_console()
        if choice == "1":
            if first_run:
                count = prompt_positive_int("Amount of key files to be generated", int(DEFAULT_CONFIG["count_files"]), "1.txt")
                words_per_key = prompt_positive_int("Length of a key (amount of words inside the key)", int(DEFAULT_CONFIG["words_per_key"]), "1.txt")
                out_path = input(f"Key files destination [{DEFAULT_CONFIG['output_path']}]: ").strip()
                clear_console()
                if not out_path:
                    out_path = DEFAULT_CONFIG["output_path"]
                cfg["count_files"] = str(count)
                cfg["words_per_key"] = str(words_per_key)
                cfg["output_path"] = out_path
                write_config(cfg)
                first_run = False
            else:
                count = int(cfg.get("count_files", DEFAULT_CONFIG["count_files"]))
                words_per_key = int(cfg.get("words_per_key", DEFAULT_CONFIG["words_per_key"]))
                out_path = cfg.get("output_path", DEFAULT_CONFIG["output_path"])

            # load wordlist once, show ASCII-art, then plain text without auto-clear
            wordlist = load_and_clean_wordlist(WORDLIST_FILE)
            print_ascii("saved.txt")
            print("Словарь загружен:", f"{len(wordlist)} слов(а).")
            if len(wordlist) == 0:
                input("Press any key to return to the main menu...")
                continue
            generate_keys(wordlist, count, words_per_key, out_path)
            input("Press any key to return to the main menu...")
        elif choice == "2":
            settings_menu(cfg)
            first_run = False
            input("Press any key to return to the main menu...")
        elif choice == "3":
            print_timed("Leaving.", ascii_name="0.txt")
            print_fin()
            break
        else:
            print_timed("Incorrect selection, enter 1, 2 or 3.", ascii_name="0.txt")
            print_fin()
            input("Press any key to return to the main menu...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        clear_console()
        print_with_ascii("0.txt", "Interrupted by the user.")
        print_fin()
