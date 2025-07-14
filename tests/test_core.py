"""
Automated tests for moviebox_api.core module
"""

import unittest
from moviebox_api.requests import Session
from moviebox_api.core import Homepage
from moviebox_api.models import HomepageContentModel


class BaseRequestsSession(unittest.TestCase):
    session = Session()


class HomepageTest(BaseRequestsSession):

    def setUp(self):
        self.homepage = Homepage(self.session)

    def test_content_fetching(self):
        contents: dict = self.homepage.content
        self.assertIsInstance(contents, dict)

    def test_content_modelling(self):
        modelled_contents = self.homepage.modelled_content
        self.assertIsInstance(modelled_contents, HomepageContentModel)
