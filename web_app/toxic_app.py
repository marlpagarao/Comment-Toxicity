
from unicodedata import category
from unittest import result
from warnings import catch_warnings
from flask import Flask, render_template, url_for, request, jsonify
from requests import get
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

import pickle
import numpy as np
import pandas as pd
import urllib.parse as urlparse
from comment_scraper import scrape_comments_with_replies,get_video_thumbnail,get_video_title

app = Flask(__name__)

# Load the TF-IDF vocabulary specific to the category
tox = pickle.load(open("toxic_vect.pkl", "rb"))
sev = pickle.load(open("severe_toxic_vect.pkl", "rb"))
obs = pickle.load(open("obscene_vect.pkl", "rb"))
ins = pickle.load(open("insult_vect.pkl", "rb"))
thr = pickle.load(open("threat_vect.pkl", "rb"))
ide = pickle.load(open("identity_hate_vect.pkl", "rb"))

tox_model = pickle.load(open("toxic_model.pkl", "rb"))
sev_model = pickle.load(open("severe_toxic_model.pkl", "rb"))
obs_model = pickle.load(open("obscene_model.pkl", "rb"))
ins_model = pickle.load(open("insult_model.pkl", "rb"))
thr_model = pickle.load(open("threat_model.pkl", "rb"))
ide_model = pickle.load(open("identity_hate_model.pkl", "rb"))

# Render the HTML file for the home page


@app.route("/")
def home():
    return render_template('index_toxic.html')


@app.route("/text")
def text():
    return render_template('text_only.html')


@app.route("/predict", methods=['POST'])
def predict():

    # Take a string input from user

    user_input = request.form['text']
    # data = [user_input]

    url_data = urlparse.urlparse(user_input)
    query = urlparse.parse_qs(url_data.query)
    user_input = query["v"][0]


    thumbnail=get_video_thumbnail(user_input)
    title=get_video_title(user_input)
    df = scrape_comments_with_replies(user_input)

    results_tally = {"Toxic": 0, 'Severe Toxic': 0, 'Obscene': 0,
                     'Insult': 0, 'Threat': 0, 'Identity Hate': 0, 'Non Toxic': 0}

    for index, row in df['Comment'].items():
        row = [row]
        vect = tox.transform(row)
        pred_tox = tox_model.predict_proba(vect)[:, 1]

        vect = sev.transform(row)
        pred_sev = sev_model.predict_proba(vect)[:, 1]

        vect = obs.transform(row)
        pred_obs = obs_model.predict_proba(vect)[:, 1]

        vect = thr.transform(row)
        pred_thr = thr_model.predict_proba(vect)[:, 1]

        vect = ins.transform(row)
        pred_ins = ins_model.predict_proba(vect)[:, 1]

        vect = ide.transform(row)
        pred_ide = ide_model.predict_proba(vect)[:, 1]

        results = {"Toxic": [], 'Severe Toxic': [], 'Obscene': [],
                   'Insult': [], 'Threat': [], 'Identity Hate': []}

        out_tox = round(pred_tox[0], 2)
        results['Toxic'] = out_tox

        out_sev = round(pred_sev[0], 2)
        results['Severe Toxic'] = out_sev

        out_obs = round(pred_obs[0], 2)
        results['Obscene'] = out_obs

        out_ins = round(pred_ins[0], 2)
        results['Insult'] = out_ins

        out_thr = round(pred_thr[0], 2)
        results['Threat'] = out_thr

        out_ide = round(pred_ide[0], 2)
        results['Identity Hate'] = out_ide

        result_values = list(results.values())

        if all(i <= 0.30 for i in result_values):
            category = 'Non Toxic'
            results_tally['Non Toxic'] += 1
        else:
            category = max(zip(results.values(), results.keys()))[1]
            results_tally[category] += 1

    return render_template('index_toxic.html',
                           data='You Entered:' + user_input,
                           pred_tox='Prob (Toxic): {}'.format(
                               results_tally['Toxic']),
                           pred_sev='Prob (Severe Toxic): {}'.format(
                               results_tally['Severe Toxic']),
                           pred_obs='Prob (Obscene): {}'.format(
                               results_tally['Obscene']),
                           pred_ins='Prob (Insult): {}'.format(
                               results_tally['Insult']),
                           pred_thr='Prob (Threat): {}'.format(
                               results_tally['Threat']),
                           pred_ide='Prob (Identity Hate): {}'.format(
                               results_tally['Identity Hate']),
                           category='Prob (Non Toxic): {}'.format(
                               results_tally['Non Toxic']),
                           pred_tox_num=results_tally['Toxic'],
                           pred_sev_num=results_tally['Severe Toxic'],
                           pred_obs_num=results_tally['Obscene'],
                           pred_ins_num=results_tally['Insult'],
                           pred_thr_num=results_tally['Threat'],
                           pred_ide_num=results_tally['Identity Hate'],
                           pred_non_num=results_tally['Non Toxic'],
                           thumbnail=thumbnail,
                           title=title,
                           
                           )


@app.route("/comment", methods=['POST', 'GET'])
def predict_text():

    # Take a string input from user
    user_input = request.form['text']
    data = [user_input]

    vect = tox.transform(data)
    pred_tox = tox_model.predict_proba(vect)[:, 1]

    vect = sev.transform(data)
    pred_sev = sev_model.predict_proba(vect)[:, 1]

    vect = obs.transform(data)
    pred_obs = obs_model.predict_proba(vect)[:, 1]

    vect = thr.transform(data)
    pred_thr = thr_model.predict_proba(vect)[:, 1]

    vect = ins.transform(data)
    pred_ins = ins_model.predict_proba(vect)[:, 1]

    vect = ide.transform(data)
    pred_ide = ide_model.predict_proba(vect)[:, 1]

    results = {"Toxic": [], 'Severe Toxic': [], 'Obscene': [],
               'Insult': [], 'Threat': [], 'Identity Hate': []}

    out_tox = round(pred_tox[0], 2)
    results['Toxic'] = out_tox

    out_sev = round(pred_sev[0], 2)
    results['Severe Toxic'] = out_sev

    out_obs = round(pred_obs[0], 2)
    results['Obscene'] = out_obs

    out_ins = round(pred_ins[0], 2)
    results['Insult'] = out_ins

    out_thr = round(pred_thr[0], 2)
    results['Threat'] = out_thr

    out_ide = round(pred_ide[0], 2)
    results['Identity Hate'] = out_ide

    result_values = list(results.values())

    if all(i <= 0.30 for i in result_values):
        category = 'Non Toxic'
        print(category)
    else:
        category = max(zip(results.values(), results.keys()))[1]
        print(category)

    return render_template('text_only.html',
                           data='You Entered: ' + user_input,
                           pred_tox='Prob (Toxic): {}'.format(out_tox),
                           pred_sev='Prob (Severe Toxic): {}'.format(out_sev),
                           pred_obs='Prob (Obscene): {}'.format(out_obs),
                           pred_ins='Prob (Insult): {}'.format(out_ins),
                           pred_thr='Prob (Threat): {}'.format(out_thr),
                           pred_ide='Prob (Identity Hate): {}'.format(out_ide),
                           category=category)


# Server reloads itself if code changes so no need to keep restarting:
app.run(debug=True)
