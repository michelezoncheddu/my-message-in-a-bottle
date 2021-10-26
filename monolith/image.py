import os
from werkzeug.utils import secure_filename

#utility function for saving attachments (messages) or profile pics (users)
def save_image(file, path):
    filename = secure_filename(file.filename)
    file.save(os.path.join('monolith/static/profile', filename))
    return filename

