from __future__ import print_function
from flask import Flask, render_template, request
import pandas as pd
import re
import requests
import json
from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

app = Flask(__name__)

df = pd.read_csv("minutes_v4.csv")


@app.route("/")
@app.route("/Minutes")
def hello_world():
    return render_template('Minutes.html')


@app.route('/search', methods=['GET','POST'])
def search():
    search_query = request.args.get('search_query')
    print(f'Search Query: {search_query} with Type: {type(search_query)}')
    def search_word(word):
        i = 0
        l_rows = []
        for row in df.text:
            # Rows referring to blank pages are null
            if not isinstance(row, float):
                if word in row:
                    # d_rows = {"id": '<th class="click">' + df.loc[i, "id"]+ '</th>',
                    #           "period": df.loc[i, "period"], "committee": df.loc[i, "comitee"]}
                    # d_rows = {"id": '<form action="/search" method="post" target="_blank"><input type="button" value="' + df.loc[i, "id"] + ' "id="seePage"></form>',
                    #           "period": df.loc[i, "period"], "committee": df.loc[i, "comitee"]}
                    d_rows = {"id": df.loc[i, "id"], "period": df.loc[i, "period"],
                              "committee": df.loc[i, "comitee"]}
                    l_rows.append(d_rows)
            i += 1
        new_df = pd.DataFrame.from_dict(l_rows)
        html_table = new_df.to_html(classes='my-table', border=1, escape=False)
        # Discard extra tags given from .to_html
        # html_table = '<form action="/image" method="GET">' + html_table + '</form>'
        html_table = re.sub(' <td><th class="click">', '<td class="click">', html_table)
        html_table = re.sub(' </th></td>', '</td>', html_table)
        return html_table
    if search_query is not None:
        table = search_word(search_query)
    else:
        table = ''
    cell_value = request.args.get('search') #request.form.get('buttonText')
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

    # Set the path to the client secret JSON file
    CLIENT_SECRET_FILE = 'cred_2.json'
    # Create the flow object and start the authorization flow
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES, redirect_uri='http://127.0.0.1:5000')

    credentials = flow.run_local_server(port=0)
    # Google Drive API setup

    if cell_value:
        def get_image(image):
            folder_id = '1Eo1jZDU8_BLRzw8kArrTTBJZ0zqwJRP6'
            access_token = credentials.token
            print(f'access token f{access_token}')

            headers = {'Authorization': 'Bearer ' + access_token}
            url = 'https://www.googleapis.com/drive/v3/files?q=name="' + image.strip() + '.jpg"+and+parents="' + folder_id + '"'
            print("URL: " + url)
            # Send request to Google Drive API
            response = requests.get(url, headers=headers)
            data = json.loads(response.content)
            print(f"data: {data}")
            # Get the download link of the first image with the matching name
            try:
                file_id = data['files'][0]['id']
                print(f'file id: {file_id}')
                image_url = 'https://drive.google.com/uc?id=' + file_id
                print(f'image_url: {image_url}')
                return image_url
            except IndexError:
                print('except')
                return 'except'


        image_url = get_image(cell_value)
        if image_url != 'except':
            return render_template('search_results.html', table=table, cell_value=cell_value, image_url=image_url)
        else:
            return render_template('search_results.html', table=table, cell_value=cell_value, error_message='No matching image found')
    else:
        return render_template("search_results.html", table=table)


# @app.route('/image', methods=['POST'])
# def image_display():
#     cell_value = request.form.get('buttonText')
#     print(f'cell_value: {cell_value}')
#     # return 'Success' #render_template("test.html",  cell_value='test', error_message='No matching image found')
#     print(f"The button text is: {cell_value}")
#     # Do something with the cell value
#
#     SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
#
#     # Set the path to the client secret JSON file
#     CLIENT_SECRET_FILE = 'cred_2.json'
#     # Create the flow object and start the authorization flow
#     flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES, redirect_uri='http://127.0.0.1:5000')
#
#     credentials = flow.run_local_server(port=0)
#     # Google Drive API setup
#
#     if cell_value:
#         def get_image(image):
#             folder_id = '1Eo1jZDU8_BLRzw8kArrTTBJZ0zqwJRP6'
#             access_token = credentials.token
#             print(f'access token f{access_token}')
#
#             headers = {'Authorization': 'Bearer ' + access_token}
#             url = 'https://www.googleapis.com/drive/v3/files?q=name="' + image.strip() + '.jpg"+and+parents="' + folder_id + '"'
#             print("URL: " + url)
#             # Send request to Google Drive API
#             response = requests.get(url, headers=headers)
#             data = json.loads(response.content)
#             print(f"data: {data}")
#             # Get the download link of the first image with the matching name
#             try:
#                 file_id = data['files'][0]['id']
#                 print(f'file id: {file_id}')
#                 image_url = 'https://drive.google.com/uc?id=' + file_id
#                 print(f'image_url: {image_url}')
#                 return image_url
#                 # return render_template('image.html', cell_value=cell_value, image_url=image_url)
#             except IndexError:
#                 print('except')
#                 return 'except'
#                 # return render_template('image.html', cell_value=cell_value, error_message='No matching image found')
#         image_url = get_image(cell_value)
#         if image_url != 'except':
#             return render_template('image.html', cell_value=cell_value, image_url=image_url)
#         else:
#             return render_template('image.html', cell_value=cell_value, error_message='No matching image found')
#     else:
#         return 'ok'


if __name__ == '__main__':
    app.run(debug=True,  host='0.0.0.0')
