from flask import Flask, request, render_template
from matpower import start_instance

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        path = 'uploads/' + uploaded_file.filename
        uploaded_file.save(path)
        return render_template('index.html', message='File uploaded successfully.', filename=uploaded_file.filename)
    else:
        return render_template('index.html', message='No file selected.')

@app.route('/run_power_flow', methods=['POST'])
def run_power_flow():
    file_path = 'uploads/' + request.form['filename']
    m = start_instance()
    mpc = m.loadcase(file_path)
    result = m.runpf(mpc)
    return render_template('index.html', power_flow_result=result)

if __name__ == '__main__':
    app.run(debug=True)
