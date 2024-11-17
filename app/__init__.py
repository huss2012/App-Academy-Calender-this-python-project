from flask import (Flask)
from app import config
from app import routes


app = Flask(__name__)
app.config.from_object(config)


app.register_blueprint(routes.bp)
