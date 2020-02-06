from flask import Flask, request, render_template, abort
import markdown
import yaml
import os
from html_sanitizer import Sanitizer

app = Flask(__name__, instance_relative_config=True)
app.config['APP_NAME'] = 'Unnamed Wiki'
app.config.from_pyfile('config.py')

class WikiPage(object):
	def __init__(self, path):
		self.path = path
		try:
			with open(self.path, 'r', encoding='utf-8') as f:
				text = f.read()
				if text.startswith("----"):
					parts = text.split("----\n")
					self.meta = yaml.safe_load(parts[1])
					self.content = parts[2]
				else:
					self.meta = {}
					self.content = text
			self.is_new = False
		except FileNotFoundError:
			self.meta = {}
			self.content = None
			self.is_new = True

		self.sanitizer = Sanitizer()

	def render(self):
		if self.content is None:
			return None
		html = markdown.markdown(self.content)
		return self.sanitizer.sanitize(html)

	def save(self):
		with open(self.path, 'w', encoding='utf-8') as f:
			f.write('----\n')
			f.write(yaml.dump(self.meta))
			f.write('----\n')
			f.write(self.content.replace('\r\n','\n'))

@app.route('/', methods=['GET', 'POST'])
def index():
	return page('index')

@app.route('/<path:path>', methods=['GET', 'POST'])
def page(path):
	if path.endswith('/'):
		path += "index.md"
	else:
		path += ".md"
	path = os.path.realpath(os.path.join(app.instance_path, path))
	if not path.startswith(app.instance_path):
		print(path, app.instance_path)
		abort(403)

	page = WikiPage(path)
	action = request.values.get('action')

	if action == 'save':
		assert request.method == 'POST'
		page.meta['title'] = request.form['title']
		page.content = request.form['content']
		page.save()

	elif action == 'edit' or page.is_new:
		return render_template("page_edit.html", page=page)

	return render_template("page_view.html", page=page, action=action)

