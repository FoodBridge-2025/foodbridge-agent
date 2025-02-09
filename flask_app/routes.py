from flask import Blueprint, json, render_template
from flask import request
from foodbridge.modules.getPantryDetails import PantryContentExtractor
from foodbridge.search.search import closeDriver, getContent, openPage
from foodbridge.groq.imageResoning import reason_image
from flask import jsonify

bp = Blueprint('main', __name__)
base_file_path = "/Users/kaushaldamania/llms/foodbridge/images/"


@bp.route('/autofill')
def autofill():
    link = request.args.get('link', '')
    openPage(link)
    content = getContent()
    extractor = PantryContentExtractor(content)
    info = extractor.forward()
    print(info)
    predict_dict = {
        "pantryName": info.pantryName,
        "pantryAddress": info.pantryAddress,
        "pantryPhoneNumber": info.pantryPhoneNumber,
        "operationalDays": info.operationalDays,
        "operationalHours": info.operationalHours
    }

    print(predict_dict)
    return jsonify(predict_dict)

@bp.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename:
        # Save the file or process it as needed
        file_path = base_file_path + file.filename
        file.save(file_path)
        output = reason_image(file_path)
        try:
            json_output = jsonify(output)
        except:
            return jsonify({"error": "Failed to jsonify output"}), 500

        return json_output, 200

    return jsonify({"error": "Failed Process Image"}), 500