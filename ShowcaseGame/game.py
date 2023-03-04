import crys.crystal
from crys.crystal import BuilderType

game = {"info": {"name": "test", "authors": ["JX_Snack"], "out": "out/"},
		"scenes": [{"title": "Papa", "buttons": [["Go to scen", 1]]},
				   {"title": "Scene 2", "buttons": [["Go to scene 1", 1], ["Go to scene 3", 3]]},
				   {"title": "Scene 3", "buttons": [["Go to scene 1", 1], ["Go to scene 2", 2]]}]}

crys.crystal.Game(game, BuilderType.HTMLPlus).build()
