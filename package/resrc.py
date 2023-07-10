import itertools as itls
# Settings

# setter getter
resrc = {}

# input type
resrc["input"] = itls.cycle(["M","K"])
resrc["M"] = {}
resrc["K"] = {}
# input icon
resrc["M"]["icon"] = "src/mouse.png"
resrc["K"]["icon"] = "src/key.png"
# input subacts
resrc["M"]["subacts"] = itls.cycle(["click","double"])
resrc["K"]["subacts"] = itls.cycle(["typing","copy","paste"])


# getting coor icon
resrc["coor"] = {}
resrc["coor"]["icon"] = "src/coor.png"

# subaction icon (mouse)
resrc["click"] = {}
resrc["double"] = {}
resrc["click"]["icon"] = "src/click.png"
resrc["double"]["icon"] = "src/double.png"
#resrc["press"] = 

# subaction icon (key)
resrc["typing"] = {}
resrc["copy"] = {}
resrc["paste"] = {}
resrc["all"] = {}
resrc["typing"]["icon"] = "src/typing.png"
resrc["copy"]["icon"] = "src/copy.png"
resrc["paste"]["icon"] = "src/paste.png"
resrc["all"]["icon"] = "src/all.png"

# tree icon
resrc["G"] = {}
resrc["I"] = {}
resrc["G"]["icon"] = "src/group.png"
resrc["I"]["icon"] = "src/inst.png"

# mainwin shortcut

# poswin shortcut

        
