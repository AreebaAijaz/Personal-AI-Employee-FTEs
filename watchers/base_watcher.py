#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Watcher - Abstract base class for all AI Employee watchers.

All watchers (Gmail, WhatsApp, File System, etc.) inherit from this class
and implement the check_for_updates() and create_action_file() methods.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


class BaseWatcher(ABC):
    """
    Abstract base class for AI Employee watchers.
    
    Watchers are long-running processes that monitor external sources
    (email, messaging apps, file systems) and create action files
    in the Obsidian vault's /Needs_Action folder.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory
        logs_dir = self.vault_path / 'Logs'
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # File handler for daily logs
        log_file = logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Track processed items to avoid duplicates
        self.processed_ids = set()
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check the external source for new items.
        
        Returns:
            List of new items to process. Each item should be a dict
            containing the data needed to create an action file.
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a markdown action file in /Needs_Action folder.
        
        Args:
            item: Item data from check_for_updates()
            
        Returns:
            Path to the created action file
        """
        pass
    
    def run(self):
        """
        Main run loop. Continuously checks for updates and creates action files.
        
        This method runs indefinitely until interrupted (Ctrl+C).
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    for item in items:
                        try:
                            filepath = self.create_action_file(item)
                            self.logger.info(f'Created action file: {filepath.name}')
                        except Exception as e:
                            self.logger.error(f'Error creating action file: {e}')
                except Exception as e:
                    self.logger.error(f'Error in check cycle: {e}')
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise
    
    def generate_filename(self, prefix: str, identifier: str) -> str:
        """
        Generate a standardized filename.
        
        Args:
            prefix: Type prefix (e.g., 'EMAIL', 'FILE', 'WHATSAPP')
            identifier: Unique identifier for the item
            
        Returns:
            Filename with date suffix
        """
        date_str = datetime.now().strftime('%Y-%m-%d')
        # Sanitize identifier for filesystem
        safe_id = ''.join(c if c.isalnum() or c in '-_' else '_' for c in identifier)
        return f"{prefix}_{safe_id}_{date_str}.md"
    
    def create_metadata_file(self, action_path: Path, metadata: dict):
        """
        Create a companion metadata JSON file.
        
        Args:
            action_path: Path to the action file
            metadata: Dictionary of metadata to store
        """
        meta_path = action_path.with_suffix('.json')
        import json
        metadata['created_at'] = datetime.now().isoformat()
        meta_path.write_text(json.dumps(metadata, indent=2))
