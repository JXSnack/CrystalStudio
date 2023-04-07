import json
import string
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
	def __init__(self, script, lang, mem):
		self.script = script
		self.lang = lang
		self.mem = mem

	def make_function_handler(self, functions: list):
		rv = ""
		if self.lang == BuilderType.JavaScript:
			rv += "function handleCrystalFunction(function_name, coming_from_button = null) {\n"

			if functions != []:
				func2 = functions[0]
				rv += f"\t\t\t\tif (function_name === \"{func2}\") " + "{\n"
				rv += f"\t\t\t\t\tif (coming_from_button === null) " + "{ " + f"crys_f_{func2}();" + " \n} else {\n" + f"crys_f_{func2}("
				num = 0
				for arg in self.script["functions"][functions[0]]["args"]:
					rv += f"game[current_scene][\"buttons\"][coming_from_button][3][{num}], "
					num += 1

				rv = rv[:-1]
				rv = rv[:-1]
				rv += ")"

				rv += "\t\t\t\t} }"
				functions.pop(0)
			else:
				rv += "// No functions\n"

			for func in functions:
				rv += f"\t\t\t\telse if (function_name === \"{func}\") " + "{\n"
				rv += f"\t\t\t\t\tif (coming_from_button === null) " + "{ " + f"crys_f_{func}();" + " \n} else {\n" + f"crys_f_{func}("
				num = 0
				for arg in self.script["functions"][functions[0]]["args"]:
					rv += f"game[current_scene][\"buttons\"][coming_from_button][3][{num}], "
					num += 1

				rv += ")"

				rv += "\t\t\t\t} }"

			if functions != []:
				rv += "else { alert(\"ERROR: Cannot 'handleCrystalFunction': \" + function_name + \". Please contact the creator of this game and report this issue on the CrystalStudio GitHub page (github.com/JXSnack/CrystalStudio/issues)\"); \n\t\t\t\t}\n\t\t\t}\n"

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
		func_exec = self.script["functions"][func]["execute"]
		args = []
		for arg in self.script["functions"][func]["args"]:
			args.append(arg)

		args_formatted = ""

		for un_arg in args:
			if type(self.script['functions'][func]['args'][un_arg]) != str:
				args_formatted += f"crys_f_arg_{un_arg} = {self.script['functions'][func]['args'][un_arg]}, "
			else:
				args_formatted += f"crys_f_arg_{un_arg} = \"{self.script['functions'][func]['args'][un_arg]}\", "

		args_formatted = args_formatted[:-1]
		args_formatted = args_formatted[:-1]

		if self.lang == BuilderType.JavaScript:
			rv = ""
			rv += f"\tfunction crys_f_{func}({args_formatted}) " + "{\n"
			for un_code in func_exec:
				code = ScriptHandler(self.lang, self.mem).decode(un_code)
				for arg2 in args:
					code = code.replace("{" + f"arg:{arg2}" + "}", f"\" + crys_f_arg_{arg2} + \"")
				rv += f"\t\t{code}\n"

			rv += "\t}\n\n"
			return rv
		else:
			Error().unknown_lang(self.lang)

	def make_check(self, check):
		rv = ""

		check_condition = self.script["checks"][check]["condition"]
		check_exec = self.script["checks"][check]["execute"]

		rv += ScriptHandler(self.lang, self.mem).decode_condition(check_condition) + f"// {check}\n"

		for un_code in check_exec:
			code = ScriptHandler(self.lang, self.mem).decode(un_code)
			rv += f"{code}"

		rv += "\t}\n\n"

		return rv


