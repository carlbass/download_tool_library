import adsk.core, adsk.fusion, adsk.cam, traceback
import os
import base64
import json

def run(context):

    app = adsk.core.Application.get()
    ui  = app.userInterface
    text_palette = ui.palettes.itemById('TextCommands')
    
    try:

        # start by seeing what tool libraries are in the github repository

        repo_url = "https://api.github.com/repos/carlbass/fusion_tool_libraries/contents"

        request = adsk.core.HttpRequest.create(repo_url, adsk.core.HttpMethods.GetMethod)
        request.setHeader ('accept', 'application/vnd.github+json')
        response = request.executeSync()

        if response.statusCode == 200:

            jdata = json.loads(response.data)
    
            if jdata:
                for jd in jdata:
                    #text_palette.writeText (f'{jd["name"]} ====> {jd["sha"]}')
                    if jd['name'] == 'OMAX.json':
                        omax_sha = jd["sha"]
                        text_palette.writeText (f'{jd["name"]} ====> {jd["sha"]}')

        library_manager = adsk.cam.CAMManager.get().libraryManager
        tool_libraries = library_manager.toolLibraries
        tool_library_url = tool_libraries.urlByLocation(adsk.cam.LibraryLocations.LocalLibraryLocation)

        local_libraries = tool_libraries.childAssetURLs(tool_library_url)
        
        for ll in local_libraries:
            text_palette.writeText (f'{ll.toString()}')
            basename = os.path.basename(ll.toString())
            if basename == 'OMAX':
                text_palette.writeText (f'{basename}')
                omax_tool_library = tool_libraries.toolLibraryAtURL(ll)

                file_contents = omax_tool_library.toJson()       
                text_palette.writeText ('_____________________________')
                text_palette.writeText (file_contents)
                text_palette.writeText ('_____________________________')        
                
        github_token = os.getenv ('GITHUB_TOKEN')
        text_palette.writeText (f'token = {github_token}')
        github_token_string = f'Bearer {github_token}'
        text_palette.writeText (f'token string = {github_token_string}')

        text_palette.writeText ('_____________________________')

        json_request_data = {
            "message": "tool library push",
            "content": base64.b64encode(file_contents.encode()).decode(),
            "sha": omax_sha
            }
        
        json_request_string = json.dumps (json_request_data)

        text_palette.writeText ('_____________________________')

        text_palette.writeText (f'token string = {github_token_string}')

        text_palette.writeText ('_____________________________')

        put_url = "https://api.github.com/repos/carlbass/fusion_tool_libraries/contents/OMAX.json"
        put_request = adsk.core.HttpRequest.create(put_url, adsk.core.HttpMethods.PutMethod)
        put_request.data = json_request_string
        
        put_request.setHeader ('accept', 'application/vnd.github+json')
        put_request.setHeader ('Authorization', github_token_string)
        
        put_response = put_request.executeSync()

        text_palette.writeText (f'put response code: {put_response.statusCode}')

        response_json = json.loads(put_response.data)
        text_palette.writeText (f'put response: {response_json}')
    
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

