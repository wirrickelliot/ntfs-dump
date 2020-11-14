# NTFS DUMP

A simple NTFS file system parser. Does not support file records with non-resident attributes. Limited file signature support. Requires Python 3.

## Features

- Takes two arguments in the following order
    - image file (IMAGE)
        - A disk image
    - volume offset (VOLOFFSET)
        - The offset in bytes to the NTFS formatted volume
- Parses the boot sector to determine the location of the master file table (MFT)
- Parses MFT to locate all files and directories
- Writes to STDOUT all files on the NTFS volume including at least the following attributes:
    - File Name
    - File Path
    - File type (derived from file signature)
    - Creation date
    - Last modified date
    - Allocated size of file
    - Actual size of file

## Example Usage

```
$ python3 ntfs_dump.py ntfs-test.img 1048576
64: Downloads
        File Path: /
        File Type: Directory
        Date Created: 2020-10-15 17:43:54.863980 UTC
        Date Modified: 2020-10-15 17:43:54.863980 UTC
        Allocated Size: 0 bytes
        Real Size: 0 bytes
65:
        File Name: Documents
        File Path: /
        File Type: Directory
        Date Created: 2020-10-15 17:45:28.212008 UTC
        Date Modified: 2020-10-15 17:45:28.212008 UTC
        Allocated Size: 0 bytes
        Real Size: 0 bytes
66:
        File Name: Music
        File Path: /
        File Type: Directory
        Date Created: 2020-10-15 17:46:08.756946 UTC
        Date Modified: 2020-10-15 17:46:08.756946 UTC
        Allocated Size: 0 bytes
        Real Size: 0 bytes
```
