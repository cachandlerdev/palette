from flask import Flask, render_template, redirect, request, session
from flask_session import Session
import helpers
from config import Config
import sys


# Setup flask and sessions
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# App settings

config = Config(12, 8)

# Website code
@app.route("/")
def index():
    """Home page"""
    if not config.loaded_settings:
        config.num_of_colors = session.get("num_of_colors_to_show", 12)
        config.num_of_generated_colors = session.get("num_of_colors_to_generate", 8)
        config.loaded_settings = True

    # Clear existing colors stored in the session.
    for color in config.colors:
        if color in session.keys():
            session.pop(color)

    return render_template("index.html", hide_logo=True)


@app.route("/get_started")
def get_started():
    """Where you go when clicking 'get started'."""
    return redirect("/colors")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    """Loads the settings page."""
    if request.method == "POST":
        # Save settings
        num_to_show = request.form.get("num_of_colors_to_show", type=int)
        num_to_gen = request.form.get("num_of_colors_to_generate", type=int)
        if helpers.verify_settings(num_to_show, num_to_gen):
            session["num_of_colors_to_show"] = num_to_show
            session["num_of_colors_to_generate"] = num_to_gen
            config.num_of_colors = num_to_show
            config.num_of_generated_colors = num_to_gen
            return render_template("settings.html", num_to_show=config.num_of_colors, 
                                    num_to_gen=config.num_of_generated_colors, message="Saved!")
        else:
            return render_template("settings.html", num_to_show=config.num_of_colors, 
                                    num_to_gen=config.num_of_generated_colors, 
                                    message="Sorry, your input could not be processed. Are you sure that you put valid numbers?")

    else:
        # Show form
        return render_template("settings.html", num_to_show=config.num_of_colors, 
                               num_to_gen=config.num_of_generated_colors, message="")


@app.route("/colors", methods=["GET", "POST"])
def colors():
    """First lets the user pick a primary, then secondary, then accent color by first choosing a 
    base value and then a shade."""

    if request.method == "POST":
        # The user has picked a color.
        user_choices = dict()

        for choice in config.colors:
            if choice in session.keys():
                # If this color exists, skip to the next one
                user_choices[choice] = session[choice]
                continue

            # Look at color options
            shade = request.form.get(choice + "-shade")
            if shade == None:
                # Check that the base exists
                base = request.form.get(choice + "-base")
                if base == None:
                    if choice == config.colors[0]:
                        return "No colors set.", 500
                    
                    # Show form for base
                    options = helpers.get_color_bases(config.num_of_colors)
                    return render_template("color-selector.html", color_options=options, 
                                           user_choices=user_choices, colors=config.colors, 
                                           title=choice, type="base")
                
                # Show form for shade
                options = helpers.get_color_shades(config.num_of_colors, base)
                return render_template("color-selector.html", color_options=options, 
                                       user_choices=user_choices, colors=config.colors,
                                       title=choice, type="shade")
            
            # Add the shade to user choices and as a cookie
            user_choices[choice] = shade
            session[choice] = shade
        
        # All colors have been picked.
        return redirect("/confirm")

    else:
        # Show the user the form (pick primary).
        user_choices = dict()
        options = helpers.get_color_bases(config.num_of_colors)
        title = config.colors[0]
        return render_template("color-selector.html", title=title, color_options=options, 
                               type="base", user_choices=user_choices, colors=config.colors)
    

@app.route("/confirm", methods=["GET", "POST"])
def confirm():
    """Lets the user confirm his current color choices and change one if needed."""
    user_choices = helpers.get_user_choices(config.colors)

    if request.method == "POST":
        choice = request.form.get('to_update')
        if choice in config.colors:
            session['to_update'] = choice
            return redirect("/change")
        
        # He must have hit the "generate palette" button.
        return redirect("/generate")

    else:
        # Show the form to let the user confirm his choices.
        session['to_update'] = None
        return render_template("confirm.html", user_choices=user_choices, colors=config.colors)
    

