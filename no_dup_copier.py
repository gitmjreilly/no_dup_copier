#!/usr/bin/python3.8

import os
import sys
from pathlib import Path
import hashlib
from typing import Dict
import shutil



SOURCE_BASE_DIR = Path("d:/source_pictures")
DESTINATION_BASE_DIR = Path("d:/destination_pictures")

CHUNK_SIZE = 8192 * 512


def get_file_checksum(filename : Path) -> str:
    """ Given a filename, return a hexdigest string """
    with open(filename, "rb") as f:
        hash = hashlib.blake2b()
        chunk_num = 0
        while True:
            chunk = f.read(CHUNK_SIZE)
            if len(chunk) == 0:
                break
            hash.update(chunk)
            chunk_num += 1

    return(str(hash.hexdigest()))


def folders_are_mutually_relative(f1 : Path, f2 : Path) -> int:
    """ 
    Check if two folders are relative to each other

    if f1 is within f2 return 1

    if f2 is within f1 return 2

    else return 0
    
    """

    try:
        f1.relative_to(f2)
        return(1)
    except:
        pass
        
    try:
        f2.relative_to(f1)
        return(2)
    except:
        pass
        

    return(0)




def main():
    print("No duplicate file copier.")

    num_files_seen = 0
    num_copied = 0
    num_duplicates = 0
    num_symlinks = 0
    num_non_regular = 0
    copy_info_by_checksum : Dict[str, Path] = {}

    n = folders_are_mutually_relative(SOURCE_BASE_DIR, DESTINATION_BASE_DIR)
    if (n == 1):
        print("ERROR Source is within dest; not allowed!")
        sys.exit(1)
    elif (n == 2):
        print("ERROR Destination folder is within the Source folder; not allowed!")
        sys.exit(1)

 


    for (fully_qualified_source_dir, _, unqualified_file_names) in os.walk(SOURCE_BASE_DIR):

        fully_qualified_source_dir = Path(fully_qualified_source_dir)

        print("\n+++++++++++++++++++++")
        # print("DEBUG fully qualified source dir [%s] " % (fully_qualified_source_dir))

        #
        # create the qualified dir based on the qualified_source_dir
        # We do this by looking at the number of parts in the SOURCE_BASE_DIR
        # and removing that many parts from a copy of the fully_qualified_source_dir
        # I copied the parts to a list to do this...
        #
        l = list(fully_qualified_source_dir.parts)
        l = l[len(SOURCE_BASE_DIR.parts):]
        
        qualified_dir = Path("./")
        for part in l:
            qualified_dir = qualified_dir / part

        # print("DEBUG qualified dir [%s] " % (qualified_dir))

        fully_qualified_destination_dir = DESTINATION_BASE_DIR /  qualified_dir
        # print("DEBUG fully qualified destination dir [%s] " % (fully_qualified_destination_dir))
        fully_qualified_destination_dir.mkdir(parents = True, exist_ok=True)

        for unqualified_file_name in unqualified_file_names:
            num_files_seen += 1
            print("  ########")
                     
            fully_qualified_source_name = fully_qualified_source_dir / unqualified_file_name
            fully_qualified_destination_name = fully_qualified_destination_dir / unqualified_file_name

            print("  SOURCE Name   [%s]" % (fully_qualified_source_name))
            if (not fully_qualified_source_name.is_file() ):
                print("INFO source file is not a regular file; skipping it.")
                num_non_regular += 1
                continue

            if (fully_qualified_source_name.is_symlink()):
                print("INFO source file is symlink; skipping it.")
                num_symlinks += 1
                continue


            check_sum = get_file_checksum(fully_qualified_source_name)
            # print("  DEBUG      Digest is [%s]" % check_sum)
            print("  DEST  Name    [%s]" % (fully_qualified_destination_name))

            if check_sum not in copy_info_by_checksum:
                print("  INFO - We have not seen this file before; will copy it")
                shutil.copy(str(fully_qualified_source_name), str(fully_qualified_destination_name))
                copy_info_by_checksum[check_sum] = fully_qualified_source_name
                num_copied += 1
            else:
                print("  INFO We already saw %s - will NOT copy" % (fully_qualified_source_name))
                print("  It was copied as [%s]" % (copy_info_by_checksum[check_sum]))
                num_duplicates += 1

    print("Num files seen : %d" % (num_files_seen))
    print("Num copied     : %d" % (num_copied))
    print("Num dups       : %d" % (num_duplicates))
    print("Num symlinks   : %d" % (num_symlinks))
    print("Num non_reg    : %d" % (num_non_regular))

#
main()
