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
    def __init__(self, authID, accessKey, debug=None):
        if (authID is None) or (accessKey is None):
            raise Exception('Error 401: You must provide both an authID and access key.')

        self.authID = authID
        self.accessKey = accessKey
        self.baseURL = 'https://api.bananatag.com/'
        self.debug = False

        if debug is not None:
            self.debug = True


    # Send request and return the results
    def send(self, endpoint, params=None):
        params = params or {}
        self.checkData(params)
        url = self.baseURL + endpoint
        method = self.getMethod(endpoint)
        result = self.makeRequest(url, method, params)

        return result


    # Make request and raise any exceptions
    def makeRequest(self, url, method, params):
        safe_url = urllib.quote(url, ':/~')
        queryString = urllib.urlencode(params)
        requestHeaders = {'Authorization': base64.b64encode(self.authID + ':' + self.generateSignature(params))}

        if method == 'GET':
            request = urllib2.Request(safe_url + '?' + queryString, headers=requestHeaders)
        else:
            request = urllib2.Request(safe_url, queryString, headers=requestHeaders)

        startTime = time.clock()
        if self.debug:
            self.log('Call to {0} {1} \n'.format(method, url))
            pprint(params)

        try:
            response = urllib2.urlopen(request)
            if self.debug:
                self.log('\nCompleted In: {0} seconds\n'.format(str(time.clock() - startTime)))
                self.log('Response Code: {0}\n'.format(str(response.getcode())))
                self.log('Response Info: ')
                self.log(response.info())

            return json.loads(response.read())
        except (urllib2.HTTPError, urllib2.URLError, httplib.HTTPException) as e:
            raise Exception('Error: {0}'.format(e))


    # Check that date format is in yyyy-mm-dd
    def validateDate(self, date):
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise Exception('Error 400: Error with provided parameters: Date string must be in format yyyy-mm-dd.')


    # Validate params data and raise any exceptions before request is made
    def checkData(self, data):
        if ('start' in data) and (data['start'] is not None):
            self.validateDate(data['start'])

        if ('end' in data) and (data['end'] is not None):
            self.validateDate(data['end'])

        if ('start' in data) and ('end' in data) and (data['start'] is not None) and (data['end'] is not None):
            if data['start'] > data['end']:
                raise Exception('Error 400: Error with provided parameters: Start date is greater than end date.')

        if ('aggregateData' in data) and (data['aggregateData'] != 'true') and (data['aggregateData'] != 'false'):
            raise Exception('Error 400: Error with provided parameters: aggregateData must either be \'true\' or \'false\'.')


    def log(self, msg):
        if self.debug:
            print msg


    # Generate hmac sha1 hex signature
    def generateSignature(self, params):
        dataString = self.buildDataString(params)
        signature = hmac.new(self.accessKey, dataString, sha1)
        return signature.hexdigest()


    # Create data string by ordering params list by key
    def buildDataString(self, params):
        return urllib.urlencode(params)


    # Get correct request method based on what endpoint is given
    def getMethod(self, endpoint):
        if endpoint == '':
            return 'PUT'
        else:
            return 'GET'