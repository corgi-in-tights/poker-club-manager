# Django Jinja2 Template Syntax Quick Reference

Jinja2 is a templating engine that can quickly generate HTML from templates, in conjunction with HTMX it becomes a very powerful tool.

## Variables & Attributes
Use `{{ variable }}` to output a variable's value. You can access attributes or dictionary keys with dot notation:

```jinja
{{ user.username }}
{{ event.date }}
{{ item["name"] }}
```

## Context
The context is a dictionary of data passed from your Django view to the template. Variables in the context are available for use in the template.

To see the context for each template, please see docs/views-templates.md.

## Default Context in Django
These variables will always be avaliable:
- `request`: The current HttpRequest object
- `user`: The current logged-in user (if using auth context processor)
- `messages`: Django messages module

### Hitting Django URLs
You can use Django's `{% url %}` tag to generate URLs:

```html
<button hx-get="{% url 'events:list' %}" hx-target="#event-list">Load Events</button>
```

No hard-coding URLs needed, each associated view is documented in docs/views-templates.md. Sometimes the URL expects an argument (i.e. `events:detail`), then if given the eventid, you can:

```html
<a href="{% url 'events:detail event.id' %}">View Details</a>
```

## For Loops
Loop over lists or querysets:

```jinja
{% for player in players %}
	{{ player.name }}
{% endfor %}
```

## If Conditions
Conditional logic:

```jinja
{% if user.is_authenticated %}
	Welcome, {{ user.username }}!
{% else %}
	Please log in.
{% endif %}
```

## `{% partialdef %}`
`partialdef` is from a third-party library. It allows defining reusable template blocks (partials):

```jinja
{% load partials %}
# Define
{% partialdef player_card %}
	<div>{{ player.name }}</div>
{% endpartialdef %}

# Render
{% partial player_card %}
```

The main usage is a Django view can access them (without having to make another partial template in the partials/ directory), HTMX then can hit the Django view for a re-render. Makes structuring a bit neater, and easier to follow.


## Static Files (JS, CSS, etc.)
Static files are assets like CSS, JavaScript, and images. In this project, all static files are stored in `static/`, with subfolders like `static/css/` and `static/js/`.

```jinja
{% load static %}

<link rel="stylesheet" href="{% static 'css/main.css' %}">
<script src="{% static 'js/app.js' %}"></script>
<img src="{% static 'images/logo.png' %}" alt="Logo">
```

Resolves to `poker_club_manager/static/js/app.js`, no hard-coding paths needed.


## HTMX Quick Reference

HTMX lets you make AJAX requests and update parts of your page with minimal JavaScript.

### `hx-post` / `hx-get`
- `hx-get`: Makes a GET request to a URL when the element is triggered (e.g., clicked).
- `hx-post`: Makes a POST request to a URL (often used with forms or buttons).

**Example:**
```html
<button hx-get="{% url events:list %}" hx-target="#event-list">Load Events</button>
```

### Picking a Target
Use `hx-target` to specify which element should be updated with the response:

```html
<div id="event-list"></div>
<button hx-get="{% url events:list %}" hx-target="#event-list">Load Events</button>
```


