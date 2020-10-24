import seaborn


def set_color_palette():
    """
    Set seaborn color palette
    """
    seaborn.set_palette(ColorPalette.palette)


class ColorPalette:
    """
    Color palette extracted from macOS Big Sur wallpaper
    """

    palette = seaborn.color_palette(
        ('#5596cb', '#6b3e79', '#dc3759', '#eeb760', '#2c4c7c', '#4b4378', '#69addf', '#eca25c', '#e8765a', '#a83a76',
         '#2f6cab', '#8cccf7', '#e1bf94', '#b2c2e0', '#cd4676', '#d5e0f1', '#1e406a', '#4484c4', '#873d7a', '#b289af',
         '#448cc4', '#244c74', '#3778b3', '#c83867', '#e14859', '#7fc1f1', '#c77391', '#a799c6', '#d2c6bc', '#e3635a',
         '#143c5c', '#96b2db', '#654c7e', '#bac0bc', '#a33c84', '#b63d64', '#ba7c9b', '#ec675c', '#e15d6c', '#374171',
         '#4e86ba', '#e55456', '#7da5cb', '#3b447c', '#e6624c', '#d8a4bc', '#5e89b9', '#4481b8', '#3c6c9c', '#4c84c4',
         '#ae638e', '#e8a195', '#54a4d4', '#2c74ac', '#448cbc', '#f46464', '#d86444', '#d4605c', '#3f74a4'))
