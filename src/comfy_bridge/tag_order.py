import re


def format_pixai_tags(results):
    def ordered(category):
        scores = results.get(category, {})
        return sorted(scores, key=scores.get, reverse=True)

    quality_tags = {'masterpiece', 'best_quality', 'great_quality', 'good_quality',
                    'normal_quality', 'low_quality', 'worst_quality', 'very_aesthetic',
                    'aesthetic', 'displeasing', 'very_displeasing'}
    general = ordered('general')
    quality = [tag for tag in general if tag.replace(' ', '_') in quality_tags]
    counts = [tag for tag in general if re.fullmatch(r'(?:\d+|multiple)_(?:girls?|boys?|others?)|\d+(?:girls?|boys?|others?)', tag)]
    remaining = [tag for tag in general if tag not in quality and tag not in counts]
    tags = quality + ordered('meta') + ordered('rating') + ordered('character') + ordered('copyright') + ordered('style') + counts + remaining
    return ', '.join(dict.fromkeys(tags))
