import os
import sqlite3
import asyncio
import tkinter as tk
from tkinter import filedialog, messagebox
from tqdm import tqdm
from PIL import Image
from pathlib import Path

size = 512, 512

async def resize_image(file_path):
    with Image.open(file_path) as im:
        im.thumbnail(size)
        im.save(os.path.join(os.path.dirname(file_path), Path(file_path).stem  + "_thumb.jpg"), "JPEG")

async def process_file(file_path, file_name, pbar):
    await resize_image(file_path)
    pbar.set_description(f"Processing: {file_name.ljust(30)[:30]}")
    pbar.update(1)

async def process_folder(folder_path, pbar):
    tasks = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            task = asyncio.create_task(process_file(file_path, file_name, pbar))
            tasks.append(task)
    await asyncio.gather(*tasks)

async def main():
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(parent=root, title="Choose a folder")
    root.destroy()

    num_files = sum(len(files) for root, dirs, files in os.walk(folder_path))
    pbar = tqdm(total=num_files, desc='Creating thumbnails', colour="green")

    await process_folder(folder_path, pbar)

    pbar.close()