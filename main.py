from flask import Flask, render_template, request, redirect, url_for
import json
import os
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageTk
import io
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'json'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def load_data(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def generate_barcode(value):
    barcode = Code128(value, writer=ImageWriter())
    buffer = io.BytesIO()
    barcode.write(buffer)
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'data.json')
            file.save(filepath)
            return redirect(url_for('display_barcodes'))

    return render_template('index.html')

@app.route('/display')
def display_barcodes():
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'data.json')
    items = load_data(filepath)
    for item in items:
        item['index_barcode'] = generate_barcode(item['index'])
        item['amount_barcode'] = generate_barcode(item['amount'])
    return render_template('display.html', items=items)

if __name__ == '__main__':
    app.run(debug=True)