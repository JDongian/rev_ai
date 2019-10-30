# -*- coding: utf-8 -*-
"""Speech recognition tools for using Rev.ai"""

import requests
from requests.exceptions import HTTPError
from . import __version__
from . import CustomVocabulary


class BaseClient:
    """Base for clients that communicate with RevAI Apis"""

    # Default version of Rev.ai
    version = 'v1'

    # Default address of the API
    base_url = 'https://api.rev.ai/speechtotext/{}/'.format(version)

    def __init__(self, access_token):
        """Constructor

        :param access_token: access token which authorizes all requests and
                             links them to your account. Generated on the
                             settings page of your account dashboard
                             on Rev.ai
        """
        if not access_token:
            raise ValueError('access_token must be provided')

        self.default_headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'User-Agent': 'RevAi-PythonSDK/{}'.format(__version__)
        }

    def _make_http_request(self, method, url, **kwargs):
        """Wrapper method for initiating HTTP requests and handling potential
            errors.

        :param method: string of HTTP method request
        :param url: string containing the URL to make the request to
        :param (optional) **kwargs: potential extra arguments including header
            and stream
        :raises: HTTPError
        """
        headers = self.default_headers.copy()
        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
            del kwargs['headers']
        with requests.Session() as session:
            response = session.request(method, url, headers=headers, **kwargs)

        try:
            response.raise_for_status()
            return response
        except HTTPError as err:
            if (response.content):
                err.args = (err.args[0] +
                            "; Server Response : {}".
                            format(response.content.decode('utf-8')),)
            raise

    def _process_vocabularies(self, unprocessed_vocabularies):
        return list(map(lambda custom_vocabulary: custom_vocabulary.to_dict()
                        if isinstance(custom_vocabulary, CustomVocabulary)
                        else custom_vocabulary, unprocessed_vocabularies))
