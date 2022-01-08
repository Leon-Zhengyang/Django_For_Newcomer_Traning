from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.http import HttpResponse
from django.db import transaction

from .models import Choice, Question

# 一覧画面遷移
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:10]

# 詳細画面遷移
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    vote_start = get_vote_start(question_id)

    return render(request, 'polls/detail.html', {
        'question': question,
        'vote_start':vote_start,
        })

# 投票開始かを判断するメソッド
def get_vote_start(question_id):
    question = get_object_or_404(Question, pk=question_id)
    vote_start = False
    for choice in question.choice_set.all():
        if choice.votes > 0:
            vote_start = True
            break
    return vote_start

# 編集画面遷移
def edit(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    choices_q = question.choice_set.all()
    choices=[]
    for choice in choices_q:
        choices.append(choice)
    count_len = len(choices)
    for count_len in range(count_len,4):
        choices.append("")
    print(question)
    return render(request, 'polls/edit.html', {
        'question': question,
        'Choices':choices,
        })

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

# 投票機能
def vote(request, question_id):
    if request.method == 'POST':
        if 'goBack' in request.POST:
            return HttpResponseRedirect(reverse('polls:index'))
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        vote_start = get_vote_start(question_id)
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_messages': "１つを選択してください。",
            'vote_start':vote_start,
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:detail', args=(question.id,)))

# 投票結果（使わない）
def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {
        'question': question
        })
    # return render(request, 'polls/results.html', {'question': question})

# 新規作成画面遷移
def ToCreate(request):
    return render(request, 'polls/create.html')

# 選択肢は重複チェック
def has_duplicates(seq):
    return len(seq) != len(set(seq))

# 新規登録機能
@transaction.atomic 
def regist(request):
    if request.method == 'POST':
        if 'goBack' in request.POST:
            return HttpResponseRedirect(reverse('polls:index'))
    error_messages = []
    myQuestion1 = request.POST.get('myQuestion1', "")
    double_check=Question.objects.filter(question_text=myQuestion1).count()
    if double_check > 0:
        error_messages.append("この質問既に存在しています。")
    if len(myQuestion1.strip()) ==0:
        error_messages.append("質問を入力してください。")
    choices = []
    count = 0
    duplicate = False
    duplicate_choice = []
    choices.append(request.POST.get('myChoice1', ""))
    choices.append(request.POST.get('myChoice2', ""))
    choices.append(request.POST.get('myChoice3', ""))
    choices.append(request.POST.get('myChoice4', ""))
    
    for choice in choices:
        if len(choice.strip()) !=0:
            count += 1
            duplicate_choice.append(choice)
    duplicate = has_duplicates(duplicate_choice)
    if duplicate is True:
        error_messages.append("選択肢を重複しないように登録してください。")
    
    if count < 2:
        error_messages.append("選択肢を２つ以上入力してください。")
    if len(error_messages) > 0:
        return render(request, 'polls/create.html', {
            'error_messages': error_messages,
            'myQuestion1':myQuestion1,
            'Choices':choices,
        })
    if len(error_messages) == 0:
        q = Question(question_text=myQuestion1, pub_date=timezone.now())
        q.save()
        for choice in choices:
            if len(choice.strip()) !=0:
                q.choice_set.create(choice_text=choice, votes=0)
        
    return HttpResponseRedirect(reverse('polls:index'))

# 編集機能
@transaction.atomic 
def update(request, question_id):
    if request.method == 'POST':
        if 'goBack' in request.POST:
            question = get_object_or_404(Question, pk=question_id)
            vote_start = get_vote_start(question_id)
            return render(request, 'polls/detail.html', {
                            'question': question,
                            'vote_start':vote_start,
                        })
    error_messages = []
    myQuestion1 = request.POST.get('myQuestion1', "")
    if len(myQuestion1.strip()) ==0:
        error_messages.append("質問を入力してください。")

    double_check=Question.objects.exclude(pk=question_id).filter(question_text=myQuestion1).count()
    print(double_check)
    if double_check > 0:
        error_messages.append("この質問既に存在しています。")
    choices = []
    count = 0
    duplicate = False
    duplicate_choice = []
    choices.append(request.POST.get('myChoice1', ""))
    choices.append(request.POST.get('myChoice2', ""))
    choices.append(request.POST.get('myChoice3', ""))
    choices.append(request.POST.get('myChoice4', ""))
    
    for choice in choices:
        if len(choice.strip()) !=0:
            count += 1
            duplicate_choice.append(choice)
    duplicate = has_duplicates(duplicate_choice)
    if duplicate is True:
        error_messages.append("選択肢を重複しないように登録してください。")
    
    if count < 2:
        error_messages.append("選択肢を２つ以上入力してください。")
    
    if len(error_messages) > 0:
        question = get_object_or_404(Question,pk=question_id)
        return render(request, 'polls/edit.html', {
            'error_messages': error_messages,
            'question':question,
            'Choices':choices,
        })
    if len(error_messages) == 0:
        question_old = get_object_or_404(Question, pk=question_id)
        question_old.question_text=myQuestion1
        Choice.objects.filter(question=question_old).delete()
        question_old.save()
        for choice in choices:
            if len(choice.strip()) !=0:
                question_old.choice_set.create(choice_text=choice, votes=0)
        
    return HttpResponseRedirect(reverse('polls:index'))

