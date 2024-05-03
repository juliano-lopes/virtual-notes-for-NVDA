# Add-on virtualNotesForNVDA
import addonHandler

import tones

import api
import globalPluginHandler
import keyboardHandler
import textInfos
import ui
from scriptHandler import getLastScriptRepeatCount
import config
import json
import os

# Fix compatibility with the new role constants introduced in NVDA 2022.1."""
try:
    from controlTypes import Role
    ROLE_EDITABLETEXT = Role.EDITABLETEXT
    ROLE_DOCUMENT = Role.DOCUMENT
except ImportError:
    from controlTypes import ROLE_EDITABLETEXT, ROLE_DOCUMENT

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    memory = []
    index = 0
    line = 0
    def script_save_note_to_memory(self, gesture):
        self.line = 0
        focus = api.getFocusObject()
        textInfo = None
        if focus.treeInterceptor is not None:
            textInfo = focus.treeInterceptor.makeTextInfo(textInfos.POSITION_SELECTION)
        elif focus.windowClassName in ["AkelEditW"] or focus.role in [ROLE_EDITABLETEXT, ROLE_DOCUMENT]:
            textInfo = focus.makeTextInfo(textInfos.POSITION_SELECTION)
        if textInfo is not None:
            text = textInfo.text
            if len(text) > 0:
                #keyCode = str(gesture.vkCode) # Get which number the user pressed.
                self.memory.append(text)
                self.index = len(self.memory) - 1
                
                tones.beep(880, 100)  # Beep a standard middle A for 1 second.
                ui.message(f"{self.index+1} {self.memory[self.index]}")
            else:
                # Translators: this message is shown when no text is selected
                ui.message(_("No text selected"))

    def script_next_note(self, gesture):
        self.line = 0
        if self.index < (len(self.memory) - 1):
            self.index+=1
            ui.message(f"{self.index+1} {self.memory[self.index]}")
        else:
            tones.beep(280, 100)  # Beep a standard middle A for 1 second.
            if len(self.memory) > 0:
                ui.message(f"{self.index+1} {self.memory[self.index]}")

    def script_previous_note(self, gesture):
        self.line = 0
        if self.index >= 1:
            self.index-=1
            if len(self.memory) > 0:
                ui.message(f"{self.index+1} {self.memory[self.index]}")
        else:
            tones.beep(280, 100)
            if len(self.memory) > 0:
                ui.message(f"{self.index+1} {self.memory[self.index]}")

    def script_current_note(self, gesture):
        if len(self.memory) > 0:
            ui.message(f"{self.index+1} {self.memory[self.index]}")
        else:
            tones.beep(280, 100)

    def script_delete_note(self, gesture):
        self.line = 0
        if len(self.memory) > 0:
            self.memory.pop(self.index)
            if self.index > 0 and self.index == len(self.memory):
                self.index -= 1
            tones.beep(580, 220)
            if len(self.memory) > 0:
                ui.message(f"{self.index+1} {self.memory[self.index]}")
        else:
            tones.beep(180, 220)

    def script_replace_note(self, gesture):
        self.line = 0
        focus = api.getFocusObject()
        textInfo = None
        if focus.treeInterceptor is not None:
            textInfo = focus.treeInterceptor.makeTextInfo(textInfos.POSITION_SELECTION)
        elif focus.windowClassName in ["AkelEditW"] or focus.role in [ROLE_EDITABLETEXT, ROLE_DOCUMENT]:
            textInfo = focus.makeTextInfo(textInfos.POSITION_SELECTION)
        if textInfo is not None:
            text = textInfo.text
            if len(text) > 0:
                self.memory[self.index] = text
                tones.beep(580, 220)
                ui.message(f"{self.index+1} {self.memory[self.index]}")
            else:
                # Translators: this message is shown when no text is selected
                ui.message(_("No text selected"))

    def script_next_note_line(self, gesture):
        if len(self.memory) > 0:
            lines = self.memory[self.index].split("\n")
            if len(lines) > 0 and self.line < (len(lines) - 1):
                self.line+=1
                ui.message(f"{self.index + 1}.{self.line + 1} {lines[self.line]}")
            else:
                tones.beep(280, 100)
                ui.message(f"{self.index + 1}.{self.line + 1} {lines[self.line]}")
        else:
            tones.beep(280, 100)

    def script_previous_note_line(self, gesture):
        if len(self.memory) > 0:
            lines = self.memory[self.index].split("\n")
            if len(lines) > 0 and self.line >= 1:
                self.line-=1
                ui.message(f"{self.index + 1}.{self.line + 1} {lines[self.line]}")
            else:
                tones.beep(280, 100)
                ui.message(f"{self.index + 1}.{self.line + 1} {lines[self.line]}")
        else:
            tones.beep(280, 100)

    def script_current_note_line(self, gesture):
        if len(self.memory) > 0:
            lines = self.memory[self.index].split("\n")
            if len(lines) > 0:
                ui.message(f"{self.index + 1}.{self.line + 1} {lines[self.line]}")
            else:
                tones.beep(280, 100)
        else:
            tones.beep(280, 100)

    __gestures={
        "kb:NVDA+ALT+A": "save_note_to_memory",
        "kb:NVDA+ALT+L":"next_note",
        "kb:NVDA+ALT+J":"previous_note",
        "kb:NVDA+ALT+U":"current_note",
        "kb:NVDA+ALT+S":"replace_note",
        "kb:NVDA+ALT+D":"delete_note",
        "kb:NVDA+ALT+K":"next_note_line",
        "kb:NVDA+ALT+I":"previous_note_line",
        "kb:NVDA+ALT+O":"current_note_line",
    }