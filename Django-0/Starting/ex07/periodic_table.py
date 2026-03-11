import sys;

def openFile(filename: str) -> list[str]:
	with open(filename, 'r') as file:
		f = []
		for line in file:
			f.append(line.strip());
		return f;

def listToDict(l: list[str]) -> dict[str, dict[str]]:
	d = {}
	for line in l:
		key, value = line.split('=');
		attr = {}

		for item in value.split(','):
			k, v = item.split(':');
			attr[k.strip()] = v.strip();

		d[key.strip()] = attr;

	return d

def build_css(title: str) -> str:
	if not isinstance(title, str):
		raise ValueError("__TYPE_ERROR__")

	title = title.split('.')[0] + '.css'
	
	doc = """
	body {
		background-color: #0b1d3a;
		color: white;
		font-family: Arial, sans-serif;
	}
	table {
		border-collapse: collapse;
		margin: auto;
	}
	td {
		padding: 10px;
		text-align: center;
	}
	h4 {
		margin: 5px;
	}
	ul {
		list-style: none;
		padding: 0;
	}
	td:hover {
		scale: 1.1;
		transition: all 0.3s ease;
		border: 1px solid white;
	}
	"""
 
	with open(title, 'w') as file:
		file.write(doc)

	return title
 
def build_table(data) -> str:
	doc = ''
	col = 0
 
	doc += '<tr>'
	
	for key, value in data.items():
		pos = int(value['position'])

		while col < pos:
			doc += '<td></td>'
			col += 1

		doc += f'''
			<td style="border: 1px solid white; padding:10px; background-color: #1f3b73;">
				<h4>{key}</h4>
				<ul>
					<li>No {value['number']}</li>
					<li>{value['small']}</li>
					<li>{value['molar']}</li>
					<li>{value['electron']} electron</li>
				</ul>
			</td>
		'''
  
		col += 1
		if col > 17:
			doc += '</tr>\n<tr>'
			col = 0
  
	doc += '</tr>'
	return doc

def build_html(filename: str, dict: dict[str, dict[str]]) -> None:
	title = filename.split('.')[0].replace('_', ' ').title()

	css = build_css(filename)

	head = f"""
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>{title}</title>
		<link rel="stylesheet" href="{css}">
	"""


	body = f"""
		<table style="border-collapse: collapse;">
			{build_table(dict)}
		</table>
 """

	doc = f"""<!DOCTYPE html>
	<html lang="en">
		<head>
			{head}
		</head>
		<body>
			{body}
			<p>
				<a href="https://jigsaw.w3.org/css-validator/check/referer">
					<img style="border:0;width:88px;height:31px"
						src="https://jigsaw.w3.org/css-validator/images/vcss"
						alt="Valid CSS!" />
				</a>
			</p>
		</body>
	</html>
"""

	with open(filename, 'w') as file:
		file.write(doc)

def main():
	file = openFile('periodic_table.txt');
	myDict = listToDict(file);
	name = sys.argv[0].split('.')[0] + '.html';
	build_html(name, myDict);

if __name__ == '__main__':
	main();
