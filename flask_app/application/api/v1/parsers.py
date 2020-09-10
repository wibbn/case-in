from flask import current_app
from application import app
from flask_restx.reqparse import RequestParser
with app.app_context():
    config = app.config

paging_parser = RequestParser()
paging_parser.add_argument("page", type=int, default=1,
                           help="Page number")
paging_parser.add_argument("per_page", type=int,
                           default=config["APP_ROW_PER_PAGE"],
                           help="Number of items per each request")
paging_parser.add_argument("order_by", type=str,
                           help="Order by some attribute")
paging_parser.add_argument("desc", type=bool,
                           help="Desc ordering if it is provided")
