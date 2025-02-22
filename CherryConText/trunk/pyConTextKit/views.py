#Copyright 2010 Annie T. Chen
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
"""
This module contains the views that are used in the pyConTextKit application.
"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout
from django.db.models import Count
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
import csv
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#connection for raw sql
from pyConTextKit.models import *
from pyConTextKit.runConText import runConText
from pyConTextKit.forms import *
from dataParser import *
from pyConTextKit.models import *
from settings import CherryConTextHome
import re
import time
import gzip
import cPickle
import datetime

from django.forms.models import modelformset_factory

@login_required
def index(request):
    """
    This in the index page.
    """
    #the following lines of code loads the settings in itemDatumSet as the default
    #criterion set
    #itemDatum.objects.all().update(include=0)
    #testset = itemDatumSet.objects.filter(setname__contains="SO")
    #for i in testset:
    #    j = itemDatum.objects.get(pk=i.itemDatum_id)
    #    print j.id, j.include, i.include
    #    j.include = i.include
    #    j.save()
    return render_to_response('pyConTextKit/index.html',context_instance=RequestContext(request))
@csrf_protect
@login_required
def logout_view(request):
    """
    This logs the user out of the application.
    """
    logout(request)
    return render_to_response('registration/logout.html',context_instance=RequestContext(request))
@csrf_protect
@login_required
def run(request):
    """
    This executes the Annotate feature.
    """
    if request.method == "POST":
        rform = RunForm(data = request.POST)
        if rform.is_valid():
            dataset = rform.cleaned_data['dataset']
            #limit = rform.cleaned_data['limit']
            label = rform.cleaned_data['label']
            labelDomain = rform.cleaned_data['labelDomain']
            outputLabel = rform.cleaned_data['outputLabel']

            filelocation = runConText(CherryConTextHome,dataset,label,labelDomain)
            s = Result.objects.create(label=outputLabel,path=filelocation,date=int(time.time()))
            s.save()
            #populate the database with value and other info

            return HttpResponseRedirect(reverse('pyConTextKit.views.complete'))
        else:
            rform=RunForm()
    else:
        rform=RunForm()

    return render_to_response('pyConTextKit/run.html', {'form': rform,},context_instance=RequestContext(request))

@csrf_protect
@login_required
def complete(request):
    """
    This page is rendered by the run view when the Annotate feature is finished.
    """
    return render_to_response('pyConTextKit/complete.html',context_instance=RequestContext(request))

"""
	UPDATED 7/27/12 G.D.
	Changed reference from itemDatum object to Lexical object, formset shares same names w/ Lexical's
	names, they did not need modification. (Line 122, Declaration of formset)
"""
@csrf_protect
@login_required
def itemData_view(request):
    itemFormSet = modelformset_factory(Items, fields=('id',), extra=0)
    sform = SearchForm(data = request.POST)

    domain = ""
    linguistic = ""
    item_array = Items.objects.all().values_list("lex_type","label").distinct()
    for i in item_array:
    	if i[0] == "domain":
    		domain += "<a style='margin-left:5px;' href='/pyConTextKit/itemData_filter/"+i[1]+"'/>"+i[1]+"</a>"
    	elif i[0] == "linguistic":
    		linguistic += "<a style='margin-left:5px;' href='/pyConTextKit/itemData_filter/"+i[1]+"'/>"+i[1]+"</a>"

    if request.method == "POST" and sform.is_valid():
        term = sform.cleaned_data['term']
        if term != '':
            #print "non-space"
            #literal__contains looks at field, literal and checks against term
            formset = itemFormSet(queryset = Items.objects.filter(literal__contains=term))
            return render_to_response('pyConTextKit/itemdata.html',{'formset': formset, 'form': sform, 'domain': domain, 'linguistic':linguistic},context_instance=RequestContext(request))
        else:
            formset = itemFormSet(request.POST, request.FILES)
            if formset.is_valid():
                formset.save()
                return HttpResponseRedirect(reverse('pyConTextKit.views.itemData_complete'))
    formset = itemFormSet()
    return render_to_response("pyConTextKit/itemdata.html", {
        "formset": formset,'form': sform,'domain': domain, 'linguistic':linguistic}, context_instance=RequestContext(request))

"""
	UPDATED 7/27/12 G.D.
	Removed supercategory and replaced w/ category, not sure if we want this method anymore
