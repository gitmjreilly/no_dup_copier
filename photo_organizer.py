#!python

import os
from pathlib import Path
import hashlib
from typing import  Dict
import shutil

# Photo organizer program

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


def main():

    num_copied = 0
    num_skipped = 0
    copy_info_by_checksum : Dict[str, Path]  = {}

    print("Photo organizer program!")
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
            print("  ########")
                     
            fully_qualified_source_name = fully_qualified_source_dir / unqualified_file_name
            fully_qualified_destination_name = fully_qualified_destination_dir / unqualified_file_name

            print("  SOURCE Name   [%s]" % (fully_qualified_source_name))
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
                num_skipped += 1

    print("Num copied : %d" % (num_copied))
    print("Num skipped: %d" % (num_skipped))

#
main()