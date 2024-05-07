# -*- coding: UTF-8 -*-

# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

# Full getext (please don't change)
_ = lambda x : x

# Add-on information variables
addon_info = {
        # for previously unpublished addons, please follow the community guidelines at:
        # https://bitbucket.org/nvdaaddonteam/todo/raw/master/guidelines.txt
        # add-on Name, internal for nvda
        "addon_name" : "virtualNotesForNVDA",
        # Add-on summary, usually the user visible name of the addon.
        # Translators: Summary for this add-on to be shown on installation and add-on information.
        "addon_summary" : _("Virtual Notes For NVDA (creates virtual notes to be read by NVDA)"),
        # Add-on description
        # Translators: Long description to be shown for this add-on on add-on information from add-ons manager
        "addon_description" : _("""
This add-on (Virtual Notes for NVDA) creates virtual notes that can be read by NVDA screen reader. Here are the available steps:  
* Select text;  
* Use shortcuts (all starting with the keys "NVDA + Alt").  
By pressing these keys combined with specific letters, you can perform the following actions:
* A: Add a new temporary note to memory;  
* J: Go to the previous note;  
* L: Go to the next note;  
* U: Read out the current note;  
* S: Replace the note in the current position (you need to select some text first);  
* D: Delete the note in the current position.  
If the current note contains multiple lines (like text copied from a text editor), use these additional letters:  
* I: Move to the previous line of the current note;  
* K: Move to the next line of the current note;  
* O: read out the current line of the current note.  
Note: The key positions mimic the arrow keys (I = up, L = right, K = down, and J = left).  
After using a shortcut, a specific sound will play to indicate the action performed.

"""),
        # version
        "addon_version" : "1.1.2",
        # Author(s)
        "addon_author" : _("Juliano Lopes"),
        # URL for the add-on documentation support
        "addon_url" : "https://github.com/juliano-lopes/virtual-notes-for-NVDA",
        # Documentation file name
        "addon_docFileName" : "readme.html",
        # Minimum NVDA version supported (e.g. "2018.3.0", minor version is optional)
        "addon_minimumNVDAVersion" : "2019.3.0",
        # Last NVDA version supported/tested (e.g. "2018.4.0", ideally more recent than minimum version)
        "addon_lastTestedNVDAVersion" : "2024.1",
        # Add-on update channel (default is None, denoting stable releases, and for development releases, use "dev"; do not change unless you know what you are doing)
        "addon_updateChannel" : None,
}


import os.path

# Define the python files that are the sources of your add-on.
# You can use glob expressions here, they will be expanded.
pythonSources = [os.path.join("addon", "globalPlugins", "virtualNotesForNVDA", "*.py")]

# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory, not to the root directory of your addon sources.
excludedFiles = [os.path.join("addon", "doc", "*", "contributing*.*")]