"""
@csrf_protect
@login_required
def itemData_filter(request, cat):
    """
    This method takes a supercategory name as an argument and renders a view of
    the criteria in this supercategory.
    """
    domain = ""
    linguistic = ""
    item_array = Items.objects.all().values_list("lex_type","label").distinct()
    for i in item_array:
    	if i[0] == "domain":
    		domain += "<a style='margin-left:5px;' href='/pyConTextKit/itemData_filter/"+i[1]+"'/>"+i[1]+"</a>"
    	elif i[0] == "linguistic":
    		linguistic += "<a style='margin-left:5px;' href='/pyConTextKit/itemData_filter/"+i[1]+"'/>"+i[1]+"</a>"

    itemFormSet = modelformset_factory(Items, fields=('id',), extra=0)
    sform = SearchForm(data = request.POST)
    formset = itemFormSet(queryset=Items.objects.filter(label=cat))
    return render_to_response('pyConTextKit/itemdata.html',{'formset': formset,'form': sform,'domain': domain, 'linguistic':linguistic},context_instance=RequestContext(request))

"""
	UPDATED 7/27/12
	Changed reference from itemDatum to Lexical
"""
@csrf_protect
@login_required
def itemData_edit(request, itemData_id=None):
    cat_items_temp = Items.objects.all().values_list("category").distinct()
    cat_items = ()
    for i in range(0,len(cat_items_temp)):
        new_string = str(cat_items_temp[i][0])
        cat_items = cat_items + (new_string,)
    """
    This method takes an Lexical ID as an argument and renders a form for the
    user to edit the specified extraction criterion.  If no argument is supplied,
    a blank form is rendered, which the user can use to enter a new criterion.

    Note: A useful addition to this would be examples that the user can use as
    a reference.
    """
    intro="""<style type="text/css">
    .indent{
    	margin-left:15px;
    }
    </style>
    <p>This application employs Python regular expressions. Refer to the key below
    for guidance on how to create regular expressions.<p><b>\s:</b> space<br><b>|:</b> or<br>
    <b>\w:</b> alphanumeric character or underscore (equivalent to [a-zA-Z0-9_])<br>
    <b>*:</b> match one or more repetitions of the preceding regular expression<br>
    <b>?:</b> matches 0 or 1 of the preceding regular expressions<br>
    You can learn more about Python regular expressions at:
    <a href="http://docs.python.org/library/re.html">http://docs.python.org/library/re.html</a>"""
    dup = ""
    iform = itemForm(request.POST or None,instance=itemData_id and Items.objects.get(id=itemData_id))
    if request.method == "POST" and iform.is_valid():
    	items = Items.objects.filter(literal__contains=iform.cleaned_data['literal'])
    	if items.count() > 0 and 'submit2' not in request.POST:
    	    dup = "<span style=\"color:red\"><b>"+str(items.count())+"</b> Duplicate(s) detected</span><br />"
    	    dup += "<div class=\"indent\">"
    	    for i in items:
    	        dup += re.sub(r'('+iform.cleaned_data['literal']+')', r'<b style=\"color:green;\">\1</b>', i.literal, flags=re.I)+"<br />"
    	    dup += """</div><br />What would you like to do?<br />
    	    <div class="indent">
    	    <ul>
    	    <li><input type="submit" name="submit2" value="Ignore, and post item" /></li>
    	    <li>Make edits to item below, and resubmit.</li>
    	    <li><a href="/pyConTextKit/itemData_edit">Reset form</a></li>
    	    </ul>
    	    </div>
    	    """
    	    return render_to_response('pyConTextKit/itemdata_edit.html', {'form': iform, 'intro': intro, 'dup':dup, 'cat_items':cat_items}, context_instance=RequestContext(request))
    	else:
            iform.save()
        return HttpResponseRedirect(reverse('pyConTextKit.views.itemData_complete'))

    return render_to_response('pyConTextKit/itemdata_edit.html', {'form': iform, 'intro': intro, 'dup':dup, 'cat_items':cat_items}, context_instance=RequestContext(request))

@csrf_protect
@login_required
def itemData_complete(request):
    return render_to_response('pyConTextKit/itemdata_complete.html',context_instance=RequestContext(request))

@csrf_protect
@login_required
def output_results(request):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=results.csv'

    writer = csv.writer(response)
    results=Result.objects.all()
    writer.writerow(['id', 'label', 'path', 'date'])
    for r in results:
        writer.writerow([smart_str(r.id), smart_str(r.label), smart_str(r.path), smart_str(r.date)])
    return response

@csrf_protect
@login_required
def reports(request):
    report_list=Report.objects.all()
    paginator = Paginator(report_list, 50) # Show N reports per page
    page = int(request.GET.get('page','1'))
    try:
        reports = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reports = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        reports = paginator.page(paginator.num_pages)

    return render_to_response('pyConTextKit/reports.html', {"report": reports},context_instance=RequestContext(request))

@csrf_protect
@login_required
def report_detail(request, reportid):
    try:
        r = Report.objects.get(id=reportid)
    except Report.DoesNotExist:
        raise Http404
    return render_to_response('pyConTextKit/report_detail.html',{'report': r},context_instance=RequestContext(request))

