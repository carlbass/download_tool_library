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
        library_button = command_definitions.addButtonDefinition('pull_tool_library', 'Pull tool library', tooltip, './resources')
        
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
            control = moose_cam_panel.controls.addCommand(library_button)
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
        list.add ('Haas VM3', False, '')
        list.add ('Thermwood Model 90', False, '')
        list.add ('Hass ST30SSY', False, '')
        
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
                            text_palette.writeText (f'{l.name}')
                elif (input.id == 'debug'):
                    debug = input.value           
                else: 
                    debug_print (f'OOOPS --- too much input')

        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))	


def debug_print (msg):
    if debug:
        text_palette = ui.palettes.itemById('TextCommands')
        text_palette.writeText (msg)


def stop(context):
    try:
        global handlers

        # Clean up the UI.
        command_definitions = ui.commandDefinitions.itemById('pull_tool_library')
        if command_definitions:
            command_definitions.deleteMe()
        
        # get rid of this button
        moose_tools_panel = ui.allToolbarPanels.itemById('Moose CAM')
        control = moose_tools_panel.controls.itemById('pull_tool_library')
        if control:
            control.deleteMe()

        # and if it's the last button, get rid of the moose panel
        if moose_tools_panel.controls.count == 0:
                    moose_tools_panel.deleteMe()
        
        handlers = []

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))	
