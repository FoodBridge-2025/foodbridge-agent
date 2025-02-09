import base64
from socket import SocketIO
from flask import Blueprint, Flask, json, render_template
from flask import request
from flask_cors import CORS
from foodbridge.modules.getPantryDetails import PantryContentExtractor
from foodbridge.search.search import closeDriver, getContent, openPage
from foodbridge.groq.imageResoning import reason_image
from flask_socketio import SocketIO, send
from flask import jsonify

base_file_path = "/Users/kaushaldamania/llms/foodbridge/images/"

app = Flask(__name__)

MEGABYTE = (2 ** 10) ** 2
app.config['MAX_CONTENT_LENGTH'] = None
# Max number of fields in a multi part form (I don't send more than one file)
# app.config['MAX_FORM_PARTS'] = ...
app.config['MAX_FORM_MEMORY_SIZE'] = 50 * MEGABYTE

app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
        "supports_credentials": True
    }
})


# Basic configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['DEBUG'] = False

# Basic route
@app.route('/')
def home():
    return 'Welcome to Flask!'

@app.route('/autofill')
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

@app.route('/upload_image', methods=['POST'])
def upload_image():
    image_base64 = request.form.get('image')  # Get Base64 string
    if not image_base64:
        return jsonify({"error": "No image data received"}), 400

    try:
        image_data = base64.b64decode(image_base64)  # Decode Base64
        file_path = base_file_path + "uploaded_image.jpg"
        with open(file_path, "wb") as f:
            f.write(image_data)  # Save as a file
            output = reason_image(file_path)
            try:
                json_output = jsonify(json.loads(output))
            except:
                return jsonify({"error": "Failed to jsonify output"}), 500

        return json_output, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload_image_og', methods=['POST'])
def upload_image_og():
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

@socketio.on('message')
def handle_message(msg):
    print(f"Message: {msg}")
    send(f"your message: {msg}", broadcast=True) 

if __name__ == '__main__':
    app.run(port=5005)

