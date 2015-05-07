import epub

import unittest
import tempfile
import logging
import shutil
import os.path
import lxml.etree
import io
import zipfile

logging.basicConfig(level = logging.DEBUG)

class Basic(unittest.TestCase):

  def setUp(self):
    self.base_path = tempfile.mkdtemp()
    logging.debug('Tempdir is: %s', self.base_path)

    book = epub.Book(self.base_path)
    self.book = book
    book.title = 'Der Mann ohne Eigenschaften'
    book.uuid = '4223xxx'
    book.push_author('Robert', 'Musil')
    

  def tearDown(self):
    logging.debug('Removing %s', self.base_path)
    shutil.rmtree(self.base_path)


  def test_hello_world(self):
    self.assertEqual(1, 2-1)

  def test_mimetype(self):
    l = []
    self.book.write()
    with open(self.base_path + '/archive/mimetype', 'r') as f:
      l = f.read().splitlines()
    self.assertEqual(len(l), 1)
    self.assertEqual(l[0], 'application/epub+zip')

  def test_container(self):
    ref = '''<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OPS/book.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>'''
    x = lxml.etree.fromstring(ref)
    xb = io.BytesIO()
    x.getroottree().write_c14n(xb)
    s = ''
    self.book.write()
    with open(self.base_path + '/archive/META-INF/container.xml', 'r') as f:
      s = f.read()
    y = lxml.etree.fromstring(s)
    yb = io.BytesIO()
    y.getroottree().write_c14n(yb)
    self.assertEqual(xb.getvalue(), yb.getvalue())

  def test_css(self):
    self.book.write()
    self.assertTrue(os.path.isfile(self.base_path + '/archive/OPS/book.css'))


class OPF(unittest.TestCase):

  def setUp(self):
    self.base_path = tempfile.mkdtemp()
    logging.debug('Tempdir is: %s', self.base_path)

    book = epub.Book(self.base_path)
    self.book = book
    book.title = 'Der Mann ohne Eigenschaften'
    book.uuid = '4223xxx'
    book.push_author('Robert', 'Musil')
    divs = [ lxml.etree.fromstring('<div><h1>123</h1><p>lorum lipsum</p></div>'), lxml.etree.fromstring('<div><h1>456</h1><p>foo bar</p></div>') ]
    book.push_chapter('Auch ein Mann ohne Eigenschaften hat einen Vater mit Eigenschaften', divs)
    divs = [ lxml.etree.fromstring('<div><h1>23</h1><p>abcd</p></div>') ]
    book.push_chapter('Woraus bemerkenswerter Weise nichts hervorgeht', divs)
    

  def tearDown(self):
    logging.debug('Removing %s', self.base_path)
    shutil.rmtree(self.base_path)


  def test_chapter_files(self):
    self.book.write()
    self.assertTrue(os.path.isfile(self.base_path + '/archive/OPS/chapter/0000.html'))
    self.assertTrue(os.path.isfile(self.base_path + '/archive/OPS/chapter/0001.html'))

  def test_chapter_content(self):
    ref = '''<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8"/>
    <title>Der Mann ohne Eigenschaften</title>
    <link href="book.css" rel="stylesheet" type="text/css"/>
  </head>
  <body>
    <div>
      <h1>23</h1>
      <p>abcd</p>
    </div>
  </body>
</html>'''
    x = lxml.etree.fromstring(ref)
    xb = io.BytesIO()
    x.getroottree().write_c14n(xb, with_comments=False)
    s = ''
    self.book.write()
    with open(self.base_path + '/archive/OPS/chapter/0001.html', 'r') as f:
      s = f.read()
    y = lxml.etree.fromstring(s)
    yb = io.BytesIO()
    y.getroottree().write_c14n(yb, with_comments=False)
    #logging.debug('Ref: %s', xb.getvalue())
    #logging.debug('New: %s', yb.getvalue())
    self.assertEqual(xb.getvalue(), yb.getvalue())

  def test_opf(self):
    ref = '''<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:title>Der Mann ohne Eigenschaften</dc:title>
    <dc:language>en</dc:language>
    <dc:identifier id="BookId" opf:scheme="ISBNPLUS">4223xxx</dc:identifier>
    <dc:creator opf:file-as="Musil, Robert" opf:role="aut">Robert Musil</dc:creator>
  </metadata>
  <manifest>
    <item href="book.css" id="stylesheet" media-type="text/css"></item>
    <item href="book.ncx" id="ncx" media-type="application/x-dtbncx+xml"></item>
    <item href="chapter/0000.html" id="chapter_0000" media-type="application/xhtml+xml"></item>
    <item href="chapter/0001.html" id="chapter_0001" media-type="application/xhtml+xml"></item>
  </manifest>
  <spine toc="ncx">
    <itemref idref="chapter_0000"></itemref>
    <itemref idref="chapter_0001"></itemref>
  </spine>
  <guide>
    <reference href="chapter/chapter_0000.html" title="Contents" type="toc"></reference>
    <reference href="chapter/chapter_0000.html" title="Title" type="title-page"></reference>
    <reference href="chapter/chapter_0000.html" title="Foreword" type="foreword"></reference>
    <reference href="chapter/chapter_0000.html" title="License" type="copyright-page"></reference>
    <reference href="chapter/chapter_0000.html" title="Start" type="text"></reference>
    <reference href="chapter/chapter_0001.html" title="Bibliography"></reference>
  </guide>
</package>'''
    x = lxml.etree.fromstring(ref)
    xb = io.BytesIO()
    x.getroottree().write_c14n(xb, with_comments=False)
    s = ''
    self.book.write()
    with open(self.base_path + '/archive/OPS/book.opf', 'r') as f:
      s = f.read()
    y = lxml.etree.fromstring(s)
    yb = io.BytesIO()
    y.getroottree().write_c14n(yb, with_comments=False)
    #print(yb.getvalue().decode('utf-8'))
    #logging.debug('Ref: %s', xb.getvalue())
    #logging.debug('New: %s', yb.getvalue())
    self.assertEqual(xb.getvalue(), yb.getvalue())


