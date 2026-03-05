
def get_dict()-> dict:
	d = {
		'Hendrix' : '1942',
		'Allman' : '1946',
		'King' : '1925',
		'Clapton' : '1945',
		'Johnson' : '1911',
		'Berry' : '1926',
		'Vaughan' : '1954',
		'Cooder' : '1947',
		'Page' : '1944',
		'Richards' : '1943',
		'Hammett' : '1962',
		'Cobain' : '1967',
		'Garcia' : '1942',
		'Beck' : '1944',
		'Santana' : '1947',
		'Ramone' : '1948',
		'White' : '1975',
		'Frusciante': '1970',
		'Thompson' : '1949',
		'Burton' : '1939',
		}
	
	sorted_d = sorted(d.items(), key=lambda item: (item[1], item[0]));
	return sorted_d

def print_dict(d: dict) -> None:
	for key, value in d:
		print(f"{key}");

def main() -> None:
	d = get_dict();
	print_dict(d);

	return;

if __name__ == '__main__':
	main();