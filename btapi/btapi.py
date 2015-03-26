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
from hashlib import sha1


class BTagAPI:
    def __init__(self, auth_id, access_key):
        """
        Bananatag API access object

        :param auth_id: User's Bananatag-provided authentication ID
        :param access_key: User's Bananatag-provided API access key
        """
        if (auth_id is None) or (access_key is None):
            raise Exception('Error 401: You must provide both an authentication ID and access key.')

        self.auth_id = auth_id
        self.access_key = access_key
        self.base_url = 'https://api.bananatag.com/'

    def request(self, endpoint, params=None):
        """
        Request method to be used by API library end user to make requests to Bananatag Data API

        :param endpoint: Request endpoint
        :param params: Dictionary of request parameters
        :return: JSON encoded response object
        """
        params = params or {}
        self.check_data(params)
        url = self.base_url + endpoint
        method = self.get_method(endpoint)
        result = self.make_request(url, method, params)

        return result

    def make_request(self, url, method, params):
        """
        Makes request and returns JSON data

        :param url: URL endpoint of request
        :param method: HTTP requests method (GET, PUT)
        :param params: Dictionary of request parameters
        :return: JSON object with request response data
        """
        safe_url = urllib.quote(url, ':/~')
        query_string = urllib.urlencode(params)
        request_headers = {'Authorization': base64.b64encode(self.auth_id + ':' + self.generate_signature(params))}

        if method == 'GET':
            request = urllib2.Request(safe_url + '?' + query_string, headers=request_headers)
        else:
            request = urllib2.Request(safe_url, query_string, headers=request_headers)

        try:
            response = urllib2.urlopen(request)
            return json.loads(response.read())
        except (urllib2.HTTPError, urllib2.URLError, httplib.HTTPException) as e:
            raise Exception('Error: {0}'.format(e))

    @staticmethod
    def validate_date(date):
        """
        Validates that the date format is yyyy-mm-dd

        :param date: Date string
        :raise Exception:
        """
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise Exception('Error 400: Error with provided parameters: Date string must be in format yyyy-mm-dd.')

    def check_data(self, data):
        """
        Validate that the query parameters are within acceptable ranges

        :param data: Dictionary of requests parameters
        :raise Exception:
        """
        if ('start' in data) and (data['start'] is not None):
            self.validate_date(data['start'])

        if ('end' in data) and (data['end'] is not None):
            self.validate_date(data['end'])

        if ('start' in data) and ('end' in data) and (data['start'] is not None) and (data['end'] is not None):
            if data['start'] > data['end']:
                raise Exception('Error 400: Error with provided parameters: Start date is greater than end date.')

    def generate_signature(self, params):
        """
        Generate HMAC SHA1 signature

        :param params: Dictionary of request parameters to build signature
        :return: String signature
        """
        data_string = self.build_data_string(params)
        signature = hmac.new(self.access_key, data_string, sha1)
        return signature.hexdigest()

    @staticmethod
    def build_data_string(params):
        """
        URL encode request parameters

        :param params: Dictionary of request parameters to encode
        :return: URL encoded parameter string
        """
        return urllib.urlencode(params)

    @staticmethod
    def get_method(endpoint):
        """
        Get HTTP request method based on request endpoint

        :param endpoint: HTTP request endpoint
        :return: Request method string
        """
        if endpoint == '':
            return 'PUT'
        else:
            return 'GET'