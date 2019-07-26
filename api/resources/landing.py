from flask_restful import Resource
from flask import render_template



class Landing(Resource):
    def __init__(self, **kwargs):
        super().__init__()
        self.excelHandler = kwargs['handler']

    def get(self):
        m = "testing static file from landing.py"
        #return render_template('index.html',message=m)
        return self.excelHandler.test_val()