@csrf_protect
@login_required
def alerts(request):
    if request.method == "POST":
        rform = DocClassForm(data = request.POST)
        if rform.is_valid():
            limit_pos = rform.cleaned_data['limit_pos']
            uncertainty = rform.cleaned_data['uncertainty']
            limit_new = rform.cleaned_data['limit_new']
            if limit_pos:
                if uncertainty=='separate_uncertainty':
                    if limit_new:
                        print "here"
                        r=Result.objects.values('reportid','category','disease','uncertainty','historical').filter(disease="Pos").filter(historical="New").annotate(Count('id'))
                        print r
                    else:
                        r=Result.objects.values('reportid','category','disease','uncertainty','historical').filter(disease="Pos").annotate(Count('id'))
                elif uncertainty=='allow_uncertainty':
                    if limit_new:
                        r=Result.objects.values('reportid','category','disease','historical').filter(disease="Pos").filter(historical="New").annotate(Count('id'))
                    else:
                        r=Result.objects.values('reportid','category','disease','historical').filter(disease="Pos").annotate(Count('id'))
                else:
                    if limit_new:
                        r=Result.objects.values('reportid','category','disease','historical').filter(disease="Pos").filter(uncertainty="No").filter(historical="New").annotate(Count('id'))
                    else:
                        r=Result.objects.values('reportid','category','disease','historical').filter(disease="Pos").filter(uncertainty="No").annotate(Count('id'))
            else:
                if uncertainty=='separate_uncertainty':
                    if limit_new:
                        r=Result.objects.values('reportid','category','disease','uncertainty','historical').filter(historical="New").annotate(Count('id'))
                    else:
                        r=Result.objects.values('reportid','category','disease','uncertainty','historical').annotate(Count('id'))
                elif uncertainty=='allow_uncertainty':
                    if limit_new:
                        r=Result.objects.values('reportid','category','disease','historical').filter(historical="New").annotate(Count('id'))
                    else:
                        r=Result.objects.values('reportid','category','disease','historical').annotate(Count('id'))
                else:
                    if limit_new:
                        r=Result.objects.values('reportid','category','disease','historical').filter(uncertainty="No").filter(historical="New").annotate(Count('id'))
                    else:
                        r=Result.objects.values('reportid','category','disease','historical').filter(uncertainty="No").annotate(Count('id'))

            return render_to_response('pyConTextKit/alerts.html',{'alert': r},context_instance=RequestContext(request))
        else:
            print rform.errors
            print "error"

    else:
        rform=DocClassForm()

    return render_to_response('pyConTextKit/run_alert.html', {'form': rform,},context_instance=RequestContext(request))

@csrf_protect
@login_required
def results(request):
    r=Result.objects.all()
    return render_to_response('pyConTextKit/results.html',{'result': r},context_instance=RequestContext(request))

@csrf_protect
@login_required
def result_detail(request, result_id):
    try:
        r = Result.objects.get(id=result_id)
    except Result.DoesNotExist:
        raise Http404
    return render_to_response('pyConTextKit/result_detail.html', {'result': r},context_instance=RequestContext(request))

@csrf_protect
@login_required
def report_text(request, reportid):
    if request.is_ajax() and request.method == 'POST':
        report = Report.objects.get(pk=request.POST.get('reportid', ''))
    return render_to_response('pyConTextKit/report_test.html', {'report':report}, context_instance=RequestContext(request))

@csrf_protect
@login_required
def ajax_user_search( request ):
    if request.is_ajax():
        q = request.GET.get( 'q' )
        if q is not None:
            results = Report.objects.get(pk=q)
            template = 'pyConTextKit/report_test.html'
            data = {
                'results': results,
            }
            return render_to_response( template, data,
                                       context_instance = RequestContext( request ) )

