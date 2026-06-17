# Add-on virtualNotesForNVDA
import addonHandler
import wx

import tones

import api
import globalPluginHandler
import keyboardHandler
import textInfos
import ui
from scriptHandler import getLastScriptRepeatCount
from scriptHandler import script
import config
import json
import os
import globalVars

# Fix compatibility with the new role constants introduced in NVDA 2022.1."""
try:
    from controlTypes import Role
    ROLE_EDITABLETEXT = Role.EDITABLETEXT
    ROLE_DOCUMENT = Role.DOCUMENT
except ImportError:
    from controlTypes import ROLE_EDITABLETEXT, ROLE_DOCUMENT

#_ = lambda x : x
addonHandler.initTranslation()

def get_notes_file_path():
    return os.path.join(globalVars.appArgs.configPath, "virtualNotesData.json")

def save_notes_to_disk(memory_list):
    try:
        file_path = get_notes_file_path()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(memory_list, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

def load_notes_from_disk():
    file_path = get_notes_file_path()
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

class MultilineTextEntryDialog(wx.Dialog):
    def __init__(self, parent, title, message, has_current_note, callback):
        wx.Dialog.__init__(self, parent, title=title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.callback = callback
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.label = wx.StaticText(self, label=message)
        sizer.Add(self.label, 0, wx.ALL | wx.EXPAND, 10)
        
        self.text_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        sizer.Add(self.text_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        
        btn_sizer = wx.GridSizer(rows=3, cols=2, hgap=5, vgap=5)
        
        self.create_btn = wx.Button(self, label=_("Create new note"))
        self.prepend_btn = wx.Button(self, label=_("Add to beginning of current note"))
        self.insert_after_btn = wx.Button(self, label=_("Add after current line"))
        self.append_btn = wx.Button(self, label=_("Add to end of current note"))
        self.replace_btn = wx.Button(self, label=_("Replace current note"))
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, label=_("Cancel"))
        
        if not has_current_note:
            self.prepend_btn.Disable()
            self.insert_after_btn.Disable()
            self.append_btn.Disable()
            self.replace_btn.Disable()
            
        btn_sizer.Add(self.create_btn, 0, wx.EXPAND)
        btn_sizer.Add(self.prepend_btn, 0, wx.EXPAND)
        btn_sizer.Add(self.insert_after_btn, 0, wx.EXPAND)
        btn_sizer.Add(self.append_btn, 0, wx.EXPAND)
        btn_sizer.Add(self.replace_btn, 0, wx.EXPAND)
        btn_sizer.Add(self.cancel_btn, 0, wx.EXPAND)
        
        sizer.Add(btn_sizer, 0, wx.ALL | wx.EXPAND, 10)
            
        self.SetSizer(sizer)
        self.SetMinSize((500, 400))
        self.Size = (500, 400)
        self.CentreOnScreen()
        
        self.create_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_action("create"))
        self.prepend_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_action("prepend"))
        self.insert_after_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_action("insert_after"))
        self.append_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_action("append"))
        self.replace_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_action("replace"))
        self.cancel_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_action("cancel"))
        self.Bind(wx.EVT_CLOSE, lambda evt: self.on_action("cancel"))
        
        self.text_ctrl.SetFocus()

    def on_action(self, action_type):
        typed_text = self.text_ctrl.GetValue()
        self.callback(action_type, typed_text)
        self.Destroy()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("Virtual Notes For NVDA")
    
    def __init__(self):
        super(GlobalPlugin, self).__init__()
        raw_memory = load_notes_from_disk()
        self.memory = [note.replace("\r\n", "\n").replace("\r", "\n") for note in raw_memory]
        self.index = len(self.memory) - 1 if len(self.memory) > 0 else 0
        self.line = 0
    
    @script(
        description=_("Add a new temporary note to memory")
    )
    def script_save_note_to_memory(self, gesture):
        focus = api.getFocusObject()
        textInfo = None
        try:
            if focus.treeInterceptor is not None:
                textInfo = focus.treeInterceptor.makeTextInfo(textInfos.POSITION_SELECTION)
            elif focus.windowClassName in ["AkelEditW"] or focus.role in [ROLE_EDITABLETEXT, ROLE_DOCUMENT]:
                textInfo = focus.makeTextInfo(textInfos.POSITION_SELECTION)
        except Exception as e:
            import logHandler
            logHandler.log.error("Failed to get textInfo", exc_info=True)
            tones.beep(300, 500)
            ui.message(f"Error selecting: {str(e)}")
            return
        
        text = ""
        if textInfo is not None:
            try:
                text = textInfo.text
            except Exception as e:
                import logHandler
                logHandler.log.error("Failed to get textInfo text", exc_info=True)
                tones.beep(300, 500)
                ui.message(f"Error reading text: {str(e)}")
                return

        if text and len(text) > 0:
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            self.memory.append(text)
            self.index = len(self.memory) - 1
            save_notes_to_disk(self.memory)
            self.line = 0
            
            tones.beep(880, 100)  # Beep a standard middle A for 1 second.
            ui.message(f"{self.index+1} {self.memory[self.index]}")
        else:
            import wx
            wx.CallAfter(self.open_add_note_dialog)

    def open_add_note_dialog(self):
        import wx
        import gui
        try:
            gui.mainFrame.prePopup()
            dialog = MultilineTextEntryDialog(
                gui.mainFrame,
                _("Add Note"),
                _("Write your note:"),
                len(self.memory) > 0,
                self.on_note_dialog_result
            )
            dialog.Show()
            gui.mainFrame.postPopup()
        except Exception as e:
            tones.beep(150, 500)
            import logHandler
            logHandler.log.error("Failed to open add note dialog", exc_info=True)
            ui.message(f"Error: {str(e)}")

    def on_note_dialog_result(self, action_type, typed_text):
        if action_type == "cancel":
            tones.beep(180, 220)
            ui.message(_("Note addition canceled"))
            return

        if not typed_text or len(typed_text.strip()) == 0:
            tones.beep(180, 220)
            ui.message(_("Empty note discarded"))
            return

        typed_text = typed_text.replace("\r\n", "\n").replace("\r", "\n")

        if action_type == "create":
            self.memory.append(typed_text)
            self.index = len(self.memory) - 1
            self.line = 0
        elif action_type == "prepend":
            current_note = self.memory[self.index]
            self.memory[self.index] = typed_text + "\n" + current_note
            self.line = 0
        elif action_type == "insert_after":
            current_note = self.memory[self.index]
            lines = current_note.split("\n")
            insert_idx = min(len(lines), self.line + 1)
            lines.insert(insert_idx, typed_text)
            self.memory[self.index] = "\n".join(lines)
            self.line = insert_idx
        elif action_type == "append":
            current_note = self.memory[self.index]
            self.memory[self.index] = current_note + "\n" + typed_text
        elif action_type == "replace":
            self.memory[self.index] = typed_text
            self.line = 0

        save_notes_to_disk(self.memory)
        tones.beep(880, 100)
        
        if action_type == "insert_after":
            lines = self.memory[self.index].split("\n")
            ui.message(f"{self.index + 1}.{self.line + 1} {lines[self.line]}")
        else:
            ui.message(f"{self.index+1} {self.memory[self.index]}")

    @script(
        description=_("Go to the next note")
    )
    def script_next_note(self, gesture):
        self.line = 0
        if self.index < (len(self.memory) - 1):
            self.index+=1
            ui.message(f"{self.index+1} {self.memory[self.index]}")
        else:
            tones.beep(280, 100)  # Beep a standard middle A for 1 second.
            if len(self.memory) > 0:
                ui.message(f"{self.index+1} {self.memory[self.index]}")

    @script(
        description=_("Go to the previous note")
    )
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

    @script(
        description=_("Anounce the current note")
    )
    def script_current_note(self, gesture):
        if len(self.memory) > 0:
            ui.message(f"{self.index+1} {self.memory[self.index]}")
        else:
            tones.beep(280, 100)

    @script(
        description=_("Delete the note in the current position")
    )
    def script_delete_note(self, gesture):
        self.line = 0
        if len(self.memory) > 0:
            self.memory.pop(self.index)
            if self.index > 0 and self.index == len(self.memory):
                self.index -= 1
            save_notes_to_disk(self.memory)
            tones.beep(580, 220)
            if len(self.memory) > 0:
                ui.message(f"{self.index+1} {self.memory[self.index]}")
        else:
            tones.beep(180, 220)

    @script(
        description=_("Replace the note in the current position (you need to select some text first)")
    )
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
                text = text.replace("\r\n", "\n").replace("\r", "\n")
                self.memory[self.index] = text
                save_notes_to_disk(self.memory)
                tones.beep(580, 220)
                ui.message(f"{self.index+1} {self.memory[self.index]}")
            else:
                # Translators: this message is shown when no text is selected
                ui.message(_("No text selected"))

    @script(
        description=_("Move to the next line of the current note")
    )
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

    @script(
        description=_("Move to the previous line of the current note")
    )
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

    @script(
        description=_("Anounce the current line of the current note")
    )
    def script_current_note_line(self, gesture):
        if len(self.memory) > 0:
            lines = self.memory[self.index].split("\n")
            if len(lines) > 0:
                ui.message(f"{self.index + 1}.{self.line + 1} {lines[self.line]}")
            else:
                tones.beep(280, 100)
        else:
            tones.beep(280, 100)

    @script(
        description=_("Paste the current note to the current application")
    )
    def script_paste_note(self, gesture):
        if len(self.memory) > 0:
            api.copyToClip(self.memory[self.index])
            self.paste_data()
            tones.beep(1080, 200)
            ui.message(f"{self.index+1} {self.memory[self.index]}")
        else:
            tones.beep(180, 220)
    @script(
        description=_("Paste the current line in the note to the current application")
    )
    def script_paste_note_line(self, gesture):
        if len(self.memory) > 0:
            lines = self.memory[self.index].split("\n")
            if len(lines) > 0:
                api.copyToClip(lines[self.line])
                self.paste_data()
                tones.beep(1080, 200)
                ui.message(f"{self.index + 1}.{self.line + 1} {lines[self.line]}")
            else:
                tones.beep(180, 220)
        else:
            tones.beep(180, 220)

    @script(
        description=_("Add a new temporary note from clipboard")
    )
    def script_add_note_from_clipboard(self, gesture):
        self.line = 0
        try:
            text = api.getClipData()
        except Exception:
            text = ""
        if text and len(text) > 0:
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            self.memory.append(text)
            self.index = len(self.memory) - 1
            save_notes_to_disk(self.memory)
            tones.beep(880, 100)
            ui.message(f"{self.index+1} {self.memory[self.index]}")
        else:
            tones.beep(180, 220)
            ui.message(_("Clipboard is empty or does not contain text"))

    @script(
        description=_("Insert selected text after the current line of the active note")
    )
    def script_insert_text_at_current_line(self, gesture):
        if len(self.memory) == 0:
            tones.beep(180, 220)
            ui.message(_("No active note to insert into"))
            return

        focus = api.getFocusObject()
        textInfo = None
        if focus.treeInterceptor is not None:
            textInfo = focus.treeInterceptor.makeTextInfo(textInfos.POSITION_SELECTION)
        elif focus.windowClassName in ["AkelEditW"] or focus.role in [ROLE_EDITABLETEXT, ROLE_DOCUMENT]:
            textInfo = focus.makeTextInfo(textInfos.POSITION_SELECTION)
        
        if textInfo is None or len(textInfo.text) == 0:
            tones.beep(180, 220)
            ui.message(_("No text selected"))
            return

        selected_text = textInfo.text.replace("\r\n", "\n").replace("\r", "\n")
        current_note = self.memory[self.index]
        lines = current_note.split("\n")
        
        insert_idx = min(len(lines), self.line + 1)
        lines.insert(insert_idx, selected_text)
        
        new_note = "\n".join(lines)
        self.memory[self.index] = new_note
        save_notes_to_disk(self.memory)
        
        self.line = insert_idx
        
        tones.beep(880, 100)
        ui.message(f"{self.index + 1}.{self.line + 1} {selected_text}")

    def paste_data(self):
        focus = api.getFocusObject()
        if focus.appModule.appName == "winword":
            focus.WinwordSelectionObject.Paste()
        else:
            keyboardHandler.KeyboardInputGesture.fromName("CONTROL+V").send()

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
        "kb:NVDA+CONTROL+SHIFT+U":"paste_note",
        "kb:NVDA+CONTROL+SHIFT+O":"paste_note_line",
        "kb:NVDA+ALT+V":"add_note_from_clipboard",
        "kb:NVDA+SHIFT+ALT+A":"insert_text_at_current_line"
    }