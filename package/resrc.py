import itertools as itls
# Settings

# setter getter
rsc = {}

# input type
rsc["input"] = itls.cycle(["M","K"])
rsc["M"] = {}
rsc["K"] = {}
# input icon
rsc["M"]["icon"] = "src/mouse.png"
rsc["K"]["icon"] = "src/key.png"
# input subacts
rsc["M"]["subacts"] = itls.cycle(["click","double"])
rsc["K"]["subacts"] = itls.cycle(["typing","copy","paste"])


# getting coor icon
rsc["coor"] = {}
rsc["coor"]["icon"] = "src/coor.png"

# subaction icon (mouse)
rsc["click"] = {}
rsc["double"] = {}
rsc["click"]["icon"] = "src/click.png"
rsc["double"]["icon"] = "src/double.png"
#rsc["press"] = 

# subaction icon (key)
rsc["typing"] = {}
rsc["copy"] = {}
rsc["paste"] = {}
rsc["all"] = {}
rsc["typing"]["icon"] = "src/typing.png"
rsc["copy"]["icon"] = "src/copy.png"
rsc["paste"]["icon"] = "src/paste.png"
rsc["all"]["icon"] = "src/all.png"

# tree icon
rsc["G"] = {}
rsc["I"] = {}
rsc["G"]["icon"] = "src/group.png"
rsc["I"]["icon"] = "src/inst.png"

# mainwin shortcut

# poswin shortcut

        