@csrf_protect
@login_required
def upload_csv(request, formType=None):
    status = ''
    uploadDbFormReports = UploadDatabaseReports(request.POST, request.FILES)
    uploadDbFormLexicon = UploadDatabaseLexicon(request.POST, request.FILES)
    if formType is not None:
    	if formType == "report":
            if request.method == 'POST':
                if uploadDbFormReports.is_valid():
                    res = handle_uploaded_reports_file(request.FILES['csvfile'], uploadDbFormReports.cleaned_data['dataset'])
                    #uploadDbFormReports.save()
                    if len(res) > 0:
                    	status = "<span style=\"color:red;\">The following errors occured:<br /><ul>"
                    	for i in res:
                    		status += "<li>"+i+"</li>"
                    	status += "</ul></span>"
                    else:
                    	status = "<b style=\"color:green;\">Report uploaded successfully</b>"
                else:
                    status = "<b style=\"color:red;\">Report: Please fix errors before proceeding</b>"
                return render_to_response('pyConTextKit/upload_db.html',{'status': status, 'form_reports': uploadDbFormReports, 'state': True, 'formType': formType},context_instance=RequestContext(request))
            else:
                uploadDbFormReports = UploadDatabaseReports()
                return render_to_response('pyConTextKit/upload_db.html',{'status': status, 'form_reports': uploadDbFormReports, 'state': True, 'formType': formType},context_instance=RequestContext(request))

        elif formType == "lexicon":       #===LEXICON===
            if request.method == 'POST':
                if uploadDbFormLexicon.is_valid():
                    lex_type = uploadDbFormLexicon.cleaned_data['like']
                    res = handle_uploaded_lexical_file(request.FILES['csvfile'], uploadDbFormLexicon.cleaned_data['label'], "lexicon", lex_type=lex_type)
                    #uploadDbFormLexicon.save()
                    if len(res) > 0:
                    	status = "<span style=\"color:red;\">The following errors occured:<br /><ul>"
                    	for i in res:
                    		status += "<li>"+i+"</li>"
                    	status += "</ul></span>"
                    else:
                    	status = "<b style=\"color:green;\">Lexicon uploaded successfully</b>"
                else:
                    status = "<b style=\"color:red;\">Lexicon: Please fix errors before proceeding</b>"
                return render_to_response('pyConTextKit/upload_db.html',{'status': status, 'form_lexicon': uploadDbFormLexicon, 'state': True, 'formType': formType},context_instance=RequestContext(request))
            else:
                uploadDbFormLexicon = UploadDatabaseLexicon()
                return render_to_response('pyConTextKit/upload_db.html',{'status': status, 'form_lexicon': uploadDbFormLexicon, 'state': True, 'formType': formType},context_instance=RequestContext(request))
        else:
        	return render_to_response('pyConTextKit/upload_db.html',{'status': status, 'state': False},context_instance=RequestContext(request))
    else:
         return render_to_response('pyConTextKit/upload_db.html',{'status': status, 'state': False},context_instance=RequestContext(request))

def handle_uploaded_reports_file(f, label):
    user_home = os.path.expanduser('~')
    CherryConTextHome = os.path.join(user_home,'CherryConText','pyConTextKit','templates','media','csvuploads') #this needs to be modifed to accomodate othe user's home directory
    destPath = os.path.join(CherryConTextHome,str(int(round(time.time() * 1000)))+'.txt')
    destination = open(destPath,'wb+')
    for chunk in f.chunks():
            destination.write(chunk)
    destination.close()
    #then implement the csvparser class here
    c = reportParser(destPath, label)
    c.uploadReports("","")
    return c.returnIssues() #updates DB with table information
def handle_uploaded_lexical_file(f, label, type, lex_type=None):
    user_home = os.path.expanduser('~')
    CherryConTextHome = os.path.join(user_home,'CherryConText','pyConTextKit','templates','media','csvuploads') #this needs to be modifed to accomodate othe user's home directory
    destPath = os.path.join(CherryConTextHome,str(int(round(time.time() * 1000)))+'.csv')
    destination = open(destPath,'wb+')
    for chunk in f.chunks():
            destination.write(chunk)
    destination.close()
    #then implement the csvparser class here
    c = lexicalParser(destPath, label, lex_type=lex_type)
    c.uploadData()
    return c.returnIssues() #updates DB with table information

@csrf_protect
@login_required
def hide(request, idp, idp2):
    item = Items.objects.get(id=idp)
    item.show = '0'
    item.save()
    return HttpResponseRedirect('/pyConTextKit/itemData/#'+str(idp2))

@csrf_protect
@login_required
def show(request, idp, idp2):
    if idp == "showall":
        items = Items.objects.all()
        for i in items:
            i.show = '1'
            i.save()
    elif idp == "hideall":
        items = Items.objects.all()
        for i in items:
            i.show = '0'
            i.save()
    else:
        item = Items.objects.get(id=idp)
        item.show = '1'
        item.save()

    return HttpResponseRedirect('/pyConTextKit/itemData/#'+str(idp2))

@csrf_protect
@login_required
def resultVisualize(request, idp):
    result = Result.objects.get(id=idp)
    fo = gzip.open(result.path,"rb")

    t = datetime.datetime.fromtimestamp(int(result.date))
    date = t.strftime('%m/%d/%Y at %H:%M')

    output = ""
    output += str(cPickle.load(fo))

    return render_to_response('pyConTextKit/visualize.html',{ 'output':output,'result':result, 'date':date },context_instance=RequestContext(request))

@csrf_protect
@login_required
def reports_index(request):
	return render_to_response('pyConTextKit/reports_index.html',context_instance=RequestContext(request))

@csrf_protect
@login_required
def annotation_index(request):
	return render_to_response('pyConTextKit/annotation_index.html',context_instance=RequestContext(request))
