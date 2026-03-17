import sys, os, re
import settings

def write_file(filename, content) -> bool:
    try:
        with open(filename, 'w') as file:
            file.write(content)
            return 1
    except Exception:
       return 0

def read_file(filename):
    try:
        with open(filename, 'r') as file:
           return file.read()
    except Exception:
        message(f"Failed to read {highlight(filename)}.", "error")
        sys.exit(1)

def render_template(template):
	if not isinstance(template, str):
		return None
	
	#@Create a context dictionary from settings, excluding private attributes
	context = {
		k: v
		for k, v in vars(settings).items()
		if not k.startswith('__')
	}

	def replace_variable(match):
		#group(0) == {name} | group(1) == name
		key = match.group(1)
		#return the context[key] or {name} by default if key is not found
		value = context.get(key, match.group(0))

		if isinstance(value, list):
			return ', '.join(map(str, value))

		return str(value)
  
	return re.sub(r'{\s*(\w+)\s*}', replace_variable, template)

    
def is_valid_file(filename) -> bool:
    if not isinstance(filename,str):
        return 0
    
    check = os.path.exists(filename) and os.path.isfile(filename)
    name, ext = os.path.splitext(filename)
    
    if not check or ext != ".template":
       return 0

    return 1

def highlight(text: str) -> str:
    colors = {
		"file": "\033[34m",
		"reset": "\033[0m"
	}
    return f"{colors['file']}{text}{colors['reset']}"

def message(msg, _type="info") -> None:
    colors = {
		"error": "\033[31m",
		"success": "\033[32m",
		"warning": "\033[33m",
		"info": "\033[34m",
		"reset": "\033[0m"
	}
    labels = {
		"error": f"{colors['error']}[Error]{colors['reset']}",
		"success": f"{colors['success']}[Success]{colors['reset']}",
		"warning": f"{colors['warning']}[Warning]{colors['reset']}",
		"info": f"{colors['info']}[Info]{colors['reset']}",
	}
    print(f"{labels.get(_type, labels['info'])} {msg}")

def main() -> None:
    if len(sys.argv) != 2:
        message(f"Usage: python3 {highlight(sys.argv[0])} <template_file>", "warning")
        return

    #check extension
    arg = sys.argv[1]
    if not is_valid_file(arg):
        message(f"{highlight(arg)} is not supported or does not exist.", "error")
        return
    
	#Execute the program
    template = read_file(arg)
    rendered_string = render_template(template)
    if rendered_string is not None:
        name = arg.split('.')[0]
        if not write_file(f"{name}.html", rendered_string):
            message(f"Failed to create {highlight(f'{name}.html')}.", "error")
        else:
        	message(f"{highlight(f'{name}.html')} has been created successfully.", "success")

if __name__ == "__main__":
    main()
    