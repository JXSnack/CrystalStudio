import os


class BuilderType:
	GAME = {"builder_type": "cs"}
	JavaScript = {"builder_type": "JavaScript"}


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
		elif self.build_type == BuilderType.JavaScript:
			print("Building game with " + BuilderType.JavaScript["builder_type"])
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

