import os


class BuilderType:
	GAME = {"builder_type": "cs"}
	PYTHON = {"builder_type": "Python"}
	HTML = {"builder_type": "HTML"}
	HTMLPlus = {"builder_type": "HTML Plus"}
	RAWQT = {"builder_type": "cs"}


class Game:
	def __init__(self, game: dict, how: BuilderType, from_editor: bool = False) -> None:
		self.game = game  # what game
		self.build_type = how  # how should it be exported?
		self.from_editor = from_editor # does the request come from the editor?

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

		elif self.build_type == BuilderType.PYTHON:  # if the builder type is python export
			print("Building game with " + BuilderType.PYTHON["builder_type"])
			returned_game = f"""

import time
import sys

print("Made with CrystalStudio")
print("Game: {self.name}")
print("Written by: {self.authors}")

game = {self.scenes}
game_running = True
current_scene = 0
next_scene = None

time.sleep(3)

for i in range(20):
	print("")

while game_running:
	print(game[current_scene]["title"])
	num = 1
	buttons = game[current_scene]["buttons"]
	for i in buttons:
		print(str(num) + ". " + i[0])
		num+=1
	print("exit. Exit the game")

	action = input("> ")

	try:
		int(action)
		yes_it_is_int = True
	except ValueError:
		yes_it_is_int = False

	if action == "exit":
		game_running = False
	elif yes_it_is_int:
		try:
			next_scene = int(action)
			next_scene-=1
			next_scene = buttons[next_scene][1]
			next_scene-=1
			current_scene = next_scene
			next_scene = None
			yes_it_is_int = None
			continue
		except IndexError:
			print("That's not a valid button!")
	else:
		print("Unknown command, '" + action + "'")
		continue

			"""

			print("Creating file...")
			file = open(self.out + "game.py", "w")

			file.write(returned_game)
			file.close()
			print("Finished!")
		elif self.build_type == BuilderType.HTML:  # if the builder type is html export
			print("Building game with " + BuilderType.HTML["builder_type"])
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
		<button onclick="window.location.replace('1.html')">Play</button><br/>
	</center>
</body>
			"""

			print("Creating file...")
			os.mkdir(self.out + "HTML/")
			folder = self.out + "HTML/"
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
}
			""")
			css.close()
			file = open(folder + "index.html", "w")

			file.write(returned_game)
			file.close()

			num = 0
			for i in self.scenes:
				scene_file = open(folder + f"{num + 1}.html", "w")

				buttons = i['buttons']
				btn_text = ""
				for i2 in buttons:
					btn_text += f"<button onclick=\"window.location.replace('{i2[1]}.html')\">{i2[0]}</button><br/><br/>\n"

				btn_text += f"<button onclick=\"window.location.replace('index.html')\">Back to main menu</button>\n"

				scene_file.write(f"""
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
		<h1>{i["title"]}</h1>
		{btn_text}
	</center>
</body>
""")
				scene_file.close()
				num+=1
		elif self.build_type == BuilderType.HTMLPlus:
			print("Building game with " + BuilderType.HTMLPlus["builder_type"])
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
			os.mkdir(self.out + "HTMLPlus/")
			folder = self.out + "HTMLPlus/"
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
  var game = {str(self.scenes).replace("(", "[").replace(")", "]")}
  var game_running = true
  var current_scene = 0
"""
			returned_player += """
  function setText(id, text) {
    document.getElementById(id).innerHTML = text;
  }

  function updateScene(scene) {
    current_scene = scene;
    setText("title", game[scene]["title"])
    clearDiv("buttons")

    for (let i2 = 0; i2 < game[current_scene]["buttons"].length;) {
      createButton(game[current_scene]["buttons"][i2][0], game[current_scene]["buttons"][i2][1])
      i2++;
    }

    createMainMenuButton("Back to main menu")
  }

  function clearDiv(id) {
    var div = document.getElementById(id);
    while (div.firstChild) {
      div.removeChild(div.firstChild);
    }
  }

  function createButton(name, next_scene) {
    var btn = document.createElement("button")
    btn.innerHTML = name
    btn.onclick = function () {
      next_scene--;
      updateScene(next_scene);
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


  updateScene(0)
</script>
			"""

			player.write(returned_player)
			player.close()

			print("Finished")

