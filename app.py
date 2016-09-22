from PIL import Image, ImageChops, ImageEnhance
import requests
import os
from flask import Flask, redirect, jsonify, render_template, request, send_file
import werkzeug
import datetime
import uuid

app = Flask(__name__)

ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def process_image(img):
  #open up the mask
  overlay = Image.open('./filters/BigLittleFilter.png')

  #make sure our images have alpha channel
  overlay = overlay.convert('RGBA')
  img = img.convert('RGBA')

  #make sure it matches the size of the image
  overlay = overlay.resize(img.size)

  img.paste(overlay, (0, 0), overlay)

  #unique name
  filename = uuid.uuid4().hex + '.png'
  filename = os.path.join('/tmp', filename)
  img.save(filename, 'PNG')
  #send it back
  return filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasafy', methods=['POST'])
def classify_upload():
  try:
    #get the image from the request
    imagefile = request.files['imagefile']
    filename_ = str(datetime.datetime.now()).replace(' ', '_') + \
            werkzeug.secure_filename(imagefile.filename)
    filename = os.path.join('/tmp', filename_)

    #make sure it has the correct file type
    b = False
    for ext in ALLOWED_IMAGE_EXTENSIONS:
      if ext in filename:
        b = True
    if not b:
      return 'Invalid filetype.'

    #save the file to /tmp
    imagefile.save(filename)
    #open the image for Pillow
    image = Image.open(filename)
  except Exception as err:
    #uh oh. Something went wrong.
    print('Uploaded image open error: ' + err)
    return 'Error: ' + err

  #process the image
  resultFilename = process_image(image)
  #send it back
  return send_file(resultFilename)

if __name__ == '__main__':
  app.run(debug=True)