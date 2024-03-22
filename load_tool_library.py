import adsk.core, adsk.fusion, adsk.cam, traceback
import json
global text_palette 
global ui

def run(context):
    global text_palette
    global ui

    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        text_palette = ui.palettes.itemById('TextCommands')

        # start by seeing what tool libraries are in the github repository

        repo_url = "https://api.github.com/repos/carlbass/fusion_tool_libraries/contents"

        request = adsk.core.HttpRequest.create(repo_url, adsk.core.HttpMethods.GetMethod)
        request.setHeader ('accept', 'application/vnd.github+json')
        response = request.executeSync()

        # if we got a good response put up a UI to chhose which tool library to download from git

        if response.statusCode == 200:
            #text_palette.writeText (f'data: {response.data}')
            tool_library_names = parse_github_json (response.data)

            output  = ''
            i = 1
            for t in tool_library_names:
                #text_palette.writeText (f'<{t}>')
                output = output + str(i) + ') ' + t + '\n'
                i = i + 1
        else:
            text_palette.writeText (f'error: {response.statusCode}')

        (choice, isCancelled) = ui.inputBox(output, 'choice', '1')

        text_palette.writeText (f'choice = {choice}')
        text_palette.writeText (f'choice = {tool_library_names[int(choice) - 1]}')

        # download the chosen tool library from the git repository
        library_manager = adsk.cam.CAMManager.get().libraryManager

        tool_libraries = library_manager.toolLibraries
        tool_library_url = tool_libraries.urlByLocation(adsk.cam.LibraryLocations.LocalLibraryLocation)
        
        tool_library_name = tool_library_names[int(choice) - 1] + '.json'

        base_url = "https://raw.githubusercontent.com/carlbass/thermwood/main/"
        download_url = base_url + tool_library_name
        download_url = "https://raw.githubusercontent.com/carlbass/thermwood/main/thermwood90.json"
        download_url = "https://raw.githubusercontent.com/carlbass/fusion_tool_libraries/main/z.json"
        download_url = "https://raw.githubusercontent.com/carlbass/fusion_tool_libraries/main/HAAS12345.json"
        download_url = "https://raw.githubusercontent.com/carlbass/fusion_tool_libraries/main/Haas VM3.json"

        text_palette.writeText (f'Requesting: {download_url}')

        request = adsk.core.HttpRequest.create(download_url, adsk.core.HttpMethods.GetMethod)
        if request.hasHeader:
            (status, hnames, hvalues) = request.headers()
            for h in hnames:
                text_palette.writeText (f'{h}')            
            for h in hvalues:
                text_palette.writeText (f'{h}')

        response = request.executeSync()
        
        if response.statusCode == 200:
            tool_library = adsk.cam.DocumentToolLibrary.createFromJson(response.data)
            text_palette.writeText (f'# tools: {tool_library.count}')
            tool_libraries.importToolLibrary (tool_library, tool_library_url, tool_library_name)
        else:
            text_palette.writeText (f'ERROR: {response.statusCode}')

        # delete library if same one exists before making a new one
        # returnValue = toolLibraries_var.deleteAsset(url)
        
        local_libraries = tool_libraries.childAssetURLs(tool_library_url)

        for ll in local_libraries:
            text_palette.writeText (ll.toString())

    


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

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
