"""
Cross-platform case-insensitive path resolver.
Enables Linux environments to gracefully load files with case mismatches (e.g. from Windows project backups).
"""
import os

def resolve_case_insensitive_path(path: str) -> str:
    """
    Recursively resolves a path case-insensitively on case-sensitive file systems (like Linux).
    If a path or filename has a different case (e.g., .JPG vs .jpg or folder case mismatches),
    this function will discover and return the correct existing path.
    """
    if not path:
        return path
        
    path = path.replace('\\', '/')
    if os.path.exists(path):
        return path
        
    parts = path.split('/')
    is_absolute = path.startswith('/')
    
    resolved = '/' if is_absolute else ''
    
    for part in parts:
        if not part:
            continue
            
        current_check = os.path.join(resolved, part) if resolved not in ('/', '') else resolved + part
        if os.path.exists(current_check):
            resolved = current_check
        else:
            # Try case-insensitive match in parent directory
            parent = resolved if resolved else '.'
            if os.path.exists(parent):
                try:
                    entries = os.listdir(parent)
                    matched = False
                    part_lower = part.lower()
                    for entry in entries:
                        if entry.lower() == part_lower:
                            resolved = os.path.join(resolved, entry) if resolved not in ('/', '') else resolved + entry
                            matched = True
                            break
                    if not matched:
                        # Fallback
                        resolved = os.path.join(resolved, part) if resolved not in ('/', '') else resolved + part
                except Exception:
                    resolved = os.path.join(resolved, part) if resolved not in ('/', '') else resolved + part
            else:
                resolved = os.path.join(resolved, part) if resolved not in ('/', '') else resolved + part
                
    # Sibling folder scanning fallback (Self-Healing)
    # If the file still doesn't exist, check if it exists inside sibling folders (e.g. Good, Bad, Empty)
    if not os.path.exists(resolved):
        dir_name = os.path.dirname(resolved)
        parent_dir = os.path.dirname(dir_name)
        filename = os.path.basename(resolved)
        
        if os.path.exists(parent_dir):
            try:
                # Look inside sibling directories
                siblings = [
                    os.path.join(parent_dir, d) 
                    for d in os.listdir(parent_dir) 
                    if os.path.isdir(os.path.join(parent_dir, d))
                ]
                filename_lower = filename.lower()
                for sib in siblings:
                    for entry in os.listdir(sib):
                        if entry.lower() == filename_lower:
                            return os.path.join(sib, entry)
            except Exception:
                pass
                
    return resolved
