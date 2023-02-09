import hashlib
import os
import sqlite3
import asyncio
import sys
import tkinter as tk
from tkinter import filedialog
from termcolor import colored
from tqdm import tqdm
from pathlib import Path

async def calculate_md5(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
        return hashlib.md5(content).hexdigest()

async def check_if_hash_exists(hash, filesize, cursor):
    cursor.execute("SELECT * FROM hashes WHERE hash=? AND file_size=?", (hash, filesize))
    return cursor is not None

async def process_file(file_path, cursor, pbar):
    hash = await calculate_md5(file_path)
    if await check_if_hash_exists(hash, os.path.getsize(file_path), cursor):
        for row in cursor.fetchall():
            pbar.write("│ " + colored(f"{link(os.path.dirname(file_path), os.path.basename(file_path).ljust(35)[:35])}", 'red') + " │ " + colored(f"{link(os.path.join(os.path.join(os.getcwd(), 'thumbs'), Path(row[0]).stem + '_thumb.jpg'), row[0].ljust(40)[:40])}", 'green') + " │ " + colored(f"{row[2].ljust(35)[:35]}", 'blue') + "│")
    
    pbar.set_description(f"Processing: {os.path.basename(file_path).ljust(33)[:33]}")
    pbar.update(1)

async def process_folder(folder_path, cursor, pbar):
    tasks = []
    pbar.write('┌───────── Current file name ─────────┬─────────── Original file name ───────────┬──────────────── Hash ──────────────┐')
    pbar.write('│                                     │                                          │                                    │')
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            task = asyncio.create_task(process_file(file_path, cursor, pbar))
            tasks.append(task)
    await asyncio.gather(*tasks)
    pbar.write('└─────────────────────────────────────┴──────────────────────────────────────────┴────────────────────────────────────┘')
    pbar.set_description_str("Done!")

async def main():
    root = tk.Tk()
    root.withdraw()

    # Check if SQLite database is present
    if not (os.path.isfile("hashes.db")):
        sys.exit("Database not found!")
    else:
        folder_path = filedialog.askdirectory(parent=root, title="Choose a folder to scan")

    root.destroy()

    # Connect to SQLite database
    conn = sqlite3.connect("hashes.db")
    cursor = conn.cursor()
    
    num_files = sum(len(files) for root, dirs, files in os.walk(folder_path))
    pbar = tqdm(total=num_files, desc='Checking Hashes', colour="green")

    await process_folder(folder_path, cursor, pbar)

    pbar.close()
    conn.close()

def link(uri, label=None):
    if label is None: 
        label = uri
    parameters = ''

    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST 
    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'

    return escape_mask.format(parameters, uri, label)


if __name__ == '__main__':
    asyncio.run(main())

    input("\nPress enter to exit;")