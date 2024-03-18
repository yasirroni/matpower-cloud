import os

from flask import Flask, request, render_template, abort
from werkzeug.utils import secure_filename
from matpower import start_instance
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(app, default_limits=["100 per 1 day", "10 per 1 hour"])
limiter.key_func = get_remote_address

# Continue with the rest of your code...


# Set maximum file size to 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'m'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@limiter.limit("60 per 1 minute")  # Limit upload endpoint to 60 requests per minute
def upload_file():
    if 'file' not in request.files:
        abort(400, "No file part")
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        abort(400, "No selected file")
    if uploaded_file and allowed_file(uploaded_file.filename):
        filename = secure_filename(uploaded_file.filename)
        path = 'uploads/' + filename
        uploaded_file.save(path)
        return render_template('index.html', message='File uploaded successfully.', filename=filename)
    else:
        abort(400, "Invalid file format")

@app.route('/run_power_flow', methods=['POST'])
@limiter.limit("10 per minute")  # Limit power flow calculation endpoint to 10 requests per minute
def run_power_flow():
    filename = request.form.get('filename')
    if not filename:
        abort(400, "No file selected")
    file_path = 'uploads/' + filename
    if not os.path.isfile(file_path):
        abort(400, "File does not exist")
    m = start_instance()
    mpc = m.loadcase(file_path)
    result = m.runpf(mpc)
    return render_template('index.html', power_flow_result=result)

if __name__ == '__main__':
    app.run(debug=True)
