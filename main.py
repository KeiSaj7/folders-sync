import os
import shutil
import hashlib
import time
import logging
import argparse

class Sync():

    def __init__(self, src_root_path, rep_root_path, interval, amount, log_path: str):
        self.src_root_path = src_root_path
        self.rep_root_path = rep_root_path
        self.interval = interval
        self.amount = amount
        self.log_path = log_path

        self.path = None
        self.dirs = None
        self.files = None
        self.rep_path = None

        self.logger = logging.getLogger('sync_logger')
        self.initialize_logger()

    def initialize_logger(self) -> None:
        self.logger.setLevel(logging.INFO)
    
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        logs_handler = logging.FileHandler(self.log_path)
        logs_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.logger.addHandler(logs_handler)
        self.logger.addHandler(console_handler)

    def log(self, msg) -> None:
            self.logger.info(msg)

    def assign_walk_values(self, path: str, dirs: list[str], files: list[str]) -> None:
        self.path = path
        self.dirs = dirs
        self.files = files
        self.rep_path = path.replace(self.src_root_path, self.rep_root_path)

    def compare_dirs(self) -> None:
        if os.path.exists(self.rep_path):
            src_dirs = set(self.dirs)
            rep_dirs = set(dir for dir in os.listdir(self.rep_path) if os.path.isdir(os.path.join(self.rep_path, dir)))
            to_remove = rep_dirs.difference(src_dirs)
            for dir in to_remove:
                path = os.path.join(self.rep_path, dir)
                walk = os.walk(path)
                for path, dirs, files in walk:
                    files = [f for f in files]
                    abspath = os.path.abspath(path)
                    self.log(f"[REMOVE] Removed {abspath} and its files: {files}")
                shutil.rmtree(path)
            rep_files = set(file for file in os.listdir(self.rep_path) if os.path.isfile(os.path.join(self.rep_path, file)))
            self.compare_files(rep_files)
        else:
            shutil.copytree(self.path, self.rep_path)
            walk = os.walk(self.rep_path)
            for path, dirs, files in walk:
                files = [f for f in files]
                abspath = os.path.abspath(path)
                self.log(f"[CREATE] Created {abspath} and its files: {files}")

    def compare_files(self, rep_files: set) -> None:
        src_files = set(self.files)
        for file in src_files:
            if file in rep_files:
                self.verify_content(file)
            else:
                src = os.path.join(self.path, file)
                dest = os.path.join(self.rep_path, file)
                shutil.copyfile(src, dest)
                rep_files.add(file)
                abspath = os.path.abspath(dest)
                self.log(f"[CREATE] {abspath} has been created")
        to_remove = rep_files.difference(src_files)
        for file in to_remove:
            path = os.path.join(self.rep_path, file)
            os.remove(path)
            abspath = os.path.abspath(path)
            self.log(f"[REMOVE] {abspath} has been removed")

    def verify_content(self, file: str) -> None:
        src_hash = self.calculate_md5(f'{self.path}/{file}')
        rep_hash = self.calculate_md5(f'{self.rep_path}/{file}')
        if src_hash != rep_hash:
            src = os.path.join(self.path, file)
            dest = os.path.join(self.rep_path, file)
            shutil.copyfile(src, dest)
            src_abspath = os.path.abspath(src)
            dest_abspath = os.path.abspath(dest)
            self.log(f"[COPY] {src_abspath} has been copied to {dest_abspath}")

    def calculate_md5(self, file_path: str) -> str:
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def start_sync(self) -> None:
        print("Starting synchronization program...")
        for i in range(self.amount):
            source = os.walk(self.src_root_path)
            print(f"Starting synchronization num {i+1}")
            for path, dirs, files in source:
                self.assign_walk_values(path, dirs, files)
                self.compare_dirs()
            print(f"Synchronization num {i+1} completed")
            if i == self.amount-1:
                break
            time.sleep(self.interval)
        print("All synchronizations completed")

def is_dir(path: str) -> str:
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"{path} is not a valid directory")
    return path

def is_file(path: str) -> str:
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"{path} doesn't exist")
    log_path = os.path.join(path, ".LOG")
    return log_path

def is_negative_int(val: str) -> int:
    try:
        int_val = int(val)
    except:
        raise argparse.ArgumentTypeError(f"Interval/amount must be a positive integer")
        
    if int_val < 0:
        raise argparse.ArgumentTypeError(f"Interval/amount must be a positive integer")
    
    return int_val


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('src_root_path', type=is_dir, help='Path to source directory')
    parser.add_argument('rep_root_path', type=is_dir, help='Path to replica directory')
    parser.add_argument('interval', type=is_negative_int, help='Interval between synchronizations in seconds')
    parser.add_argument('amount', type=is_negative_int, help='Number of synchronizations to perform')
    parser.add_argument('log_path', type=is_file, help='Path to the log file')
    args = parser.parse_args()
    sync_instance = Sync(args.src_root_path, args.rep_root_path, args.interval, args.amount, args.log_path)
    sync_instance.start_sync()

main()