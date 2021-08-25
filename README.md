# NO DUP COPIER

Program to copy directory trees, maintaining tree structure but avoiding duplicate files (ie files with equal checksums)

## Requirements

This program was built using a pipenv environment on Windows 10.

Install pipenv!

From a command line run "pipenv install" to install the necessary runtime environment.

To run the program run pipenv run no_dup_copier.py.

The source and destination folders are specified as constants in the code.

## TODO Check for proper function on Windows and Unix

Uses python pathlib so it may be OK assuming pipenv is installed.

Allow for rerunning where files are NOT copied if they are already present in the destination folder.
