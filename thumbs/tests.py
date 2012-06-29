from django.test import TestCase

from thumbs.fields import validate_size, split_original, determine_thumb
from thumbs.fields import SizeError, OriginalError

import logging
logger = logging.getLogger(__name__)

try:
    from PIL import Image, ImageOps
except ImportError:
    import Image
    import ImageOps


class SplitOriginalTest(TestCase):
    '''Tests split_original.'''

    def test_type(self):
        self.assertRaises(OriginalError, split_original, None)
        self.assertRaises(OriginalError, split_original, {})
        self.assertRaises(OriginalError, split_original, False)

    def test_empty_string(self):
        self.assertRaises(OriginalError, split_original, '')

    def test_no_extension(self):
        split = split_original('photo')
        self.assertEqual(split['base'], 'photo')
        self.assertEqual(split['ext'], '')

    def test_multiple_dots(self):
        split = split_original('photo.photo.photo.jpg')
        self.assertEqual(split['base'], 'photo.photo.photo')
        self.assertEqual(split['ext'], 'jpg')

    def test_string(self):
        split = split_original('photo.jpg')
        self.assertEqual(split['base'], 'photo')
        self.assertEqual(split['ext'], 'jpg')

    def test_unicode(self):
        split = split_original(u'photo.jpg')
        self.assertEqual(split['base'], 'photo')
        self.assertEqual(split['ext'], 'jpg')


class DetermineThumbTest(TestCase):
    '''Tests determine_name.'''

    def setUp(self):
        self.size = {'code': 'small', 'wxh': '100x100'}

    def test_delimiter(self):
        thumb = determine_thumb(self.size,
            'original.jpg', jpg=False, delimiter='-')
        self.assertEqual('original-small.jpg', thumb)
        thumb = determine_thumb(self.size,
            'original.jpg', jpg=False, delimiter='_')
        self.assertEqual('original_small.jpg', thumb)

    def test_jpg_true(self):
        thumb = determine_thumb(self.size,
            'original.jpg', jpg=True, delimiter='-')
        self.assertEqual('original-small.jpg', thumb)
        thumb = determine_thumb(self.size,
            'original.png', jpg=True, delimiter='-')
        self.assertEqual('original-small.jpg', thumb)
        thumb = determine_thumb(self.size,
            'original.gif', jpg=True, delimiter='-')
        self.assertEqual('original-small.jpg', thumb)
        thumb = determine_thumb(self.size,
            'original.jpeg', jpg=True, delimiter='-')
        self.assertEqual('original-small.jpg', thumb)

    def test_jpg_false(self):
        thumb = determine_thumb(self.size,
            'original.jpg', jpg=False, delimiter='-')
        self.assertEqual('original-small.jpg', thumb)
        thumb = determine_thumb(self.size,
            'original.png', jpg=False, delimiter='-')
        self.assertEqual('original-small.png', thumb)
        thumb = determine_thumb(self.size,
            'original.gif', jpg=False, delimiter='-')
        self.assertEqual('original-small.gif', thumb)
        thumb = determine_thumb(self.size,
            'original.jpeg', jpg=False, delimiter='-')
        self.assertEqual('original-small.jpeg', thumb)

    def test_no_extension(self):
        # with no ext, jpg true false doesn't matter
        thumb = determine_thumb(self.size,
            'original', jpg=True, delimiter='-')
        self.assertEqual('original-small.jpg', thumb)
        thumb = determine_thumb(self.size,
            'original', jpg=False, delimiter='-')
        self.assertEqual('original-small.jpg', thumb)


class ValidateSizeTest(TestCase):
    '''Tests validate size.'''

    def test_type(self):
        self.assertRaises(SizeError, validate_size, None)
        self.assertRaises(SizeError, validate_size, '')
        self.assertRaises(SizeError, validate_size, u'')
        self.assertRaises(SizeError, validate_size, False)

    def test_code_wxh_required(self):
        validate_size({'code': 'small', 'wxh': '100x100'})

        self.assertRaises(SizeError, validate_size, {'code': 'small'})
        self.assertRaises(SizeError, validate_size, {'wxh': '100x100'})
        self.assertRaises(SizeError, validate_size, {})

    def test_code_re(self):
        validate_size({'code': 'small', 'wxh': '100x100'})
        validate_size({'code': 's', 'wxh': '100x100'})
        validate_size({'code': '2', 'wxh': '100x100'})

        self.assertRaises(SizeError, validate_size,
            {'code': ' ', 'wxh': '100x100'})
        self.assertRaises(SizeError, validate_size,
            {'code': '&', 'wxh': '100x100'})
        self.assertRaises(SizeError, validate_size,
            {'code': 's ', 'wxh': '100x100'})
        self.assertRaises(SizeError, validate_size,
            {'code': 's!', 'wxh': '100x100'})
        self.assertRaises(SizeError, validate_size,
            {'code': '2+', 'wxh': '100x100'})

    def test_wxh_re(self):
        validate_size({'code': 'small', 'wxh': '100x100'})
        validate_size({'code': 'small', 'wxh': '5x5'})
        validate_size({'code': 'small', 'wxh': '1024x512'})

        self.assertRaises(SizeError, validate_size,
            {'code': 'small', 'wxh': 'x100'})
        self.assertRaises(SizeError, validate_size,
            {'code': 'small', 'wxh': '100x'})
        self.assertRaises(SizeError, validate_size,
            {'code': 'small', 'wxh': 'x'})
        self.assertRaises(SizeError, validate_size,
            {'code': 'small', 'wxh': '100xx100'})
        self.assertRaises(SizeError, validate_size,
            {'code': 'small', 'wxh': 'x100x100'})
        self.assertRaises(SizeError, validate_size,
            {'code': 'small', 'wxh': '100x100x'})
        self.assertRaises(SizeError, validate_size,
            {'code': 'small', 'wxh': '1-0x100'})
        self.assertRaises(SizeError, validate_size,
            {'code': 'small', 'wxh': '100x 100'})

    def test_resize_optional(self):
        validate_size({'code': 'small', 'wxh': '100x100'})

    def test_resize_valid(self):
        validate_size({'code': 'small', 'wxh': '100x100', 'resize': 'crop'})
        validate_size({'code': 'small', 'wxh': '100x100', 'resize': 'scale'})

    def test_resize_invalid(self):
        self.assertRaises(SizeError, validate_size,
            {'code': 'small', 'wxh': '100x100', 'resize': 'fail'})
