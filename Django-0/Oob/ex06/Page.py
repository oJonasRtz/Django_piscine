from elem import Elem, Text

class Page:
	def __init__(self, element: Elem):
		if not isinstance(element, Elem):
			raise TypeError("Root element must be an instance of Elem")

		self.root = element
	
	def _check_valid_tags(self, node):
		"""
			Rule:
				If, on the tree path, a node has not one of the following types: html, head, body,
				title, meta, img, table, th, tr, td , ul, ol, li, h1, h2, p, div, span, hr, br or
				Text, the tree is invalid.
		"""
		allowed_tags = {
			"html", "head", "body",
			"title", "meta", "img",
			"table", "th", "tr", "td",
			"ul", "ol", "li",
			"h1", "h2", "p", "div", "span", "hr", "br"
		}
		if isinstance(node, Text):
			return True
		if isinstance(node, Elem) and node.tag not in allowed_tags:
			return False
		for child in node.content:
			if not self._check_valid_tags(child):
				return False
		return True

	def _check_hierarchy(self, node: Elem):
		allowed_children = {
			"html": ["head", "body"],
			"head": ["title", "meta"],
			"body": ["h1", "h2", "div", "table", "ul", "ol", "span"],
			"div": ["h1", "h2", "div", "table", "ul", "ol", "span"],
			"table": ["tr"],
			"tr": ["th", "td"],
			"ul": ["li"],
			"ol": ["li"],
			'span': ['p']
		}
		only_text_tags = {'p', 'h1', 'h2', 'li', 'th', 'td', 'title'}

		if isinstance(node, Text):
			return True

		if node.tag in only_text_tags:
			for child in node.content:
				if not isinstance(child, Text):
					return False
			return True

		if node.tag in allowed_children:
			for child in node.content:
				if isinstance(child, Elem) and child.tag not in allowed_children[node.tag]:
					return False
				if not self._check_hierarchy(child):
					return False
		return True
		
	def is_valid(self) -> bool:
		return (
			self._check_valid_tags(self.root)
			and self._check_hierarchy(self.root)
		)
  
	def _add_doctype(self, doc: str, is_html_doc: bool) -> str:
		if is_html_doc and not doc.startswith("<!DOCTYPE html>"):
			doc = "<!DOCTYPE html>\n" + doc
		return doc
  
	def write_to_file(self, filename: str):
		if not isinstance(filename, str):
			raise TypeError("Filename must be a string")
		ext = filename.split('.').pop()
		should_add_doctype = (self.root.tag == "html" and ext == "html")
		doc = self._add_doctype(str(self.root), should_add_doctype)
		with open(filename, "w") as f:
			f.write(doc)

	def __str__(self):
		doc = self._add_doctype(str(self.root), self.root.tag == "html")
		return doc