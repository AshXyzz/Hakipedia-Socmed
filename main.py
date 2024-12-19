from website import create_app
from markupsafe import Markup # markup is so I can filter out variables with jinja syntax

app = create_app()

def nl2br(value): # Custom filter function to convert newlines to <br> tags
    try:
        paragraphs = value.split('\n')
        paragraphs_html = '<br>'.join(paragraphs)
        return Markup(paragraphs_html)
    except AttributeError: # if the user doesn't have a bio, etc
        pass

app.jinja_env.filters['nl2br'] = nl2br # register the custom filter


if __name__ == "__main__":
    app.run(debug=True)