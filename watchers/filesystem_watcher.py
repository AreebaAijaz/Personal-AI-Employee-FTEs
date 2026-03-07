#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File System Watcher - Monitors a drop folder for new files.

When files are added to the watched directory, this watcher creates
corresponding action files in the Obsidian vault's /Needs_Action folder.

This is the simplest watcher to set up and perfect for Bronze Tier.
"""

import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from base_watcher import BaseWatcher


class FileDropHandler(FileSystemEventHandler):
    """Handles file system events for the drop folder."""
    
    def __init__(self, watcher):
        """
        Initialize the handler.
        
        Args:
            watcher: FilesystemWatcher instance
        """
        self.watcher = watcher
        self.logger = watcher.logger
    
    def on_created(self, event):
        """Called when a file or directory is created."""
        if event.is_directory:
            return
        
        self.logger.info(f'File created: {event.src_path}')
        try:
            self.watcher.process_new_file(Path(event.src_path))
        except Exception as e:
            self.logger.error(f'Error processing file {event.src_path}: {e}')


class FilesystemWatcher(BaseWatcher):
    """
    Watches a drop folder for new files and creates action files.
    
    Files dropped into the watch folder are copied to the vault
    and an action file is created in /Needs_Action.
    """
    
    def __init__(self, vault_path: str, drop_folder: str = None, check_interval: int = 30):
        """
        Initialize the filesystem watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            drop_folder: Path to the folder to watch (default: vault/Inbox)
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        # Set up drop folder
        if drop_folder:
            self.drop_folder = Path(drop_folder).resolve()
        else:
            self.drop_folder = self.vault_path / 'Inbox'
        
        # Ensure drop folder exists
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files by hash to avoid duplicates
        self.processed_files = {}  # path -> hash
        
        self.logger.info(f'Drop folder: {self.drop_folder}')
    
    def check_for_updates(self) -> list:
        """
        Check drop folder for new files.
        
        Returns:
            List of new file paths to process
        """
        new_files = []
        
        try:
            for file_path in self.drop_folder.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    file_hash = self._hash_file(file_path)
                    
                    # Check if this is a new file
                    if file_path not in self.processed_files:
                        self.processed_files[file_path] = file_hash
                        new_files.append(file_path)
                    elif self.processed_files[file_path] != file_hash:
                        # File was modified
                        self.processed_files[file_path] = file_hash
                        new_files.append(file_path)
        except Exception as e:
            self.logger.error(f'Error scanning drop folder: {e}')
        
        return new_files
    
    def _hash_file(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file for change detection."""
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def create_action_file(self, file_path: Path) -> Path:
        """
        Create an action file for a dropped file.
        
        Args:
            file_path: Path to the dropped file
            
        Returns:
            Path to the created action file
        """
        # Get file metadata
        stat = file_path.stat()
        file_size = stat.st_size
        file_mtime = datetime.fromtimestamp(stat.st_mtime)
        
        # Copy file to vault
        vault_files_dir = self.vault_path / 'Files'
        vault_files_dir.mkdir(parents=True, exist_ok=True)
        dest_path = vault_files_dir / file_path.name
        
        # Handle name collisions
        counter = 1
        while dest_path.exists():
            stem = file_path.stem
            suffix = file_path.suffix
            dest_path = vault_files_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        shutil.copy2(file_path, dest_path)
        
        # Create action file content
        content = f'''---
type: file_drop
original_name: {file_path.name}
original_path: {file_path}
vault_path: {dest_path}
size: {file_size}
size_human: {self._human_readable_size(file_size)}
dropped: {file_mtime.isoformat()}
received: {datetime.now().isoformat()}
priority: normal
status: pending
---

# File Dropped for Processing

## File Details

- **Original Name**: {file_path.name}
- **Size**: {self._human_readable_size(file_size)}
- **Dropped At**: {file_mtime.strftime('%Y-%m-%d %H:%M:%S')}
- **Vault Location**: `[[{dest_path.name}]]`

## Content Preview

'''
        
        # Try to read first few lines if text file
        if file_path.suffix.lower() in ['.txt', '.md', '.json', '.csv', '.py', '.js']:
            try:
                preview = file_path.read_text(encoding='utf-8', errors='ignore')[:500]
                content += f"```\n{preview}\n"
                if len(preview) >= 500:
                    content += "\n... (truncated)\n"
                content += "```\n"
            except Exception as e:
                content += f"*Could not preview: {e}*\n"
        else:
            content += f"*Binary file - cannot preview*\n"
        
        content += '''
## Suggested Actions

- [ ] Review file content
- [ ] Determine required action
- [ ] Process and move to /Done when complete

---
*Created by Filesystem Watcher*
'''
        
        # Generate filename
        filename = self.generate_filename('FILE', file_path.stem)
        action_path = self.needs_action / filename
        
        # Write action file
        action_path.write_text(content)
        
        self.logger.info(f'Copied file to vault: {dest_path}')
        
        return action_path
    
    def process_new_file(self, file_path: Path):
        """
        Process a newly detected file immediately.
        
        This is called by the event handler when a file is created.
        
        Args:
            file_path: Path to the new file
        """
        self.logger.info(f'Processing new file: {file_path.name}')
        try:
            self.create_action_file(file_path)
        except Exception as e:
            self.logger.error(f'Error processing new file: {e}')
    
    def _human_readable_size(self, size_bytes: int) -> str:
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def run_with_observer(self):
        """
        Run the watcher using the Observer pattern for real-time detection.
        
        This is more efficient than polling and provides instant response.
        """
        self.logger.info(f'Starting FilesystemWatcher with Observer')
        self.logger.info(f'Watching: {self.drop_folder}')
        
        event_handler = FileDropHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.drop_folder), recursive=False)
        observer.start()
        
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info('Stopping observer...')
            observer.stop()
        
        observer.join()
        self.logger.info('FilesystemWatcher stopped')


def main():
    """Main entry point for running the watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='File System Watcher for AI Employee'
    )
    parser.add_argument(
        '--vault', '-v',
        default='AI_Employee_Vault',
        help='Path to Obsidian vault (default: AI_Employee_Vault)'
    )
    parser.add_argument(
        '--drop-folder', '-d',
        default=None,
        help='Path to drop folder (default: vault/Inbox)'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=30,
        help='Check interval in seconds (default: 30)'
    )
    parser.add_argument(
        '--observer', '-o',
        action='store_true',
        help='Use Observer pattern for real-time detection'
    )
    
    args = parser.parse_args()
    
    watcher = FilesystemWatcher(
        vault_path=args.vault,
        drop_folder=args.drop_folder,
        check_interval=args.interval
    )
    
    if args.observer:
        watcher.run_with_observer()
    else:
        watcher.run()


if __name__ == '__main__':
    main()
