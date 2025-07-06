import os
import shutil
import hashlib

def compare_subdirs(path: str, dirs: list[str], files: list[str]):
    rep_path = path.replace('source', 'replica')
    if os.path.exists(rep_path):
        rep = (rep_path, [dir for dir in os.listdir(rep_path) if os.path.isdir(os.path.join(rep_path, dir))], [file for file in os.listdir(rep_path) if os.path.isfile(os.path.join(rep_path, file))])
        compare_files(path, rep_path, set(files), set(rep[2]))
    else:
        shutil.copytree(path, rep_path)


def compare_files(src_root: str, rep_root: str, src_files: set, rep_files: set):
    for file in src_files:
        if file in rep_files:
            verify_content(src_root, rep_root, file)
        else:
            shutil.copyfile(f'{src_root}/{file}', f'{rep_root}/{file}')
            rep_files.add(file)
            print(f'[CREATE] {src_root}/{file} created in {rep_root}/{file}')
    print(src_files.difference(rep_files)) #### REMOVE DOESNT WORK!!!
    for file in src_files.difference(rep_files):
        os.remove(f'{rep_root}/{file}')
        print(f'[REMOVE] {rep_root}/{file} has been removed')

def verify_content(src_root: str, rep_root: str, file: str):
    src_hash = calculate_md5(f'{src_root}/{file}')
    rep_hash = calculate_md5(f'{rep_root}/{file}')
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

def main():
    rep_root = 'replica'
    source = os.walk('source')
    for dir in source:
        compare_subdirs(dir[0], dir[1], dir[2])

main()