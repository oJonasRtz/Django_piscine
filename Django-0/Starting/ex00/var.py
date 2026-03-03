
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

	for var in myVars:
		print(str(var) + ' has a type ' + str(type(var)));

if __name__ == "__main__":
	my_var()
