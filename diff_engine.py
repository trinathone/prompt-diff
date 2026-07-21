import difflib
import json
import re
from typing import Any, List, Dict, Optional


def tokenize_simple(text: str) -> int:
    tokens = re.findall(r'\w+|[^\w\s]', text)
    return len(tokens)


def is_json_conversation(text: str) -> bool:
    try:
        obj = json.loads(text)
        if isinstance(obj, list):
            return all(
                isinstance(item, dict) and 'role' in item and 'content' in item
                for item in obj
            )
        return False
    except (json.JSONDecodeError, TypeError):
        return False


def parse_conversation(text: str) -> Optional[List[Dict[str, str]]]:
    try:
        obj = json.loads(text)
        if isinstance(obj, list):
            return obj
        return None
    except json.JSONDecodeError:
        return None


def get_diff_hunks(left: str, right: str) -> List[Dict[str, Any]]:
    left_lines = left.splitlines(keepends=True)
    right_lines = right.splitlines(keepends=True)

    matcher = difflib.SequenceMatcher(None, left_lines, right_lines)
    hunks = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            hunks.append({
                'type': 'equal',
                'left_lines': left_lines[i1:i2],
                'right_lines': right_lines[j1:j2],
                'left_start': i1,
                'right_start': j1,
            })
        elif tag == 'insert':
            hunks.append({
                'type': 'insert',
                'left_lines': [],
                'right_lines': right_lines[j1:j2],
                'left_start': i1,
                'right_start': j1,
            })
        elif tag == 'delete':
            hunks.append({
                'type': 'delete',
                'left_lines': left_lines[i1:i2],
                'right_lines': [],
                'left_start': i1,
                'right_start': j1,
            })
        elif tag == 'replace':
            hunks.append({
                'type': 'replace',
                'left_lines': left_lines[i1:i2],
                'right_lines': right_lines[j1:j2],
                'left_start': i1,
                'right_start': j1,
            })

    return hunks


def get_char_diff(old_line: str, new_line: str) -> tuple:
    matcher = difflib.SequenceMatcher(None, old_line, new_line)
    old_chars, new_chars = [], []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            old_chars.append(old_line[i1:i2])
            new_chars.append(new_line[j1:j2])
        elif tag == 'delete':
            old_chars.append(f'<del>{old_line[i1:i2]}</del>')
        elif tag == 'insert':
            new_chars.append(f'<ins>{new_line[j1:j2]}</ins>')
        elif tag == 'replace':
            old_chars.append(f'<del>{old_line[i1:i2]}</del>')
            new_chars.append(f'<ins>{new_line[j1:j2]}</ins>')

    return ''.join(old_chars), ''.join(new_chars)


def count_conversation_turns(conv: List[Dict[str, str]]) -> Dict[str, int]:
    roles = {}
    for msg in conv:
        role = msg.get('role', 'unknown')
        roles[role] = roles.get(role, 0) + 1
    return roles


def find_role_changes(left_conv: List[Dict[str, str]], right_conv: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    changes = []
    min_len = min(len(left_conv), len(right_conv))

    for i in range(min_len):
        left_role = left_conv[i].get('role', '')
        right_role = right_conv[i].get('role', '')
        if left_role != right_role:
            changes.append({
                'turn': i,
                'from_role': left_role,
                'to_role': right_role,
            })

    return changes


def compute_diff(left: str, right: str) -> Dict[str, Any]:
    left_tokens = tokenize_simple(left)
    right_tokens = tokenize_simple(right)
    token_delta = right_tokens - left_tokens

    hunks = get_diff_hunks(left, right)

    left_lines = left.splitlines()
    right_lines = right.splitlines()
    lines_added = sum(len(h['right_lines']) for h in hunks if h['type'] in ('insert', 'replace'))
    lines_removed = sum(len(h['left_lines']) for h in hunks if h['type'] in ('delete', 'replace'))

    is_json = is_json_conversation(left) and is_json_conversation(right)
    turns_added = 0
    turns_removed = 0
    roles_changed = []

    if is_json:
        left_conv = parse_conversation(left)
        right_conv = parse_conversation(right)
        if left_conv and right_conv:
            turns_added = max(0, len(right_conv) - len(left_conv))
            turns_removed = max(0, len(left_conv) - len(right_conv))
            roles_changed = find_role_changes(left_conv, right_conv)

    return {
        'hunks': hunks,
        'stats': {
            'left_tokens': left_tokens,
            'right_tokens': right_tokens,
            'token_delta': token_delta,
            'lines_added': lines_added,
            'lines_removed': lines_removed,
            'is_json_conversation': is_json,
            'turns_added': turns_added,
            'turns_removed': turns_removed,
            'roles_changed': roles_changed,
        },
    }
