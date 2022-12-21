import pathlib
from flask import send_from_directory
from werkzeug.utils import secure_filename


def build_assets(server):
    @server.route("/MLA/assets/<path:file_name>")
    def _host_assets(file_name):
        return send_from_directory(pathlib.Path(__file__).parent / "misc", secure_filename(file_name))

