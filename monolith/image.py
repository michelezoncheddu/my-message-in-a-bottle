import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# utility function for saving attachments (messages) or profile pics (users)
def save_image(file, path):
    filename = secure_filename(file.filename)
    file.save(os.path.join('monolith/static/profile', filename))
    return filename

# utility for checking if attachments have a valid format
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

