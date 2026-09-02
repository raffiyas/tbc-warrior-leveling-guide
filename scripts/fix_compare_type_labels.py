from pathlib import Path
p=Path('compare.html')
s=p.read_text(encoding='utf-8')
s=s.replace('>2H Sword<','>Sword<').replace('>2H Mace<','>Mace<').replace('>2H Axe<','>Axe<')
p.write_text(s,encoding='utf-8')
print('fixed comparator type labels')
