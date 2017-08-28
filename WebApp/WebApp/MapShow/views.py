# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
import json
import MapShow.db
import MapShow.business
from datetime import datetime
from operator import itemgetter

#from django.template import loader
# Create your views here.
def index(request):
    latest_question_list = [1,2,4,5,6]
    #template = loader.get_template('MapShow/index.html')
    DBS = MapShow.db.DBConnect()
    DBS.connect()



    d_t = DBS.getLatestDateTime()
    date_str = d_t[0].strftime('%Y-%m-%d')



    context = {
        'dt': date_str,'ti': int(d_t[1])
    }
    return render(request, 'MapShow/index.html', context)
    #return HttpResponse(template.render(context, request))

def quest(request):

    lat = None
    lon = None

    if request.method == 'POST':
        lat = request.POST.get('lat')
        lon = request.POST.get('lon')
        date = request.POST.get('date')
        hour = request.POST.get('hour')

        print('--------')
        print(lat)
        print(lon)
        print(date)

        date_str = date
        print(hour)
        print('--------')

    DBS = MapShow.db.DBConnect()
    DBS.connect()

    data = DBS.getSuburbCoordinates(lon,lat)

    DBS.close()
    j_data = [lon,lat]

    if data is not None and len(data) > 0:

        if data[0]['features'] is not None:
            suburb_id = data[0]['features'][0]['properties']['f1']

            process = MapShow.business.Process()
            terms = process.collect_words(suburb_id , date_str, hour)

            dataset = list(data)

            if terms is not None:
                wordsList = []

                for text, size in terms.items():
                    cur = {}
                    if size > 10:
                        cur['size'] = size * 100
                    else:
                        cur['size'] = size * 1000
                    cur['text'] = text
                    wordsList.append(cur)

                #data = json.dumps(data)

                dataset.append(wordsList[:20])

            data = json.dumps(dataset)
            print(data)
        else:
            data = json.dumps(data)
    else:
        data = json.dumps(data)

    return HttpResponse(data, content_type="application/json")


def prediction(request):

    DBS = MapShow.db.DBConnect()
    DBS.connect()

    d_t = DBS.getLatestDateTime()
    date_str = d_t[0].strftime('%Y-%m-%d')

    context = {
        'dt': date_str, 'ti': int(d_t[1])
    }

    return render(request, 'MapShow/prediction.html', context)

def estimation(request):

    if request.method == 'POST':
        text = request.POST.get('text')
        date = request.POST.get('date')
        hour = request.POST.get('hour')

        print('--------')

        print(text)
        print(date)
        print(hour)

        process = MapShow.business.Process()

        process.collect_allwords(date, hour)
        # print(process.checkResult())
        tfidftable = process.tf_idf_table()
        if tfidftable == None:
            data = None
            return HttpResponse(data, content_type="application/json")
        Query = text.split(' ')
        Q = process.GenerateQueryDoc(Query)
        Ranking = process.RankCosineSimilarities(Q, tfidftable)

        sql_parameter = [ x[0] for x in Ranking[:5] if float(x[1]) > 0 ]

        data = {}
        new_rank_list = []

        if (len(sql_parameter) > 0):

            print(sql_parameter.__str__())

            DBS = MapShow.db.DBConnect()
            DBS.connect()

            data = DBS.getMultipleSuburbCoordinates(sql_parameter)

            DBS.close()

            rank_list = []
            for d in data[0]['features']:
                newdict = d['properties']
                for x in Ranking[:5]:
                    if newdict['f1'] == x[0]:
                        newdict['f5'] = x[1]
                        rank_list.append(newdict)

            new_rank_list = sorted(rank_list, key=itemgetter('f5'), reverse=True)

            data= list(data)
            data.append(new_rank_list)


        data = json.dumps(data)




    return HttpResponse(data, content_type="application/json")