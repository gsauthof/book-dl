# 2015-05-03, Georg Sauthoff <mail@georg.so>, GPLv3+

import lxml
import lxml.html
import requests
import urllib.parse
import logging
import re
import hashlib
import random
import time



class GB_DE(object):

  def __init__(self, url, book, args):
    self.url = url
    self.base_url = '{0.scheme}://{0.netloc}'.format(
        urllib.parse.urlsplit(url))
    self.book = book
    self.args = args
    self.headers = { 'User-Agent': args.agent }
    self.dump_count = 0


  def get_url(self, url):
    logging.info('Getting {} ...'.format(url))
    time.sleep(random.expovariate(1.0/self.args.wait))
    page = requests.get(url, headers=self.headers)
    if self.args.dump:
      with open('{0}/dump_{1:04d}.html'.format(self.args.out,
        self.dump_count), 'w') as f:
        f.write(page.text)
        self.dump_count += 1
    return page

  def chapter_urls_from_string(self, s):
    tree = lxml.html.fromstring(s)
    chapter_urls = tree.xpath(
        '//ul[@class="gbnav"]//li/a/@href')
    if not chapter_urls:
      logging.error('Could not find any chapters')
    return chapter_urls

  def get_chapter_urls(self):
    page = self.get_url(self.url)
    return self.chapter_urls_from_string(page.text)

  def download(self):
    chapter_urls = self.get_chapter_urls()
    self.download_chapters(chapter_urls)

  def download_chapters(self, chapter_urls):
    i = 1
    for chapter_url in chapter_urls:
      self.download_chapter(self.base_url + chapter_url, i)
      i += 1

  def meta_data(self, root, key):
    l = root.xpath('.//div[@id="metadata"]//tr[./td = "{}"]/td[2]/text()'.format(key))
    if l:
      return str(l[0])
    else:
      return None

  def set_meta_data(self, root, div):
    self.set_author(root, div)
    self.set_title(root, div)
    self.set_uuid(root, div)

  def set_author(self, root, div):
    if self.args.author:
      for author in self.args.author:
        self.push_author(author)
    else:
      author = self.meta_data(root, 'author')
      if author:
        logging.info('Found author in metadata: {}'.format(author))
        self.push_author(author)
      else:
        l = div.xpath('.//h3[1]/text()')
        if not l:
          raise RuntimeError('Could not find author in first chapter - consider specifying it with an option')
        logging.info('Found author: {}'.format(l[0]))
        self.push_author(l[0])

  def push_author(self, author):
      e = re.compile('(.+) (.+)')
      m = e.match(author)
      if not m:
        raise RuntimeError('Could not seperate author name by blank: {}'.format(author))
      self.book.push_author(m.group(1), m.group(2))

  def set_title(self, root, div):
    if self.args.title:
      self.book.title = self.args.title
    else:
      title = self.meta_data(root, 'title')
      if title:
        logging.info('Found title in metadata: {}'.format(title))
        self.book.title = title
      else:
        l = div.xpath('.//h2[1]/text()')
        if not l:
          raise RuntimeError('Could not find title in first chapter - consider specifying it with an option')
        m = []
        for s in l:
          m.append(str(s).strip().replace('.', ''))
        title = ' - '.join(m)
        logging.info('Found title: {}'.format(title))
        self.book.title = title

  def set_uuid(self, root, div):
    if self.args.uuid:
      self.book.uuid = self.args.uuid
    else:
      isbn = self.meta_data(root, 'isbn')
      if isbn:
        logging.info('Found isbn in metadata: {}'.format(isbn))
        self.book.uuid = isbn
      else:
        m = hashlib.md5()
        for author in self.book.authors:
          m.update(author[0].encode('utf-8'))
          m.update(author[1].encode('utf-8'))
        m.update(self.book.title.encode('utf-8'))
        logging.info('Generated uuid: {}'.format(m.hexdigest()))
        self.book.uuid = m.hexdigest()

  def chapter_title(self, root):
    title = ''
    l = root.xpath('.//p[@class="centerbig"]/text()')
    if l:
      title = str(l[0])
      logging.info('Found chapter title: {}'.format(title))
    else:
      logging.info('Chapter title not found - using book title: {}'.format(self.book.title))
      title = self.book.title
    return title

  def remove_class_attributes(self, div):
    for e in div.xpath('.//*[@class]'):
      e.attrib.pop('class')

  def remove_anchors(self, div):
    # wtf ... with lxml an element may have 
    # tailing text (.tail) - thus, when removing
    # an element, the tail is removed as well ...
    # thus, getparent().remove(e) can't be used here
    for e in div.xpath('.//a[not(@href)]'):
      e.drop_tag()

  def remove_empty_paragraphs(self, div):
    #for e in div.xpath('.//p[not(node())]'):
    for e in div.xpath('.//p[not(*)][not(normalize-space())]'):
      e.getparent().remove(e)

  def push_chapter(self, s, i):
    tree = lxml.html.fromstring(s)
    div = tree.xpath('//div[@id="gutenb"]')[0]
    if i == 1:
      self.set_meta_data(tree, div)
    title = self.chapter_title(div)
    self.remove_class_attributes(div)
    self.remove_anchors(div)
    self.remove_empty_paragraphs
    self.book.push_chapter(title, [div])

  def download_chapter(self, url, i):
    page = self.get_url(url)
    self.push_chapter(page.text, i)


