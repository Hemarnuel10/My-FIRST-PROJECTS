from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
import random
import markdown2
from . import util


class NewText(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={"class": "title-input"}))
    text = forms.CharField(widget=forms.Textarea(
        attrs={"class": "text-area"}), label="Add Text Here")


class SearchForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={"class": "search-box"}))


class EditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(
        attrs={"class": "text-area"}), label="Edit your Content")


def entry(request, title):
    entry_md = util.get_entry(title)

    if entry_md == None:
        return render(request, "encyclopedia/error.html", {
            "message": "This Page Does not exist."
        })

    else:
        entry_html = markdown2.markdown(entry_md)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": entry_html
        })


def index(request):
    entries = util.list_entries()
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def new_page(request):
    if request.method == "POST":
        form = NewText(request.POST)

        if form. is_valid():
            title = form.cleaned_data["title"]
            text = form.cleaned_data["text"]

            if util.get_entry(title) is not None:
                return render(request, "encyclopedia/error.html", {
                    "message": "This title already exists."
                })

            util.save_entry(title, text)

            return HttpResponseRedirect(reverse("entry", args=[title]),)

    return render(request, "encyclopedia/create.html", {
        "form": NewText(),

    })


def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            entries = util.list_entries()

            for entry in entries:
                if entry.lower() == title.lower():
                    return HttpResponseRedirect(reverse("entry", args=[entry]))

            related_titles = [
                entry for entry in entries
                if title.lower() in entry.lower()
            ]

            return render(request, "encyclopedia/search.html", {
                "query": title,
                "results": related_titles,
                "form": SearchForm()
            })

    return render(request, "encyclopedia/search.html", {
        "form": SearchForm(),
        "results": []
    })


def edit(request, title):
    if request.method == "GET":
        content = util.get_entry(title)
        form = EditForm(initial={"content": content})
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "form": form
        })
    else:
        if request.method == "POST":
            form = EditForm(request.POST)
            if form.is_valid():
                new_content = form.cleaned_data["content"]
                util.save_entry(title, new_content)
                return HttpResponseRedirect(reverse("entry", args=[title]))
                # If POST is invalid, re-render with errors
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "form": form
            })


def random_page(request):
    pages = util.list_entries()
    random_title = random.choice(pages)
    return HttpResponseRedirect(reverse("entry", args=[random_title]))
