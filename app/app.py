from __future__ import division
from flask import Flask, session, redirect, url_for, escape, request, render_template, jsonify
import random
from models import get_model, make_pred, sample_row, make_top_n_dict
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
# app.permanent_session_lifetime = 60 * 60 * 1.5 # seconds, so 1.5 hours
# TODO: uncomment the below
# model = get_model() # temporary
d_top_5 = make_top_n_dict()


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


@app.route('/get-top-types')
def get_top_types():
    return jsonify(d_top_5) 


# set the secret key.  keep this really secret:
app.secret_key = 'alex'

if __name__ == '__main__':
    app.run(debug=True)