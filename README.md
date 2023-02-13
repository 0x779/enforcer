# enforcer
MD5 hash generator and scanner
 
![enforcer_anim](https://user-images.githubusercontent.com/1897654/217857361-8e09c416-85d0-4097-9335-79e20262f1ec.gif)

## generateHashes.py
Generate MD5 hashes for all the files in a selected folder, then store the hash, file name and file size in an SQLite database.

## generateThumbs.py
Generate thumbnails of a certain (configurable) size, and save them next to the original images with the `_thumbs` suffix.

## scan.py
Scan the selected folders against the database of hashes. 
