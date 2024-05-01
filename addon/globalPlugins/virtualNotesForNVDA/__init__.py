# Add-on development first example
import addonHandler

import tones # We want to hear beeps.

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
                ui.message("Nenhum texto selecionado")
    def script_next_note(self, gesture):
        if self.index < (len(self.memory) - 1):
            self.index+=1
            ui.message(f"{self.index+1} {self.memory[self.index]}")
        else:
            tones.beep(280, 100)  # Beep a standard middle A for 1 second.
    def script_previous_note(self, gesture):
        if self.index >= 1:
            self.index-=1
            ui.message(f"{self.index+1} {self.memory[self.index]}")
        else:
            tones.beep(280, 100)  # Beep a standard middle A for 1 second.
    def script_current_note(self, gesture):
        if len(self.memory) > 0:
            ui.message(f"{self.index+1} {self.memory[self.index]}")

    def script_replace_note(self, gesture):
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
                ui.message("Nenhum texto selecionado")
    def script_next_note_line(self, gesture):
        t = self.memory[self.index].split("\n")
        if len(t) > 0 and self.line < (len(t) - 1):
            self.line+=1
            ui.message(f"{self.index + 1} ponto {self.line + 1} {t[self.line]}")
        else:
            tones.beep(280, 100)
            
    def script_previous_note_line(self, gesture):
        t = self.memory[self.index].split("\n")
        if len(t) > 0 and self.line >= 1:
            self.line-=1
            ui.message(f"{self.index + 1} ponto {self.line + 1} {t[self.line]}")
        else:
            tones.beep(280, 100)
    def script_current_note_line(self, gesture):
        t = self.memory[self.index].split("\n")
        if len(t) > 0:
            ui.message(f"{self.index + 1} ponto {self.line + 1} {t[self.line]}")

    __gestures={
        "kb:NVDA+CONTROL+SHIFT+A": "save_note_to_memory",
        "kb:NVDA+CONTROL+SHIFT+K":"next_note",
        "kb:NVDA+CONTROL+SHIFT+J":"previous_note",
        "kb:NVDA+CONTROL+SHIFT+L":"current_note",
        "kb:NVDA+CONTROL+SHIFT+M":"replace_note",
        "kb:NVDA+CONTROL+SHIFT+O":"next_note_line",
        "kb:NVDA+CONTROL+SHIFT+U":"previous_note_line",
        "kb:NVDA+CONTROL+SHIFT+P":"current_note_line",
    }