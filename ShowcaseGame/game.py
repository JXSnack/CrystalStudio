import crys.crystal
from crys.crystal import BuilderType

game = {
	"info": {
		"name": "Showcase Game",
		"authors": ["JX_Snack"],
		"out": "out/"
	},

	"scenes": [
		{
			"title": "Mami",
			"buttons": [
				["Papi", 2],
				["Schnupps", 3]
			]
		},

		{
			"title": "Papi",
			"buttons": [
				["Go to scene 1", 1],
				["Go to scene 3", 3]
			]
		},

		{
			"title": "Schnuppi",
			"buttons": [
				["Go to scene 1", 1],
				["Go to scene 2", 2]
			]
		}
	]
}

crys.crystal.Game(game, BuilderType.HTMLPlus).build()
