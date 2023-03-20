from __future__ import print_function
from flask import Flask, render_template, request
import requests
import json
from google_auth_oauthlib.flow import InstalledAppFlow


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

app = Flask(__name__)


@app.route('/')
@app.route('/dummy', methods=['GET', 'POST'])
def index():
    print("here")
    # Set the scope to the Google Drive API
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

    # Set the path to the client secret JSON file
    CLIENT_SECRET_FILE = 'cred_2.json'
    # Create the flow object and start the authorization flow
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES,  redirect_uri='http://127.0.0.1:5000')
    print(1)
    credentials = flow.run_local_server( port=0)
    print(2)

    if request.method == 'GET':
        print(3)
        # search_term = request.args.get('search')
        search_term = request.args.get('search')
        print(search_term)
        if search_term:
            # Google Drive API setup
            folder_id = '1Eo1jZDU8_BLRzw8kArrTTBJZ0zqwJRP6'
            access_token = credentials.token

            headers = {'Authorization': 'Bearer ' + access_token}
            url = 'https://www.googleapis.com/drive/v3/files?q=name="' + search_term + '.jpg"+and+parents="' + folder_id + '"'
            print("URL: " + url)
            # Send request to Google Drive API
            response = requests.get(url, headers=headers)
            data = json.loads(response.content)

            # Get the download link of the first image with the matching name
            try:
                file_id = data['files'][0]['id']
                image_url = 'https://drive.google.com/uc?id=' + file_id
                print(image_url)
                return render_template('dummy.html', search_term=search_term, image_url=image_url)
            except IndexError:
                return render_template('dummy.html', search_term=search_term, error_message='No matching image found')
        else:
            return render_template('dummy.html', message='Please provide a search term.')




    # return render_template('dummy.html')


if __name__ == '__main__':
    app.run(debug=True)
