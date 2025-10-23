import os
import re

class FileProcessor:
    """Handles reading and writing files with merge conflict resolution."""
    
    def __init__(self):
        pass
    
    def resolve_conflicts_in_file(self, file_path, conflict_file_data):
        """Resolve conflicts in a file and write the result back."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Process each conflict from bottom to top (to preserve line numbers)
            conflicts = sorted(conflict_file_data['conflicts'], 
                             key=lambda x: x.get('start_line', 0), 
                             reverse=True)
            
            for conflict in conflicts:
                if conflict.get('resolution') is None:
                    # Skip unresolved conflicts
                    continue
                
                # Find and replace the conflict block
                content = self._replace_conflict_block(
                    content, 
                    conflict['current'], 
                    conflict['incoming'], 
                    conflict['resolution']
                )
            
            # Write the resolved content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"    ⚠️  Error writing file: {e}")
            return False
    
    def _replace_conflict_block(self, content, current, incoming, resolution):
        """Replace a merge conflict block with the resolution."""
        # Escape special regex characters
        current_escaped = re.escape(current)
        incoming_escaped = re.escape(incoming)
        
        # Pattern to match the entire conflict block
        # <<<<<<< HEAD
        # current content
        # =======
        # incoming content
        # >>>>>>> branch
        pattern = (
            r'<<<<<<<[^\n]*\n'  # Start marker
            + current_escaped
            + r'\n=======[^\n]*\n'  # Separator
            + incoming_escaped
            + r'\n>>>>>>>[^\n]*\n?'  # End marker
        )
        
        # Replace with resolution + newline
        replacement = resolution
        if not replacement.endswith('\n'):
            replacement += '\n'
        
        # Perform the replacement
        new_content = re.sub(pattern, replacement, content, count=1)
        
        return new_content


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)