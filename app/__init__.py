from flask import Flask, request, render_template, abort, redirect
import markdown
import yaml
import os
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
				"p", "br", "hr", "pre", "div",
				"ul", "ol", "li",
				"table", "thead", "tbody", "tr", "th", "td",
				),	
			remove_unknown_tags = False,
			safe_attrs = set(["class", "href", "src", "alt"]),
			)
	def renderer(self, text):
		html = self.markdown.convert(text)
		html = self.cleaner.clean_html(html)
		return html

class WikiPage(object):
	def __init__(self, wiki, path):
		self.wiki = wiki
		self.path = path
		try:
			with open(self.path, 'r', encoding='utf-8') as f:
				text = f.read()
				if text.startswith("---"):
					parts = text.split("---\n",2)
					self.meta = yaml.safe_load(parts[1])
					self.content = parts[2]
				else:
					self.meta = {}
					self.content = text
			self.is_new = False
		except FileNotFoundError:
			title = os.path.splitext(os.path.basename(self.path))[0].capitalize().replace("_"," ").replace("-", " ")
			self.meta = {'title':title}
			self.content = None
			self.is_new = True

	# This is called from the Jinja template to render the content HTML
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

@app.route('/', methods=['GET', 'POST'])
def index():
	return page('index')

@app.route('/<path:path>', methods=['GET', 'POST'])
def page(path):
	if path.endswith("/"):
		folders = path.split('/')[:-2]
	else:
		folders = path.split('/')[:-1]

	if path.endswith('/'):
		path += "index.md"
	else:
		path += ".md"

	path = os.path.realpath(os.path.join(app.instance_path, path))
	if not path.startswith(app.instance_path):
		abort(403)

	page = WikiPage(wiki, path)
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
	for i in range(len(folders)):
		breadcrumbs.append((folders[i].capitalize(), "/" + "/".join(folders[:i+1]) + "/"))

	return render_template("page_view.html", page=page, action=action, breadcrumbs=breadcrumbs)

class DummyPage(object):
	def __init__(self, title):
		self.meta = {'title':title}

@app.route('/sitemap')
def sitemap():
	pages = []
	for path in glob(app.instance_path + "/**/*.md", recursive=True):
		href = path[len(app.instance_path):-3]
		if href.endswith("/index"):
			href = href[:-5]
		page = WikiPage(wiki, path)
		pages.append((page.meta['title'], href))
	pages = sorted(pages, key=itemgetter(1))
	return render_template("sitemap.html", page=DummyPage("Sitemap"), pages=pages)

