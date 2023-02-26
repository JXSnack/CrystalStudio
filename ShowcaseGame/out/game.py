

import time
import sys

print("Made with CrystalStudio")
print("Game: Showcase Game")
print("Written by: JX_Snack")

game = [{'title': 'Scene 1', 'buttons': [('Go to scene 2', 2), ('Go to scene 3', 3)]}, {'title': 'Scene 2', 'buttons': [('Go to scene 1', 1), ('Go to scene 3', 3)]}, {'title': 'Scene 3', 'buttons': [('Go to scene 1', 1), ('Go to scene 2', 2)]}]
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

			