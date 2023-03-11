import sys


class BuilderType:
	GAME = {"builder_type": "cs", "lang": "Coming soon!"}
	JavaScript = {"builder_type": "Web application", "lang": "JavaScript"}


class Script:
	def __init__(self, script, lang):
		self.script = script
		self.lang = lang

	def make_var(self, var):
		rv = ""
		if not type(self.script["global_variables"][var]) == str:
			rv += f"\tvar crys_v_{var} = {self.script['global_variables'][var]};\n"
		else:
			rv += f"\tvar crys_v_{var} = \"{self.script['global_variables'][var]};\"\n"

		return rv

	def make_func(self, func):
		func_exec = self.script["functions"][func]
		if self.lang == BuilderType.JavaScript:
			rv = ""
			rv += f"\tfunction crys_f_{func} " + "{\n"
			for un_code in func_exec:
				code = ScriptHandler(self.lang).decode(un_code)
				rv += f"\t\t{code}\n"

			rv += "\t}\n\n"
			return rv
		else:
			Error().unknown_lang(self.lang)

	def make_check(self, check):
		rv = ""

		check_condition = self.script["checks"][check]["condition"]
		check_exec = self.script["checks"][check]["execute"]

		rv += ScriptHandler(self.lang).decode_condition(check_condition) + f"// {check}\n\n"

		for un_code in check_exec:
			code = ScriptHandler(self.lang).decode(un_code)
			rv += f"{code}"

		rv += "\t}\n\n"

		return rv

class ScriptHandler:
	def __init__(self, lang):
		self.lang = lang

	def decode_condition(self, text: list):
		rv = ""
		if type(text[0]) == str:
			cond_1 = f"crys_v_{text[0]}"
		else:
			cond_1 = text[0]

		if type(text[2]) == str:
			cond_2 = f"crys_v_{text[2]}"
		else:
			cond_2 = text[2]

		if text[1] == "is":
			if self.lang == BuilderType.JavaScript:
				try:
					rv += f"if {cond_1} === {cond_2} " + "{\n"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode_condition: {text}")
					Error().arg_missing("text", 2)
					return ""
			else:
				Error().unknown_lang(self.lang)
				return ""
		else:
			Error().unknown_cond(text[1])
			return ""

	def decode(self, text: list):
		rv = ""

		if text[0] == "scene":  # scene switch command
			if self.lang == BuilderType.JavaScript:
				try:
					rv += f"updateScene({text[1] - 1});"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 1)
					return ""
			else:
				Error().unknown_lang(self.lang)
				return ""

		elif text[0] == "add":  # add command (plus)
			if self.lang == BuilderType.JavaScript:
				try:
					rv += f"crys_v_{text[2]} = crys_v_{text[2]} + {text[1]};"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 2)
					return f""
			else:
				Error().unknown_lang(self.lang)
				return ""

		elif text[0] == "remove":  # remove command (minus)
			if self.lang == BuilderType.JavaScript:
				try:
					rv += f"crys_v_{text[2]} = crys_v_{text[2]} - {text[1]};"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 2)
					return f""
			else:
				Error().unknown_lang(self.lang)
				return ""

		elif text[0] == "function":  # function call
			if self.lang == BuilderType.JavaScript:
				try:
					rv += f"crys_f_{text[1]}();;"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 1)
					return f""
			else:
				Error().unknown_lang(self.lang)
				return ""
		else:
			Error().unknown_cmd(text)
			return ""


class Error:
	def __init__(self):
		pass

	def unknown_lang(self, lang):
		print(f"Error: Cannot handle builder language '{lang['lang']}'. Please report this issue on GitHub!")
		sys.exit(0)

	def arg_missing(self, arg_var: str, arg: int):
		print(f"Error: Make sure all arguments up to {arg_var}[{arg}] aren't missing (starting from 0).")
		sys.exit(0)

	def unknown_cmd(self, cmd):
		print(f"Error: Unknown command: {cmd}")
		sys.exit(0)

	def unknown_cond(self, condition):
		print(f"Error: Unknown condition: {condition}")
		sys.exit(0)
