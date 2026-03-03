
#'with' manages the opening e closing, preventing memory leaks
#'strip()' === 'trim()' in other languages, removes leading and trailing whitespace

def print_line(line: str) -> None:
	val = line.split(',');
	for n in val:
		print(n.strip());

def	readNumbers(fileName: str) -> None:
	with open(fileName, 'r') as file:
		for line in file:
			print_line(line);

def main() -> None:
	try:
		readNumbers('numbers.txt');
	except Exception as e:
		print(f"An error occurred: {e}");

if __name__ == '__main__':
	main();
