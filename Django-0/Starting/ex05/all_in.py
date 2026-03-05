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
		return None;
	c = capital.strip();
	states, capitals = get_dictionaries();
	
	abb, arg = next(((a, city) for a, city in capitals.items() if city.lower() == c.lower()), (None, None));
	if abb is None:
		return None;
	res = next((state for state, ab in states.items() if ab.lower() == abb.lower()), None);
	if res is None:
		return None;
	
	return res, arg;

def find_capital(state: str) -> str:
	if not isinstance(state, str):
		return None;
	s = state.strip();
	states, capitals = get_dictionaries();
	key, arg = next(((ab, name) for name, ab in states.items() if name.lower() == s.lower()), (None, None));
	if key is None:
		return None;
	res = capitals.get(key, None);
	if res is None:
		return None;
	return res, arg;


def main() -> None:
	if len(sys.argv) != 2:
		return;
	
	#Parsing args
	args = [arg.strip() for arg in sys.argv[1].split(',')];
	outputs = {
		'capital': lambda capital: print(f'{capital[0]} is the capital of {capital[1]}'),
		'city': lambda city: print(f'{city[1]} is the capital of {city[0]}'),
		'unknown': lambda arg: print(f'{arg} is neither a capital city nor a state')
	};

	for arg in args:
		if not arg:
			continue;
		
		capital = find_capital(arg);
		city = find_city(arg);

		key = 'capital' if capital else 'city' if city else 'unknown';
		value = capital or city or arg;

		outputs[key](value);

if __name__ == '__main__':
	main();
