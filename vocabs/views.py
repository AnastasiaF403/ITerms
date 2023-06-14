from pprint import pprint
from time import sleep
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render, redirect
from .models import Term, Dictionary, User
from django.urls import reverse_lazy
from .forms import *
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login
from .utils import *
from django.views.generic import TemplateView, ListView
from django.db.models import Q
from django.views.generic import (
    ListView,
)
from random import randint, sample, shuffle, choices
from django.forms.models import model_to_dict
from django.core import serializers


class SearchResultsView(ListView):
    model = Term
    template_name = 'search.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = Term.objects.filter(Q(term__icontains=query) | Q(translate__icontains=query))
        return object_list


def terms_list(request):
    terms = Term.objects.all().order_by(Lower("term"))
    return render(request, 'vocabs/terms_list.html', {'terms': terms})


def main(request):
    return render(request, 'vocabs/main.html')


def learn(request):
    unlearned_dict_id = Dictionary.objects.filter(Q(user_id=request.user) & Q(states='Не изучены'))[0]
    learned_dict_id = Dictionary.objects.filter(Q(user_id=request.user) & Q(states='Изучены'))[0]
    unlearned_words = Term.objects.filter(dictionaries=unlearned_dict_id).values('id', 'term', 'transcript',
                                                                                 'translate', 'examples')
    if len(unlearned_words) == 0:
        return redirect('all_words_learned')

    random_id = randint(0, len(unlearned_words) - 1) if len(unlearned_words) > 1 else 0
    random_word = unlearned_words[random_id]


    request.session['unlearned_dict_id'] = unlearned_dict_id.pk
    request.session['learned_dict_id'] = learned_dict_id.pk
    request.session['unlearned_words'] = list(unlearned_words)
    request.session['check_word'] = random_word
    request.session['words_to_learn'] = []

    request.session.save()

    return render(request, 'vocabs/learn.html')


def check_quiz_word(request):
    n = request.session.get('unlearned_words')
    if request.method == 'POST':
        check_word = request.session.get('check_word')
        if 'learn' in request.POST:
            request.session['words_to_learn'].append(check_word)
            request.session.save()
        elif 'i_know' in request.POST:
            word_to_learned = Term.objects.get(id=check_word['id'])
            word_to_learned.dictionaries.remove(request.session.get('unlearned_dict_id'))
            word_to_learned.dictionaries.add(request.session.get('learned_dict_id'))


        request.session.get('unlearned_words').remove(check_word)
        unlearned_words = request.session.get('unlearned_words')
        if len(unlearned_words) > 1:
            random_id = randint(0, len(unlearned_words) - 1)
        else:
            random_id = 0


        if len(request.session['words_to_learn']) == 5 or not request.session.get('unlearned_words'):
            terms = Term.objects.all()
            for word in request.session['words_to_learn']:
                terms = terms.exclude(pk=word['id'])
            request.session['another_words'] = list(terms.values('id', 'term', 'transcript', 'translate'))
            request.session['answers'] = []
            return redirect('quiz')
        request.session['check_word'] = unlearned_words[random_id]
        request.session['unlearned_words'] = unlearned_words



    request.session.save()
    context = {
        'word': request.session['check_word'],
        'count': len(request.session['words_to_learn']) + 1,
    }
    return render(request, 'vocabs/check_quiz_word.html', context)


def quiz(request):
    if request.method == 'POST':
        sleep(1)
        word = request.session.get('check_word')
        user_answer = request.POST.get('word')
        if word['term'] == user_answer:
            answer = {
                'result': True,
                'word': word['term'],
                'answer': user_answer,
                'example': word['examples'],
            }
            word_to_learned = Term.objects.get(id=request.session.get('check_word')['id'])
            word_to_learned.dictionaries.remove(request.session.get('unlearned_dict_id'))
            word_to_learned.dictionaries.add(request.session.get('learned_dict_id'))
            request.session['answers'].append(answer)
        elif word['term'] != user_answer:
            answer = {
                'result': False,
                'word': word['term'],
                'answer': user_answer,
                'right_answer': word['translate'],
                'example': word['examples'],
            }
            request.session['answers'].append(answer)
        if not request.session.get('words_to_learn'):
            request.session.save()
            return redirect('quiz_result')

    random_words = sample(request.session.get('another_words'), 3)

    request.session['check_word'] = request.session.get('words_to_learn').pop()
    request.session.save()
    random_words.append(request.session['check_word'])
    shuffle(random_words)
    context = {
        'word': request.session['check_word'],
        'words': random_words
    }

    return render(request, 'vocabs/quiz.html', context)