@app.route("/change", methods=["GET", "POST"])
def change():
    """Lets the user change a color before returning to the confirm screen."""
    # Check that the "to_update" entry is valid.
    to_update = session['to_update']
    if to_update not in config.colors:
        return "Invalid color entry.", 500
    
    # Remove the existing color, then retrieve the others for the ui 
    session[to_update] = None
    user_choices = helpers.get_user_choices(config.colors)

    if request.method == "POST":
        # The user has picked a color
        shade = request.form.get("updated-shade")
        if shade == None:
            # Check that the base exists
            base = request.form.get("updated-base")
            if base == None:
                return "Updated color not found.", 500
            
            # Show the form to let the user pick a shade
            options = helpers.get_color_shades(config.num_of_colors, base)
            return render_template("color-corrector.html", color_options=options, 
                                   user_choices=user_choices, colors=config.colors,
                                   title=to_update, type="shade")
        
        # The color has been selected.
        session[to_update] = shade
        return redirect("/confirm")

    else:
        # Show the form to select the updated base color.
        options = helpers.get_color_bases(config.num_of_colors)
        return render_template("color-corrector.html", color_options=options,
                               user_choices=user_choices, colors=config.colors,
                               title=to_update, type="base")


@app.route("/generate")
def generate():
    """Displays the generated color palette."""
    user_choices = helpers.get_user_choices(config.colors)

    if user_choices == None:
        return redirect("/")

    palette = helpers.generate_palette(user_choices, config.colors, 
                                       config.num_of_generated_colors)
    session['palette'] = palette
    return render_template("palette.html", palette=palette, colors=config.colors)
    

@app.route("/preview")
def preview():
    """Displays a chat app preview with the generated colors."""

    return render_template("preview.html")


@app.route("/show-chat-app")
def show_chat_app():
    """Needed to let the html template load in the preview iframe."""
    palette = session['palette']
    html_palette = dict()

    main_color = palette[config.colors[0]][int(config.num_of_generated_colors / 2)]
    html_palette["main"] = main_color

    lighter_main_index = int(helpers.clamp((config.num_of_generated_colors / 2) + 2, 0, 
                             config.num_of_generated_colors - 1))
    lighter_main = palette[config.colors[0]][lighter_main_index]
    html_palette["lighter_main"] = lighter_main

    lightest_main_index = int(helpers.clamp((config.num_of_generated_colors / 2) + 3, 0, 
                             config.num_of_generated_colors - 1))
    lightest_main = palette[config.colors[0]][lightest_main_index]
    html_palette["lightest_main"] = lightest_main

    darker_main_index = int(helpers.clamp((config.num_of_generated_colors / 2) - 2, 0, 
                             config.num_of_generated_colors - 1))
    darker_main = palette[config.colors[0]][darker_main_index]
    html_palette["darker_main"] = darker_main

    even_darker_main_index = int(helpers.clamp((config.num_of_generated_colors / 2) - 3, 0, 
                             config.num_of_generated_colors - 1))
    even_darker_main = palette[config.colors[0]][even_darker_main_index]
    html_palette["even_darker_main"] = even_darker_main

    darkest_main_index = int(helpers.clamp((config.num_of_generated_colors / 2) - 4, 0, 
                             config.num_of_generated_colors - 1))
    darkest_main = palette[config.colors[0]][darkest_main_index]
    html_palette["darkest_main"] = darkest_main

    secondary_color = palette[config.colors[1]][int(config.num_of_generated_colors / 2)]
    html_palette["secondary"] = secondary_color

    darker_secondary_index = int(helpers.clamp((config.num_of_generated_colors / 2) - 2, 0, 
                             config.num_of_generated_colors - 1))
    darker_secondary = palette[config.colors[1]][darker_secondary_index]
    html_palette["darker_secondary"] = darker_secondary

    accent_color = palette[config.colors[2]][int(config.num_of_generated_colors / 2)]
    html_palette["accent"] = accent_color

    darker_accent_index = int(helpers.clamp((config.num_of_generated_colors / 2) - 2, 0, 
                             config.num_of_generated_colors - 1))
    darker_accent = palette[config.colors[2]][darker_accent_index]
    html_palette["darker_accent"] = darker_accent

    darkest_accent_index = int(helpers.clamp((config.num_of_generated_colors / 2) - 4, 0, 
                             config.num_of_generated_colors - 1))
    darkest_accent = palette[config.colors[2]][darkest_accent_index]
    html_palette["darkest_accent"] = darkest_accent

    html_palette["main_gray"] = "#EEEEEE"
    html_palette["darker_gray"] = "#7D8898"
    html_palette["darkest_gray"] = "#616975"

    html_palette["lighter_positive"] = "#53DA62"

    html_palette["warning"] = "#DBB55D"
    html_palette["lighter_warning"] = "#FBD887"
    html_palette["lightest_warning"] = "#FDF2DA"
    html_palette["darker_warning"] = "#B5954D"
    html_palette["darkest_warning"] = "#776333"

    return render_template("chat-app.html", palette=html_palette)


if __name__ == '__main__':
    app.run()