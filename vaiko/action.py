from abc import ABC, abstractmethod

import pynput

def is_keyboard_code(code_str):
    return len(code_str) == 1 and (
        code_str.isalnum() or 
        code_str in pynput.keyboard.Key.__members__
    )

def is_mouse_code(code_str):
    return code_str in pynput.mouse.Button.__members__

def resolve_keyboard_code(code_str):
    if code_str.isalnum():
        return code_str
    
    return pynput.keyboard.Key[code_str]

def resolve_mouse_code(code_str):
    return pynput.mouse.Button[code_str]

class Action(ABC):

    def __init__(self):
        self.input_code = ''

    @abstractmethod
    def invoke():
        pass

class KeyAction(Action):

    keyboard = pynput.keyboard.Controller()

    def __init__(self, key):
        super().__init__()

        self.input_code = key

    def invoke(self):
        KeyAction.keyboard.press(self.input_code)
        KeyAction.keyboard.release(self.input_code)

class MouseAction(Action):

    mouse = pynput.mouse.Controller()

    def __init__(self, button):
        super().__init__()

        self.input_code = button

    def invoke(self):
        MouseAction.mouse.press(self.input_code)
        MouseAction.mouse.release(self.input_code)