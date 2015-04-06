#!/usr/bin/python
# Bananatag Public API Python Library
#
# @author Bananatag Systems <eric@bananatag.com>
# @version 0.1.0

import urlparse
import urllib
import urllib2
import httplib
import json
import datetime
import hmac
import base64
from hashlib import sha1

import mimetypes
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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

        self.post_endpoints = ['tags/send']

        self.last_endpoint = None
        self.last_params = {}
        self.next_url = None

    def request(self, endpoint, params=None):
        """
        Request method to be used by API library end user to make requests to Bananatag Data API

        :param endpoint: Request endpoint
        :param params: Dictionary of request parameters
        :return: JSON encoded response object
        """
        params = params or {}

        # If the current request is identical to the previous request use the next page URL
        if endpoint == self.last_endpoint and params == self.last_params:
            result = self.make_request(self.next_url, urlparse.urlparse(self.next_url).query)
        else:
            self.validate_data(params)
            self.save_current_request(endpoint, params)
            url = urllib.quote(self.base_url + endpoint, ':/-')
            query_string = self.build_data_string(params)
            post = endpoint in self.post_endpoints
            if not post:
                url += '?' + query_string

            result = self.make_request(url, query_string, post)

        try:
            self.save_response(result.get('paging'))
        except AttributeError:
            # No response object to save
            pass

        return result

    def make_request(self, url, params, post=False):
        """
        Makes request and returns JSON data

        :param url: URL endpoint of request
        :param params: URL encoded string of request parameters
        :param post: Whether the request method should be POST (default: False)
        :return: JSON object with request response data
        """
        request_headers = {'Authorization': base64.b64encode(self.auth_id + ':' + self.generate_signature(params))}
        if post:
            request = urllib2.Request(url, params, headers=request_headers)
        else:
            request = urllib2.Request(url, headers=request_headers)

        try:
            response = urllib2.urlopen(request)
            return json.loads(response.read())
        except (urllib2.HTTPError, urllib2.URLError, httplib.HTTPException) as e:
            raise Exception('Error: {0}'.format(e))
        except ValueError:
            # No more results
            return {}

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

    def validate_data(self, data):
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

        :param params: URL encoded string of query parameters to build signature with
        :return: String signature
        """
        signature = hmac.new(self.access_key, params, sha1)
        return signature.hexdigest()

    @staticmethod
    def build_data_string(params):
        """
        URL encode request parameters

        :param params: Dictionary of request parameters to encode
        :return: URL encoded parameter string
        """
        return urllib.urlencode(params)

    def save_current_request(self, endpoint, params):
        """
        Save a representation of the request for pagination purposes

        :param endpoint: Last requested URL endpoint
        :param params: Dictionary of parameters used in last request
        """
        self.last_endpoint = endpoint
        self.last_params = params

    def save_response(self, data):
        """
        Save pagination details from response object

        :param data: Paging data returned from current request
        """
        self.next_url = data.get('nextURL')

    @staticmethod
    def build_message(params):
        """
        Builds an HTML email message with optional attachments
        :param params: Dictionary of parameters to build email with
        :return: Base64 encoded raw message body
        """
        if params.get('from') is None:
            raise Exception('You must specify the From header.')
        if params.get('to') is None:
            raise Exception('You must specify the To header.')
        elif not isinstance(params.get('to'), list):
            raise Exception('To header must be specified as a list.')
        if params.get('html') is None:
            raise Exception('You must include the html parameter.')

        attachments = params.get('attachments')
        if attachments is not None:
            if not isinstance(attachments, list):
                raise Exception('Attachments must be a list.')

        msg = MIMEMultipart()
        msg['Subject'] = params.get('subject')
        msg['From'] = params.get('from')
        msg['To'] = ','.join(params.get('to'))
        msg.attach(MIMEText(params.get('html'), 'html', 'utf-8'))

        headers = params.get('headers')
        if headers:
            for header, value in headers:
                msg.add_header(header, value)

        if attachments is not None:
            for item in attachments:
                fname = item.get('filename')
                if fname is None:
                    raise Exception('Attachment filename must be specified.')

                if item.get('content-type'):
                    content_type = item.get('content-type')
                else:
                    content_type, encoding = mimetypes.guess_type(fname)
                    if content_type is None or encoding is not None:
                        content_type = 'application/octet-stream'
                main, sub = content_type.split('/', 1)
                attachment = MIMEBase(main, sub)

                attachment.set_payload(item.get('contents'))

                if item.get('content-disposition') == 'inline' and 'content-id' in item:
                    attachment.add_header('Content-ID', item.get('content-id'))

                attachment.add_header('Content-Disposition', item.get('content-disposition'), filename=fname)

                if item.get('content-transfer-encoding') is not None:
                    attachment.add_header('Content-Transfer-Encoding', item.get('content-transfer-encoding'))

                msg.attach(attachment)

        return base64.b64encode(msg.as_string())
