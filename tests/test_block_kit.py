from typing import Dict
import unittest

from slacktools.block_kit import BlockKitBuilder as BKitB

from .common import (
    get_test_logger,
    random_string,
)


class TestBlockKit(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._log = get_test_logger()

    def test_plaintext(self):
        txt = 'hello'
        exp = {
            'type': 'plain_text',
            'text': txt,
            'emoji': True
        }
        resp = BKitB.plaintext_section(text=txt)  # type: Dict
        self.assertDictEqual(exp, resp)

    def test_markdown(self):
        txt = 'hello'
        exp = {
            'type': 'mrkdwn',
            'text': txt,
            'verbatim': False
        }
        resp = BKitB.markdown_section(text=txt)  # type: Dict
        self.assertDictEqual(exp, resp)

    def test_make_header(self):
        txt = 'hello'
        exp = {
            'type': 'header',
            'text': BKitB.plaintext_section(txt),
        }
        resp = BKitB.make_header_block(text=txt)  # type: Dict
        self.assertDictEqual(exp, resp)

    def test_divider(self):
        exp = {
            'type': 'divider'
        }
        resp = BKitB.make_divider_block()  # type: Dict
        self.assertDictEqual(exp, resp)

    def test_make_image_element(self):
        url = random_string(20)
        alt_txt = 'here\'s an image'
        exp = {
            'type': 'image',
            'image_url': url,
            'alt_text': alt_txt
        }
        resp = BKitB.make_image_element(url=url, alt_txt=alt_txt)  # type: Dict
        self.assertDictEqual(exp, resp)

    def test_build_link(self):
        url = random_string(100)
        name = 'something'
        resp = BKitB.build_link(url=url, text=name)
        self.assertEqual(f'<{url}|{name}>', resp)


if __name__ == '__main__':
    unittest.main()
