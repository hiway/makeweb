#!/usr/bin/env python
#
# static_site.py
#
#
# The early Web was not live servers manipulating html on-the-fly,
# rather, but rather hand-crafted documents saved in a directory tree,
# served passively by a patchy server somewhere.
#
# https://en.wikipedia.org/wiki/History_of_the_Internet
#
# We will use MakeWeb library to generate html
# and write it out to files in this example.
#
import random
import re
import os
import sys

# We will use Faker, a library to generate fake blog posts for us.
from faker import Faker

# Also, markdown to automatically format the content.
from markdown import markdown

from makeweb import (
    Doc,
    head, link, title, nav,
    body, div, h1, h3, div, p, a,
)

# We will store the blog output in this directory
OUTPUT_DIR = os.path.abspath('./tmp')


# Here we take in specific arguments
# and render an HTML page from them.
def render_post(_title, author, published, content):
    doc = Doc(doctype='html')
    with head():
        title(_title)
        link(href='../static/retro.css', _type='text/css', rel='stylesheet')
    with body():
        with div(id='content'):
            h1(_title)
            h3(author)
            p(published)
            div(markdown(content))
    return str(doc)


# Here we take a list of posts and render an index page.
def render_index(_title, posts):
    doc = Doc('html')
    with head():
        title(_title)
        link(href='../static/retro.css', _type='text/css', rel='stylesheet')
    with body():
        with div(id='content'):
            for post in posts:
                with div():
                    a(h3(post['title']), href='{}.html'.format(slugify(post['title'])))
                    content = post['content']
                    if len(content) > 50:
                        content = content[:50] + '...'
                    p(markdown(content))

    return str(doc)


# A quick n' dirty cleanup function for post title => filename and url.
def slugify(text):
    text = text.strip().lower().replace(' ', '-')
    text = re.sub(r'[^A-Za-z0-9-]', r'', text)
    return text


fake = Faker()

# M^hFake some posts with Faker!
posts = [{
    'title': fake.text(random.randrange(10, 60)),
    'author': fake.name(),
    'published': fake.date(),
    'content': '\n\n'.join([fake.text(random.randrange(120, 1000))
                            for _ in range(random.randrange(2, 10))])
} for _ in range(10)]

# Check if we're about to overwrite previous output.
if os.path.exists(OUTPUT_DIR):
    response = input('Overwrite existing output at {}? (y,N): '.format(OUTPUT_DIR))
    if not response or response.lower().startswith('n'):
        sys.stderr.write('Not overwriting existing output, exiting.\n')
        sys.exit(-1)
    os.system('rm -r {}'.format(OUTPUT_DIR))

os.mkdir(OUTPUT_DIR)

# Generate and write out each post to the output directory
for post in posts:
    page = render_post(post['title'], post['author'],
                       post['published'], post['content'])
    slug = slugify(post['title'])
    with open(os.path.join(OUTPUT_DIR, slug + '.html'), 'w') as outfile:
        outfile.write(page)

# Generate and write index.html
index = render_index("Fake Blog", posts)
with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w') as outfile:
    outfile.write(index)

# Now use your shell or file manager and open index.html in your browser :D
