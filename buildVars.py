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
This Addon (Virtual Notes For NVDA
) creates virtual notes to be read by NVDA. The following steps are available:
* Select a text;  
* Use shortcuts (they all start with the keys "NVDA + Control + Shift).  
So, by pressing these keys, you can press the following letters further:  
* A to add a new temporary note to memory;  
* J for previous note;  
* K for next note;  
* L for current note;  
* M to replace note in current position.  
If the current note has more than one line (text copied from a text editor) use the following letters:  
* U for previous line of current note;  
* O for next line of current note;  
* P for current line of current note.  
"""),
        # version
        "addon_version" : "1.0.0",
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
