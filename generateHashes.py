import hashlib
import os
import sqlite3
import asyncio
import tkinter as tk
from tkinter import filedialog, messagebox
from tqdm import tqdm

async def calculate_md5(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
        return hashlib.md5(content).hexdigest()

async def store_hash_in_db(file_name, file_size, hash, conn):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO hashes(file_name, file_size, hash) VALUES (?,?,?)", (file_name, file_size, hash))
    conn.commit()

async def check_if_hash_exists(hash, cursor):
    cursor.execute("SELECT * FROM hashes WHERE hash=?", (hash,))
    return cursor.fetchone() is not None

async def process_file(file_path, file_name, file_size, conn, pbar):
    hash = await calculate_md5(file_path)
    cursor = conn.cursor()
    if not await check_if_hash_exists(hash, cursor):
        await store_hash_in_db(file_name, file_size, hash, conn)
        pbar.set_description(f"Processing: {file_name.ljust(30)[:30]}")
        pbar.update(1)

async def process_folder(folder_path, conn, pbar):
    tasks = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            task = asyncio.create_task(process_file(file_path, file_name, file_size, conn, pbar))
            tasks.append(task)
    await asyncio.gather(*tasks)

async def main():
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(parent=root, title="Choose a folder to scan")
    root.destroy()

    conn = sqlite3.connect("hashes.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS hashes (file_name TEXT, file_size INT, hash TEXT)")

    num_files = sum(len(files) for root, dirs, files in os.walk(folder_path))
    pbar = tqdm(total=num_files, desc='Calculating Hashes', colour="green")

    await process_folder(folder_path, conn, pbar)

    pbar.close()
    conn.close()