import sys
sys.path.insert(0, '../..')
import mint
del sys.path[0]

proj = mint.load()
print proj
print proj.components
