from flask import Flask
from flask import render_template
from flask import request, Response
from flask import jsonify
from flask import redirect
from flask import send_from_directory
import requests
import json
import os
import numpy as np
from PIL import Image
import cv2
import helpers as driver

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='assets/img/favicon_cmc.ico')

@app.route('/')
def hello_world():
    searchbox = request.args.get('search')
    return render_template('dashboard.html', searchbox=searchbox)


@app.route('/getdata', methods=['POST'])
def get_data_search():
    if request.method == 'POST':
        if 'search' in request.form:
            search = request.form['search']
            condition = request.form['condition'] if 'condition' in request.form else ""
            limit = str(request.form['limit']) if 'limit' in request.form else "10"
            data_specific = driver.data_search(search, type=0, condition=condition, limit=limit)
        else:
            search = request.form['cypher-search']
            search = search.lower()
            if search.find("create") > -1 or search.find("merge") > -1\
                    or search.find("delete") > -1 or search.find("call") > -1:
                raise ValueError("Cú pháp không được phép")
            data_specific = driver.data_search(search, type=1)
        return jsonify(data_specific)



@app.route('/get-detail-data', methods=['POST'])
def get_detail_data():
    if request.method == 'POST':
        id = request.form['id']
        limit = int(request.form['limit'])
        data_specific = driver.data_detail(id, limit)
        return jsonify(data_specific)


def get_search_data():
    return 0


@app.route('/realtime-camera')
def get_realtime_camera():
    return render_template('realtime_camera.html')


@app.route('/get-more-infomation', methods=['POST'])
def get_more_information():
    node_id = request.form['node_id']
    result = driver.more_data(node_id)
    return jsonify(result)


@app.route('/recent_id', methods=['GET', 'PUT'])
def get_recent_id():
    if request.method == 'GET':
        with open('recent_id.txt', 'r') as f:
            recent_id = f.read().replace('\n', '')
        return jsonify({'id': recent_id, 'link': 'http://124.158.1.123:5000/recent_image'})
    elif request.method == 'PUT':
        recent_id = request.json['recent_id']
        with open('recent_id.txt', 'w') as f:
            f.write(recent_id)
        return Response(status=200)


@app.route('/face_upload', methods=['GET', 'POST'])
def face_upload():
    if request.method == 'GET':
        return render_template('face_upload.html')
    elif request.method == 'POST':
        global recent_id
        image = request.files['image']
        img_read_stream = Image.open(image.stream)
        image = np.array(img_read_stream)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imwrite('temp.jpg', image)
        url = 'http://localhost:5000/face/findsimilars'
        headers = {'Auth-Token': '"AzfqFfnBXaXzr0bA4oUL".MUHJ-mN0vOSG0osqIL-jG-j0NvQ'}
        values = {'face_list_id': 'ekgdemo', 'max_nrof_candidate_returned': 5, 'detect_face': 'True'}
        files = {'image': open('temp.jpg', 'rb')}
        response = requests.post(url, headers=headers, data=values, files=files)
        json_data = json.loads(response.text)
        if len(json_data)>0:
            with open('recent_id.txt', 'w') as f:
                f.write(json_data[0]['persistedFaceId'])
            return redirect("/realtime-camera")
        else:
            return 'Not recognized!'


if __name__ == '__main__':
    app.run()
