from typing import Dict
import unittest

from slacktools.block_kit.blocks import (
    DividerBlock,
    HeaderBlock,
)
from slacktools.block_kit.elements.display import (
    ImageElement,
    MarkdownTextElement,
    PlainTextElement,
)
from slacktools.block_kit.elements.formatters import TextFormatter

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
        resp = PlainTextElement(text=txt).asdict()  # type: Dict
        self.assertDictEqual(exp, resp)

    def test_markdown(self):
        txt = 'hello'
        exp = {
            'type': 'mrkdwn',
            'text': txt,
            'verbatim': False
        }
        resp = MarkdownTextElement(text=txt).asdict()
        self.assertDictEqual(exp, resp)

    def test_make_header(self):
        txt = 'hello'
        exp = {
            'type': 'header',
            'text': PlainTextElement(txt).asdict(),
        }
        resp = HeaderBlock(PlainTextElement(text=txt)).asdict()
        self.assertDictEqual(exp, resp)

    def test_divider(self):
        exp = {
            'type': 'divider'
        }
        resp = DividerBlock().asdict()  # type: Dict
        self.assertDictEqual(exp, resp)

    def test_make_image_element(self):
        url = random_string(20)
        alt_txt = 'here\'s an image'
        exp = {
            'type': 'image',
            'image_url': url,
            'alt_text': alt_txt
        }
        resp = ImageElement(image_url=url, alt_text=alt_txt).asdict()
        self.assertDictEqual(exp, resp)

    def test_build_link(self):
        url = random_string(100)
        name = 'something'
        resp = TextFormatter.build_link(url=url, link_name=name)
        self.assertEqual(f'<{url}|{name}>', resp)


if __name__ == '__main__':
    unittest.main()
