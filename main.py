# Script that synchronizes two folders (source and replica)
import os
import shutil
import time
import hashlib
from itertools import zip_longest

# at the start we check last modification time of source and replica, if source is newer than replica we have to synchronize folders
# os.walk() thrught source and replica at the same time
# compare each iteration (names and files hashes)
# if they are not equal -> take an action (create/copy/remove)
# if equal -> skip to the next iteration

def sort_dirs(path: str) -> tuple:
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames.sort()
        filenames.sort()
        return (dirpath, dirnames, filenames)

def compare_dir_names(rep_path: str ,src_dirs: list[str], rep_dirs: list[str]):
    for src, rep in zip_longest(src_dirs, rep_dirs, fillvalue=None):
       if src != rep:
            if src is None:
               # remove replica
               os.rmdir(f'{rep_path}/{rep}')
               print(f"Removed {rep_path}/{rep}")
            elif rep is None:
                #create replica
                os.mkdir(f'{rep_path}/{src}')
                print(f"Created {rep_path}/{src}")
            else:
                # change replica name to source name
                os.rename(f'{rep_path}/{rep}', f'{rep_path}/{src}')
                print(f"Renamed {rep_path}/{rep} to {rep_path}/{src}")

    
def comparison(src: tuple, rep: tuple):
    src_root = src[0]
    rep_root = rep[0]
    src_dirs = set(src[1])
    rep_dirs = set(rep[1])

    for dir in src_dirs:
        if dir not in rep_dirs:
            os.mkdir(f'{rep_root}/{dir}')
            print(f'[CREATE] {rep_root}/{dir} has been created')
    for dir in src_dirs.difference(rep_dirs):
        os.rmdir(f'{rep_root}/{dir}')
        print(f'[REMOVE] {rep_root}/{dir} has been removed')

    compare_files(src_root, rep_root, set(src[2]), set(rep[2]))
    if src_dirs == {}:
        return
    return comparison((f'{src_root}/'))

def compare_files(src_root: str, rep_root: str, src_files: set, rep_files: set):
    for file in src_files:
        if file in rep_files:
            verify_content(src_root, rep_root, file)
        else:
            shutil.copyfile(f'{src_root}/{file}', f'{rep_root}/{file}')
            print(f'[CREATE] {src_root}/{file} created in {rep_root}/{file}')
    for file in src_files.difference(rep_files):
        os.remove(f'{rep_root}/{file}')
        print(f'[REMOVE] {rep_root}/{file} has been removed')

def verify_content(src_root: str, rep_root: str, file: str):
    src_hash = calculate_md5(f'{src_root}/{file}')
    rep_hash = calculate_md5(f'{rep_root}/{file}')
    print(src_hash, rep_hash)
    if src_hash != rep_hash:
        shutil.copyfile(f'{src_root}/{file}', f'{rep_root}/{file}')
        print(f'[COPY] {src_root}/{file} copied to {rep_root}/{file}')
    return

def calculate_md5(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def compare():

    ''' 
    if we can assume that source and replica exist from the beggining and replica was created later than source, 
    we can just compare their last modification times to check whether there was any change in source
    '''

    source_time = time.ctime(os.path.getmtime("source"))
    replica_time = time.ctime(os.path.getmtime("replica"))
    if replica_time >= source_time:
        pass#return
    
    # we can't assume that os.walk will return dircs in the same odrder, so we have to sort them
    source = sort_dirs("source")
    replica = sort_dirs("replica")
    comparison(source, replica)
    #print(source)
    #print(replica)
    #print(os.listdir(source[0]))
    #print(os.listdir(replica[0]))

    """
    1. itereate through directory-tree of source and replica
    2. compare dirnames and filenames
    3. compare file contents by hash function
    4. if something is different take an action (create/copy/remove)
    5. log into the file and console output
    """
    # I use zip_longest becasue normal zip will stop at the shortest iterable
    for src, rep in zip_longest(source, replica, fillvalue=['', [], []]):
        pass#print(src, rep)
        #compare_dir_names(rep[0], src[1], rep[1])
        #compare_files_names(src[2], rep[2]) 


def main():
    compare()

main()