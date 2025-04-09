
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# @api_bp.route('/recognize', methods=['POST'])
# def recognize_plate():
#     if 'image' not in request.files:
#         return jsonify({'error': 'No image file provided'}), 400

#     file = request.files['image']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     if file and allowed_file(file.filename):
#         try:
#             # Save uploaded file
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
#             file.save(filepath)

#             # Process image
#             cropped_plate = recognizer().crop_plate(filepath)
            
#             if cropped_plate is None:
#                 return jsonify({'error': 'No license plate detected'}), 400

#             # Detect text
#             result = recognizer().detect_text(np.array(cropped_plate))
#             cleaned_texts = recognizer().clean_text(result[1])

#             return jsonify({
#                 'status': 'success',
#                 'texts': cleaned_texts,
#                 'raw_result': result,
#                 'debug_image': result[2]
#             })

#         except Exception as e:
#             return jsonify({'error in /api/recognize ': str(e)}), 500

#         finally:
#             # Cleanup uploaded file
#             if os.path.exists(filepath):
#                 os.remove(filepath)

#     return jsonify({'error': 'Invalid file type'}), 400

# @api_bp.route('/recognize', methods=['POST'])
# def recognize_plate():
#     logger.info("Received request to /api/recognize")
    
#     if 'image' not in request.files:
#         logger.info("No image file provided in request")
#         return jsonify({'error': 'No image file provided'}), 400

#     file = request.files['image']
#     if file.filename == '':
#         logger.info("No selected file (empty filename)")
#         return jsonify({'error': 'No selected file'}), 400

#     if file and allowed_file(file.filename):
#         try:
#             # Save uploaded file
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
#             logger.debug(f"Saving file to {filepath}")
#             file.save(filepath)
            
#             # Verify file exists and has content
#             if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
#                 logger.info(f"File {filepath} is missing or empty")
#                 raise Exception("Saved file is missing or empty")

#             # Process image
#             logger.debug("Cropping plate")
#             cropped_plate = recognizer().crop_plate(filepath)
#             if cropped_plate is None:
#                 logger.info("No license plate detected in image")
#                 return jsonify({'error': 'No license plate detected'}), 400

#             # Convert to numpy array and detect text
#             logger.info("Detecting text")
#             result = recognizer().detect_text(np.array(cropped_plate))
#             cleaned_texts = recognizer().clean_text(result[1])

#             logger.info(f"Recognition successful: {cleaned_texts}")
#             return jsonify({
#                 'status': 'success',
#                 'texts': cleaned_texts,
#                 'raw_result': result,
#                 'debug_image': result[2]
#             })

#         except Exception as e:
#             logger.info(f"Error processing image: {str(e)}")
#             return jsonify({'error': str(e)}), 500

#         finally:
#             # Cleanup uploaded file
#             if os.path.exists(filepath):
#                 logger.info(f"Removing temporary file {filepath}")
#                 os.remove(filepath)

#     logger.info(f"Invalid file type: {file.filename}")
#     return jsonify({'error': 'Invalid file type'}), 400
# @api_bp.route('/recognize', methods=['POST'])
# def recognize_plate():
#     logger.info("Received request to /api/recognize")
    
#     if 'image' not in request.files:
#         logger.error("No image file provided in request")
#         return jsonify({'error': 'No image file provided'}), 400

#     file = request.files['image']
#     if file.filename == '':
#         logger.error("No selected file (empty filename)")
#         return jsonify({'error': 'No selected file'}), 400

#     if file and allowed_file(file.filename):
#         try:
#             # Save uploaded file
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
#             logger.info(f"Saving file to {filepath}")
#             file.save(filepath)
            
#             # Verify file exists and has content
#             if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
#                 logger.error(f"File {filepath} is missing or empty")
#                 raise Exception("Saved file is missing or empty")

#             # Check recognizer initialization
#             if recognizer() is None:
#                 logger.error("Recognizer is not initialized")
#                 raise Exception("License plate recognizer not initialized")

#             # Process image
#             logger.info("Cropping plate")
#             cropped_plate = recognizer().crop_plate(filepath)
#             if cropped_plate is None:
#                 logger.error("No license plate detected in image")
#                 return jsonify({'error': 'No license plate detected'}), 400

#             # Log cropped plate details
#             from PIL import Image  # Ensure this is imported
#             logger.info(f"Cropped plate type: {type(cropped_plate)}, size: {cropped_plate.size if isinstance(cropped_plate, Image.Image) else 'N/A'}")

#             # Detect text
#             logger.info("Detecting text")
#             result = recognizer().detect_text(cropped_plate)
#             if not isinstance(result, list) or len(result) != 3:
#                 logger.error(f"Invalid result format from detect_text: {result}")
#                 raise Exception("Text detection returned invalid result")

