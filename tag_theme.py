"""Application palettes; styling only."""
DARK=dict(BG='#1f1f30',PANEL='#29293e',FIELD='#323249',CHIP='#34344b',TEXT='#c2d5ff',MUTED='#8292b8',BLUE='#83b1ff',LINE='#39394f',RED='#d8788c',SELECT='#456797',HOVER='#414761',ROW='#25263b',EDIT='#3b405b',EDIT_TEXT='#e1eaff',BADGE_TEXT='#172846')
CLASSIC=dict(BG='#e8e6e1',PANEL='#f0eeea',FIELD='#ffffff',CHIP='#e2dfd9',TEXT='#222222',MUTED='#666666',BLUE='#54758c',LINE='#b7b3ac',RED='#a33e42',SELECT='#d5e1e8',HOVER='#dedbd5',ROW='#e3e9ed',EDIT='#ffffff',EDIT_TEXT='#222222',BADGE_TEXT='#ffffff')
MODE='dark'
def set_mode(mode):
 global MODE
 MODE='classic' if mode=='classic' else 'dark'
 globals().update(CLASSIC if MODE=='classic' else DARK)
set_mode('dark')
