# enforcer
MD5 hash generator and scanner
 
![enforcer_anim](https://user-images.githubusercontent.com/1897654/217857361-8e09c416-85d0-4097-9335-79e20262f1ec.gif)

## How to use
```
python . --arguments

Arguments:
    --scan - Scan the selected folder against known hashes (in hashes.db)\n
    --scan result - Scan the selected folder against known hashes (in hashes.db) and save a comparison result image\n
    --generate hashes - Generate MD5 hashes for all the files in a selected folder, then store the hash, file name and file size in an SQLite database.\n
    --generate thumbs - Generate thumbnails of a certain (configurable) size, and save them next to the original images with the `_thumbs` suffix.\n
```
