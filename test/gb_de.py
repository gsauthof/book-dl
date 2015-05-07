import gb_de
import epub

import unittest
import logging
import shutil
import tempfile
import lxml.etree
import lxml.html
import re

logging.basicConfig(level = logging.DEBUG)

class Args(object):

  def __init__(self):
    self.agent = 'some agent'
    self.author = [] 
    self.title = None
    self.uuid = None


class Basic(unittest.TestCase):

  def setUp(self):
    self.base_path = tempfile.mkdtemp()
    logging.debug('Tempdir is: %s', self.base_path)
    self.book = epub.Book(self.base_path)
    self.args = Args()
    self.gb = gb_de.GB_DE('http://gutenberg.spiegel.de/musil/mannohne/mannohne.xml', self.book, self.args)

  def tearDown(self):
    logging.debug('Removing %s', self.base_path)
    shutil.rmtree(self.base_path)
    
  def test_chapter_urls(self):
    s = ''
    with open('test/in/dmoe_1.html', 'r') as f:
      s = f.read()
    ref = []
    for i in range(1, 125):
      ref.append('/buch/der-mann-ohne-eigenschaften-erstes-buch-7588/{}'.format(i))
    urls = self.gb.chapter_urls_from_string(s)
    self.assertEqual(ref, urls)

  def test_meta_data(self):
    s = ''
    with open('test/in/dmoe_1.html', 'r') as f:
      s = f.read()
    root = lxml.html.fromstring(s)
    self.assertEqual(self.gb.meta_data(root, 'isbn'), '3498092766')
    self.assertEqual(self.gb.meta_data(root, 'author'), 'Robert Musil')
    self.assertEqual(self.gb.meta_data(root, 'title'), 'Der Mann ohne Eigenschaften. Erstes Buch')

  def test_set_meta_data(self):
    s = ''
    with open('test/in/dmoe_1.html', 'r') as f:
      s = f.read()
    root = lxml.html.fromstring(s)
    div = root.xpath('//div[@id="gutenb"]')[0]
    self.gb.set_meta_data(root, div)
    self.assertEqual(self.book.uuid, '3498092766')
    self.assertEqual(self.book.authors, [('Robert', 'Musil', 'aut')])
    self.assertEqual(self.book.title, 'Der Mann ohne Eigenschaften. Erstes Buch')

  def test_meta_data_overrides(self):
    s = ''
    with open('test/in/dmoe_1.html', 'r') as f:
      s = f.read()
    root = lxml.html.fromstring(s)
    div = root.xpath('//div[@id="gutenb"]')[0]
    self.args.uuid = '2423'
    self.args.title = 'Naked Lunch'
    self.args.author = [ 'William S. Burroughs' ]
    self.gb.set_meta_data(root, div)
    self.assertEqual(self.book.uuid, '2423')
    self.assertEqual(self.book.authors, [('William S.', 'Burroughs', 'aut')])
    self.assertEqual(self.book.title, 'Naked Lunch')

  def test_chapter_title(self):
    s = ''
    with open('test/in/dmoe_2.html', 'r') as f:
      s = f.read()
    root = lxml.html.fromstring(s)
    self.assertEqual(self.gb.chapter_title(root), 'Wirkung eines Mannes ohne Eigenschaften auf einen Mann mit Eigenschaften')

  def test_book_title(self):
    s = ''
    with open('test/in/dmoe_1.html', 'r') as f:
      s = f.read()
    root = lxml.html.fromstring(s)
    self.book.title = 'foo bar'
    self.assertEqual(self.gb.chapter_title(root), 'foo bar')

  def test_push_chapter(self):
    s = ''
    with open('test/in/dmoe_2.html', 'r') as f:
      s = f.read()
    self.gb.push_chapter(s, 2)
    s = ''
    with open(self.base_path + '/archive/OPS/chapter/0000.html', 'r') as f:
      s = f.read()
    self.assertTrue(s.find('Wirkung eines Mannes ohne Eigenschaften') > 0)
    self.assertEqual(s.find('moepschen/JWE'), -1)
    self.assertEqual(s.find('"class"'), -1)
    self.assertTrue(s.find('zukünftigen Schwiegerpapa') > 0)

  def test_remove_class(self):
    div = lxml.html.fromstring('<div class="foo"><h3 class="blah">xyz</h3><p>foo</p><p class="bar">bar</p></div>')
    self.gb.remove_class_attributes(div)
    s = lxml.html.tostring(div)
    self.assertEqual(s, b'<div class="foo"><h3>xyz</h3><p>foo</p><p>bar</p></div>')

  def test_remove_anchors(self):
    div = lxml.html.fromstring('<div><p>foo <a name="1"/> lorum <a name="2"> </a> lipsum <a name="3"/> baz</p><p>rab oof xyz</p></div>')
    self.gb.remove_anchors(div)
    s = lxml.html.tostring(div)
    self.assertEqual(s, b'<div><p>foo  lorum   lipsum  baz</p><p>rab oof xyz</p></div>')

  def test_remove_empty_paras(self):
    div = lxml.html.fromstring('''<div><p>non empty</p><p/><p>another</p><p></p><p>    </p><p>fill</p><p>
        </p><p>end</p><p/><p></div>''')
    self.gb.remove_empty_paragraphs(div)
    s = lxml.html.tostring(div)
    self.assertEqual(s, b'<div><p>non empty</p><p>another</p><p>fill</p><p>end</p></div>')


  def test_chapter_text(self):
    s = ''
    with open('test/in/dmoe_2.html', 'r') as f:
      s = f.read()
    root = lxml.html.fromstring(s)
    self.gb.push_chapter(s, 2)
    div = root.xpath('//div[@id="gutenb"]')[0]
    s = lxml.html.tostring(div, encoding='unicode')
    s = re.sub('<[^>]+>', '', s)
    s = re.sub('[ \\t\\r\\n\\xa0]+', ' ', s)
    t = ''
    with open(self.base_path + '/archive/OPS/chapter/0000.html', 'r') as f:
      t = f.read()
    t = re.sub('<[^>]+>', '', t)
    t = re.sub('[ \\t\\r\\n\\xa0 ]+', ' ', t)
    self.assertEqual(s, t)