#             detected_texts, texts_only, debug_url = result
#             cleaned_texts = recognizer().clean_text(texts_only)

#             logger.info(f"Recognition successful: {cleaned_texts}")
#             return jsonify({
#                 'status': 'success',
#                 'texts': cleaned_texts,
#                 'raw_result': detected_texts,
#                 'debug_image': debug_url
#             })

#         except Exception as e:
#             logger.exception(f"Error processing image: {str(e)}")
#             return jsonify({'error': str(e)}), 500

#         finally:
#             # Cleanup uploaded file
#             if os.path.exists(filepath):
#                 logger.info(f"Removing temporary file {filepath}")
#                 os.remove(filepath)

#     logger.error(f"Invalid file type: {file.filename}")
#     return jsonify({'error': 'Invalid file type'}), 400

# app/routes/api.py

# @api_bp.route('/recognize', methods=['POST'])
# def recognize_plate():
#     logger.info("Received request to /api/recognize")
    
#     if 'image' not in request.files:
#         logger.error("No image file provided in request")
#         return jsonify({'error': 'No image file provided'}), 400

#     file = request.files['image']
#     if file.filename == '':
#         logger.error("No selected file (empty filename)")
#         return jsonify({'error': 'No selected file'}), 400

#     if file and allowed_file(file.filename):
#         try:
#             # Save uploaded file
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
#             logger.info(f"Saving file to {filepath}")
#             file.save(filepath)
            
#             # Verify file exists and has content
#             if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
#                 logger.error(f"File {filepath} is missing or empty")
#                 raise Exception("Saved file is missing or empty")

#             # Check recognizer initialization
#             if recognizer() is None:
#                 logger.error("Recognizer is not initialized")
#                 raise Exception("License plate recognizer not initialized")

#             # Process image
#             logger.info("Cropping plate")
#             cropped_plate = recognizer().crop_plate(filepath)
#             if cropped_plate is None:
#                 logger.error("No license plate detected in image")
#                 return jsonify({'error': 'No license plate detected'}), 400

#             # Detect text
#             logger.info("Detecting text")
#             result = recognizer().detect_text(cropped_plate)
#             if not isinstance(result, list) or len(result) != 3:
#                 logger.error(f"Invalid result format from detect_text: {result}")
#                 raise Exception("Text detection returned invalid result")

#             detected_texts, texts_only, debug_url = result
#             cleaned_texts = recognizer().clean_text(texts_only)
#             logger.info(f"OCR OUTPUT:{result} cleaned_texts:{cleaned_texts}")

#             # Convert debug image to base64
#             debug_image_path = os.path.join(current_app.root_path, debug_url.lstrip('/'))
#             with open(debug_image_path, "rb") as image_file:
#                 debug_image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

#             # cleaned_texts=cleaned_texts.join(' ')
#             final=f"{cleaned_texts[0]}{cleaned_texts[1]}"
#             logger.info(f"Recognition successful: {final}")
#             return jsonify({
#                 'status': 'success',
#                 'texts': final,
#                 'raw_result': detected_texts,
#                 'debug_image': debug_image_base64,
#                 'debug_url': debug_url
#             })

#         except Exception as e:
#             logger.exception(f"Error processing image: {str(e)}")
#             return jsonify({'error': str(e)}), 500

#         finally:
#             # Cleanup uploaded file
#             if os.path.exists(filepath):
#                 logger.info(f"Removing temporary file {filepath}")
#                 os.remove(filepath)

#     logger.error(f"Invalid file type: {file.filename}")
#     return jsonify({'error': 'Invalid file type'}), 400

# @api_bp.route('/recognize', methods=['POST'])
# def recognize_plate():
#     logger.info("Received request to /api/recognize")
    
#     if 'image' not in request.files:
#         logger.error("No image file provided in request")
#         return jsonify({'error': 'No image file provided'}), 400

#     file = request.files['image']
#     if file.filename == '':
#         logger.error("No selected file (empty filename)")
#         return jsonify({'error': 'No selected file'}), 400

#     if file and allowed_file(file.filename):
#         try:
#             # Save uploaded file
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
#             logger.info(f"Saving file to {filepath}")
#             file.save(filepath)
            
#             # Verify file exists and has content
#             if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
#                 logger.error(f"File {filepath} is missing or empty")
#                 raise Exception("Saved file is missing or empty")

#             # Check recognizer initialization
#             if recognizer() is None:
#                 logger.error("Recognizer is not initialized")
#                 raise Exception("License plate recognizer not initialized")

#             # Process image
#             logger.info("Cropping plate")
#             cropped_plate = recognizer().crop_plate(filepath)
#             if cropped_plate is None:
#                 logger.error("No license plate detected in image")
#                 return jsonify({'error': 'No license plate detected'}), 400

#             # Convert PIL Image to numpy array
#             import numpy as np
#             cropped_plate_np = np.array(cropped_plate)

