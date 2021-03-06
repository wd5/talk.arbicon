# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext as _
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from guardian.decorators import permission_required_or_403
from common.pagination import get_page
from django.contrib.auth import login, REDIRECT_FIELD_NAME
from django.utils.translation import to_locale, get_language

from core.forms import LanguageForm
from pages.models import Page, Content
from forms import PageForm, ContentForm, get_content_form

#@permission_required_or_403('accounts.view_users')
def index(request):
    return render(request, 'pages/administration/index.html')


@permission_required_or_403('pages.add_page')
def pages_list(request, parent=None):
    if parent:
        parent = get_object_or_404(Page, id=parent)

    pages_page = get_page(request, Page.objects.filter(parent=parent))
    contents = list(Content.objects.filter(page__in=list(pages_page.object_list), lang=get_language()[:2]))

    pages_dict = {}
    for page in pages_page.object_list:
        pages_dict[page.id] = {'page':page}

    for content in contents:
        pages_dict[content.page_id]['page'].content = content

    pages = [page['page'] for page in pages_dict.values()]


    return render(request, 'pages/administration/pages_list.html', {
        'parent': parent,
        'pages': pages,
        'pages_page': pages_page,
    })


@permission_required_or_403('auth.add_page')
def create_page(request, parent=None):
    if parent:
        parent = get_object_or_404(Page, id=parent)

    if request.method == 'POST':
        page_form = PageForm(request.POST, prefix='page_form')

        if page_form.is_valid():
            page = page_form.save(commit=False)
            if parent:
                page.parent = parent
            page.save()
            return redirect('pages:administration:create_page_content', page_id=page.id)
    else:
        page_form = PageForm(prefix='page_form')

    return render(request, 'pages/administration/create_page.html', {
        'parent': parent,
        'page_form': page_form,
     })


@permission_required_or_403('auth.change_page')
def edit_page(request, id):
    langs = []
    for lang in settings.LANGUAGES:
        langs.append({
            'code': lang[0],
            'title': _(lang[1])
        })

    page = get_object_or_404(Page, id=id)

    if request.method == 'POST':
        page_form = PageForm(request.POST, prefix='page_form', instance=page)

        if page_form.is_valid():
            page_form.save()
            return redirect('pages:administration:pages_list')

    else:
        page_form = PageForm(prefix='page_form', instance=page)

    return render(request, 'pages/administration/edit_page.html', {
        'page': page,
        'langs': langs,
        'page_form': page_form,
    })


@permission_required_or_403('auth.change_page')
def delete_page(request, id):
    page = get_object_or_404(Page, id=id)
    page.delete()
    return redirect('pages:administration:pages_list')


@permission_required_or_403('auth.add_page')
def create_page_content(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    if request.method == 'POST':
        content_form = ContentForm(request.POST, prefix='content_form')

        if content_form.is_valid():
            content = content_form.save(commit=False)
            content.page = page
            content.save()

            save = request.POST.get('save', u'save_edit')
            if save == u'save':
                return redirect('pages:administration:edit_page', id=page_id)
            else:
                return redirect('pages:administration:edit_page_content', page_id=page_id, lang=content.lang)
    else:
        content_form = ContentForm(prefix='content_form')
    return render(request, 'pages/administration/create_page_content.html', {
        'page': page,
        'content_form': content_form,
    })


@permission_required_or_403('auth.change_page')
def edit_page_content(request, page_id, lang):
    lang_form = LanguageForm({'lang': lang})
    if not lang_form.is_valid():
        return HttpResponse(_(u'Language is not registered in system.') + _(u" Language code: ") + lang)

    page = get_object_or_404(Page, id=page_id)

    try:
        content = Content.objects.get(page=page_id, lang=lang)
    except Content.DoesNotExist:
        content = Content(page=page, lang=lang)

    ContentForm = get_content_form(('page', 'lang'))

    if request.method == 'POST':
        content_form = ContentForm(request.POST, prefix='content_form', instance=content)

        if content_form.is_valid():
            content = content_form.save(commit=False)
            content.page = page
            content.save()

        save = request.POST.get('save', u'save_edit')
        if save == u'save':
            return redirect('pages:administration:edit_page', id=page_id)

    else:
        content_form = ContentForm(prefix='content_form', instance=content)
    return render(request, 'pages/administration/edit_page_content.html', {
        'content': content,
        'content_form': content_form,
    })






