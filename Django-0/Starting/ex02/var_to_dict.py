
def list_to_dict(l: list) -> dict:
	#key[year] : value[name]
	myDict = {};
	for name, year in l:
		if year in myDict:
			myDict.update({year: myDict[year] + ' ' + name});
		else:	
			myDict.update({year: name});

	return myDict;

def print_dict(d: dict) -> None:
	for key, value in d.items():
		print(f"{key} : {value}");

def main() -> None:
	d = [
		('Hendrix' , '1942'),
		('Allman' , '1946'),
		('King' , '1925'),
		('Clapton' , '1945'),
		('Johnson' , '1911'),
		('Berry' , '1926'),
		('Vaughan' , '1954'),
		('Cooder' , '1947'),
		('Page' , '1944'),
		('Richards' , '1943'),
		('Hammett' , '1962'),
		('Cobain' , '1967'),
		('Garcia' , '1942'),
		('Beck' , '1944'),
		('Santana' , '1947'),
		('Ramone' , '1948'),
		('White' , '1975'),
		('Frusciante', '1970'),
		('Thompson' , '1949'),
		('Burton' , '1939')
	];

	myDict = list_to_dict(d);
	print_dict(myDict);

if __name__ == '__main__':
	main();
