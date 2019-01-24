from django.shortcuts import render, get_object_or_404
from .models import Question, Survey
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.files.storage import default_storage
from django.conf import settings
from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import ColumnChart

import os

def survey(request):
	for question in Question.objects.all():
		if default_storage.exists(question.question_img) == False:
			question.question_img = os.path.join(settings.MEDIA_ROOT,'check.png')
			question.save()

	context = {
		'questions' : Question.objects.all(),
		'title' : 'Survey!',
		'survey': Survey.objects.first()
	}

	return render(request,'survey/home.html' ,context)

def results(request):
	charts =  []

	for question in Question.objects.all():
		data=[]
		data.append(['answer', 'Votos'])
		for answer in question.answer_set.all():
			list_tmp=[]
			list_tmp.append(answer.answer_txt)
			list_tmp.append(answer.answer_votes)
			data.append(list_tmp)
		charts.append(ColumnChart(SimpleDataSource(data=data),
			options={
						'title': str(question.question_txt),
						'legend': { 'position': 'bottom' },
						'titleTextStyle': {'color': 'black', 'fontSize':22},
						'colors': ['#ff9400']
 					}))

	context = {
		'questions' : Question.objects.all(),
		'title' : 'Survey Results',
		'survey': Survey.objects.first(),
		'charts' : charts,
	}

	return render(request, 'survey/results.html', context)

def submitVote(request, survey_id):
	survey = get_object_or_404(Survey, pk=survey_id)
	for question in survey.question_set.all():
		answered = question.answer_set.get(pk=request.POST['answer'+str(question.id)])
		answered.answer_votes += 1
		answered.save()

	survey.amount_votes +=1
	survey.save()
	return HttpResponseRedirect(reverse('survey:survey-results'))
