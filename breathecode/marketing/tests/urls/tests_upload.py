"""
Test /v1/marketing/upload
"""
import csv
import tempfile
import os
import hashlib
from unittest.mock import MagicMock, Mock, PropertyMock, call, patch
from django.urls.base import reverse_lazy
from rest_framework import status
from ..mixins import MarketingTestCase
from breathecode.marketing.views import MIME_ALLOW
import pandas as pd


class MarketingTestSuite(MarketingTestCase):
    """Test /answer"""
    def test_upload_without_auth(self):
        from breathecode.services.google_cloud import Storage, File

        self.headers(content_disposition='attachment; filename="filename.csv"')

        url = reverse_lazy('marketing:upload')
        data = {}
        response = self.client.put(url, data)
        json = response.json()
        expected = {'detail': 'Authentication credentials were not provided.', 'status_code': 401}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_wrong_academy(self):
        from breathecode.services.google_cloud import Storage, File

        self.headers(academy=1, content_disposition='attachment; filename="filename.csv"')

        url = reverse_lazy('marketing:upload')
        data = {}
        response = self.client.put(url, data)
        json = response.json()
        expected = {'detail': 'Authentication credentials were not provided.', 'status_code': 401}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_without_capability(self):
        from breathecode.services.google_cloud import Storage, File

        self.headers(academy=1, content_disposition='attachment; filename="filename.csv"')

        url = reverse_lazy('marketing:upload')
        self.generate_models(authenticate=True)
        data = {}
        response = self.client.put(url, data)
        json = response.json()
        expected = {
            'detail': "You (user: 1) don't have this capability: crud_media for academy 1",
            'status_code': 403
        }

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.multiple('breathecode.services.google_cloud.Storage',
                    __init__=MagicMock(return_value=None),
                    client=PropertyMock(),
                    create=True)
    @patch.multiple(
        'breathecode.services.google_cloud.File',
        __init__=MagicMock(return_value=None),
        bucket=PropertyMock(),
        file_name=PropertyMock(),
        upload=MagicMock(),
        url=MagicMock(return_value='https://storage.cloud.google.com/media-breathecode/hardcoded_url'),
        create=True)
    def test_upload_without_data(self):
        from breathecode.services.google_cloud import Storage, File

        self.headers(academy=1)

        model = self.generate_models(authenticate=True,
                                     profile_academy=True,
                                     capability='crud_media',
                                     role='potato')
        url = reverse_lazy('marketing:upload')
        data = {}
        response = self.client.put(url, data)
        json = response.json()

        self.assertEqual(json, {
            'detail': 'Missing file in request',
            'status_code': 400,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.all_media_dict(), [])

        self.assertEqual(Storage.__init__.call_args_list, [])
        self.assertEqual(File.__init__.call_args_list, [])
        self.assertEqual(File.upload.call_args_list, [])
        self.assertEqual(File.url.call_args_list, [])

    @patch('breathecode.marketing.tasks.create_form_entry.delay', MagicMock())
    @patch.multiple('breathecode.services.google_cloud.Storage',
                    __init__=MagicMock(return_value=None),
                    client=PropertyMock(),
                    create=True)
    @patch.multiple(
        'breathecode.services.google_cloud.File',
        __init__=MagicMock(return_value=None),
        bucket=PropertyMock(),
        file_name=PropertyMock(),
        upload=MagicMock(),
        url=MagicMock(return_value='https://storage.cloud.google.com/media-breathecode/hardcoded_url'),
        create=True)
    def test_upload_random(self):
        from breathecode.services.google_cloud import Storage, File
        from breathecode.marketing.tasks import create_form_entry

        self.headers(academy=1)

        model = self.generate_models(authenticate=True,
                                     profile_academy=True,
                                     capability='crud_media',
                                     role='potato')

        url = reverse_lazy('marketing:upload')

        file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w+')

        # list of name, degree, score
        first_names = [self.bc.fake.first_name() for _ in range(0, 3)]
        last_names = [self.bc.fake.last_name() for _ in range(0, 3)]

        # dictionary of lists
        obj = {'first_name': first_names, 'last_name': last_names}

        df = pd.DataFrame(obj)

        # saving the dataframe
        df.to_csv(file.name)

        print(dir(file))
        # with open(file.name, 'wb') as f:
        # writer = csv.writer(file)
        # writer.writerow(['first_name', 'last_name'])
        # writer.writerow([self.bc.fake.first_name(), self.bc.fake.last_name()])

        with open(file.name, 'rb') as data:
            hash = hashlib.sha256(data.read()).hexdigest()

        with open(file.name, 'rb') as data:
            response = self.client.put(url, {'name': file.name, 'file': data})
            json = response.json()

            self.assertHash(hash)

            expected = [{
                'academy': 1,
                'categories': [],
                'hash': hash,
                'hits': 0,
                'id': 1,
                'mime': 'text/csv',
                'name': 'filename.csv',
                'slug': 'filename-csv',
                'thumbnail': 'https://storage.cloud.google.com/media-breathecode/hardcoded_url-thumbnail',
                'url': 'https://storage.cloud.google.com/media-breathecode/hardcoded_url'
            }]

            self.assertEqual(json, expected)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertEqual(create_form_entry.delay.call_args_list(), [call()])

            self.assertEqual(
                self.all_media_dict(),
                [{
                    'academy_id': 1,
                    'hash': hash,
                    'hits': 0,
                    'id': 1,
                    'mime': 'image/csv',
                    'name': 'filename.csv',
                    'slug': 'filename-csv',
                    'thumbnail': 'https://storage.cloud.google.com/media-breathecode/hardcoded_url-thumbnail',
                    'url': 'https://storage.cloud.google.com/media-breathecode/hardcoded_url'
                }])

            self.assertEqual(Storage.__init__.call_args_list, [call()])
            self.assertEqual(File.__init__.call_args_list, [
                call(Storage().client.bucket('bucket'), hash),
            ])

            args, kwargs = File.upload.call_args_list[0]

            self.assertEqual(len(File.upload.call_args_list), 1)
            self.assertEqual(len(args), 1)
            self.assertEqual(len(args), 1)

            self.assertEqual(args[0].name, os.path.basename(file.name))
            self.assertEqual(args[0].size, 1024)
            self.assertEqual(kwargs, {'content_type': 'text/csv'})

            self.assertEqual(File.url.call_args_list, [call()])
            assert False
