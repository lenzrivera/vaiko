import yaml

from action import (
    is_keyboard_code,
    is_mouse_code,
    resolve_keyboard_code,
    resolve_mouse_code,
    KeyAction
)    

def gen_action(action_str):
    if is_keyboard_code(action_str):
        return KeyAction(resolve_keyboard_code(action_str))
    elif is_mouse_code(action_str):
        return KeyAction(resolve_mouse_code(action_str))
    else:
        raise ValueError('Invalid keystroke value.')

def gen_word_dict(raw_word_dict):
    phrase_dict = {}

    for phrase, action_str in raw_word_dict.items():
        # pyyaml auto converts the values based on their type, but only strings
        # are valid in this case.
        phrase_dict[phrase] = gen_action(str(action_str))

    return phrase_dict

def read_word_file(word_file_path):
    try:
        with open(word_file_path, 'r') as phrase_file:
            yaml_dict = yaml.safe_load(phrase_file)

            # To handle the case where the file is empty:
            if yaml_dict is None:
                return {}
            else:
                return yaml_dict
    except FileNotFoundError:
        # Create the file if it doesn't exist.
        with open(word_file_path, 'x'):
            return {}
    except yaml.scanner.ScannerError:
        raise