def quiz_result(request):
    answers = request.session.get('answers')
    right_answers_count = sum(answer['result'] is True for answer in answers)
    context = {
        'answers': answers,
        'count': right_answers_count,
    }
    keys = ['unlearned_dict_id', 'learned_dict_id', 'unlearned_words', 'check_word', 'words_to_learn', 'another_words',
            'answers', 'words_to_repeat']

    request.session.save()

    return render(request, 'vocabs/quiz_result.html', context)


def all_words_learned(request):
    return render(request, 'vocabs/all_words_learned.html')


def repeat(request):
    learned_dict_id = Dictionary.objects.filter(Q(user_id=request.user) & Q(states='Изучены'))
    learned_words = list(Term.objects.filter(dictionaries__in=learned_dict_id).values('id', 'term', 'transcript',
                                                                                      'translate', 'examples'))
    all_words = list(Term.objects.values('id', 'term', 'transcript', 'translate', 'examples'))
    shuffle(all_words)
    shuffle(learned_words)
    request.session['words_to_repeat'] = learned_words
    request.session['all_words'] = all_words
    request.session['count'] = 0
    request.session['wrong_answers'] = []

    return render(request, 'vocabs/repeat.html')


def repeat_words(request):

    if request.method == 'POST':
        sleep(1)

        if 'result' in request.POST:
            return redirect('repeat_result')

        request.session['count'] += 1


        if (request.session['word'] == request.session['random']) and not eval(request.POST.get('choice')):
            request.session['wrong_answers'].append({
                'word': request.session['word'],
                'random': request.session['random'],
                'equal': True
            })

            if not request.session.get('words_to_repeat'):
                return redirect('repeat_result')

        elif (request.session['word'] != request.session['random']) and eval(request.POST.get('choice')):
            request.session['wrong_answers'].append({
                'word': request.session['word'],
                'random': request.session['random'],
                'equal': False
            })
            #если нет больше слов на повторение
            if not request.session.get('words_to_repeat'):
                return redirect('repeat_result')

        if not request.session.get('words_to_repeat'):
            return redirect('repeat_result')

        request.session.save()
    try:
        request.session['word'] = request.session.get('words_to_repeat').pop()
    except:
        return redirect('no_words_learned')
    request.session['random_word'] = request.session.get('all_words').pop()
    #print('words',request.session['word'])
    #print('randoms',request.session['random_word'])
    request.session['random'] = choices([request.session['word'], request.session['random_word']], [0.5,0.5])[0]
    #print('рандом',request.session['random'])
    request.session.save()
    context = {
        'word': request.session['word'],
        'random': request.session['random'],
    }

    return render(request, 'vocabs/repeat_words.html', context)


def repeat_result(request):
    count = request.session.get('count')
    wrong_answers = request.session.get('wrong_answers')


    context = {
        'count': count,
        'count_wrong': count - len(wrong_answers),
        'wrong_answers': wrong_answers,
    }
    return render(request, 'vocabs/repeat_result.html', context)


def no_words_learned(request):
    return render(request, 'vocabs/no_words_learned.html')


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Регистрация")
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        user = form.save()
        non_learned_dict = Dictionary(user_id_id=user.id, states='Не изучены')
        non_learned_dict.save()
        learned_dict = Dictionary(user_id_id=user.id, states='Изучены')
        learned_dict.save()
        terms = Term.objects.all()
        for t in terms:
            t.dictionaries.add(non_learned_dict)
        login(self.request, user)
        return redirect('main')


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Авторизация")
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('terms_list')


def logout_user(request):
    logout(request)
    return redirect('main')
