import hashlib
import os
import sqlite3
import asyncio
import tkinter as tk
from tkinter import filedialog, messagebox
from termcolor import colored

async def calculate_md5(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
        return hashlib.md5(content).hexdigest()

async def insert_hash(hash, file_path, cursor):
    cursor.execute("INSERT INTO hashes (hash, file_path) VALUES (?, ?)", (hash, file_path))

async def check_if_hash_exists(hash, cursor):
    cursor.execute("SELECT * FROM hashes WHERE hash=?", (hash,))
    return cursor.fetchone() is not None

async def process_file(file_path, cursor, pbar):
    hash = await calculate_md5(file_path)
    await insert_hash(hash, file_path, cursor)
    pbar.update(1)

async def process_folder(folder_path, cursor, pbar):
    tasks = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            task = asyncio.create_task(process_file(file_path, cursor, pbar))
            tasks.append(task)
    await asyncio.gather(*tasks)

async def generate_hashes(folder_path):
    conn = sqlite3.connect("hashes.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hashes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT NOT NULL,
            file_path TEXT NOT NULL
        )
    ''')

    num_files = sum(len(files) for root, dirs, files in os.walk(folder_path))
    pbar = tqdm(total=num_files, desc='Generating Hashes')

    await process_folder(folder_path, cursor, pbar)

    pbar.close()
    conn.commit()
    conn.close()

async def check_hashes(folder_path):
    conn = sqlite3.connect("hashes.db")
    cursor = conn.cursor()

    num_files = sum(len(files) for root, dirs, files in os.walk(folder_path))
    pbar = tqdm(total=num_files, desc='Checking Hashes')

    await process_folder(folder_path, cursor, pbar)

    pbar.close()
    conn.close()

def main():
    root = tk.Tk()
    root.withdraw()

    action = messagebox.askyesno("Choose Action", "Do you want to generate new hashes or check existing hashes?")

    if action:
        folder_path = filedialog.askdirectory(parent=root, title="Choose a folder


