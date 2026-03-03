
def get_type(var) -> str:
	return 'has a type ' + str(type(var));

# *args is a variable length argument tuple list
def show_vars(*args) -> None:
	for (var) in args:
		print(str(var) + ' ' + get_type(var));

def my_var() -> None:

	myVars = (
		42,
		'42',
		'quarante-deux',
		42.0,
		True,
		[42],		#Works like an array, but can contain different types of data [42, 'banana', 3.14, False]
		{42: 42},	#Works like std::map, but can contain different types of data {42: 42, 'banana': 'yellow', 3.14: 'pi', False: 'false'}
		(42,),		#immutable list of data, can contain different types of data (42, 'banana', 3.14, False)
		set()		#A list with unique values {1, 2, 1} turns {1, 2}
	);

	# *myVars is used to unpack the tuple and pass each element as a separate argument to the function
	show_vars(*myVars);

if __name__ == "__main__":
	my_var()
