#!/usr/bin/env python3

# 2015-05-03, Georg Sauthoff <mail@georg.so>, GPLv3+

import logging
import argparse
import sys
import re

import gb_de
import epub

user_agent = 'Mozilla/5.0 (Android; Mobile; rv:30.0) Gecko/30.0 Firefox/30.0' 


parser = argparse.ArgumentParser(description='Download books.')
parser.add_argument('url', nargs='+', help = 'URL to download'
                    )
parser.add_argument('--out', help = 'Output directory',
                    required = True)
parser.add_argument('--name', help = 'epub base name')
parser.add_argument('--wait', help='wait rate',
                    #default=0.1,
                    default=1.1,
                    type=float)
parser.add_argument('--agent', help='user agent',
                    default = user_agent)
parser.add_argument('--title', help='override book title')
parser.add_argument('--author', help='override author',
                    default=[], action='append')
parser.add_argument('--uuid', help='set uuid, e.g. ISBN')
parser.add_argument('--style', help='disable auto-detect of source and explicitly specify one (e.g. gb)')
parser.add_argument('--level',
    help='set log level (e.g. debug, warning, ...)', default = 'info')
parser.add_argument('--dump', action='store_true',
    help='dump requested pages for debugging purposes')


sources = [ ('gb', gb_de.GB_DE, [ re.compile('gutenberg\\.spiegel\\.de') ] ) ]

sources_map = {}

for s in sources:
  sources_map[s[0]] = (s[1], s[2])

name_exp = re.compile('.+/([^/]+)\\.xml')

def base_name(url):
  m = name_exp.match(url)
  r = ''
  if m:
    r = m.group(1)
  else:
    r = 'book'
  logging.info('automatic epub base name: {}'.format(r))
  return r

if __name__ == '__main__':
  try:
    logging.debug('Parsing arguments ...')
    args = parser.parse_args()
    if not args.url:
      raise ValueError('no url given')
    level = getattr(logging, args.level.upper())
    logging.getLogger('').setLevel(level)
    for url in args.url:
      if args.style:
        c = sources_map[args.style]
      else:
        for s in sources:
          for e in s[2]:
            if e.search(url):
              c = s[1]
              break
      book = epub.Book(args.out)
      if args.name:
        book.epub_base_name = args.name
      else:
        book.epub_base_name = base_name(url)
      o = c(url, book, args)
      o.download()
      logging.info('Book written to: {}/{}.epub'.format(args.out,
        book.epub_base_name))
      book.write()
  except Exception as e:
    raise
    logging.error('Error: {}'.format(e))
    sys.exit(1)
  except:
    raise
    logging.error('Error: {}'.format(sys.exc_info()))
    sys.exit(1)

