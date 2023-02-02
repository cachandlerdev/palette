from flask import session
import colorsys
import matplotlib.colors as colors
import sys
from math import floor
    

def get_user_choices(config_colors):
    """Gets all of the user's current color choices stored in the website session."""
    user_choices = dict()
    for choice in config_colors:
        try:
            user_choices[choice] = session[choice]
        except KeyError:
            return None
    return user_choices


def get_color_bases(num_of_options):
    """Gives the user a list of bright colors to pick from."""
    hue = 0
    saturation = 1
    lightness = 0.5
    add_factor = 1 / num_of_options

    options = list()
    for i in range(num_of_options):
        if i > 0:
            hue += add_factor
        hex_color = hls_to_hex(hue, lightness, saturation)
        options.append(hex_color)

    return options


def get_color_shades(num_of_options, base):
    """Gives the user a list of color shades to pick from, given a base HEX color."""
    hls = hex_to_hls(base)

    minimum_l = 0.25
    maximum_l = 0.975
    minimum_s = 0.7
    maximum_s = 1

    hue = hls[0]
    saturation = maximum_s
    saturation_factor = (maximum_s - minimum_s) / num_of_options
    lightness = minimum_l
    lightness_factor = (maximum_l - minimum_l) / num_of_options

    options = list()
    for i in range(num_of_options):
        if i > 0:
            saturation = clamp(saturation - saturation_factor, minimum_s, maximum_s)
            lightness = clamp(lightness + lightness_factor, minimum_l, maximum_l)
        hex_color = hls_to_hex(hue, lightness, saturation)
        options.append(hex_color)

    return options


def hls_to_hex(hue, lightness, saturation):
    """Converts HLS colors to HEX ones."""
    rgb_color = colorsys.hls_to_rgb(hue, lightness, saturation)
    hex_color = colors.to_hex(rgb_color)
    return hex_color


def hex_to_hls(hex_color):
    """Converts HEX colors to HLS ones."""
    rgb_color = colors.to_rgb(hex_color)
    hls_color = colorsys.rgb_to_hls(rgb_color[0], rgb_color[1], rgb_color[2])
    return hls_color


def generate_palette(user_choices, colors, num_to_generate):
    """Generates a color palette."""
    palette = dict()
    for color in colors:
        options = list()
        palette[color] = options

        hls_color = hex_to_hls(user_choices[color])

        minimum = 0.15
        maximum = 0.98
        factor = ((maximum - minimum) / num_to_generate)
        
        num_of_darker_colors = floor(hls_color[1] / factor) - 1
        num_of_lighter_colors = int(clamp((num_to_generate - num_of_darker_colors), 0, num_to_generate))

        hue = hls_color[0]
        # Add darker colors
        for i in range(num_of_darker_colors, 0, -1):
            # Check this
            lightness = clamp(hls_color[1] - (factor * i), minimum, maximum)
            saturation = clamp(hls_color[2] + (factor * i), minimum, maximum)
            hex_color = hls_to_hex(hue, lightness, saturation)
            options.append(hex_color)

        # Add original color
        options.append(user_choices[color])

        # Add lighter colors
        for i in range(1, num_of_lighter_colors, 1):
            lightness = clamp(hls_color[1] + (factor * i), minimum, maximum)
            saturation = clamp(hls_color[2] - (factor * i), minimum, maximum)
            hex_color = hls_to_hex(hue, lightness, saturation)
            options.append(hex_color)
    
    return palette


def verify_settings(num_of_colors_to_show, num_of_colors_to_generate):
    type_check = (num_of_colors_to_show is not None and num_of_colors_to_generate is not None)
    show_check = (num_of_colors_to_show > 0)
    gen_check = (num_of_colors_to_generate > 0)
    return type_check and show_check and gen_check


def clamp(number: float, min: float, max: float):
    """Clamps a given number to the specified range."""
    if number < min:
        return min
    if number > max:
        return max
    return number