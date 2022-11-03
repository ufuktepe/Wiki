from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import markdown2
from random import randint
from . import util


class NewPageForm(forms.Form):
    """
    Form for creating a new page.
    """
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'style': 'max-width: 310px'}))
    content = forms.CharField(widget=forms.Textarea(), label="Content")


class EditPageForm(forms.Form):
    """
    Form for editing an existing page.
    """
    content = forms.CharField(widget=forms.Textarea(), label="Content")


def index(request):
    """
    Default route that returns current entries.
    """
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})


def entry(request, title):
    """
    Returns an entry page by its title. If no such entry exists, returns an error page.
    """
    # Get the markdown content
    markdown_content = util.get_entry(title)

    # Check if entry exists
    if markdown_content:
        # Return the entry page.
        return render(request, "encyclopedia/entry.html",
                      {"title": title, "content": markdown2.Markdown().convert(markdown_content)})

    # Return an error page if no such entry exists.
    else:
        return render(request, "encyclopedia/notfounderror.html", {"title": title})


def search(request):
    """
    Searches entries for a typed query. If the query matches the name of an entry, redirects to that entry’s page.
    If the query doesn't match any entry, renders a search results page that displays a list of all entries that have
    the query as a substring.
    """
    # Get the query and existing entries
    query = request.GET.get('q')
    entries = util.list_entries()

    # Check if query matches the name of an entry.
    if query.casefold() not in (e.casefold() for e in entries):
        # If query doesn't match any entry, find entries that have the query as a substring.
        close_matches = [single_entry for single_entry in entries if query.casefold() in single_entry.casefold()]
        # Return a search results page with a list of all closely matching entries
        return render(request, "encyclopedia/search.html", {"entries": close_matches, "query": query})

    # Redirect to matching entry's page if query matches the name of an entry.
    return HttpResponseRedirect(reverse("encyclopedia:entry", args=(query,)))


def create(request):
    """
    Creates a new encyclopedia entry.
    """
    if request.method == "POST":
        # Fetch the form
        form = NewPageForm(request.POST)

        # Check if form is valid
        if form.is_valid():
            # Get the form title and content
            title, content = util.get_form_data(form, get_title=True)
            # Get the existing entries
            entries = util.list_entries()

            # Check if title already exists in current entries
            if title.casefold() not in (e.casefold() for e in entries):
                # Save entry and redirect to the entry page
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("encyclopedia:entry", args=(title,)))

            # If title already exists, then go to the entry exists error page
            else:
                return render(request, "encyclopedia/entryexistserror.html", {"title": title})

        # If form is invalid, return the create page with the current form
        else:
            return render(request, "encyclopedia/create.html", {"form": form})

    # If request is not a post request, return the create page with a new form
    return render(request, "encyclopedia/create.html", {"form": NewPageForm()})


def edit(request, title):
    """
    If request method is POST, updates the entry and redirects to the updated entry page.
    If request method is not POST, returns the edit page pre-populated with the current content of the page.
    """
    # Check if request method is POST
    if request.method == "POST":
        # Fetch the form
        form = EditPageForm(request.POST)

        # Check if form is valid
        if form.is_valid():
            # Get the form content, save the entry and redirect to the entry page
            _, content = util.get_form_data(form)
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("encyclopedia:entry", args=(title,)))

        # If form is invalid, return the edit page with the current form and title
        else:
            return render(request, "encyclopedia/edit.html", {"form": form, "title": title})

    # Create an edit page form pre-populated with the current content of the page
    form = EditPageForm(initial={'content': util.get_entry(title)})
    # Return the edit page with the form and title
    return render(request, "encyclopedia/edit.html", {"form": form, "title": title})


def random(request):
    """
    Redirects to a random entry page.
    """
    # Get the existing entries
    entries = util.list_entries()
    # Generate a random number
    random_index = randint(0, len(entries) - 1)
    # Redirect to an entry page using the random number as an index for the entries list.
    return HttpResponseRedirect(reverse("encyclopedia:entry", args=(entries[random_index],)))
