import os
import shutil

from crys.script import *

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class Game:
	def __init__(self, game: dict, how: BuilderType, from_editor: bool = False,
				 replace_old_build: bool = False) -> None:
		self.game = game  # what game
		self.build_type = how  # how should it be exported?
		self.mem = game  # memory for all MemCheck(self.mem)
		self.from_editor = from_editor  # does the request come from the editor?
		self.replace_old_build = replace_old_build  # should we replace the old build?

		self.name = game["info"]["name"]  # game name
		self.authors = ", ".join(game["info"]["authors"])  # authors
		self.out = game["info"]["out"]
		self.scenes = game["scenes"]  # the scenes

		if self.from_editor is True:
			self.out = f"editor/{self.name}/" + self.out

		print("Initialized '" + game["info"]["name"] + "'")  # debug check

	def build(self):
		if self.build_type == {"builder_type": "cs"}:
			print("Sadly, this builder type isn't ready yet. Try another one!")
		elif self.build_type == BuilderType.JavaScript:
			print("Building game with " + BuilderType.JavaScript["builder_type"])
			if self.replace_old_build == Qt.CheckState.Checked:
				print("Trying to replace old build...")
				try:
					shutil.rmtree(self.out + "JavaScript/")
					print("Deleted old build")
				except FileNotFoundError:
					print("No old build found to delete!")
			returned_game = f"""
			<!DOCTYPE html>
<html lang="en">

<head>
  <meta name="description" content="Crystal Studio Game" />
  <meta charset="utf-8">
  <title>{self.name} - Crystal Studio</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="css/style.css">
</head>

<body>
	<center>
		<h1>{self.name} by {self.authors}</h1>
		<button onclick="window.location.replace('player.html')">Play</button><br/>
	</center>
</body>
			"""

			print("Creating file...")
			os.mkdir(self.out + "JavaScript/")
			folder = self.out + "JavaScript/"
			os.mkdir(folder + "css")
			css = open(folder + "css/style.css", "w")
			css.write("""
html {
	background-color: #252525ff;
	color: white;
	font-family: Arial;
}

button {
  background-color: #4CAF50; /* Green */
  border: none;
  color: white;
  padding: 15px 32px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  cursor: pointer;
}""")
			css.close()
			file = open(folder + "index.html", "w")

			file.write(returned_game)
			file.close()

			script = open(f"editor/{self.name}/script.json", "r")
			script = json.load(script)

			cs_vars = ""
			cs_funcs = ""
			cs_checks = ""
			cs_func_handler = ""
			for var in script["global_variables"]:  # variables
				cs_vars += Script(script, BuilderType.JavaScript, self.mem).make_var(var)

			for func in script["functions"]:  # functions
				cs_funcs += Script(script, BuilderType.JavaScript, self.mem).make_func(func)

			for check in script["checks"]:  # checks
				cs_checks += Script(script, BuilderType.JavaScript, self.mem).make_check(check)

			# function handler
			cs_func_handler += Script(script, BuilderType.JavaScript, self.mem).make_function_handler(
				MemCheck(self.mem).get_all_functions())

			# variables
			variables = []
			for var in script["global_variables"]:
				variables.append(var)

			variables_replace = []
			for i999 in range(len(script["global_variables"])):
				variables_replace.append(script["global_variables"][variables[i999]])

			player = open(folder + "player.html", "w")

			returned_player = f"""

<!DOCTYPE html>
<html lang="en">

<head>
  <meta name="description" content="Crystal Studio Game" />
  <meta charset="utf-8">
  <title>{self.name} - Crystal Studio</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="css/style.css">
</head>

<body>
	<center>
		<h1 id="title">PLAYER</h1>
		<div id="buttons">

        </div>
	</center>
</body>

<script>
  // CrystalScript global variables
{cs_vars}
  
  // CrystalScript functions
{cs_funcs}

  // CrystalStudio init game
  var game = {str(self.scenes).replace("'", '"')}
  var game_running = true
  var current_scene = 0
  
  
  // CrystalScript checks
  crys_manager_checker = setInterval(function ()
"""
			returned_player += " {\n"
			returned_player += cs_checks + "\n}, 200)\n\n\n"
			returned_player += "crys_internal_updater = setInterval(function () {\n"
			returned_player += f"\tgame = game\nupdateScene(current_scene)\n"
			returned_player += "}, 500)\n\n\n"
			returned_player += f"""
			// CrystalScript Handlers
			{cs_func_handler}
			"""
			returned_player += """
  function setText(id, text) {
    document.getElementById(id).innerHTML = text;
  }

  function updateScene(scene, coming_from_button = null) {
    if (coming_from_button === null) {
	  current_scene = scene;
      setText("title", game[scene]["title"])
	  clearDiv("buttons")
	  for (let i2 = 0; i2 < game[current_scene]["buttons"].length;) {
	    if (game[current_scene]["buttons"][i2][0] === 1) {
        createInput(game[current_scene]["buttons"][i2][1], game[current_scene]["buttons"][i2][2], i2)
      } else {
        createButton(game[current_scene]["buttons"][i2][0], game[current_scene]["buttons"][i2][1], i2)
      }
	    i2++;
	  }
      createMainMenuButton("Back to main menu")
    } else if (game[current_scene]["buttons"][coming_from_button][1] === "script") {
      handleCrystalFunction(game[current_scene]["buttons"][coming_from_button][2], coming_from_button);
    } else if (coming_from_button !== null) {
      if (game[current_scene]["buttons"][coming_from_button][1] !== "script") {
        current_scene = scene;
        setText("title", game[scene]["title"])
        clearDiv("buttons")
	    for (let i2 = 0; i2 < game[current_scene]["buttons"].length;) {
		  createButton(game[current_scene]["buttons"][i2][0], game[current_scene]["buttons"][i2][1], i2)
		  i2++;
	    }

        createMainMenuButton("Back to main menu")
      }
    }
  }


  function clearDiv(id) {
    var div = document.getElementById(id);
    while (div.firstChild) {
      div.removeChild(div.firstChild);
    }
  }

  function createButton(name, next_scene, coming_from_button) {
    var btn = document.createElement("button")
    btn.innerHTML = name
    btn.onclick = function () {
      next_scene--;
      updateScene(next_scene, coming_from_button);
    };

    document.getElementById("buttons").appendChild(btn)
    btn = null

    var br = document.createElement("br")
    document.getElementById("buttons").appendChild(br)
    br = null

    var br = document.createElement("br")
    document.getElementById("buttons").appendChild(br)
    br = null
  }

  function createMainMenuButton(name) {
    var btn = document.createElement("button")
    btn.innerHTML = name
    btn.onclick = function () {
      window.location.replace("index.html");
    }

    document.getElementById("buttons").appendChild(btn)
    btn = null
  }

  function createInput(label, default_vaulue, id) {
    var lab = document.createElement("label")
    lab.innerHTML = label

    document.getElementById("buttons").appendChild(lab)
    lab = null

    var inp = document.createElement("input")
    inp.value = default_vaulue
    inp.addEventListener('click', function() {
      var new_value = prompt("Enter new value");
      // alert(game[current_scene]["buttons"][id][2])
      while (game[current_scene]["buttons"][id][2] !== new_value) {
        game[current_scene]["buttons"][id][2] = new_value
      }
      // alert(game[current_scene]["buttons"][id][2])
      new_value = null
    })
    document.getElementById("buttons").appendChild(inp)

    var br = document.createElement("br")
    document.getElementById("buttons").appendChild(br)
    br = null

    var br = document.createElement("br")
    document.getElementById("buttons").appendChild(br)
    br = null
  }

  function createMainMenuButton(name) {
    var btn = document.createElement("button")
    btn.innerHTML = name
    btn.onclick = function () {
      window.location.replace("index.html");
    }

    document.getElementById("buttons").appendChild(btn)
    btn = null
  }


  updateScene(0)
</script>
			"""

			for i998 in range(len(variables)):
				returned_player = str(returned_player).replace(
					ScriptValues.VARIABLE_START + variables[i998] + ScriptValues.VARIABLE_END,
					f"\" + crys_v_{variables[i998]} + \"")

			player.write(returned_player)
			player.close()

			if ScriptValues.in_an_if != 0:
				print("Error: Exported game may not work, because not all ifs, loops and/or whiles are 'end'ed!")

			print("Finished")
