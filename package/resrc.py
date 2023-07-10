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
resrc["coor"] = "src/coor.png"

# subaction icon (mouse)
resrc["click"] = "src/click.png"
resrc["double"] = "src/double.png"
#resrc["press"] = 

# subaction icon (key)
resrc["typing"] = "src/typing.png"
resrc["copy"] = "src/copy.png"
resrc["paste"] = "src/paste.png"
resrc["all"] = "src/all.png"

# tree icon
resrc["G"] = "src/group.png"
resrc["I"] = "src/inst.png"

# mainwin shortcut

# poswin shortcut

        
