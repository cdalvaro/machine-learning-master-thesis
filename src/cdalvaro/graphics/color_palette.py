import seaborn as sns


def set_color_palette():
    """
    Set seaborn color palette
    """
    sns.set_palette(color_palette(as_cmap=False))


def color_palette(as_cmap: bool = False, **kwargs):
    # https://medium.com/@morganjonesartist/color-guide-to-seaborn-palettes-da849406d44f
    return sns.color_palette('BrBG_r', as_cmap=as_cmap, **kwargs)
