from app import app
from flask import request, jsonify, send_file
import os
import uuid
from pdf2docx import Converter
from werkzeug.utils import secure_filename

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf'}

@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'pdf_file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
    file = request.files['pdf_file']
    conversion_id = request.form.get('conversion_id', str(uuid.uuid4()))
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Only PDF files allowed'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(f"{conversion_id}.pdf")
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # Convert to DOCX
        output_filename = f"{conversion_id}.docx"
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
        
        cv = Converter(upload_path)
        cv.convert(output_path)
        cv.close()
        
        # Return download URL
        download_url = f"https://{request.host}/download/{conversion_id}"
        
        return jsonify({
            'success': True,
            'download_url': download_url,
            'conversion_id': conversion_id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<conversion_id>', methods=['GET'])
def download_file(conversion_id):
    try:
        filename = f"{conversion_id}.docx"
        file_path = os.path.join(app.config['CONVERTED_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"converted_{conversion_id[:8]}.docx"
        )
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
