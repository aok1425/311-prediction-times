from __future__ import division
from flask import Flask, session, redirect, url_for, escape, request, render_template, jsonify
import random
from models import get_model, make_pred, sample_row, make_q1_map_json
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
# app.permanent_session_lifetime = 60 * 60 * 1.5 # seconds, so 1.5 hours
# TODO: uncomment the below
# model = get_model() # temporary
q1_dict = make_q1_map_json()


@app.route('/')
def start(): 
    return render_template('home.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    return render_template('predict.html')


@app.route('/predict-results', methods=['POST'])
def predict_results():
    pred = make_pred(request.form, model)
    return str(pred)[:4]


@app.route('/explore', methods=['GET', 'POST'])
def explore():
    return render_template('explore.html')


@app.route('/get-q1-top-types')
def get_top_types():
    return jsonify(q1_dict) 


@app.route('/map3')
def map_q1_income():
    return render_template('map_q1_income.html') 


@app.route('/map2')
def map():
    return render_template('map_q1.html')    


@app.route('/map')
def map_per_1000():
    return render_template('map_q1_per_1000.html')   


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

# set the secret key.  keep this really secret:
app.secret_key = 'alex'

if __name__ == '__main__':
    app.run(debug=True)