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

def build_html(filename: str, dict: dict[str, dict[str]]) -> None:
	title = filename.split('.')[0].replace('_', ' ').title()

	head = f"""
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>{title}</title>
	"""

	body = f"""
		<table>
					{''.join(
						f'''
						<tr>
							<td style="border: 1px solid black; padding:10px">
								<h4>{key}</h4>
								<ul>
									<li>No {value['number']}</li>
									<li>{value['small']}</li>
									<li>{value['molar']}</li>
									<li>{value['electron']} electron</li>
								</ul>
							</td>
						</tr>
						'''
						for key, value in dict.items()
					)}
		</table>
	"""

	doc = f"""<!DOCTYPE html>
	<html lang="en">
		<head>
			{head}
		</head>
		<body>
			{body}
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
