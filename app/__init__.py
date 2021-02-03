from flask import Flask, request, render_template, abort, redirect
import markdown
import yaml
import os
import re
from lxml.html.clean import Cleaner
from glob import glob
from operator import itemgetter

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
	APP_DISPLAY_NAME = 'Pocket Wiki',
	)
app.config.from_pyfile('config.py')

class Wiki(object):
	def __init__(self):
		self.markdown = markdown.Markdown(extensions=['tables', 'codehilite', 'fenced_code', 'smarty'])
		self.cleaner = Cleaner(
			allow_tags = (
				"a", "img",
				"h1", "h2", "h3",
				"strong", "em", "b", "i", "sub", "sup",
				"p", "pre", "div", "blockquote",
				"br", "hr",
				"ul", "ol", "li",
				"table", "thead", "tbody", "tr", "th", "td",
				),	
			remove_unknown_tags = False,
			safe_attrs = set(["class", "href", "src", "alt"]),
			)

	# Convert Markdown to HTML
	def renderer(self, text):
		html = self.markdown.convert(text)
		html = self.cleaner.clean_html(html)
		return html

	def load_page(self, path):
		return WikiPage(self, path)

class WikiPage(object):
	def __init__(self, wiki, path):
		self.wiki = wiki

		# Take the path from the requested URL and figure out the following:
		# 1) The path of the actual Markdown file
		# 2) The names of the folders to reach it (for use as breadcrumbs)
		# 3) The last component of the path which the user chose (as the initial title)
		split_path = path.split('/')
		if path.endswith("/"):					# "animals/elephants/"
			self.folders = split_path[:-2]
			path += "index.md"
			default_title = split_path[-2]
		else:									# "animals/elephants/habits"
			self.folders = split_path[:-1]
			path += ".md"
			default_title = split_path[-1]

		# Make sure the Markdown file really is in our instance directory
		path = os.path.realpath(os.path.join(app.instance_path, path))
		if not path.startswith(app.instance_path):
			abort(403)	# forbidden

		self.path = path

		try:
			# Load page from a file
			with open(self.path, 'r', encoding='utf-8') as f:
				text = f.read()
				if text.startswith("---"):				# YAML metadata present
					parts = text.split("---\n",2)
					self.meta = yaml.safe_load(parts[1])
					self.content = parts[2]
				else:									# YAML metadata not present
					self.meta = {}
					self.content = text
			self.is_new = False
		except FileNotFoundError:
			self.meta = {}
			self.content = None
			self.is_new = True

		if not 'title' in self.meta:
 			self.meta['title'] = default_title.capitalize().replace("_"," ").replace("-", " ")

	# Convert the wiki page body from Markdown to an HTML fragment
	def render(self):
		if self.content is None:
			return None
		return self.wiki.renderer(self.content)

	# Save self.content to the markdown file
	def save(self):
		if self.is_new:
			folder = os.path.dirname(self.path)
			if not os.path.exists(folder):
				os.makedirs(folder)
		with open(self.path, 'w', encoding='utf-8') as f:
			f.write('---\n')
			f.write(yaml.dump(self.meta))
			f.write('---\n')
			f.write(self.content.replace('\r\n','\n'))

wiki = Wiki()

@app.route('/', methods=['GET','POST'])
def index():
	return page('index')

# A page from the wiki
@app.route('/<path:path>', methods=['GET','POST'])
def page(path):
	page = wiki.load_page(path)
	action = request.values.get('action')

	if action == 'save':
		assert request.method == 'POST'
		page.meta['title'] = request.form['title']
		page.content = request.form['content']
		page.save()
		return redirect(request.url)

	if action == 'edit' or page.is_new:
		return render_template("page_edit.html", page=page)

	breadcrumbs = [(app.config['APP_DISPLAY_NAME'], '/')]
	for i in range(len(page.folders)):
		breadcrumbs.append((page.folders[i].capitalize(), "/" + "/".join(page.folders[:i+1]) + "/"))

	return render_template("page_view.html", page=page, action=action, breadcrumbs=breadcrumbs)

# List of all the pages in the wiki
@app.route('/sitemap')
def sitemap():
	pages = []
	for path in glob(app.instance_path + "/**/*.md", recursive=True):
		href = path[len(app.instance_path)+1:-3]		# cut off instance_path and ".md"
		if href.endswith("/index"):
			href = href[:-5]
		page = WikiPage(wiki, href)
		pages.append((page.meta['title'], href))
	pages = sorted(pages, key=itemgetter(1))
	return render_template("sitemap.html", page=DummyPage("Sitemap"), pages=pages)

class DummyPage(object):
	def __init__(self, title):
		self.meta = {'title':title}

@app.route('/favicon.ico')
def favicon():
	abort(404)


