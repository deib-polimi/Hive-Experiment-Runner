import sys
from regularExpressions import AM

for line in sys.stdin:
  if AM.is_relevant (line):
    print line
