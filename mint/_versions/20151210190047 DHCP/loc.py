from f6 import loc
print loc(excludes=lambda path, fname: '_versions' in path)
