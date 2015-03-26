#!/usr/bin/python
# Bananatag Public API Python Library
#
# @author Bananatag Systems <eric@bananatag.com>
# @version 1.0.0

import urllib
import urllib2
import httplib
import json
import datetime
import hmac
import base64
import time
from pprint import pprint
from hashlib import sha1

class BTagAPI:
    # Constructor
    def __init__(self, auth_id, access_key, debug=False):
        if (auth_id is None) or (access_key is None):
            raise Exception('Error 401: You must provide both an authentication ID and access key.')

        self.auth_id = auth_id
        self.access_key = access_key
        self.base_url = 'https://api.bananatag.com/'
        self.debug = debug


    # Send request and return the results
    def request(self, endpoint, params=None):
        params = params or {}
        self.check_data(params)
        url = self.base_url + endpoint
        method = self.get_method(endpoint)
        result = self.make_request(url, method, params)

        return result


    # Make request and raise any exceptions
    def make_request(self, url, method, params):
        safe_url = urllib.quote(url, ':/~')
        query_string = urllib.urlencode(params)
        request_headers = {'Authorization': base64.b64encode(self.auth_id + ':' + self.generate_signature(params))}

        if method == 'GET':
            request = urllib2.Request(safe_url + '?' + query_string, headers=request_headers)
        else:
            request = urllib2.Request(safe_url, query_string, headers=request_headers)

        start = time.clock()
        if self.debug:
            self.log('Call to {0} {1} \n'.format(method, url))
            pprint(params)

        try:
            response = urllib2.urlopen(request)
            if self.debug:
                self.log('\nCompleted In: {0} seconds\n'.format(str(time.clock() - start)))
                self.log('Response Code: {0}\n'.format(str(response.getcode())))
                self.log('Response Info: ')
                self.log(response.info())

            return json.loads(response.read())
        except (urllib2.HTTPError, urllib2.URLError, httplib.HTTPException) as e:
            raise Exception('Error: {0}'.format(e))


    # Check that date format is in yyyy-mm-dd
    def validate_date(self, date):
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise Exception('Error 400: Error with provided parameters: Date string must be in format yyyy-mm-dd.')


    # Validate params data and raise any exceptions before request is made
    def check_data(self, data):
        if ('start' in data) and (data['start'] is not None):
            self.validate_date(data['start'])

        if ('end' in data) and (data['end'] is not None):
            self.validate_date(data['end'])

        if ('start' in data) and ('end' in data) and (data['start'] is not None) and (data['end'] is not None):
            if data['start'] > data['end']:
                raise Exception('Error 400: Error with provided parameters: Start date is greater than end date.')


    def log(self, msg):
        if self.debug:
            print msg


    # Generate hmac sha1 hex signature
    def generate_signature(self, params):
        dataString = self.build_data_string(params)
        signature = hmac.new(self.access_key, dataString, sha1)
        return signature.hexdigest()


    # Create data string by ordering params list by key
    def build_data_string(self, params):
        return urllib.urlencode(params)


    # Get correct request method based on what endpoint is given
    def get_method(self, endpoint):
        if endpoint == '':
            return 'PUT'
        else:
            return 'GET'