"""
File utility functions for repository analysis.
"""

import os
import stat
import shutil
import tempfile
import subprocess
import time
from pathlib import Path
from typing import Optional

def create_temp_directory(prefix: str = "whisper_") -> str:
    """Create a temporary directory for analysis."""
    return tempfile.mkdtemp(prefix=prefix)

def cleanup_directory(directory_path: str) -> bool:
    """
    Safely clean up a directory, handling Windows read-only files.
    
    Args:
        directory_path: Path to the directory to clean up
        
    Returns:
        bool: True if cleanup was successful, False otherwise
    """
    if not os.path.exists(directory_path):
        return True
    
    def handle_remove_readonly(func, path, exc):
        """Handle read-only files on Windows."""
        try:
            # Make the file/directory writable
            os.chmod(path, stat.S_IWRITE)
            # For directories, also make all contents writable
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for d in dirs:
                        try:
                            os.chmod(os.path.join(root, d), stat.S_IWRITE)
                        except:
                            pass
                    for f in files:
                        try:
                            os.chmod(os.path.join(root, f), stat.S_IWRITE)
                        except:
                            pass
            func(path)
        except Exception:
            pass
    
    # Method 1: Try shutil.rmtree with error handler
    try:
        shutil.rmtree(directory_path, onerror=handle_remove_readonly)
        if not os.path.exists(directory_path):
            return True
    except Exception:
        pass
    
    # Method 2: Try to make everything writable first, then delete
    try:
        for root, dirs, files in os.walk(directory_path):
            for d in dirs:
                try:
                    os.chmod(os.path.join(root, d), stat.S_IWRITE)
                except:
                    pass
            for f in files:
                try:
                    os.chmod(os.path.join(root, f), stat.S_IWRITE)
                except:
                    pass
        
        # Small delay to let Windows release file handles
        time.sleep(0.1)
        shutil.rmtree(directory_path)
        return True
    except Exception:
        pass
    
    # Method 3: Try Windows-specific rmdir command
    try:
        result = subprocess.run(['rmdir', '/s', '/q', directory_path], 
                              shell=True, check=False, capture_output=True, text=True)
        if not os.path.exists(directory_path):
            return True
    except Exception:
        pass
    
    # Method 4: Try PowerShell Remove-Item (more powerful than rmdir)
    try:
        ps_command = f'Remove-Item -Path "{directory_path}" -Recurse -Force -ErrorAction SilentlyContinue'
        result = subprocess.run(['powershell', '-Command', ps_command], 
                              check=False, capture_output=True, text=True)
        if not os.path.exists(directory_path):
            return True
    except Exception:
        pass
    
    # If all methods fail, return False but don't crash
    return False

def get_file_extension(file_path: str) -> str:
    """Get the file extension from a file path."""
    return Path(file_path).suffix.lower()

def is_text_file(file_path: str) -> bool:
    """Check if a file is likely a text file based on its extension."""
    text_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.sass',
        '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
        '.txt', '.md', '.rst', '.tex', '.csv', '.sql', '.sh', '.bat', '.ps1',
        '.php', '.rb', '.go', '.rs', '.cpp', '.c', '.h', '.hpp', '.cs', '.java',
        '.kt', '.swift', '.dart', '.vue', '.svelte', '.r', '.m', '.scala'
    }
    return get_file_extension(file_path) in text_extensions

def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def count_lines_in_file(file_path: str) -> int:
    """Count the number of lines in a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0 