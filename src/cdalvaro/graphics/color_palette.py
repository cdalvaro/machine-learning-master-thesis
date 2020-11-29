import seaborn as sns


def set_color_palette():
    """
    Set seaborn color palette
    """
    sns.set_palette(color_palette(as_cmap=False))


def color_palette(reverse: bool = False, **kwargs):
    # http://seaborn.pydata.org/tutorial/color_palettes.html
    if 'as_cmap' not in kwargs:
        kwargs['as_cmap'] = False

    palette_name = 'rocket'
    if reverse:
        palette_name += '_r'

    return sns.color_palette(palette_name, **kwargs)
