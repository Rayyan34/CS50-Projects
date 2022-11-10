import random
from django import forms
from django.http import response
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from markdown2 import Markdown 
from . import util
from django.urls import reverse


class NewPageForm(forms.Form):
    title = forms.CharField(label="Title:", max_length=100,
                                                            widget=forms.TextInput(attrs={'class': 'formpgtitle', 'placeholder': 'Type in the title of your page'}))
    content = forms.CharField(label="Content:",
                                                widget=forms.Textarea(attrs={'class': 'formpgcont', 'placeholder': 'Type content in markdown form starting with page heading - ## heading.'}))

    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    markdowner = Markdown()
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/error.html", {
            "entryTitle": entry
        })

    else:
        return render(request, "encyclopedia/page.html", {
            "entry": markdowner.convert(entryPage),
            "entryTitle": entry
        })

def search(request):
    entries = util.list_entries() 
    entries = [x.lower() for x in entries]
    query = request.GET.get('q', '')

    if query.lower() in entries:
        return HttpResponseRedirect(f"wiki/{query}")
#try
    else:
        entries_found = []
        for entry in util.list_entries():
            if query.lower() in entry.lower():
                entries_found.append(entry)

        return render(request, "encyclopedia/index.html", {
            "entries": entries_found,
            "sub": True
        })


def newpage(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if(util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                util.save_entry(title, content)
                return HttpResponseRedirect(f"wiki/{title}")
            else:
                return render(request, "encyclopedia/newpage.html", {
                "message": "This page already exists",
                "entryTitle": title,
                "exists": True
                })
        else:
            return render(request, "encyclopedia/newpage.html", {
            "form": form
            })

    return render(request, "encyclopedia/newpage.html", {
        "form": NewPageForm()
    } )    

def edit(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/error.html", {
            "entryTitle": entry
        })
    else:
        form = NewPageForm()
        form.fields["title"].initial = entry
        form.fields["title"].widget.attrs['readonly'] = True
        form.fields["content"].initial = entryPage
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/newpage.html", {
            "form": form,
            "edit": True,
            "entryName": entry
        })

def randompg(request):
    entries = util.list_entries()
    selected_page = random.choice(entries)
    return HttpResponseRedirect(reverse('entry', args=[selected_page])) 