class NCX(unittest.TestCase):

  def setUp(self):
    self.base_path = tempfile.mkdtemp()
    logging.debug('Tempdir is: %s', self.base_path)

    book = epub.Book(self.base_path)
    self.book = book
    book.title = 'Der Mann ohne Eigenschaften'
    book.uuid = '4223xxx'
    book.push_author('Robert', 'Musil')
    divs = [ lxml.etree.fromstring('<div><h1>123</h1><p>lorum lipsum</p></div>'), lxml.etree.fromstring('<div><h1>456</h1><p>foo bar</p></div>') ]
    book.push_chapter('Auch ein Mann ohne Eigenschaften hat einen Vater mit Eigenschaften', divs)
    divs = [ lxml.etree.fromstring('<div><h1>23</h1><p>abcd</p></div>') ]
    book.push_chapter('Woraus bemerkenswerter Weise nichts hervorgeht', divs)
    

  def tearDown(self):
    logging.debug('Removing %s', self.base_path)
    shutil.rmtree(self.base_path)


  def test_ncx(self):
    ref = '''<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="en">
  <head>
    <meta content="4223xxx" name="dtb:uid"></meta>
    <meta content="1" name="dtb:depth"></meta>
    <meta content="0" name="dtb:totalPageCount"></meta>
    <meta content="0" name="dtb:maxPageNumber"></meta>
  </head>
  <docTitle>
    <text>Der Mann ohne Eigenschaften</text>
  </docTitle>
  <docAuthor>
    <text>Musil, Robert</text>
  </docAuthor>
  <navMap>
    <navPoint class="chapter" id="chapter_0000" playOrder="1">
      <navLabel>
        <text>0. Auch ein Mann ohne Eigenschaften hat einen Vater mit Eigenschaften</text>
      </navLabel>
      <content src="chapter/0000.html"></content>
    </navPoint>
    <navPoint class="chapter" id="chapter_0001" playOrder="2">
      <navLabel>
        <text>1. Woraus bemerkenswerter Weise nichts hervorgeht</text>
      </navLabel>
      <content src="chapter/0001.html"></content>
    </navPoint>
  </navMap>
</ncx>'''
    x = lxml.etree.fromstring(ref)
    xb = io.BytesIO()
    x.getroottree().write_c14n(xb, with_comments=False)
    s = ''
    self.book.write()
    with open(self.base_path + '/archive/OPS/book.ncx', 'r') as f:
      s = f.read()
    y = lxml.etree.fromstring(s)
    yb = io.BytesIO()
    y.getroottree().write_c14n(yb, with_comments=False)
    #print(yb.getvalue().decode('utf-8'))
    #logging.debug('Ref: %s', xb.getvalue())
    #logging.debug('New: %s', yb.getvalue())
    self.assertEqual(xb.getvalue(), yb.getvalue())



class Zip(unittest.TestCase):

  def setUp(self):
    self.base_path = tempfile.mkdtemp()
    logging.debug('Tempdir is: %s', self.base_path)

    book = epub.Book(self.base_path)
    self.book = book
    book.title = 'Der Mann ohne Eigenschaften'
    book.uuid = '4223xxx'
    book.push_author('Robert', 'Musil')
    divs = [ lxml.etree.fromstring('<div><h1>123</h1><p>lorum lipsum</p></div>'), lxml.etree.fromstring('<div><h1>456</h1><p>foo bar</p></div>') ]
    book.push_chapter('Auch ein Mann ohne Eigenschaften hat einen Vater mit Eigenschaften', divs)
    divs = [ lxml.etree.fromstring('<div><h1>23</h1><p>abcd</p></div>') ]
    book.push_chapter('Woraus bemerkenswerter Weise nichts hervorgeht', divs)
    

  def tearDown(self):
    logging.debug('Removing %s', self.base_path)
    shutil.rmtree(self.base_path)


  def test_epub(self):
    self.book.write()
    l = []
    with zipfile.ZipFile(self.base_path + '/book.epub', 'r') as z:
      l = z.namelist()
    l.sort()
    ref = ['META-INF/container.xml',
           'OPS/book.css',
           'OPS/book.ncx',
           'OPS/book.opf',
           'OPS/chapter/0000.html',
           'OPS/chapter/0001.html',
           'mimetype']
    self.assertEqual(ref, l)

