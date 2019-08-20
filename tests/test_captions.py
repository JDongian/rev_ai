# -*- coding: utf-8 -*-

import pytest
from src.rev_ai.apiclient import RevAiAPIClient
from src.rev_ai.models import CaptionType

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

JOB_ID = '1'
URL = urljoin(RevAiAPIClient.base_url, 'jobs/{}/captions'.format(JOB_ID))

@pytest.mark.usefixtures('mock_client', 'make_mock_response')
class TestCaptionEndpoint():
    def test_get_captions_default_content_type(self, mock_client, make_mock_response):
        data = 'Test'
        expected_content_type = CaptionType.SRT.value
        response = make_mock_response(url=URL, text=data)
        mock_client.session.request.return_value = response

        res = mock_client.get_captions(JOB_ID)
        assert res == data
        mock_client.session.request.assert_called_once_with(
            "GET",
            URL,
            headers={'Accept': expected_content_type}
        )

    @pytest.mark.parametrize('content_type', [CaptionType.SRT, CaptionType.VTT])
    def test_get_captions_with_content_type(self, content_type, mock_client, make_mock_response):
        data = 'Test'
        expected_content_type = content_type.value
        response = make_mock_response(url=URL, text=data)
        mock_client.session.request.return_value = response

        res = mock_client.get_captions(JOB_ID, content_type)
        assert res == data
        mock_client.session.request.assert_called_once_with(
            "GET",
            URL,
            headers={'Accept': expected_content_type}
        )
    
    def test_get_captions_with_speaker_channel(self, mock_client, make_mock_response):
        data = 'Test'
        channel_id = 1
        expected_url = URL + '?speaker_channel={}'.format(channel_id)
        expected_content_type = CaptionType.SRT.value
        response = make_mock_response(url=expected_url, text=data)
        mock_client.session.request.return_value = response

        res = mock_client.get_captions(JOB_ID, channel_id=channel_id)
        assert res == data
        mock_client.session.request.assert_called_once_with(
            "GET",
            expected_url,
            headers={'Accept': expected_content_type}
        )

    @pytest.mark.parametrize('id', [None, ''])
    def test_get_captions_with_no_job_id(self, id, mock_client):
        with pytest.raises(ValueError, match='id_ must be provided'):
            mock_client.get_captions(id)

    def test_get_captions_as_stream_default_content_type(self, mock_client, make_mock_response):
        data = 'Test'
        expected_content_type = CaptionType.SRT.value
        response = make_mock_response(url=URL, text=data)
        mock_client.session.request.return_value = response

        res = mock_client.get_captions_as_stream(JOB_ID)

        assert res.content.decode('utf-8') == data
        mock_client.session.request.assert_called_once_with(
            "GET",
            URL,
            headers={'Accept': expected_content_type},
            stream=True
        )

    @pytest.mark.parametrize('content_type', [CaptionType.SRT, CaptionType.VTT])
    def test_get_captions_as_stream_with_content_type(self, content_type, mock_client, make_mock_response):
        data = 'Test'
        expected_content_type = content_type.value
        response = make_mock_response(url=URL, text=data)
        mock_client.session.request.return_value = response

        res = mock_client.get_captions_as_stream(JOB_ID, content_type)
        assert res.content.decode('utf-8') == data
        mock_client.session.request.assert_called_once_with(
            "GET",
            URL,
            headers={'Accept': expected_content_type},
            stream=True
        )

    def test_get_captions_as_stream_with_speaker_channel(self, mock_client, make_mock_response):
        data = 'Test'
        channel_id = 8
        expected_url = URL + '?speaker_channel={}'.format(channel_id)
        expected_content_type = CaptionType.SRT.value
        response = make_mock_response(url=expected_url, text=data)
        mock_client.session.request.return_value = response

        res = mock_client.get_captions_as_stream(JOB_ID, channel_id=channel_id)
        assert res.content.decode('utf-8') == data
        mock_client.session.request.assert_called_once_with(
            "GET",
            expected_url,
            headers={'Accept': expected_content_type},
            stream=True
        )

    @pytest.mark.parametrize('id', [None, ''])
    def test_get_captions_as_stream_with_no_job_id(self, id, mock_client):
        with pytest.raises(ValueError, match='id_ must be provided'):
            mock_client.get_captions_as_stream(id)
