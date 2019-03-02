# ArchiveRotate
Rotate backup files/folders to keep expected free space on disk.
Ordering is based on alphabetical order, so it works for names
e.g. with timestamp at the beginning.
Files/folders with the 'smallest' names will be removed as the first - 
e.g. file 'a' will be removed before file 'b' or file '0001' will be removed before file '0111'.
