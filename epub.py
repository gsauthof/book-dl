# 2015-05-03, Georg Sauthoff <mail@georg.so>, GPLv3+

import lxml
import lxml.etree
import lxml.html
#import logging
import os
import zipfile

class Book(object):

  def __init__(self, out_path):
    self.out_path = out_path
    self.archive_path = self.out_path + '/archive'
    self.rel_meta_inf_path = 'META-INF'
    self.meta_inf_path = self.archive_path + '/' + self.rel_meta_inf_path
    self.rel_ops_path = 'OPS'
    self.ops_path = self.archive_path + '/' + self.rel_ops_path
    self.rel_chapter_path = 'chapter'
    self.chapter_path = self.ops_path + '/' + self.rel_chapter_path
    self.rel_image_path = 'image'
    self.image_path = self.ops_path + '/' + self.rel_image_path
    for p in [ self.meta_inf_path, self.chapter_path, self.image_path]:
      os.makedirs(p, exist_ok=True)
    self.chapters = []
    self.images = []
    self.authors = []
    self.css = []
    self.title = None
    self.uuid = None
    self.lang = 'en'
    self.xml_ns = 'http://www.w3.org/XML/1998/namespace'
    self.xml_prefix='{{{}}}'.format(self.xml_ns)
    self.opf_ns = 'http://www.idpf.org/2007/opf'
    self.opf_prefix = '{{{}}}'.format(self.opf_ns)
    self.opf_nsmap = { None : self.opf_ns }
    self.dc_ns = 'http://purl.org/dc/elements/1.1/'
    self.dc_prefix = '{{{}}}'.format(self.dc_ns)
    self.metadata_nsmap = { 'dc' : self.dc_ns, 'opf' : self.opf_ns }
    self.ncx_ns = 'http://www.daisy.org/z3986/2005/ncx/'
    self.ncx_nsmap = { None : self.ncx_ns }
    self.container_ns = 'urn:oasis:names:tc:opendocument:xmlns:container'
    self.container_nsmap = { None : self.container_ns }
    self.xhtml_ns = 'http://www.w3.org/1999/xhtml'
    self.xhtml_nsmap = { None : self.xhtml_ns }
    self.chapter_media_type = 'application/xhtml+xml'
    self.css_media_type = 'text/css'
    self.ncx_media_type = 'application/x-dtbncx+xml'
    self.png_media_type = 'image/png'
    self.jpeg_media_type = 'image/jpeg'
    self.opf_media_type = 'application/oebps-package+xml'
    self.cover_image = None
    self.epub_base_name = 'book'
    self.container_filename = 'container.xml'
    self.mimetype_filename = 'mimetype'
    self.css_filename = 'book.css'
    self.ncx_filename = 'book.ncx'
    self.opf_filename = 'book.opf'

  # properties
  #   self.title
  #   self.uuid
  #   self.lang

  def push_chapter(self, title, divs):
    self.chapters.append((title, None))
    root = lxml.etree.Element('html', nsmap=self.xhtml_nsmap)
    root.set(self.xml_prefix+'lang', self.lang)
    head = lxml.etree.SubElement(root, 'head')
    meta = lxml.etree.SubElement(head, 'meta')
    meta.set('http-equiv', 'Content-Type')
    meta.set('content', 'application/xhtml+xml; charset=utf-8')
    lxml.etree.SubElement(head, 'title').text = self.title
    link = lxml.etree.SubElement(head, 'link', rel='stylesheet',
        href=self.css_filename)
    link.set('type', 'text/css')
    body = lxml.etree.SubElement(root, 'body')
    for div in divs:
      body.append(div)
    with open('{0}/{1:04d}.html'.format(self.chapter_path,
      len(self.chapters)-1), 'w') as f:
      f.write(lxml.etree.tostring(root, pretty_print=True,
        encoding='unicode'))

  # or role = 'edt'
  def push_author(self, first, last, role = 'aut'):
    self.authors.append((first, last, role))

  def push_css(self, line):
    self.css.append(line)

  def write(self):
    self.write_mimetype()
    self.write_css()
    self.write_container()
    self.write_opf()
    self.write_ncx()
    self.write_epub()

  def write_mimetype(self):
    with open(self.archive_path + '/' + self.mimetype_filename, 'w') as f:
      f.write('application/epub+zip\n')

  def write_css(self):
    with open(self.ops_path + '/' + self.css_filename, 'w') as f:
      f.writelines(self.css)

  def write_opf_metadata(self, root):
    metadata = lxml.etree.SubElement(root, 'metadata',
        nsmap=self.metadata_nsmap)
    lxml.etree.SubElement(metadata,
        self.dc_prefix + 'title').text = self.title
    lxml.etree.SubElement(metadata,
        self.dc_prefix + 'language').text = self.lang
    identifier = lxml.etree.SubElement(metadata,
        self.dc_prefix + 'identifier', id='BookId')
    identifier.set(self.opf_prefix + 'scheme', 'ISBNPLUS')
    identifier.text = self.uuid
    for author in self.authors:
      creator = lxml.etree.SubElement(metadata,
          self.dc_prefix + 'creator')
      creator.set(self.opf_prefix + 'file-as',
          '{}, {}'.format(author[1], author[0]))
      creator.set(self.opf_prefix + 'role', author[2])
      creator.text = '{} {}'.format(author[0], author[1])

  def write_opf_manifest(self, root):
    manifest = lxml.etree.SubElement(root, 'manifest')
    item = lxml.etree.SubElement(manifest, 'item', href=self.css_filename)
    item.set('id', 'stylesheet')
    item.set('media-type', self.css_media_type)
    item = lxml.etree.SubElement(manifest, 'item', href=self.ncx_filename)
    item.set('id', 'ncx')
    item.set('media-type', self.ncx_media_type)
    i = 0
    for chapter in self.chapters:
      item = lxml.etree.SubElement(manifest, 'item',
          href='{0}/{1:04d}.html'.format(self.rel_chapter_path, i))
      item.set('id', 'chapter_{0:04d}'.format(i))
      item.set('media-type', self.chapter_media_type)
      i += 1
    i = 0
    for image in self.images:
      item = lxml.etree.SubElement(manifest, 'item',
          href='{0}/{1:04d}.{2}'.format(self.rel_image_path, i,
            image[0]))
      item.set('id', 'image_{0:04d}'.format(i))
      if image[0] == 'png':
        item.set('media-type', self.png_media_type)
      elif image[0] == 'jpg':
        item.set('media-type', self.jpeg_media_type)
      i += 1

  def write_opf_spine(self, root):
    spine = lxml.etree.SubElement(root, 'spine', toc='ncx')
    i = 0
    for chapter in self.chapters:
      lxml.etree.SubElement(spine, 'itemref',
          idref='chapter_{0:04d}'.format(i))
      i += 1

  def write_opf_guide(self, root):
    guide = lxml.etree.SubElement(root, 'guide')
    for x in [ ('toc', 'Contents'), ('title-page', 'Title'), ('foreword', 'Foreword'), ('copyright-page', 'License'), ('text', 'Start') ]:
      ref = lxml.etree.SubElement(guide, 'reference',
          title=x[1], href=self.rel_chapter_path+'/chapter_0000.html')
      ref.set('type', x[0])
    if self.cover_image:
      ref = lxml.etree.SubElement(guide, 'reference',
          title='Cover', href=self.rel_image_path + self.cover_image)
    ref = lxml.etree.SubElement(guide, 'reference',
        title='Bibliography',
        href='{0}/chapter_{1:04d}.html'.format(self.rel_chapter_path,
          len(self.chapters)-1))

  def write_opf(self):
    root = lxml.etree.Element('package', nsmap=self.opf_nsmap,
        version='2.0')
    root.set('unique-identifier', 'BookId')
    self.write_opf_metadata(root)
    self.write_opf_manifest(root)
    self.write_opf_spine(root)
    self.write_opf_guide(root)
    with open(self.ops_path + '/' + self.opf_filename, 'w') as f:
      f.write(lxml.etree.tostring(root, pretty_print=True,
        encoding='unicode'))

  def write_ncx_head(self, root):
    head = lxml.etree.SubElement(root, 'head')
    # same as in .opf
    lxml.etree.SubElement(head, 'meta', name='dtb:uid',
        content=self.uuid)
    # 1 or higher
    lxml.etree.SubElement(head, 'meta', name='dtb:depth',
        content='1')
    # must be 0
    lxml.etree.SubElement(head, 'meta', name='dtb:totalPageCount',
        content='0')
    # must be 0
    lxml.etree.SubElement(head, 'meta', name='dtb:maxPageNumber',
        content='0')

  def write_ncx_title(self, root):
    doc_title = lxml.etree.SubElement(root, 'docTitle')
    lxml.etree.SubElement(doc_title, 'text').text = self.title

  def write_ncx_authors(self, root):
    for author in self.authors:
      doc_author = lxml.etree.SubElement(root, 'docAuthor')
      lxml.etree.SubElement(doc_author, 'text').text = '{}, {}'.format(author[1], author[0])

  def write_ncx_nav_map(self, root):
    nav_map = lxml.etree.SubElement(root, 'navMap')
    i = 0
    for chapter in self.chapters:
      nav_point = lxml.etree.SubElement(nav_map, 'navPoint')
      nav_point.set('class', 'chapter')
      nav_point.set('id', 'chapter_{0:04d}'.format(i))
      nav_point.set('playOrder', str(i+1))
      nav_label = lxml.etree.SubElement(nav_point, 'navLabel')
      lxml.etree.SubElement(nav_label, 'text').text = '{}. {}'.format(i, chapter[0])
      lxml.etree.SubElement(nav_point, 'content',
          src='{0}/{1:04d}.html'.format(self.rel_chapter_path, i))
      i += 1

  def write_ncx(self):
    root = lxml.etree.Element('ncx', nsmap=self.ncx_nsmap,
        version='2005-1')
    root.set(self.xml_prefix + 'lang', self.lang)
    self.write_ncx_head(root)
    self.write_ncx_title(root)
    self.write_ncx_authors(root)
    self.write_ncx_nav_map(root)
    with open(self.ops_path + '/' + self.ncx_filename, 'w') as f:
      f.write(lxml.etree.tostring(root, pretty_print=True,
        encoding='unicode'))

  def write_container(self):
    root = lxml.etree.Element('container', nsmap=self.container_nsmap,
        version='1.0')
    rootfiles = lxml.etree.SubElement(root, 'rootfiles')
    rootfile = lxml.etree.SubElement(rootfiles, 'rootfile')
    rootfile.set('full-path',
        self.rel_ops_path + '/' + self.opf_filename)
    rootfile.set('media-type', self.opf_media_type)
    with open(self.meta_inf_path + '/' + self.container_filename, 'w') as f:
      f.write(lxml.etree.tostring(root, pretty_print=True,
        encoding='unicode'))

  def write_epub(self):
    with zipfile.ZipFile('{}/{}.epub'.format(self.out_path,
      self.epub_base_name), 'w') as z:
      z.write(self.meta_inf_path + '/' + self.container_filename,
          self.rel_meta_inf_path + '/' + self.container_filename)
      z.write(self.archive_path + '/' + self.mimetype_filename,
          self.mimetype_filename)
      for fn in [ self.css_filename, self.ncx_filename, self.opf_filename ]:
        z.write(self.ops_path + '/' + fn, self.rel_ops_path + '/' + fn)
      for i in range(0, len(self.chapters)):
        z.write('{0}/{1:04d}.html'.format(self.chapter_path, i),
            '{0}/{1}/{2:04d}.html'.format(self.rel_ops_path, self.rel_chapter_path, i),
            )
      i = 0
      for image in self.images:
        z.write(
            '{0}/{1:04d}.{2}'.format(self.image_path, i, image[0]),
            '{0}/{1}/{1:04d}.{2}'.format(self.rel_ops_path, self.rel_image_path, i, image[0]))
        i += 1


