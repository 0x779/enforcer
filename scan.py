from datetime import datetime
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
from PIL import Image, ImageDraw, ImageFont

result_images = []

async def calculate_md5(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
        return hashlib.md5(content).hexdigest()

async def check_if_hash_exists(hash, filesize, cursor):
    cursor.execute("SELECT * FROM hashes WHERE hash=? AND file_size=?", (hash, filesize))
    return cursor is not None

async def process_file(file_path, cursor, pbar, resultImage):
    hash = await calculate_md5(file_path)
    if await check_if_hash_exists(hash, os.path.getsize(file_path), cursor):
        for row in cursor.fetchall():
            pbar.write("│ " + colored(f"{link(os.path.dirname(file_path), os.path.basename(file_path).ljust(35)[:35])}", 'red') + " │ " + colored(f"{link(os.path.join(os.path.join(os.getcwd(), 'thumbs'), Path(row[0]).stem + '_thumb.jpg'), row[0].ljust(40)[:40])}", 'green') + " │ " + colored(f"{row[2].ljust(35)[:35]}", 'blue') + "│")
            if resultImage:
                result_images.append(combine_images(file_path, os.path.join(os.path.join(os.getcwd(), 'thumbs'), Path(row[0]).stem + '_thumb.jpg'), 50))

    pbar.set_description(f"Processing: {os.path.basename(file_path).ljust(33)[:33]}")
    pbar.update(1)

async def process_folder(folder_path, cursor, pbar, resultImage):
    tasks = []
    pbar.write('┌───────── Current file name ─────────┬─────────── Original file name ───────────┬──────────────── Hash ──────────────┐')
    pbar.write('│                                     │                                          │                                    │')
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            task = asyncio.create_task(process_file(file_path, cursor, pbar, resultImage))
            tasks.append(task)
    await asyncio.gather(*tasks)
    pbar.write('└─────────────────────────────────────┴──────────────────────────────────────────┴────────────────────────────────────┘')
    pbar.set_description_str("Done!")
    if resultImage and len(result_images) > 0:
        combine_result(result_images);

async def main(resultImage: bool = False):
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

    await process_folder(folder_path, cursor, pbar, resultImage)

    pbar.close()
    conn.close()

def link(uri, label=None):
    if label is None: 
        label = uri
    parameters = ''

    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST 
    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'

    return escape_mask.format(parameters, uri, label)


def combine_images(img1, img2, margin=50):
    # Open the two images
    image1 = Image.open(img1)
    image2 = Image.open(img2)

    # Get the width and height of the images
    width1, height1 = image1.size
    width2, height2 = image2.size

    # Resize the first image to match the height of the second image
    ratio = height2 / height1
    width1 = int(width1 * ratio)
    image1 = image1.resize((width1, height2))

    # Calculate the total width and height of the combined image
    total_width = width1 + width2 + margin

    # Create a new image with the total width and height
    new_image = Image.new("RGB", (total_width + margin * 2, height2 + margin *2), (50, 50, 50))

    # Paste the two images into the new image
    new_image.paste(image1, (margin, margin))
    new_image.paste(image2, (width1 + margin * 2, margin))

    # Draw the filenames under the images
    draw = ImageDraw.Draw(new_image)
    font = ImageFont.truetype("arial.ttf", 16)
    draw.text((margin, height2 + margin + 10), os.path.basename(img1), font=font)
    draw.text((width1 + margin *2, height2 + margin + 10), os.path.basename(img2), font=font)

    return new_image



def combine_result(images):
    # Create a new image, with the width of the first result image and multiply its height by the number of images
    result_img = Image.new("RGB", (images[0].size[0], len(images) * images[0].size[1]), (50, 50, 50))
    for idx, img in enumerate(images):
        result_img.paste(img, (0, idx * 612))

    # Save the result image
    files = [('PNG', '*.png')]
    defaultFilename = 'enforcerResult-{date:%Y-%m-%d_%H-%M-%S}.png'.format( date=datetime.now() )
    file = filedialog.asksaveasfilename(initialfile = defaultFilename, filetypes = files, defaultextension = files, title="Choose where to save the scan result image")

    result_img.save(file)