#             # Detect text
#             logger.info("Detecting text")
#             result = recognizer().detect_text(cropped_plate_np)  # Pass numpy array instead of PIL Image
#             if not isinstance(result, list) or len(result) != 3:
#                 logger.error(f"Invalid result format from detect_text: {result}")
#                 raise Exception("Text detection returned invalid result")

#             detected_texts, texts_only, debug_url = result
#             cleaned_texts = recognizer().clean_text(texts_only)
#             logger.info(f"OCR OUTPUT:{result} cleaned_texts:{cleaned_texts}")

#             # Convert debug image to base64
#             debug_image_path = os.path.join(current_app.root_path, debug_url.lstrip('/'))
#             with open(debug_image_path, "rb") as image_file:
#                 debug_image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

#             final = f"{cleaned_texts[1][::-1]}{cleaned_texts[0]}"
#             logger.info(f"Recognition successful: {final}")
#             return jsonify({
#                 'status': 'success',
#                 'texts': final,
#                 'raw_result': detected_texts,
#                 'debug_image': debug_image_base64,
#                 'debug_url': debug_url
#             })

#         except Exception as e:
#             logger.exception(f"Error processing image: {str(e)}")
#             return jsonify({'error': str(e)}), 500

#         finally:
#             # Cleanup uploaded file
#             if os.path.exists(filepath):
#                 logger.info(f"Removing temporary file {filepath}")
#                 os.remove(filepath)

#     logger.error(f"Invalid file type: {file.filename}")
#     return jsonify({'error': 'Invalid file type'}), 400

# @api_bp.route('/recognize', methods=['POST'])
# def recognize_plate():
#     logger.info("Received request to /api/recognize")
    
#     if 'image' not in request.files:
#         logger.error("No image file provided in request")
#         return jsonify({'error': 'No image file provided'}), 400

#     file = request.files['image']
#     if file.filename == '' or not allowed_file(file.filename):
#         logger.error("Invalid or no file selected")
#         return jsonify({'error': 'Invalid or no file selected'}), 400

#     try:
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
#         logger.info(f"Saving file to {filepath}")
#         file.save(filepath)
        
#         cropped_plate = recognizer().crop_plate(filepath)
#         if cropped_plate is None:
#             logger.error("No license plate detected in image")
#             return jsonify({'error': 'No license plate detected'}), 400

#         cropped_plate_np = np.array(cropped_plate)
#         result = recognizer().detect_text(cropped_plate_np)
#         if not isinstance(result, list) or len(result) != 3:
#             logger.error(f"Invalid result format from detect_text: {result}")
#             raise Exception("Text detection returned invalid result")

#         detected_texts, texts_only, debug_url = result
#         cleaned_texts = recognizer().clean_text(texts_only)
#         final_plate = f"{cleaned_texts[1][::-1]}{cleaned_texts[0]}" if len(cleaned_texts) >= 2 else cleaned_texts[0]
#         logger.info(f"Recognition successful: {final_plate}")

#         debug_image_path = os.path.join(current_app.root_path, debug_url.lstrip('/'))
#         with open(debug_image_path, "rb") as image_file:
#             debug_image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

#         # Check residents
#         from app.models.user import Car
#         car = Car.query.filter_by(license_plate=final_plate).first()
#         if car:
#             resident = car.resident
#             return jsonify({
#                 'status': 'success',
#                 'type': 'resident',
#                 'texts': final_plate,
#                 'debug_image': debug_image_base64,
#                 'debug_url': debug_url,
#                 'resident': {
#                     'id': resident.id,
#                     'name': resident.user.name,
#                     'email': resident.user.email
#                 }
#             }), 200

#         # Check guests
#         guest = Guest.query.filter_by(license_plate=final_plate).first()
#         if guest:
#             current_invitation = guest.get_current_invitation()
#             return jsonify({
#                 'status': 'success',
#                 'type': 'guest',
#                 'texts': final_plate,
#                 'debug_image': debug_image_base64,
#                 'debug_url': debug_url,
#                 'guest': {
#                     'id': guest.id,
#                     'name': guest.name,
#                     'resident_id': guest.resident_id,
#                     'license_plate': guest.license_plate,
#                     'current_invitation': current_invitation.to_dict() if current_invitation else None
#                 }
#             }), 200

#         return jsonify({
#             'status': 'success',
#             'type': 'unknown',
#             'texts': final_plate,
#             'debug_image': debug_image_base64,
#             'debug_url': debug_url
#         }), 200

#     except Exception as e:
#         logger.exception(f"Error processing image: {str(e)}")
#         return jsonify({'error': str(e)}), 500

#     finally:
#         if os.path.exists(filepath):
#             logger.info(f"Removing temporary file {filepath}")
#             os.remove(filepath)
