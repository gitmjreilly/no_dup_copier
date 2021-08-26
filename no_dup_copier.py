#!/usr/bin/python3.8

import os
import sys
from pathlib import Path
import hashlib
from typing import Dict
import shutil


CHUNK_SIZE = 8192 * 512


def get_file_hash(filename : Path) -> str:
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


def get_relative_path_from_absolute(base_dir : Path, absolute_dir : Path) -> Path:
    """ 
    Given a base dir like  'c:/base'

    and absolute_dir like  'c:/base/d1/d2'

    return the relative path d1/d2
    
    """
    #
    # create the relative dir based on the base_dir and absolute_dir
    # We do this by looking at the number of parts in the base_dir
    # and removing that many parts from a copy of the absolute_source_dir
    # I copied the parts to a list to do this...
    #
    l = list(absolute_dir.parts)
    l = l[len(base_dir.parts):]
    
    relative_dir = Path("./")
    for part in l:
        relative_dir = relative_dir / part

    return(relative_dir)

def get_hashes_from_dir(the_base_dir : Path) -> Dict[str, Path]:
    """ 
    given the_base_dir
    return a dict keyed by hashes and whose values are the full names of 
    every file in the_base_dir (including all sub dirs)
    """
    file_info_by_checksum : Dict[str, Path] = {}

    for (absolute_dir, _, relative_filenames) in os.walk(the_base_dir):

        # We work with Path's not the strings returned by os.walk...
        absolute_dir = Path(absolute_dir)

        for relative_filename in relative_filenames:
                     
            absolute_filename = absolute_dir / relative_filename
            if absolute_filename.exists():
                check_sum = get_file_hash(absolute_filename)
                file_info_by_checksum[check_sum] = absolute_filename

    return(file_info_by_checksum)

def usage(program_name : str):
    print(f"usage: {program_name} source_folder destination_folder")

def main():
    print("No duplicate file copier.")

    if len(sys.argv) != 3:
        usage(sys.argv[0])
        sys.exit(1)

    SOURCE_BASE_DIR = Path(sys.argv[1])
    DESTINATION_BASE_DIR = Path(sys.argv[2])

    num_files_seen = 0
    num_copied = 0
    num_duplicates = 0
    num_symlinks = 0
    num_non_regular = 0
    copy_info_by_hash : Dict[str, Path] = {}

    n = folders_are_mutually_relative(SOURCE_BASE_DIR, DESTINATION_BASE_DIR)
    if (n == 1):
        print("ERROR Source is within dest; not allowed!")
        sys.exit(1)
    elif (n == 2):
        print("ERROR Destination folder is within the Source folder; not allowed!")
        sys.exit(1)

    # Get all of the hashes for the files in the destination folder
    # The idea is we may have run this program previously and 
    # copied files into the destination.
    # If so, we want to know about those files so we don't copy
    # them (or files with same checksum) again.
    print(f"INFO Scanning {DESTINATION_BASE_DIR} so we know what files were already copied...")
    copy_info_by_hash = get_hashes_from_dir(DESTINATION_BASE_DIR)
    print(f"INFO There were {len(copy_info_by_hash)} existing files found.")


    # Recursively walk the source dir
    # Get hashes for all files and then only copy REGULAR files
    # whose hashes we have not already seen
    # And once we do copy a file, note its hash so we won't copy
    # future files with same hash
    for (absolute_source_dir, _, relative_filenames) in os.walk(SOURCE_BASE_DIR):

        # We work with Path's not the strings returned by os.walk...
        absolute_source_dir = Path(absolute_source_dir)

        print(f"INFO looking in folder {absolute_source_dir}")
        
        relative_dir = get_relative_path_from_absolute(SOURCE_BASE_DIR, absolute_source_dir)

        absolute_destination_dir = DESTINATION_BASE_DIR /  relative_dir
        absolute_destination_dir.mkdir(parents = True, exist_ok=True)

        for relative_filename in relative_filenames:
            num_files_seen += 1
                     
            absolute_source_name = absolute_source_dir / relative_filename
            absolute_destination_name = absolute_destination_dir / relative_filename

            # print("  SOURCE Name   [%s]" % absolute_source_name)
            if (not absolute_source_name.is_file() ):
                print("INFO source file is not a regular file; skipping it.")
                num_non_regular += 1
                continue

            if (absolute_source_name.is_symlink()):
                print("INFO source file is symlink; skipping it.")
                num_symlinks += 1
                continue

            hash = get_file_hash(absolute_source_name)

            # Check for easy case where file has already been seen
            if hash  in copy_info_by_hash:
                # print("  INFO We already saw %s - will NOT copy" % absolute_source_name)
                # print("  It was copied as [%s]" % (copy_info_by_hash[hash]))

                print(f"INFO SOURCE is a dup; NOT Copying {absolute_source_name}    See:  {copy_info_by_hash[hash]}")
                num_duplicates += 1
                continue


            # We have not seen this file before (at least not during this run of the program!)
            # Now what?
            # print("  INFO - We have not seen this file before; will copy it")
            print(f"INFO SOURCE is NEW; Copying... {absolute_source_name}")
            shutil.copy(str(absolute_source_name), str(absolute_destination_name))
            copy_info_by_hash[hash] = absolute_destination_name
            num_copied += 1
        

    print("Num files seen : %d" % (num_files_seen))
    print("Num copied     : %d" % (num_copied))
    print("Num dups       : %d" % (num_duplicates))
    print("Num symlinks   : %d" % (num_symlinks))
    print("Num non_reg    : %d" % (num_non_regular))

#
main()
