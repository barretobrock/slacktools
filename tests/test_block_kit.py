import unittest
from slacktools.tools import BlockKitBuilder as bkb
from .common import (
    get_test_logger,
    random_string
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
        resp = bkb.plaintext_section(text=txt)
        self.assertDictEqual(exp, resp)

    def test_markdown(self):
        txt = 'hello'
        exp = {
            'type': 'mrkdwn',
            'text': txt,
        }
        resp = bkb.markdown_section(text=txt)
        self.assertDictEqual(exp, resp)

    def test_make_header(self):
        txt = 'hello'
        exp = {
            'type': 'header',
            'text': bkb.plaintext_section(txt),
        }
        resp = bkb.make_header(txt=txt)
        self.assertDictEqual(exp, resp)

    def test_divider(self):
        exp = {
            'type': 'divider'
        }
        resp = bkb.make_block_divider()
        self.assertDictEqual(exp, resp)

    def test_make_image_element(self):
        url = random_string(20)
        alt_txt = 'here\'s an image'
        exp = {
            'type': 'image',
            'image_url': url,
            'alt_text': alt_txt
        }
        resp = bkb.make_image_element(url=url, alt_txt=alt_txt)
        self.assertDictEqual(exp, resp)

    def test_build_link(self):
        url = random_string(100)
        name = 'something'
        resp = bkb.build_link(url=url, text=name)
        self.assertEqual(f'<{url}|{name}>', resp)


if __name__ == '__main__':
    unittest.main()
