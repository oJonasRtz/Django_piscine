from elem import Elem, Text

class Page:
	def __init__(self, element: Elem):
		if not isinstance(element, Elem):
			raise TypeError("Root element must be an instance of Elem")

		self.root = element
	
	def _is_text(self, node):
		return isinstance(node, Text)

	def _is_elem(self, node):
		return isinstance(node, Elem)
 
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
		if self._is_text(node):
			return True
		if self._is_elem(node) and node.tag not in allowed_tags:
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

		if self._is_text(node):
			return True

		# <p> can can contain multi Text nodes, but others can only contain one Text node
		if node.tag in only_text_tags:
			if node.tag == 'p':
				return all(self._is_text(c) for c in node.content)
			return len(node.content) == 1 and self._is_text(node.content[0])

		if node.tag in allowed_children:
			allowed = allowed_children[node.tag]
   
			for child in node.content:
				invalid_child = self._is_elem(child) and child.tag not in allowed
				invalid_tree = not self._check_hierarchy(child)

				if invalid_child or invalid_tree:
					return False
	
		return True

	def _check_html_struct(self, node: Elem) -> bool:
		if self._is_text(node) or node.tag != "html":
			return True

		if len(node.content) != 2:
			return False
  
		head, body = node.content
		is_valid_type: bool = all(self._is_elem(c) for c in (head, body))
		is_valid_order: bool = is_valid_type and head.tag == "head" and body.tag == "body"
  
		return is_valid_order

	def _check_title(self, node: Elem) -> bool:
		if self._is_text(node) or node.tag != "html":
			return True

		if len(node.content) < 1:
			return False

		head = node.content[0]
		if not (self._is_elem(head) and head.tag == "head"):
			return True

		title_count = sum(1 for c in head.content if self._is_elem(c) and c.tag == "title")
		return title_count == 1
	
	def _check_Ul_and_Ol_content(self, node: Elem) -> bool:
		if self._is_text(node):
			return True
		if node.tag in ["ul", "ol"]:
			at_least_one_li = any(self._is_elem(c) and c.tag == "li" for c in node.content)
			is_all_li = all(self._is_elem(c) and c.tag == "li" for c in node.content)
			return at_least_one_li and is_all_li

		for child in node.content:
			if not self._check_Ul_and_Ol_content(child):
				return False
		return True
	
	def _check_Tr_content(self, node: Elem) -> bool:
		if self._is_text(node):
			return True

		if self._is_elem(node) and node.tag == 'tr':
			at_least_one_th_or_td = any(self._is_elem(c) and c.tag in ['th', 'td'] for c in node.content)
			return at_least_one_th_or_td

		for child in node.content:
			if not self._check_Tr_content(child):
				return False
		return True
 
	def is_valid(self) -> bool:
		return (
			self._check_valid_tags(self.root)
			and self._check_hierarchy(self.root)
			and self._check_html_struct(self.root)
			and self._check_title(self.root)
			and self._check_Ul_and_Ol_content(self.root)
			and self._check_Tr_content(self.root)
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