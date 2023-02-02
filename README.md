# Colette
#### Description: Colette is a web application developed with Flask that allows programmers, UI artists, and more to quickly come up with color palettes for their software programs.

## Current Website:
http://cachandlerdev.pythonanywhere.com/

## Documentation
For my submission to CS50x, I wanted to create some kind of application that would have real world value beyond merely serving as a box to check in this course, and that I would be able to use for future projects.
Initially, I considered creating a website for OSSU, which is a free and open source computer science curriculum that compiles various MOOC courses, but after completing the Week 8 Homepage assignment and seeing the relative ease with which I could create a frontend only page (I had created a website for CS50), I was uncertain that a project of that nature would be complex enough to provide a suitable challenge.
After a while, I thought about the process I usually go through when creating software mockups in Figma, and realized that one of the issues I have always had with most popular "color palette" websites is that they typically only allow the user to select (or randomly generate) 5 main colors, which is unfortunate because real software applications are not typically created that way.
As an analysis of programs like VSCode or Github would reveal, most actual tools do not bombard the senses with five randomly selected splotches of orange, green, and blue, and instead carefully choose one or two colors and apply them sparingly in several different shades so as to create a coherent and visually interesting yet not overwhelming interface.
As such, after spending some time learning the basics of how UI designers choose their color layouts, I decided to create a web application that might simplify the process somewhat.

Colette is a color palette web application written in Flask that lets developers choose a primary, secondary, and accent color before generating a collection of several similar shades in hexadecimal format that can be used in a software project.
The number of generated shades and the user's input options (choose a base hue, then select the shade) can be altered via the settings, and at the end of the process the user can see how those colors would look in a mobile chat application.
I designed Colette with a mobile first layout, which is why certain aspects may appear somewhat simplistic on a desktop interface, but it does incorporate some responsive design elements in order to ensure user friendliness in both form factors.

Next up, I should probably talk about the code itself and my design choices.
The python scripts are fairly simple and split into three files, namely `app.py`, `config.py`, and `helpers.py`.
`app.py`, as anyone familiar with Flask applications might have guessed, is used to define app routes and relay data to the HTML templates, while `helpers.py` defines a collection of helper functions to be used by the main file.
I initially considered separating these functions into various classes, but given the course's focus on procedural programming rather than an object oriented layout, I tried to stick to that philosophy here. Admittedly, `config.py` does somewhat break that rule by creating a data class to store application settings, but I did this because I was unwilling to start relying on global variables (which are obviously bad practice).

From there, it would be logical to discuss the html templates.
Firstly, `layout.html` defines the general structure of each website page, and also lays out the basics for a custom navbar.
I chose to do this manually rather than relying on something like Bootstrap because I wanted to understand what exactly was happening under the hood, although admittedly one could argue that the library's solution is superior to what I came up with.
After that, there is `index.html`, which acts as the website's homepage, and that is followed by the `color-selector.html` and `color-corrector.html` files.
As the process of choosing a primary, secondary, and accent color is virtually identical in all cases, I chose to mainly use the Jinja template engine in order to handle all of my `www.website/colors` forms.
Next up is `palette.html`, which grabs a dictionary of colors from `app.py` and displays them using hex codes for easy referral while developing other applications, and then there is `preview.html`, which embeds the final file, `chat-app.html`.
The chat app mockup was one of the more challenging aspects of this project, as I had to implement a completely different user layout and do so in such a way that colors would change dynamically depending on what hex codes were sent by the server.
This proved fairly difficult, so for the sake of time I unfortunately had to cut the desktop version, and made use of some questionable html practices like hard coding svg files and using inline css, but I was not sure how else to alter colors on the fly.

Finally, the css was fairly tedious, so I will not spend long on this section, but it was comprised of `light.css`, which made up the visual language of Colette itself, and `chat.css`, which defined the layout of the mockup.
As the name "light" implies, I was initially hoping to create a dark mode version as well, but I eventually cut that feature along with several others after this project began taking significantly longer to complete than expected, mainly because of the css styling.
(For a time, I was even considering allowing the user to choose whether he wanted more than just three color types---e.g. yellow warnings, red error messages, etc.---but while significant portions of the code are still setup to handle this, I eventually decided that I had spent enough time working on Colette and should really move on to learning something else.

All in all, I am glad I went through the course, and I would like to say thank you to everyone involved in its production or who helped out in the Discord server when I was struggling.
