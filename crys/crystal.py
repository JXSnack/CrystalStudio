class Game:
	def __init__(self, game, how):
		self.game = game  # what game
		self.build_type = how  # how should it be exported?

		self.name = game["info"]["name"]  # game name
		self.authors = ", ".join(game["info"]["authors"])  # authors
		self.out = game["info"]["out"]
		self.scenes = game["scenes"]  # the scenes

		print("Initialized '" + game["info"]["name"] + "'")  # debug check

	def build(self):
		if self.build_type == BuilderType.PYTHON:  # if the builder type is python export
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


class BuilderType:
	GAME = {"builder_type": "player"}
	PYTHON = {"builder_type": "python"}
	HTML = {"builder_type": "cs"}
	HTMLPlus = {"builder_type": "cs"}
	RAWQT = {"builder_type": "cs"}
