
#'with' manages the opening e closing, preventing memory leaks
#'strip()' === 'trim()' in other languages, removes leading and trailing whitespace

def main() -> None:
	
	with open('numbers.txt', 'r') as file:
		for line in file:
			numbersList = line.split(',');
			for n in numbersList:
				print(n.strip());

if __name__ == '__main__':
	main();