class ScriptHandler:
	def __init__(self, lang, mem):
		self.lang = lang
		self.mem = mem

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
						go_to = f"crys_v_{text[1]}".replace("\"", "").replace(" + ", "")
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

		elif text[0] == "debugtools":  # debug tools
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
					if type(text[2]) == str and text[2][0] in string.ascii_uppercase:
						num2 = f"crys_f_arg_{text[2]}"
					elif type(text[2]) == str:
						num2 = f"crys_v_{text[2]}"
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
		elif text[0] == "set": # set command
			if self.lang == BuilderType.JavaScript:
				try:
					if type(text[2]) == str:
						rv += f"crys_v_{text[1]} = \"{text[2]}\""
					else:
						rv += f"crys_v_{text[1]} = {str(text[2])}"

					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 2)
					return f""
			else:
				print(f"ScriptHandler cannot decode: {text}")
				Error().unknown_lang(self.lang)
				return ""

		elif text[0] == "remove":  # remove command (minus)
			if self.lang == BuilderType.JavaScript:
				try:
					if type(text[2]) == str and text[2][0] in string.ascii_uppercase:
						num2 = f"crys_f_arg_{text[2]}"
					elif type(text[2]) == str:
						num2 = f"crys_v_{text[2]}"
					else:
						num2 = text[2]

					if type(text[1]) != str:
						print(f"Error at {text}")
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
					if type(text[2]) == str and text[2][0] in string.ascii_uppercase:
						num2 = f"crys_f_arg_{text[2]}"
					elif type(text[2]) == str:
						num2 = f"crys_v_{text[2]}"
					else:
						num2 = text[2]

					if type(text[1]) != str:
						print(f"Error at {text}")
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
					if type(text[2]) == str and text[2][0] in string.ascii_uppercase:
						num2 = f"crys_f_arg_{text[2]}"
					elif type(text[2]) == str:
						num2 = f"crys_v_{text[2]}"
					else:
						num2 = text[2]

					if type(text[1]) != str:
						print(f"Error at {text}")
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
					try:
						args = ", ".join(text[2])
						rv += f"crys_f_{text[1]}({args});"
					except IndexError:
						rv += f"crys_f_{text[1]}();"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 1)
					return f""
			else:
				Error().unknown_lang(self.lang)
				return ""
		elif text[0] == "if":  # if condition
			if self.lang == BuilderType.JavaScript:
				try:
					rv += ScriptHandler(self.lang, self.mem).decode_condition(text)
					ScriptValues.in_an_if = ScriptValues.in_an_if + 1
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 3)
					return ""
			else:
				Error().unknown_lang(self.lang)
				return ""
		elif text[0] in ["elif", "else if"]:  # else if statement
			if self.lang == BuilderType.JavaScript:
				try:
					if ScriptValues.in_an_if != 0:
						rv += ScriptHandler(self.lang, self.mem).decode_condition(text)
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
		elif text[0] in ["else"]:  # else statement
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
		elif text[0] == "end":  # end if, else, loop, etc
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
		elif text[0] == "log":  # log function
			if self.lang == BuilderType.JavaScript:
				try:
					rv += f"console.log(\"{text[1]}\")"
					return rv
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 1)
					return ""
			else:
				Error().unknown_lang(self.lang)
				return ""
		elif text[0] == "get": # get command
			"""["get", <scene>, <element-id>, "<get something>", "<save-as>"]"""
			if self.lang == BuilderType.JavaScript:
				try:
					if type(text[1]) == int: # scene
						scene_id = int(text[1])
						if len(self.mem["scenes"]) >= scene_id: # check if the scene could even exist
							if type(text[2] == int): # element
								element_id = int(text[2])
								if len(self.mem["scenes"][scene_id]["buttons"]) >= element_id: # check if the element could even exist
									element = self.mem["scenes"][scene_id]["buttons"][element_id]
									element_type = element[0]
									if type(element_type) == str: # if element type is button
										if text[3] == "text":
											rv += f"game[{scene_id}][\"buttons\"][{element_id}][0]"
										elif text[3] == "link":
											rv +=  f"game[{scene_id}][\"buttons\"][{element_id}][1]"
										else:
											print(f"ScriptHandler cannot decode: {text}")
											Error().has_to_be("'text' or 'link'", text[3])
									elif int(element_type) == 1: # if element type is input field
										if text[3] == "label":
											rv += f"game[{scene_id}][\"buttons\"][{element_id}][1]"
										elif text[3] == "value":
											rv += f"game[{scene_id}][\"buttons\"][{element_id}][2]"
										else:
											print(f"ScriptHandler cannot decode: {text}")
											Error().has_to_be("'label' or 'value'", text[3])
									else:
										print(f"ScriptHandler cannot decode: {text}")
										Error().unknown_element_type(element_type, f"'{text}'")

									rv = f"crys_v_{text[4]} = {rv};"

									return rv
								else:
									print(f"ScriptHandler cannot decode: {text}")
									Error().unknown_element_id(element_id)
							elif text[2] == "title":  # if element type is text
								if text[3] == "text":
									rv += f"game[{scene_id}][\"title\"] = \"{text}\""
								else:
									Error().has_to_be("'text'", text[3])
							else:
								print(f"ScriptHandler cannot decode: {text}")
								Error().has_to_be(int, type(text[2]))
						else:
							print(f"ScriptHandler cannot decode: {text}")
							Error().unknown_scene_id(scene_id)
					else:
						print(f"ScriptHandler cannot decode: {text}")
						Error().has_to_be(int, type(text[1]))
				except IndexError:
					print(f"ScriptHandler cannot decode: {text}")
					Error().arg_missing("text", 4)
			else:
				print(f"ScriptHandler cannot decode: {text}")
				Error().unknown_lang(self.lang)
				return ""

		elif text[0] == "change":
			"""["change", <scene>, <element>, "<change something>", "<new value>"]"""
			try:
				if self.lang == BuilderType.JavaScript:
					if type(text[1]) == int:  # scene
						scene_id = int(text[1])
						if len(self.mem["scenes"]) >= scene_id:  # check if the scene could even exist
							if text[2] == "title": # element
								if text[3] == "text":
									rv += f"game[{scene_id}][\"title\"] = \"{text[4]}\""
									return rv
								else:
									print(f"ScriptHandler cannot decode: {text}")
									Error().has_to_be("'text'", text[3])
									return ""
							elif type(text[2] == int):  # element
								element_id = int(text[2])
								if len(self.mem["scenes"][scene_id][
										   "buttons"]) >= element_id:  # check if the element could even exist
									element = self.mem["scenes"][scene_id]["buttons"][element_id]
									element_type = element[0]

									if type(element_type) == str:
										if text[3] == "link":
											rv += f"game[{scene_id}][{element_id}][1] = {text[4]}"
											return rv
										elif text[3] == "text":
											rv += f"game[{scene_id}][{element_id}][0] = \"{text[4]}\""
											return rv
										else:
											print(f"ScriptHandler cannot decode: {text}")
											Error().has_to_be("'link' or 'text'", text[3])
											return ""
									elif element_type == 1:
										if text[3] == "label":
											rv += f"game[{scene_id}][\"buttons\"][{element_id}][1] = \"{text[4]}\""
											return rv
										elif text[3] == "value":
											rv += f"game[{scene_id}][\"buttons\"][{element_id}][2] = \"{text[4]}\""
											return rv
										else:
											print(f"ScriptHandler cannot decode: {text}")
											Error().has_to_be("'label' or 'value'", text[3])
									else:
										Error().unknown_element_type(element_type, f"'{text}'")
								else:
									Error().unknown_element_id(element_id)
							else:
								Error().has_to_be(int, type(text[2]))
						else:
							Error().unknown_scene_id(scene_id)
					else:
						Error().has_to_be(int, type(text[1]))
				else:
					Error().unknown_lang(self.lang)
			except IndexError:
				Error().arg_missing("text", 4)


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

	def unknown_element_type(self, type_, while_trying_to):
		print(f"Error: Unknown element type: {type_}. Error occurred while trying to {while_trying_to}.\n\nPlease report this issue on GitHub!")
		sys.exit(0)

	def unknown_element_id(self, id_):
		print(f"Error: Unknown element id: {id_}. Check if that element actually exists!")
		sys.exit(0)

	def unknown_scene_id(self, id_):
		print(f"Error: Unknown scene id: {id_}. Check if that scene actually exists!")
