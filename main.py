import sys
import os
import shutil
import hashlib
import time
import logging

def compare(path: str, dirs: list[str], files: list[str], rep_path: str) -> None:
    if os.path.exists(rep_path):
        rep = (rep_path, [dir for dir in os.listdir(rep_path) if os.path.isdir(os.path.join(rep_path, dir))], [file for file in os.listdir(rep_path) if os.path.isfile(os.path.join(rep_path, file))])
        compare_dirs(rep_path, set(dirs), set(rep[1]))
        compare_files(path, rep_path, set(files), set(rep[2]))
    else:
        shutil.copytree(path, rep_path)
        walk = os.walk(rep_path)
        for path, dirs, files in walk:
            files = [f for f in files]
            logger.info(f"[CREATE] Created {path} and its files: {files}")
    return

def compare_dirs(rep_path: str, src_dirs: set, rep_dirs: set) -> None:
    to_remove = rep_dirs.difference(src_dirs)
    for dir in to_remove:
        path = os.path.join(rep_path, dir)
        walk = os.walk(path)
        for path, dirs, files in walk:
            files = [f for f in files]
            logger.info(f"[REMOVE] Removed {path} and its files: {files}")
        shutil.rmtree(path)
    return

def compare_files(src_path: str, rep_path: str, src_files: set, rep_files: set) -> None:
    for file in src_files:
        if file in rep_files:
            verify_content(src_path, rep_path, file)
        else:
            src = os.path.join(src_path, file)
            dest = os.path.join(rep_path, file)
            shutil.copyfile(src, dest)
            rep_files.add(file)
            logger.info(f"[CREATE] {dest} has been created")
    to_remove = rep_files.difference(src_files)
    for file in to_remove:
        path = os.path.join(rep_path, file)
        os.remove(path)
        logger.info(f"[REMOVE] {path} has been removed")
    return

def verify_content(src_path: str, rep_path: str, file: str) -> None:
    src_hash = calculate_md5(f'{src_path}/{file}')
    rep_hash = calculate_md5(f'{rep_path}/{file}')
    if src_hash != rep_hash:
        src = os.path.join(src_path, file)
        dest = os.path.join(rep_path, file)
        shutil.copyfile(src, dest)
        logger.info(f"[COPY] {src} has been copied to {dest}")
    return

def calculate_md5(file_path: str) -> str:
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    src_root_path, rep_root_path, interval, amount, log_path = fetch_args()
    if None in (src_root_path, rep_root_path, interval, amount, log_path):
        return
    set_logger(log_path)
    print("Starting synchronization program...")
    for i in range(amount):
        source = os.walk(src_root_path)
        print(f"Starting synchronization num {i+1}")
        for path, dirs, files in source:
            rep_path = path.replace(src_root_path, rep_root_path)
            compare(path, dirs, files, rep_path)
        print(f"Synchronization num {i+1} completed")
        if i == amount-1:
            break
        time.sleep(interval)
    print("All synchronizations completed")

def fetch_args() -> tuple:
    if len(sys.argv) != 6:
        print("Provided wrong number of arguments!")
        return (None, None, None, None, None)
    try:
        src_root_path = sys.argv[1]
        rep_root_path = sys.argv[2]
        interval = int(sys.argv[3]) # in seconds
        amount = int(sys.argv[4])
        log_path = sys.argv[5]
    except:
        print("Provided wrong arguments!")
        return (None, None, None, None, None)
    return (src_root_path, rep_root_path, interval, amount, log_path)

def set_logger(log_path: str) -> None:
    global logger
    logger = logging.getLogger('sync_logger')
    logging.basicConfig(
        format = '%(asctime)s - %(levelname)s - %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
        level = logging.INFO,
            handlers = [
        logging.FileHandler(log_path),
        logging.StreamHandler()
        ]
    )

main()