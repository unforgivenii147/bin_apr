from dh import get_pyfiles

for path in get_pyfiles("."):
    print(path.name)
