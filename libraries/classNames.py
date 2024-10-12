def Classnames():

    classNames = []
    classFile = "/models/coco.names"
    with open(classFile,"rt") as f:
        classNames = f.read().rstrip("\n").split("\n")

    return classNames