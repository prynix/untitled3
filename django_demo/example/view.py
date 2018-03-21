#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Created by yaochao at 2018/3/20


from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from django_demo.misc.diagnosis_name_split import get_all_split_name


def hello(request):
    return HttpResponse("Hello world!")


def hello2(request):
    students = ['yaochao', 'dengqx', 'xusha', 'lln']
    context = {
        'students': students
    }
    return render(request, 'hello.html', context)


class DiagnosisAPI(APIView):
    def get(self, request, *args, **kwargs):
        r = {
            'name': 'yaochao',
            'sex': 'male',
            'age': '28',
        }
        return JsonResponse(r)

    def post(self, request, *args, **kwargs):
        result = {}
        params = request.data
        if not isinstance(params, list):
            result['message'] = 'must be a list'
            result['status'] = 401
            return JsonResponse(result)
        try:
            names = get_all_split_name(params)
            result['message'] = 'success'
            result['status'] = 200
            result['resource'] = names
            return JsonResponse(result)
        except Exception as e:
            print(e)
            result['message'] = e.__str__()
            result['status'] = 402
        return JsonResponse(result)
