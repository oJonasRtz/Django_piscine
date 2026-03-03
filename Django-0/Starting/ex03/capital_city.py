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

def find_capital(state: str) -> str:
	if not isinstance(state, str):
		return 'Unknown state';
	s = state.strip();
	states, capitals = get_dictionaries();
	return capitals.get(states.get(s, ''), 'Unknown state');

def main() -> None:
	if (len(sys.argv) != 2):
		return;

	state = sys.argv[1];
	capital = find_capital(state);
	print(capital);

if __name__ == '__main__':
	main();
