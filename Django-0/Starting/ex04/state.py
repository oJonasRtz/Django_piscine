import sys;

def get_dictionaries() -> tuple[dict[str, str], dict[str, str]]:
	states = {
		"Oregon" : "OR",
		"Alabama" : "AL",
		"New Jersey": "NJ",
		"Colorado" : "CO"
	}
	capital_cities = {
		"OR": "Salem",
		"AL": "Montgomery",
		"NJ": "Trenton",
		"CO": "Denver"
	}

	return states, capital_cities;

def find_city(capital: str) -> str:
	if (not isinstance(capital, str)):
		return 'Unknown capital city';
	c = capital.strip();
	states, capitals = get_dictionaries();
	
	abb = next((a for a, city in capitals.items() if city == c), '');
	return next((state for state, ab in states.items() if ab == abb), 'Unknown capital city');


def main() -> None:
	if (len(sys.argv) != 2):
		return;

	city = sys.argv[1];
	capital = find_city(city);
	print(capital);

if __name__ == '__main__':
	main();
