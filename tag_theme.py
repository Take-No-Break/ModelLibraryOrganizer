"""Application palettes; styling only."""
DARK=dict(BG='#1f1f30',PANEL='#29293e',FIELD='#323249',CHIP='#34344b',TEXT='#c2d5ff',MUTED='#8292b8',BLUE='#83b1ff',LINE='#39394f',RED='#d8788c',SELECT='#456797',HOVER='#414761',ROW='#25263b',EDIT='#3b405b',EDIT_TEXT='#e1eaff',BADGE_TEXT='#172846')
CLASSIC=dict(BG='#d9d8d2',PANEL='#cfcec7',FIELD='#f4f3ee',CHIP='#c9c8c1',TEXT='#202020',MUTED='#62615d',BLUE='#676762',LINE='#9e9d96',RED='#a33e42',SELECT='#b9bab4',HOVER='#e2e1da',ROW='#d3d2cb',EDIT='#f4f3ee',EDIT_TEXT='#202020',BADGE_TEXT='#ffffff')
MODE='dark'
ACCENT='Neutral'
PALETTES={
 'dark':{
  'Neutral':{},
  'Pink':dict(BG='#292128',PANEL='#342a33',FIELD='#44343f',TEXT='#f4e6ee',MUTED='#bca4b3',BLUE='#eca1c2',LINE='#57414f',SELECT='#70465f',HOVER='#513b49',ROW='#3a2b36',EDIT='#44343f',EDIT_TEXT='#ffedf5',BADGE_TEXT='#321b29'),
  'Blue':dict(BG='#202733',PANEL='#293344',FIELD='#34435a',TEXT='#e2edfc',MUTED='#a0b3ce',BLUE='#8bbcff',LINE='#455773',SELECT='#3f6089',HOVER='#3e506b',ROW='#293a50',EDIT='#34435a',EDIT_TEXT='#edf5ff',BADGE_TEXT='#172846'),
  'Purple':dict(BG='#272233',PANEL='#332c43',FIELD='#433856',TEXT='#eee7fc',MUTED='#b3a5ce',BLUE='#bfa1f0',LINE='#55466f',SELECT='#635083',HOVER='#514165',ROW='#372d49',EDIT='#433856',EDIT_TEXT='#f6efff',BADGE_TEXT='#2b2042'),
 },
 'classic':{
  'Neutral':{},
  'Pink':dict(BG='#f0e4e9',PANEL='#f7edf2',CHIP='#ead5df',BLUE='#a34270',LINE='#c9a9b9',SELECT='#e6bdd0',HOVER='#edd2df',ROW='#eddae4'),
  'Blue':dict(BG='#e3eaf3',PANEL='#edf3fa',CHIP='#d4e1f1',BLUE='#365f9a',LINE='#a8b9d0',SELECT='#bdd1ec',HOVER='#d1def0',ROW='#dce7f5'),
  'Purple':dict(BG='#eae4f1',PANEL='#f2edf8',CHIP='#dfd4ee',BLUE='#76509d',LINE='#bba9ce',SELECT='#d2bde8',HOVER='#e0d2ef',ROW='#e4d9f1'),
 }
}

def set_mode(mode,accent='Neutral'):
 global MODE,ACCENT
 MODE='classic' if mode=='classic' else 'dark'
 ACCENT=accent if accent in PALETTES[MODE] else 'Neutral'
 globals().update(CLASSIC if MODE=='classic' else DARK)
 globals().update(PALETTES[MODE][ACCENT])
set_mode('dark')
