import json
import sys


class BuilderType:
	GAME = {"builder_type": "cs", "lang": "Coming soon!"}
	JavaScript = {"builder_type": "Web application", "lang": "JavaScript2"}


class ScriptValues:
	VARIABLE_START = "{@"
	VARIABLE_END = "}"

	in_an_if = 0


class MemCheck:
	def __init__(self, mem: dict):
		self.script = json.load(open(f"editor/{mem['info']['name']}/script.json", "r"))

	def get_all_functions(self):
		rv = []
		for func in self.script["functions"]:
			rv.append(func)

		return rv


class Script:
	def __init__(self, script, lang):
		self.script = script
		self.lang = lang

	def make_function_handler(self, functions: list):
		rv = ""
		if self.lang == BuilderType.JavaScript:
			rv += "function handleCrystalFunction(function_name) {\n"

			if functions != []:
				func2 = functions[0]
				rv += f"\t\t\t\tif (function_name === \"{func2}\") " + "{\n"
				rv += f"\t\t\t\t\tcrys_f_{func2}();\n"
				rv += "\t\t\t\t} "
				functions.pop(0)
			else:
				rv += "// No functions\n"

			for func in functions:
				rv += f"else if (function_name === \"{func}\") " + "{\n"
				rv += f"\t\t\t\t\tcrys_f_{func}();\n"
				rv += "\t\t\t\t} "

			if functions != []:
				rv += "else { alert(\"ERROR: Cannot 'handleCrystalFunction': \" + function_name + \". Please contact the creator of this game and report this issue on the CrystalStudio GitHub page (github.com/JXSnack/CrystalStudio/issues)\"); \n\t\t\t\t}\n\t\t\t}\n"

			rv += "}" # IMPORTANT
			return rv
		else:
			Error().unknown_lang(self.lang)
			return ""

	def make_var(self, var):
		rv = ""
		if not type(self.script["global_variables"][var]) == str:
			rv += f"\tvar crys_v_{var} = {self.script['global_variables'][var]};\n"
		else:
			rv += f"\tvar crys_v_{var} = \"{self.script['global_variables'][var]}\";\n"

		return rv

	def make_func(self, func):
		func_exec = self.script["functions"][func]
		if self.lang == BuilderType.JavaScript:
			rv = ""
			rv += f"\tfunction crys_f_{func}() " + "{\n"
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

		rv += ScriptHandler(self.lang).decode_condition(check_condition) + f"// {check}\n"

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

		if text[0] == "if":
			add_to_text = 1
		elif text[0] == "elif":
			add_to_text = 1
		else:
			add_to_text = 0

		if type(text[0 + add_to_text]) == str and text[0 + add_to_text].startswith("v:"):
			cond_1 = f"crys_v_{text[0 + add_to_text].replace('v:', '', 1)}"
		elif type(text[2 + add_to_text]) == str:
			cond_1 = f"\"{text[0 + add_to_text]}\""
		else:
			cond_1 = text[2 + add_to_text]

		if type(text[2 + add_to_text]) == str and text[2 + add_to_text].startswith("v:"):
			cond_2 = f"crys_v_{text[2 + add_to_text].replace('v:', '', 1)}"
		elif type(text[2 + add_to_text]) == str:
			cond_2 = f"\"{text[2 + add_to_text]}\""
		else:
			cond_2 = text[2 + add_to_text]

		if text[1 + add_to_text] in ["is", "=="]:
			if self.lang == BuilderType.JavaScript:
				try:
					if text[0] == "elif":
						rv += "}" + f" else if ({cond_1} === {cond_2}) " + "{\n"
						return rv
					else:
						rv += f"if ({cond_1} === {cond_2}) " + "{\n"
						return rv
				except IndexError:
					print(f"ScriptHandler cannot decode_condition: {text}")
					Error().arg_missing("text", 2)
					return ""
			else:
				Error().unknown_lang(self.lang)
				return ""
		elif text[1 + add_to_text] in ["is not", "not", "!="]:
			if self.lang == BuilderType.JavaScript:
				try:
					rv += f"if ({cond_1} !== {cond_2}) " + "{\n"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode_condition: {text}")
					Error().arg_missing("text", 2)
					return ""
			else:
				Error().unknown_lang(self.lang)
				return ""
		elif text[1 + add_to_text] in ["greater than", ">"]:
			if self.lang == BuilderType.JavaScript:
				try:
					rv += f"if ({cond_1} > {cond_2}) " + "{\n"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode_condition: {text}")
					Error().arg_missing("text", 2)
					return ""
			else:
				Error().unknown_lang(self.lang)
				return ""
		elif text[1 + add_to_text] in ["less than", "<"]:
			if self.lang == BuilderType.JavaScript:
				try:
					rv += f"if ({cond_1} < {cond_2}) " + "{\n"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode_condition: {text}")
					Error().arg_missing("text", 2)
					return ""
			else:
				Error().unknown_lang(self.lang)
				return ""
		elif text[1 + add_to_text] in ["greater or equal to", ">="]:
			if self.lang == BuilderType.JavaScript:
				try:
					rv += f"if ({cond_1} >= {cond_2}) " + "{\n"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode_condition: {text}")
					Error().arg_missing("text", 2)
					return ""
			else:
				Error().unknown_lang(self.lang)
				return ""
		elif text[1 + add_to_text] in ["less or equal to", "<="]:
			if self.lang == BuilderType.JavaScript:
				try:
					rv += f"if ({cond_1} <= {cond_2}) " + "{\n"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode_condition: {text}")
					Error().arg_missing("text", 2)
					return ""
			else:
				Error().unknown_lang(self.lang)
				return ""
		else:
			Error().unknown_cond(text[1 + add_to_text])
			return ""

	def decode(self, text: list):
		rv = ""

		if text[0] == "scene":  # scene switch command
			if self.lang == BuilderType.JavaScript:
				try:
					if type(text[1]) == str:
						go_to = f"crys_v_{text[1]}"
						rv += f"updateScene({go_to} - 1);"
					else:
						go_to = text[1]
						rv += f"updateScene({go_to - 1});"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 1)
					return ""
			else:
				Error().unknown_lang(self.lang)
				return ""

		elif text[0] == "debugtools": # debug tools
			if self.lang == BuilderType.JavaScript:
				if text[1] == "alert var":
					rv = f"alert(crys_v_{text[2]});"
					return rv
				elif text[1] == "alert":
					rv = f"alert(\"{text[2]}\");"
					return rv

		elif text[0] == "add":  # add command (plus)
			if self.lang == BuilderType.JavaScript:
				try:
					if type(text[2]) == str:
						num2 = f"crys_v_{text[1]}"
					else:
						num2 = text[2]

					if type(text[1]) != str:
						print(f"Error at {text}")
						Error().has_to_be(str, type(text[1]))

					rv += f"crys_v_{text[1]} = crys_v_{text[1]} + {num2};"
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
					if type(text[2]) == str:
						num2 = f"crys_v_{text[1]}"
					else:
						num2 = text[2]

					if type(text[1]) != str:
						Error().has_to_be(str, type(text[1]))

					rv += f"crys_v_{text[1]} = crys_v_{text[1]} - {num2};"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 2)
					return f""
			else:
				Error().unknown_lang(self.lang)
				return ""

		elif text[0] == "multiply":  # multiply command
			if self.lang == BuilderType.JavaScript:
				try:
					if type(text[2]) == str:
						num2 = f"crys_v_{text[1]}"
					else:
						num2 = text[2]

					if type(text[1]) != str:
						Error().has_to_be(str, type(text[1]))

					rv += f"crys_v_{text[1]} = crys_v_{text[1]} * {num2};"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 2)
					return f""
			else:
				Error().unknown_lang(self.lang)
				return ""

		elif text[0] == "divide":  # divide command
			if self.lang == BuilderType.JavaScript:
				try:
					if type(text[2]) == str:
						num2 = f"crys_v_{text[1]}"
					else:
						num2 = text[2]

					if type(text[1]) != str:
						Error().has_to_be(str, type(text[1]))

					rv += f"crys_v_{text[1]} = crys_v_{text[1]} / {num2};"
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
					rv += f"crys_f_{text[1]}();"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 1)
					return f""
			else:
				Error().unknown_lang(self.lang)
				return ""
		elif text[0] == "if": # if condition
			if self.lang == BuilderType.JavaScript:
				try:
					rv += ScriptHandler(self.lang).decode_condition(text)
					ScriptValues.in_an_if = ScriptValues.in_an_if + 1
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 3)
					return ""
			else:
				Error().unknown_lang(self.lang)
				return ""
		elif text[0] in ["elif", "else if"]: # else if statement
			if self.lang == BuilderType.JavaScript:
				try:
					if ScriptValues.in_an_if != 0:
						rv += ScriptHandler(self.lang).decode_condition(text)
						return rv
					else:
						print("Error: Cannot 'elif' when no if has started")
						return ""
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 3)
					return ""
			else:
				Error().unknown_lang(self.lang)
				return ""
		elif text[0] in ["else"]: # else statement
			if self.lang == BuilderType.JavaScript:
				try:
					if ScriptValues.in_an_if != 0:
						rv += "} else {\n"
						return rv
					else:
						print("Error: Cannot 'else' when no if has started")
						return ""
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 0)
			else:
				Error().unknown_lang(self.lang)
		elif text[0] == "end": # end if, else, loop, etc
			if self.lang == BuilderType.JavaScript:
				try:
					if ScriptValues.in_an_if > 0:
						rv += "}"
						ScriptValues.in_an_if = ScriptValues.in_an_if - 1
						return rv
					else:
						print("Error: Cannot 'end' if there is no if, loop or while")
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 0)
					return ""
			else:
				Error().unknown_lang(self.lang)
				return ""

		else:
			Error().unknown_cmd(text)
			return ""


class Error:
	def __init__(self):
		pass

	def has_to_be(self, has, is_):
		print(f"Error: One of the arguments has to be {has} and not {is_}!")
		sys.exit(0)

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
