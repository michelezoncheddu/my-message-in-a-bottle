import os
from werkzeug.utils import secure_filename

#helper function to save images to local directory from create_message form
def save_image(file):
    filename = secure_filename(file.filename)
    file.save(os.path.join('monolith/images', filename))
    return filename

#utility function to save profile pictures
def save_profile_picture(file):
    filename = secure_filename(file.filename)
    file.save(os.path.join('monolith/static/profile', filename))
    return filename
