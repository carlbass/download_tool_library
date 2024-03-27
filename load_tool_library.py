import adsk.core, adsk.fusion, adsk.cam, traceback
import os
import time
import base64

import json
global text_palette 
global ui

def run(context):
    global text_palette
    global ui

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
            #text_palette.writeText (f'data: {response.data}')
            #tool_library_names = parse_github_json (response.data)

            jdata = json.loads(response.data)
    
            if jdata:
                for jd in jdata:
                    #text_palette.writeText (f'{jd["name"]} ====> {jd["sha"]}')
                    if jd['name'] == 'OMAX.json':
                        omax_sha = jd["sha"]
                        text_palette.writeText (f'{jd["name"]} ====> {jd["sha"]}')

        download_url = "https://raw.githubusercontent.com/carlbass/fusion_tool_libraries/main/OMAX.json"
    
        text_palette.writeText (f'Requesting: {download_url}')

        request = adsk.core.HttpRequest.create(download_url, adsk.core.HttpMethods.GetMethod)
        response = request.executeSync()
        
        if response.statusCode == 200:
            file_contents = response.data
            text_palette.writeText (file_contents)

            text_palette.writeText ('_____________________________')

            #json_file_contents = json.dumps (file_contents)
            #text_palette.writeText (json_file_contents)

            #text_palette.writeText ('_____________________________')

            #byte_file_contents = file_contents.encode('utf-8')
            
            #encoded_file_contents = base64.b64encode (byte_file_contents)

            file_contents = '{"first_name": "Michael"}'
            encoded_file_contents = base64.b64encode(file_contents.encode("utf-8"))

        else:
            text_palette.writeText (f'ERROR: {response.statusCode}')

        # now try to update it
        
        message = str(time.time())
        text_palette.writeText (f'{message}')
        #content = file_contents.decode("utf-8")

        put_data = f'"message": {message},"content": {encoded_file_contents}, "sha": {omax_sha}'

        put_url = "https://api.github.com/repos/carlbass/fusion_tool_libraries/contents/OMAX.json"
        put_request = adsk.core.HttpRequest.create(put_url, adsk.core.HttpMethods.PutMethod)
        put_request.data = put_data
        
        put_request.setHeader ('accept', 'application/vnd.github+json')
        put_request.setHeader ('Authorization', 'Bearer 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')
        
        put_response = put_request.executeSync()

        text_palette.writeText (f'put response code: {put_response.statusCode}')
        text_palette.writeText (f'put response: {put_response.data}')
    
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

