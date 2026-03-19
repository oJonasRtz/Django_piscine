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

		if isinstance(node, Text):
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