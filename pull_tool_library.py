# Author- Carl Bass
# Description- make surface gouges of specified radius tapering at both ends

import adsk.core, adsk.fusion, adsk.cam, traceback
import os

# Global list to keep all event handlers in scope.
handlers = []

# global variables available in all functions
app = adsk.core.Application.get()
ui  = app.userInterface

# global variables because I can't find a better way to pass this info around -- would be nice if fusion api had some cleaner way to do this
debug = True

def run(context):
    
    try:

        # Get the CommandDefinitions collection so we can add a command
        command_definitions = ui.commandDefinitions
        
        tooltip = 'Pull tool library from git'

        text_palette = ui.palettes.itemById('TextCommands')

        # Create a button command definition.
        library_button = command_definitions.addButtonDefinition('pull_tool_library', 'Pull tool library', tooltip, 'resources')
        
        # Connect to the command created event.
        library_command_created = command_created()
        library_button.commandCreated.add (library_command_created)
        handlers.append(library_command_created)

        # add the Moose Tools to the CAM workspace Utilities tab
                
        utilities_tab = ui.allToolbarTabs.itemById('UtilitiesTab')

        if utilities_tab:
            debug_print ('UtilitiesTab found')

            # get or create the "Moose Tools" panel.
        
            moose_cam_panel = ui.allToolbarPanels.itemById('MooseCAM')
            if not moose_cam_panel:
                moose_cam_panel = utilities_tab.toolbarPanels.add('MooseCAM', 'Moose Tools')
                debug_print ('Moose CAM panel created')

        if moose_cam_panel:
            # Add the command to the panel.
            control = moose_cam_panel.controls.addCommand (library_button)
            control.isPromoted = False
            control.isPromotedByDefault = False
            debug_print ('Moose CAM Tools installed')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the commandCreated event.
class command_created (adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):

        text_palette = ui.palettes.itemById('TextCommands')

        event_args = adsk.core.CommandCreatedEventArgs.cast(args)
        command = event_args.command
        inputs = command.commandInputs
 
        # Connect to the execute event
        onExecute = command_executed()
        command.execute.add(onExecute)
        handlers.append(onExecute)

        # create the dropdown with all the tool libraries in the github repository
        library_selection_input = inputs.addDropDownCommandInput('tool_library_select', 'Select tool library', adsk.core.DropDownStyles.CheckBoxDropDownStyle)
        library_selection_input.maxVisibleItems = 10
        list = library_selection_input.listItems

        repo_url = "https://api.github.com/repos/carlbass/fusion_tool_libraries/contents"

        request = adsk.core.HttpRequest.create(repo_url, adsk.core.HttpMethods.GetMethod)
        request.setHeader ('accept', 'application/vnd.github+json')
        response = request.executeSync()

        # if we got a good response put up a UI to chhose which tool library to download from git
        if response.statusCode == 200:
            #text_palette.writeText (f'data: {response.data}')
            tool_library_names = parse_github_json (response.data)

        for name in tool_library_names:
            list.add (name, False, '')
        
        # create debug checkbox widget
        inputs.addBoolValueInput('debug', 'Debug', True, '', debug)

# Event handler for the execute event.
class command_executed (adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global debug

        try:
            design = app.activeProduct
            text_palette = ui.palettes.itemById('TextCommands')

            # get current command
            command = args.firingEvent.sender

            for input in command.commandInputs:
                if (input.id == 'tool_library_select'):
                    libraries_selected = input.listItems
                    for l in libraries_selected:
                        if l.isSelected:
                            debug_print (f'<{l.name}>')
                elif (input.id == 'debug'):
                    debug = input.value           
                else: 
                    debug_print (f'OOOPS --- too much input')

            # download the chosen tool libraries from the git repository
            library_manager = adsk.cam.CAMManager.get().libraryManager

            tool_libraries = library_manager.toolLibraries
            tool_library_url = tool_libraries.urlByLocation(adsk.cam.LibraryLocations.LocalLibraryLocation)


            for lib in libraries_selected:
                if lib.isSelected: 
                    base_url = "https://raw.githubusercontent.com/carlbass/fusion_tool_libraries/main/"

                    tool_library_name = lib.name + '.json'
                    base_url = base_url + tool_library_name
                    download_url = base_url.replace (' ', '%20')

                    debug_print (f'Requesting: {download_url} {lib.isSelected}')
    
                    request = adsk.core.HttpRequest.create(download_url, adsk.core.HttpMethods.GetMethod)

                    if request.hasHeader:
                        (status, hnames, hvalues) = request.headers()
                        for h in hnames:
                            debug_print (f'{h}')            
                        for h in hvalues:
                            debug_print (f'{h}')

                    response = request.executeSync()

                    if response.statusCode == 200:

                        text_palette.writeText (f'About to create {tool_library_name}')
                        local_libraries = tool_libraries.childAssetURLs(tool_library_url)

                        for ll in local_libraries:
                            basename = os.path.basename(ll.toString())

                            debug_print (f'comparing {basename} => {lib.name}')

                            # delete library if same one exists before making a new one
                            if basename == lib.name:
                                status = tool_libraries.deleteAsset(ll)
                                debug_print (f'deleting {basename} => {status}')

                        tool_library = adsk.cam.ToolLibrary.createFromJson(response.data)
                        tool_libraries.importToolLibrary (tool_library, tool_library_url, tool_library_name)

                        debug_print (f'created {tool_library_name} with {tool_library.count} tools')

        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))	


def debug_print (msg):
    if debug:
        text_palette = ui.palettes.itemById('TextCommands')
        text_palette.writeText (msg)

def parse_github_json (json):

    substring = '"name"'
    indices = []

    # Set the starting index i to 0.
    i = 0

    while i < len (json):
        j = json.find(substring, i)
        if j == -1:
            break
        indices.append(j)
        i = j + len (substring)

    #text_palette.writeText (f'{indices}')

    names = []
    for i in indices:
        name_start = json.find('"', i + 7)
        name_end = json.find('"', i + 8)
        #text_palette.writeText (f'{name_start} : {name_end}')
        # check if .json and trim
        json_suffix = json.find (".json", name_start, name_end)
        if json_suffix != -1:
            names.append (json [name_start+1: json_suffix])
        
            #text_palette.writeText (f'{json [name_start + 1:json_suffix]}')
            #text_palette.writeText (f'{json [name_start + 1:name_end - 5]}')

    return names

def stop(context):
    try:
        global handlers

        # Clean up the UI.
        command_definitions = ui.commandDefinitions.itemById('pull_tool_library')
        if command_definitions:
            command_definitions.deleteMe()
        
        # get rid of this button
        moose_cam_panel = ui.allToolbarPanels.itemById('MooseCAM')

        control = moose_cam_panel.controls.itemById('pull_tool_library')
        if control:
            control.deleteMe()

        # and if it's the last button, get rid of the moose panel
        if moose_cam_panel.controls.count == 0:
            moose_cam_panel.deleteMe()
        
        handlers = []

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))	
