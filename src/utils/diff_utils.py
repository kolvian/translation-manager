def compare_texts(text1, text2):
    """Compares two texts and returns a list of differences."""
    from difflib import unified_diff

    diff = list(unified_diff(text1.splitlines(), text2.splitlines(), lineterm=''))
    return diff


def identify_merge_conflicts(original, incoming):
    """Identifies merge conflicts between original and incoming texts."""
    conflicts = []
    original_lines = original.splitlines()
    incoming_lines = incoming.splitlines()

    for i, line in enumerate(original_lines):
        if i < len(incoming_lines) and line != incoming_lines[i]:
            conflicts.append((i, line, incoming_lines[i]))

    return conflicts


def extract_conflict_sections(conflicts):
    """Extracts sections of text that are in conflict."""
    conflict_sections = []
    for conflict in conflicts:
        index, original_line, incoming_line = conflict
        conflict_sections.append({
            'index': index,
            'original': original_line,
            'incoming': incoming_line
        })
    return conflict_sections