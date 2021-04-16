"""
Summary
-------

This plugin extracts the first paragraph containing text as the article/page summary (if no summary is provided).
If no `image` metadata is provided, the plugin sets it to the `src` of the first `img` tag in the content.
"""

from bs4 import BeautifulSoup
from pelican import signals
from pelican.generators import ArticlesGenerator, StaticGenerator, PagesGenerator
import re

def set_summary(instance, summary):
	# default_status was added to Pelican Content objects after 3.7.1.
	# Its use here is strictly to decide on how to set the summary.
	# There's probably a better way to do this but I couldn't find it.
	if hasattr(instance, 'default_status'):
		instance.metadata["summary"] = summary
	else:
		instance._summary = summary

def get_summary(instance):
	if hasattr(instance, '_summary'):
		return instance._summary
	elif "summary" in instance.metadata:
		return instance.metadata["summary"]
	else:
		raise AttributeError("Pelican content object has no summary")

def extract_summary(instance, content_raw):
	try:
		get_summary(instance)
	except AttributeError:
		pass
	else:
		instance.has_summary = True
		return

	if not instance._content:
		instance.has_summary = False
		return

	content = BeautifulSoup(content_raw, "html.parser")

	summary = None

	for p in content.find_all("p"):
		for img in p.find_all("img"):
			img.extract()
		string = " ".join(p.stripped_strings)
		if instance.slug == "s02e14-keeping-up-with-the-dumbledores":
			print("STRING: "+string)
		if string:
			summary = str(p)
			break
	else:
		# TODO: Try to find the summary a different way.
		pass

	if summary is None:
		instance.has_summary = False
	else:
		set_summary(instance, summary)
		instance.has_summary = True

def extract_image(instance, content_raw):
	if hasattr(instance, "image"):
		return
	if not instance._content:
		return

	content = BeautifulSoup(content_raw, "html.parser")

	img = content.find("img")

	if img is not None:
		instance.image = img["src"]


def run_plugin(generators):
	for generator in generators:
		if isinstance(generator, ArticlesGenerator):
			for article in generator.articles:
				content_raw = article._update_content(article._content, article.settings['SITEURL'])
				extract_summary(article, content_raw)
				extract_image(article, content_raw)
		elif isinstance(generator, PagesGenerator):
			for page in generator.pages:
				content_raw = page._update_content(page._content, page.settings['SITEURL'])
				extract_summary(page, content_raw)
				extract_image(page, content_raw)


def register():
	signals.all_generators_finalized.connect(run_plugin)
