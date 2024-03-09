from flask import Flask, render_template, send_from_directory
from flask_classful import FlaskView, route, request
from utils import scores, shares
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import json
import os


app = Flask(__name__)


class X2030(FlaskView):
  def __init__(self):
    self.total_money = 1000
    self.s_list = []
    self.savepath = 'static/'
    self.prefix = 'scores/'
    self.scores_key = 'scores_matrix.json'
    self.bucket = '2030.hex7.com'
    self.api = 'http://' + self.bucket + '/' + self.prefix
    self.date = ''
    self.slow_dict = {}
    self.fast_dict = {}
    self.slow_results = {}
    self.slow_ordered = []
    self.fast_results = {}
    self.fast_ordered = []
    self.matrix = {}
    self.share_one = 0
    self.category = 0
    self.source_file = '2030.txt'
    self.debug = True

  @route('/', methods = ['GET'])
  def index(self):
    self.matrix = {}
    self.category = request.args.get('cat', '0')
    if int(self.category) < 0 or int(self.category) > 8:
      self.category = '0'
    self.debug = request.args.get('debug', False)
    self.total_money = int(request.args.get('cash', str(self.total_money)))
    self.date = datetime.now(ZoneInfo('US/Eastern')).isoformat().split('T')

    self.slow_dict = scores.get_url(self.api + 'slow-' + self.date[0] + '.json',
                                    debug=self.debug)
    self.fast_dict = scores.get_url(self.api + 'fast-' + self.date[0] + '.json',
                                    debug=self.debug)

    self.slow_results, \
    self.slow_ordered = scores.get_results(stocks=self.slow_dict,
                                           category=self.category,
                                           total_money=self.total_money,
                                           source_file=self.source_file,
                                           debug=self.debug)
    self.fast_results, \
    self.fast_ordered = scores.get_results(stocks=self.fast_dict,
                                           category=self.category,
                                           total_money=self.total_money,
                                           source_file=self.source_file,
                                           debug=self.debug)

    self.share_one = shares.get_min_shares(stocks=self.slow_dict,
                                           category=self.category,
                                           total_money=self.total_money,
                                           debug=self.debug)

    self.s_list = scores.get_scores_list(bucket=self.bucket,
                                         prefix=self.prefix,
                                         debug=self.debug)

    self.matrix = scores.get_matrix(s_list=self.s_list,
                                    results=self.slow_results,
                                    source_file='2030.txt',
                                    bucket=self.bucket,
                                    category='0',
                                    debug=self.debug)

    scores.make_charts(matrix=self.matrix,
                       debug=self.debug,
                       savepath=self.savepath)

    scores.save_scores(matrix=self.matrix,
                       results=self.slow_results,
                       scores_key=self.scores_key,
                       savepath=self.savepath,
                       debug=self.debug)

    return render_template('index.html',
                           req=self.api,
                           debug=self.debug,
                           s_list=self.s_list,
                           share_one=self.share_one,
                           datemade=' '.join(self.date),
                           slow_results=self.slow_results,
                           fast_results=self.fast_results,
                           slow_ordered=self.slow_ordered,
                           fast_ordered=self.fast_ordered,
                           matrix=self.matrix)


  @route('/test')
  def test(self):
    return '200 success'


  @route('/robots.txt')
  def robots(self):
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'robots.txt', mimetype='text/plain')


  @route('/favicon.ico')
  def favicon(self):
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')


X2030.register(app, route_base = '/')


if __name__ == "__main__":
  app.run(debug=True, passthrough_errors=True)
