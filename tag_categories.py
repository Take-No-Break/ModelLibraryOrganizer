"""Transparent local category rules, with explicit user overrides."""
import re
CATEGORIES=('All','Face','Body','Outfit','Pose','BG','Style','Expr','Chara','Title','Artist','Other')
RULES=(
 ('Artist',r'(^artist:|\(artist\)$)'),('Chara',r'(^character:|\(character\)$)'),('Title',r'(^copyright:|\(copyright\)$)'),
 ('Expr',r'(^|_)(smile|blush|crying|tears|angry|grin|frown|laughing|expression|embarrassed)(_|$)'),
 ('Face',r'(^|_)(hair|eyes|eye|eyebrows|eyelashes|mouth|lips|nose|ahoge|twintails|ponytail|bangs|braid)(_|$)'),
 ('Outfit',r'(^|_)(shirt|skirt|dress|jacket|sleeves|uniform|hat|shoes|boots|socks|gloves|swimsuit|ribbon|bow|jewelry|earrings|pants|shorts|hoodie|coat|outfit|bikini)(_|$)'),
 ('Pose',r'(^|_)(standing|sitting|lying|kneeling|walking|running|jumping|pose|arms|hands|looking)(_|$)'),
 ('BG',r'(^|_)(background|sky|clouds|indoors|outdoors|room|beach|forest|street|water|building|sunset)(_|$)'),
 ('Style',r'(^|_)(monochrome|greyscale|chibi|sketch|painting|pixel|parody|comic|watercolor|realistic|style)(_|$)'),
 ('Body',r'(^|_)(breasts|chest|navel|legs|feet|thighs|waist|hips|stomach|belly|skin|muscles|body)(_|$)'),
)
def category_of(tag,overrides=None):
 if overrides and overrides.get(tag) in CATEGORIES[1:]:return overrides[tag]
 normalized=tag.lower().replace(' ','_')
 for category,pattern in RULES:
  if re.search(pattern,normalized):return category
 return 'Other'
