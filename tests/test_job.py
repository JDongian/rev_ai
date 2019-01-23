try:
    from unittest.mock import patch, MagicMock
    from urllib.parse import urljoin
except ImportError:
    from mock import patch, MagicMock
    from urlparse import urljoin
import json
import pytest
from src.rev_ai.models import Job, JobSubmitOptions
from src.rev_ai.apiclient import RevAiAPIClient

JOB_ID = '1'
MEDIA_URL = "https://example.com/test.mp3"


@pytest.mark.usefixtures("mockclient")
class TestJobEndpoints():
    def test_get_job_details_success(self, mockclient):
        data = {
            'id': JOB_ID,
            'status': 'transcribed',
            'created_on': '2018-05-05T23:23:22.29Z'
        }
        mockclient.session.get.return_value.json.return_value = data

        res = mockclient.get_job_details(JOB_ID)

        assert isinstance(res, Job)
        assert res.id == JOB_ID
        assert res.status == data.get('status')
        assert res.created_on == data.get('created_on')
        mockclient.session.get.assert_called_once_with(
            urljoin(RevAiAPIClient.base_url, "jobs/{id}".format(id=JOB_ID))
        )

    def test_get_job_details_not_authorized_error(self, mockclient):
        data = {
            "title": "Authorization has been denied for this request",
            "status": 401
        }
        mockclient.session.get.return_value.json.return_value = data

        with pytest.raises(KeyError):
            mockclient.get_job_details(JOB_ID)

    def test_get_job_details_job_not_found_error(self, mockclient):
        data = {
            "type": "https://www.rev.ai/api/v1/errors/job-not-found",
            "title": "could not find job",
            "status": 404
        }
        mockclient.session.get.return_value.json.return_value = data

        with pytest.raises(KeyError):
            mockclient.get_job_details(JOB_ID)

    def test_submit_job_url_success(self, mockclient):
        options = JobSubmitOptions(metadata="test")
        data = {
            "id": JOB_ID,
            "status": "in_progress",
            "created_on": "2018-05-05T23:23:22.29Z"
        }
        mockclient.session.post.return_value.json.return_value = data

        res = mockclient.submit_job_url(MEDIA_URL, options)

        assert isinstance(res, Job)
        assert res.id == JOB_ID
        assert res.status == data.get('status')
        assert res.created_on == data.get('created_on')
        mockclient.session.post.assert_called_once_with(
            urljoin(RevAiAPIClient.base_url, "jobs"),
            json={
                'media_url': MEDIA_URL,
                'metadata': options.metadata
            }
        )

    @patch('src.rev_ai.apiclient.open')
    def test_submit_job_local_file_success(self, mock_open, mockclient):
        filename = "test.mp3"
        options = JobSubmitOptions(metadata="test")
        data = {
            "id": JOB_ID,
            "status": "in_progress",
            "created_on": "2018-05-05T23:23:22.29Z"
        }
        mockclient.session.post.return_value.json.return_value = data
        mock_open.return_value.__enter__ = mock_open
        mock_open.return_value.__iter__ = MagicMock(return_value='Hello')

        res = mockclient.submit_job_local_file(filename, options)

        assert isinstance(res, Job)
        assert res.id == JOB_ID
        assert res.status == data.get('status')
        assert res.created_on == data.get('created_on')
        mockclient.session.post.assert_called_once_with(
            urljoin(RevAiAPIClient.base_url, "jobs"),
            files={
                'media': (filename, mock_open.return_value),
                'options': (None, json.dumps({'metadata': options.metadata}))
            }
        )

    def test_submit_job_bad_request_error(self, mockclient):
        options = JobSubmitOptions(metadata="test")
        data = {
            "parameter": {
                "media_url": [
                    "The media_url field is required"
                ],
                "type": "https://www.rev.ai/api/v1/errors/invalid-parameters",
                "title": "Your request parameters didn't validate",
                "status": 400
            }
        }
        mockclient.session.post.return_value.json.return_value = data

        with pytest.raises(KeyError):
            mockclient.submit_job_url(MEDIA_URL, options)

    def test_submit_job_not_authorized_error(self, mockclient):
        options = JobSubmitOptions(metadata="test")
        data = {
            "title": "Authorization has been denied for this request",
            "status": 401
        }
        mockclient.session.post.return_value.json.return_value = data

        with pytest.raises(KeyError):
            mockclient.submit_job_url(MEDIA_URL, options)

    def test_submit_job_insufficient_credits_error(self, mockclient):
        options = JobSubmitOptions(metadata="test")
        data = {
            "title": "You do not have enough credits",
            "type": "https://www.rev.ai/api/v1/errors/out-of-credit",
            "detail": "You have only 60 seconds remaining",
            "current_balance": 60,
            "status": 403
        }
        mockclient.session.post.return_value.json.return_value = data

        with pytest.raises(KeyError):
            mockclient.submit_job_url(MEDIA_URL, options)