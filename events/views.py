from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages

from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt

from django.http import Http404
from django.db.models import Q

from urlparse import urlparse

from BeautifulSoup import BeautifulSoup

import xml.etree.cElementTree as etree
from django.conf import settings
import json
import os
import os.path
import urllib,urllib2

from events.models import *
from cms.models import Profile

from forms import *
import datetime
from django.utils import formats
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#pdf generate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from PyPDF2 import PdfFileWriter, PdfFileReader
from StringIO import StringIO

#randon string
import string
import random

from  filters import *

from cms.sortable import *
from events_email import send_email

@login_required
def init_events_app(request):
    try:
        # Group
        if Group.objects.filter(name = 'Resource Person').count() == 0:
            Group.objects.create(name = 'Resource Person')
        if Group.objects.filter(name = 'Organiser').count() == 0:
            Group.objects.create(name = 'Organiser')
        if Group.objects.filter(name = 'Invigilator').count() == 0:
            Group.objects.create(name = 'Invigilator')
        
        #testcategory
        try:
            TestCategory.objects.get_or_create(name= 'Workshop')
            TestCategory.objects.get_or_create(name= 'Training')
            TestCategory.objects.get_or_create(name= 'Others')
        except Exception, e:
            print e, "test_category"
        
        try:
            InstituteType.objects.get_or_create(name= 'Workshop')
            InstituteType.objects.get_or_create(name= 'Training')
            InstituteType.objects.get_or_create(name= 'ITI')
            InstituteType.objects.get_or_create(name= 'Vocational')
            InstituteType.objects.get_or_create(name= 'School')
            InstituteType.objects.get_or_create(name= 'Uncategorized')
        except Exception, e:
            print e, "institute_type"
        
        #institutecategory
        try:
            InstituteCategory.objects.get_or_create(name= 'Govt')
            InstituteCategory.objects.get_or_create(name= 'Private')
            InstituteCategory.objects.get_or_create(name= 'NGO')
            InstituteCategory.objects.get_or_create(name= 'Uncategorized')
        except Exception, e:
            print e, "InstituteCategory"
            
        #permissiontype
        try:
            PermissionType.objects.get_or_create(name= 'State')
            PermissionType.objects.get_or_create(name= 'District')
            PermissionType.objects.get_or_create(name= 'University')
            PermissionType.objects.get_or_create(name= 'Institution Type')
            PermissionType.objects.get_or_create(name= 'Institution')
        except Exception, e:
             print e, "PermissionType"
        
        #state
        state = None
        try:
            state = State.objects.get_or_create(name= 'Uncategorized')
        except Exception, e:
             print e, "State"
        #District
        try:
            District.objects.get_or_create(name= 'Uncategorized', state_id = state[0].id)
        except Exception, e:
             print e, "District"
        
        #City
        try:
            City.objects.get_or_create(name= 'Uncategorized', state_id = state[0].id)
        except Exception, e:
             print e, "City"
        
        #University
        try:
            University.objects.get_or_create(name= 'Uncategorized', state_id = state[0].id, user_id = 1)
        except Exception, e:
             print e, "University"
             
        messages.success(request, 'Events application initialised successfully!')
    except Exception, e:
        messages.error(request, str(e))
    return HttpResponseRedirect('/software-training/')

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def is_event_manager(user):
    """Check if the user is having event manger  rights"""
    if user.groups.filter(name='Event Manager').count() == 1:
        return True
        
def is_resource_person(user):
    """Check if the user is having resource person  rights"""
    if user.groups.filter(name='Resource Person').count() == 1:
        return True
        
def is_organiser(user):
    """Check if the user is having organiser rights"""
    try:
        if user.groups.filter(name='Organiser').count() == 1 and user.organiser and user.organiser.status == 1:
            return True
    except:
        pass

def is_invigilator(user):
    """Check if the user is having invigilator rights"""
    if user.groups.filter(name='Invigilator').count() == 1 and user.invigilator and user.invigilator.status == 1:
        return True
def get_page(resource, page):
    paginator = Paginator(resource, 20)
    try:
        resource =  paginator.page(page)
    except PageNotAnInteger:
        resource =  paginator.page(1)
    except EmptyPage:
        resource = paginator.page(paginator.num_pages)
    return resource

def search_participant( form):
    if form.is_valid():
        onlinetest_user = {}
        if form.cleaned_data['email']:
            onlinetest_user  = MdlUser.objects.filter(email = form.cleaned_data['email'])
        #else:
        #    onlinetest_user  = MdlUser.objects.filter(Q(username__icontains = form.cleaned_data['username']) | Q(firstname__icontains = form.cleaned_data['username']))
        if not onlinetest_user:
            onlinetest_user = 'None'
        return onlinetest_user
        
def add_participant(request, cid, category ):
    userid = request.POST['userid']
    if userid:
        if category == 'Training':
            try:
                wa = TrainingAttendance.objects.get(mdluser_id = userid, training_id = cid)
                print wa.id, " => Exits"
                messages.success(request, "User has already in the attendance list")
            except:
                wa = TrainingAttendance()
                wa.training_id = cid
                wa.mdluser_id = userid
                wa.status = 0
                wa.save()
                messages.success(request, "User has added in the attendance list")
                print wa.id, " => Inserted"
        elif category == 'Training':
            try:
                wa = TrainingAttendance.objects.get(mdluser_id = userid, training_id = cid)
                print wa.id, " => Exits"
                messages.success(request, "User has already in the attendance list")
            except:
                wa = TrainingAttendance()
                wa.training_id = cid
                wa.mdluser_id = userid
                wa.status = 0
                wa.save()
                messages.success(request, "User has added in the attendance list")
                print wa.id, " => Inserted"
                
        elif category == 'Test':
            try:
                wa = TestAttendance.objects.get(mdluser_id = userid, test_id = cid)
                print wa.id, " => Exits"
                messages.success(request, "User has already in the attendance list")
            except:
                wa = TestAttendance()
                wa.test_id = cid
                wa.mdluser_id = userid
                wa.status = 0
                wa.save()
                messages.success(request, "User has added in the attendance list")
                print wa.id, " => Inserted"

def fix_date_for_first_training(request):
    organisers = Organiser.objects.exclude(id__in = Training.objects.values_list('organiser_id').distinct())
    if organisers:
        status = 'Fix a date for your first training'
        for o in organisers:
            to = o.user.email
            send_email(status, to)
    return HttpResponse("Done!")

def training_gentle_reminder(request):
    tomorrow_training = Training.objects.filter(trdate=datetime.date.today() + datetime.timedelta(days=1))
    if tomorrow_training:
        status = 'How to upload the attendance on the training day'
        for t in tomorrow_training:
            to = t.organiser.user.email
            send_email(status, to, t)
    return HttpResponse("Done!")

@login_required
def events_dashboard(request):
    user = request.user
    user_roles = user.groups.all()
    roles = []
    events_roles = ['Resource Person', 'Organiser', 'Invigilator']
    for role in user_roles:
        if role.name in events_roles:
            roles.append(role.name)
    #print roles
    organiser_workshop_notification = None
    organiser_test_notification = None
    invigilator_test_notification = None
    organiser_training_notification = None
    rp_workshop_notification = None
    rp_test_notification = None
    rp_training_notification = None
    if is_organiser(user):
        organiser_test_notification = EventsNotification.objects.filter((Q(status = 1) | Q(status = 2)), category = 1, academic_id = user.organiser.academic_id, categoryid__in = user.organiser.academic.test_set.filter(organiser_id = user.id).values_list('id')).order_by('-created')
        #organiser_training_notification = EventsNotification.objects.filter((Q(status = 1) | Q(status = 3)), category = 2, status = 1, academic_id = user.organiser.academic_id, categoryid__in = user.organiser.academic.workshop_set.filter(organiser_id = user.id).values_list('id')).order_by('-created')

    if is_resource_person(user):
        rp_workshop_notification = EventsNotification.objects.filter((Q(status = 0) | Q(status = 5) | Q(status = 2)), category = 0).order_by('-created')
        rp_training_notification = EventsNotification.objects.filter((Q(status = 0) | Q(status = 5) | Q(status = 2)), category = 2).order_by('-created')
        rp_test_notification = EventsNotification.objects.filter((Q(status = 0) | Q(status = 4) | Q(status = 5) | Q(status = 8) | Q(status = 9)), category = 1, categoryid__in = (Training.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)))).values_list('id')).order_by('-created')
    if is_invigilator(user):
        invigilator_test_notification = EventsNotification.objects.filter((Q(status = 0) | Q(status = 1)), category = 1, academic_id = user.invigilator.academic_id, categoryid__in = user.invigilator.academic.test_set.filter(invigilator_id = user.id).values_list('id')).order_by('-created')
    context = {
        'roles' : roles,
        'organiser_workshop_notification' : organiser_workshop_notification,
        'organiser_test_notification' : organiser_test_notification,
        'organiser_training_notification' : organiser_training_notification,
        'rp_test_notification' : rp_test_notification,
        'rp_workshop_notification' : rp_workshop_notification,
        'rp_training_notification' : rp_training_notification,
        'invigilator_test_notification' : invigilator_test_notification,
    }
    return render(request, 'events/templates/events_dashboard.html', context)

@login_required
def delete_events_notification(request, notif_type, notif_id):
    notif_rec = None
    try:
        if notif_type == "organiser":
            notif_rec = EventsNotification.objects.select_related().get(pk = notif_id)
        elif notif_type == "invigilator":
            notif_rec = EventsNotification.objects.select_related().get(pk = notif_id)
        elif notif_type == "rp":
            notif_rec = EventsNotification.objects.select_related().get(pk = notif_id)
    except Exception, e:
        print e
        messages.warning(request, 'Selected notification is already deleted (or) You do not have permission to delete it.')
    if notif_rec:
        notif_rec.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def clear_events_notification(request, notif_type):
    notif_rec = None
    try:
        if notif_type == "organiser":
            notif_rec = EventsNotification.objects.filter(user = request.user).delete()
        elif notif_type == "invigilator":
            notif_rec = EventsNotification.objects.filter(user = request.user).delete()
        elif notif_type == "rp":
            notif_rec = EventsNotification.objects.filter(user = request.user).delete()
    except Exception, e:
        print e
        messages.warning(request, 'Something went wrong, contact site administrator.')

    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def new_ac(request):
    """ Create new academic center. Academic code generate by autimatic.
        if any code missing in between first assign that code then continue the serial
    """
    user = request.user
    if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page')
        
    if request.method == 'POST':
        form = AcademicForm(user, request.POST)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.user_id = user.id
            
            state = form.cleaned_data['state']
            # find the academic code available number
            try:
                ac = AcademicCenter.objects.filter(state = state).order_by('-academic_code')[:1].get()
            except:
                #print "This is first record"
                ac = None
                academic_code = 1
                
            if ac:
                code_range = int(ac.academic_code.split('-')[1])
                available_code_range = []
                for i in range(code_range):
                    available_code_range.insert(i, i+1)
                
                #find the existing numbers
                ac = AcademicCenter.objects.filter(state = state).order_by('-academic_code')
                for record in ac:
                    a = int(record.academic_code.split('-')[1])-1
                    available_code_range[a] = 0
                
                academic_code = code_range + 1
                #finding Missing number
                for code in available_code_range:
                    if code == 0:
                        academic_code = code
                        break

            # Generate academic code
            if academic_code < 10:
                ac_code = '0000'+str(academic_code)
            elif academic_code <= 99:
                ac_code = '000'+str(academic_code)
            elif academic_code <= 999:
                ac_code = '00'+str(academic_code)
            elif academic_code <= 9999:
                ac_code = '0'+str(academic_code)
            
            #get state code
            state_code = State.objects.get(pk = state.id).code
            academic_code = state_code +'-'+ ac_code
            
            form_data.academic_code = academic_code
            form_data.save()
            messages.success(request, form_data.institution_name+" has been added")
            return HttpResponseRedirect("/software-training/ac/")
        
        context = {'form':form}
        return render(request, 'events/templates/ac/form.html', context)
    else:
        context = {}
        context.update(csrf(request))
        context['form'] = AcademicForm(user=request.user)
        return render(request, 'events/templates/ac/form.html', context)

@login_required
def edit_ac(request, rid = None):
    """ Edit academic center """
    user = request.user
    if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page')
        
    if request.method == 'POST':
        contact = AcademicCenter.objects.get(id = rid)
        form = AcademicForm(request.user, request.POST, instance=contact)
        if form.is_valid():
            if form.save():
                return HttpResponseRedirect("/software-training/ac/")
        context = {'form':form}
        return render(request, 'events/templates/ac/form.html', context)
    else:
        try:
            record = AcademicCenter.objects.get(id = rid)
            context = {}
            context['form'] = AcademicForm(user=request.user, instance = record)
            context['edit'] = rid
            context.update(csrf(request))
            return render(request, 'events/templates/ac/form.html', context)
        except:
            raise Http404('Page not found')

@login_required
def ac(request):
    """ Academic index page """
    user = request.user
    if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page')
        
    context = {}
    header = {
        1: SortableHeader('State', False),
        2: SortableHeader('university__name', True, 'University'),
        3: SortableHeader('institution_name', True, 'Institution Name'),
        4: SortableHeader('institution_type__name', True, 'Institute Type'),
        5: SortableHeader('institute_category__name', True, 'Institute Category'),
        6: SortableHeader('Action', False)
    }
    
    collectionSet = AcademicCenter.objects.filter(state = user.resource_person.all())
    raw_get_data = request.GET.get('o', None)
    collection = get_sorted_list(request, collectionSet, header, raw_get_data)
    ordering = get_field_index(raw_get_data)
    
    collection = AcademicCenterFilter(request.GET, user = user, queryset=collection)
    context['form'] = collection.form
    
    page = request.GET.get('page')
    collection = get_page(collection, page)
    
    context['collection'] = collection
    context['header'] = header
    context['ordering'] = ordering
    
    context.update(csrf(request))
    return render(request, 'events/templates/ac/index.html', context)
    return HttpResponse('RP')

def has_profile_data(request, user):
    ''' check weather user profile having blank data or not '''
    if user:
        profile = Profile.objects.filter(user=user).first()
        if not profile:
            return HttpResponseRedirect("/accounts/profile/"+user.username+"/")
    
        for field in profile._meta.get_all_field_names():
            if not getattr(profile, field, None):
                return HttpResponseRedirect("/accounts/profile/"+user.username+"/")

@login_required
def organiser_request(request, username):
    """ request to bacome a new organiser """
    user = request.user
    if not user.is_authenticated():
        raise Http404('You are not allowed to view this page')
        
    if username == request.user.username:
        user = User.objects.get(username=username)
        if request.method == 'POST':
            form = OrganiserForm(request.POST)
            if form.is_valid():
                user.groups.add(Group.objects.get(name='Organiser'))
                organiser = Organiser()
                organiser.user_id=request.user.id
                organiser.academic_id=request.POST['college']
                organiser.save()
                messages.success(request, "<ul><li>Thank you. Your request has been sent for Training Manager's approval.</li><li>You will get the approval with in 24 hours.Once the request is approved, you can request for the Training / Workshop. </li><li>For more details <a target='_blank' href='http://process.spoken-tutorial.org/images/1/1f/Training-Request-Sheet.pdf'> Click Here</a></li></ul>")
                return HttpResponseRedirect("/software-training/organiser/view/"+user.username+"/")
            messages.error(request, "Please fill the following details")
            context = {'form':form}
            return render(request, 'events/templates/organiser/form.html', context)
        else:
            try:
                organiser = Organiser.objects.get(user=user)
                if organiser.status:
                    messages.error(request, "You are already an Organiser ")
                    return HttpResponseRedirect("/software-training/organiser/view/"+user.username+"/")
                else:
                    messages.info(request, "Your Organiser request is yet to be approved. Please contact the Resource person of your State. For more details <a href='http://process.spoken-tutorial.org/images/5/5d/Create-New-Account.pdf' target='_blank'> Click Here</a> ")
                    print "Organiser not yet approve "
                    return HttpResponseRedirect("/software-training/organiser/view/"+user.username+"/")
            except:
                messages.info(request, "Please fill the following details")
                context = {}
                context.update(csrf(request))
                context['form'] = OrganiserForm()
                return render(request, 'events/templates/organiser/form.html', context)
    else:
        raise Http404('You are not allowed to view this page')

@login_required
def organiser_view(request, username):
    """ view organiser details """
    user = request.user
    if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page')
    
    user = User.objects.get(username=username)
    context = {}
    organiser = Organiser.objects.get(user=user)
    context['record'] = organiser
    try:
        profile = organiser.user.profile_set.get()
    except:
        profile = ''
    context['profile'] = profile
    return render(request, 'events/templates/organiser/view.html', context)

#@login_required
def organiser_edit(request, username):
    """ view organiser details """
    #todo: confirm event_manager and resource_center can edit organiser details
    user = request.user
    if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page')
        
    user = User.objects.get(username=username)
    if request.method == 'POST':
        form = OrganiserForm(request.POST)
        if form.is_valid():
            organiser = Organiser.objects.get(user=user)
            #organiser.user_id=request.user.id
            organiser.academic_id=request.POST['college']
            organiser.save()
            messages.success(request, "Details has been updated")
            return HttpResponseRedirect("/software-training/organiser/view/"+user.username+"/")
        context = {'form':form}
        return render(request, 'events/templates/organiser/form.html', context)
    else:
            #todo : if any training and test under this organiser disable the edit
            record = Organiser.objects.get(user=user)
            context = {}
            context['form'] = OrganiserForm(instance = record)
            context.update(csrf(request))
            return render(request, 'events/templates/organiser/form.html', context)

@login_required
def rp_organiser(request, status, code, userid):
    """ Resource person: active organiser """
    user = request.user
    organiser_in_rp_state = Organiser.objects.filter(user_id=userid, academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)))
    if not (user.is_authenticated() and organiser_in_rp_state and ( is_event_manager(user) or is_resource_person(user) or (status == 'active' or status == 'block'))):
        raise PermissionDenied('You are not allowed to view this page ')

    try:
        if User.objects.get(pk=userid).profile_set.get().confirmation_code == code:
            organiser = Organiser.objects.get(user_id = userid)
            organiser.appoved_by_id = request.user.id
            message = "activated"
            organiser.status = 1
            if status == 'block':
                organiser.status = 2
                message = "blocked"
            organiser.save()
            messages.success(request, "The Organiser account has been "+message)
            return HttpResponseRedirect('/software-training/organiser/active/')
        else:
            raise Http404('Page not found ')
    except:
        raise PermissionDenied('You are not allowed to view this page')

@login_required
def invigilator_request(request, username):
    """ Request to bacome a invigilator """
    user = request.user
    if not user.is_authenticated():
        raise Http404('You are not allowed to view this page')

    if username == user.username:
        user = User.objects.get(username=username)
        if request.method == 'POST':
            form = InvigilatorForm(request.POST)
            if form.is_valid():
                user.groups.add(Group.objects.get(name='Invigilator'))
                invigilator = Invigilator()
                invigilator.user_id=request.user.id
                invigilator.academic_id=request.POST['college']
                invigilator.save()
                messages.success(request, "Thank you. Your request has been sent for Training Manager's approval. You will get the approval with in 24 hours. Once the request is approved, you can request for the workshop. For more details Click Here")
                return HttpResponseRedirect("/software-training/invigilator/view/"+user.username+"/")
            messages.error(request, "Please fill the following details")
            context = {'form':form}
            return render(request, 'events/templates/invigilator/form.html', context)
        else:
            try:
                invigilator = Invigilator.objects.get(user=user)
                #todo: send status message
                if invigilator.status:
                    messages.success(request, "You have already  invigilator role ")
                    return HttpResponseRedirect("/software-training/invigilator/view/"+user.username+"/")
                else:
                    messages.info(request, "<ul><li>Your Invigilator request is yet to be approved.</li><li>Please contact the Resource person of your State. For more details <a href='http://process.spoken-tutorial.org/images/5/5d/Create-New-Account.pdf' traget='_blank'>Click Here</a> </li></ul>")
                    return HttpResponseRedirect("/software-training/invigilator/view/"+user.username+"/")
            except:
                messages.info(request, "Please fill the following details")
                context = {}
                context.update(csrf(request))
                context['form'] = InvigilatorForm()
                return render(request, 'events/templates/invigilator/form.html', context)
    else:
        raise Http404('You are not allowed to view this page')

@login_required
def invigilator_view(request, username):
    """ Invigilator view page """
    user = request.user
    if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page')
    
    user = User.objects.get(username=username)
    context = {}
    invigilator = Invigilator.objects.get(user=user)
    context['record'] = invigilator
    try:
        profile = invigilator.user.profile_set.get()
    except:
        profile = ''
    context['profile'] = profile
    return render(request, 'events/templates/invigilator/view.html', context)
    
@login_required
def invigilator_edit(request, username):
    """ Invigilator edit page """
    user = request.user
    if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page')
        
    user = User.objects.get(username=username)
    if request.method == 'POST':
        form = InvigilatorForm(request.POST)
        if form.is_valid():
            invigilator = Invigilator.objects.get(user=user)
            invigilator.academic_id=request.POST['college']
            invigilator.save()
            messages.success(request, "Details has been updated")
            return HttpResponseRedirect("/software-training/invigilator/view/"+user.username+"/")
        context = {'form':form}
        return render(request, 'events/templates/invigilator/form.html', context)
    else:
            #todo : if any training and test under this invigilator disable the edit
            record = Invigilator.objects.get(user=user)
            context = {}
            context['form'] = InvigilatorForm(instance = record)
            context.update(csrf(request))
            return render(request, 'events/templates/invigilator/form.html', context)

@login_required
def rp_invigilator(request, status, code, userid):
    """ Resource person: active invigilator """
    user = request.user
    invigilator_in_rp_state = Invigilator.objects.filter(user_id=userid, academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)))
    if not (user.is_authenticated() and invigilator_in_rp_state and ( is_event_manager(user) or is_resource_person(user) or (status == 'active' or status == 'block'))):
        raise PermissionDenied('You are not allowed to view this page')

    try:
        if User.objects.get(pk=userid).profile_set.get().confirmation_code == code:
            invigilator = Invigilator.objects.get(user_id = userid)
            invigilator.appoved_by_id = request.user.id
            invigilator.status = 1
            message = "accepted"
            if status == 'block':
                invigilator.status = 2
                message = "blocked"
            invigilator.save()
            messages.success(request, "Invigilator has "+message)
            return HttpResponseRedirect('/software-training/invigilator/inactive/')
        else:
            raise Http404('Page not found ')
    except:
        raise PermissionDenied('You are not allowed to view this page')

@login_required
def training_request(request, role, rid = None):
    ''' Training request by organiser '''
    user = request.user
    context = {}
    if not (user.is_authenticated() and ( is_organiser(user) or is_resource_person(user) or is_event_manager(user))):
        raise Http404('You are not allowed to view this page')
    
    if request.method == 'POST':
        form = TrainingForm(request.POST, user = request.user)
        if form.is_valid():
            dateTime = request.POST['trdate'].split(' ')
            w = Training()
            if rid:
                w = Training.objects.get(pk = rid)
            else:
                w.organiser_id = user.organiser.id
                w.academic = user.organiser.academic
            w.course_id = request.POST['course']
            w.training_type = request.POST['training_type']
            w.language_id = request.POST['language']
            w.foss_id = request.POST['foss']
            w.trdate = dateTime[0]
            w.trtime = dateTime[1]
            w.skype = request.POST['skype']
            w.save()
            w.department.clear()
            for dept in form.cleaned_data.get('department'):
                w.department.add(dept)
            
            if request.POST['training_type'] == '0':
                print "Training"
                if rid and w.extra_fields:
                    print " edit update existing record"
                    w.extra_fields.paper_name = request.POST['course_number']
                    w.extra_fields.save()
                elif not rid and not w.extra_fields:
                    print "new create new record"
                    tef = TrainingExtraFields.objects.create(paper_name = request.POST['course_number'])
                    w.extra_fields_id = tef.id
                elif rid and not w.extra_fields:
                    print "edit but no ext, creating ext fild"
                    tef = TrainingExtraFields.objects.create(paper_name = request.POST['course_number'])
                    w.extra_fields_id = tef.id
                else:
                    print "Somthing" 
            else:
                if w.extra_fields:
                    eid = w.extra_fields_id
                    w.extra_fields_id = None
                    w.save()
                    TrainingExtraFields.objects.filter(pk=eid).delete()
                print "Not training"
                
            w.save()
            messages.success(request, "Please upload the attendance sheet. ")
            #update logs
            message = None
            if rid:
                if w.training_type == 0:
                    message = w.academic.institution_name+" has updated training request for "+w.foss.foss+" on dated "+w.trdate
                else:
                    message = w.academic.institution_name+" has updated a Workshop request for "+w.foss.foss+" on dated "+w.trdate
            else:
                if w.training_type == 0:
                    message = w.academic.institution_name+" has made a training request for "+w.foss.foss+" on dated "+w.trdate
                else:
                    message = w.academic.institution_name+" has made a Workshop request for "+w.foss.foss+" on dated "+w.trdate
                
            update_events_log(user_id = user.id, role = 0, category = 0, category_id = w.id, academic = w.academic_id, status = 0)
            update_events_notification(user_id = user.id, role = 0, category = 0, category_id = w.id, academic = w.academic_id, status = 0, message = message)
            
            if role == 'organiser' and not rid:
                return HttpResponseRedirect("/software-training/training/" + str(w.id) + "/attendance/")
            return HttpResponseRedirect("/software-training/training/" + role + "/pending/")
        messages.error(request, "Please fill the following details ")
        context = {'form' : form, 'role' : role, 'status' : 'request'}
        return render(request, 'events/templates/training/form.html', context)
    else:
        messages.info(request, "<ul><li>Please check if your machine is ready. For the Machine Readiness document <a href='http://process.spoken-tutorial.org/images/5/58/Machine-Readiness.pdf' class='link alert-link' target='_blank'> Click Here</a>.</li><li> Please make sure that you update the 'Attendance Sheet' while requesting the Training / Workshop.</li> ")
        if rid:
            form = TrainingForm(instance = Training.objects.get(pk = rid), user = request.user)
        else:
             form = TrainingForm(user = request.user)
        context['form'] = form
        context['role'] = role
        context.update(csrf(request))
        return render(request, 'events/templates/training/form.html', context)

@login_required
def training_list(request, role, status):
    """ Organiser index page """
    user = request.user
    if not (user.is_authenticated() and ( is_organiser(user) or is_resource_person(user) or is_event_manager(user))):
        raise Http404('You are not allowed to view this page')
        
    status_dict = {'pending': 0, 'approved' : 2, 'completed' : 4, 'rejected' : 5, 'reschedule' : 2, 'ongoing': 2}
    if status in status_dict:
        context = {}
        collectionSet = None
        if is_event_manager(user) and role == 'em':
            collectionSet = Training.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), status = status_dict[status])
        elif is_resource_person(user) and role == 'rp':
            if status == 'approved':
                collectionSet = Training.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), status = status_dict[status], trdate__gt=datetime.date.today())
            elif status =='ongoing':
                collectionSet = Training.objects.filter((Q(status = 2) | Q(status = 3)), academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), trdate__lte=datetime.date.today())
            elif status =='pending':
                collectionSet = Training.objects.filter((Q(status = 0) | Q(status = 1)), academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), trdate__gte = datetime.date.today())
                
            else:
                collectionSet = Training.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), status = status_dict[status])
        elif is_organiser(user) and role == 'organiser':
            if status == 'approved':
                collectionSet = Training.objects.filter(organiser__user = user, status = status_dict[status], trdate__gt=datetime.date.today())
            elif status == 'ongoing':
                collectionSet = Training.objects.filter((Q(status = 2) | Q(status = 3)), organiser__user = user, trdate__lte=datetime.date.today())
            elif status == 'pending':
                collectionSet = Training.objects.filter((Q(status = 0) | Q(status = 1)), organiser__user = user, trdate__gte=datetime.date.today())
                print collectionSet
            else:
                collectionSet = Training.objects.filter(organiser__user = user, status = status_dict[status])
        
        if collectionSet == None:
            raise Http404('You are not allowed to view this page')

        header = {
            1: SortableHeader('training_type', True, 'Type'),
            2: SortableHeader('academic__state', True, 'State'),
            3: SortableHeader('academic', True, 'Institution'),
            4: SortableHeader('foss', True, 'FOSS'),
            5: SortableHeader('language', True, 'Language'),
            6: SortableHeader('trdate', True, 'Date'),
            7: SortableHeader('Participants', False),
            8: SortableHeader('Action', False)
        }
        
        raw_get_data = request.GET.get('o', None)
        collection = get_sorted_list(request, collectionSet, header, raw_get_data)
        ordering = get_field_index(raw_get_data)
        
        collection = TrainingFilter(request.GET, queryset=collection)
        context['form'] = collection.form
        
        page = request.GET.get('page')
        collection = get_page(collection, page)
        
        context['collection'] = collection
        context['header'] = header
        context['ordering'] = ordering
        context['status'] = status
        context['role'] = role
        context.update(csrf(request))
        return render(request, 'events/templates/training/index.html', context)
    else:
        raise Http404('Page not foundddddd ')

@login_required
@csrf_exempt
def training_approvel(request, role, rid):
    """ Resource person: confirm or reject training """
    user = request.user
    if not (user.is_authenticated() and (is_resource_person(user) or (is_organiser(user) and request.GET['status'] == 'completed'))):
        raise Http404('You are not allowed to view this page')
    try:
        w = Training.objects.get(pk=rid)
        if request.GET['status'] == 'accept':
            status = 2
        if request.GET['status'] == 'reject':
            status = 5
        if request.GET['status'] == 'completed':
            status = 4
    except Exception, e:
        print e
        raise Http404('Page not found ')
    #todo: check rp state same or not
    #if status != 2:
    #    if not (user.is_authenticated() and ( is_event_manager(user) or is_resource_person(user))):
    #        raise PermissionDenied('You are not allowed to view this page')
    
    w.status = status
    w.appoved_by_id = user.id
    #todo: add training code
    if w.status == 2:
        w.training_code = "WC-"+str(w.id)
        send_email('Instructions to be followed before conducting the training', w.organiser.user.email, w)
    if request.GET['status'] == 'completed':
        # calculate the participant list
        wpcount = TrainingAttendance.objects.filter(training_id = rid, status = 1).count()
        w.participant_counts = wpcount
    w.save()
    #send email
    if w.status == 4:
        status = 'Future activities after conducting the workshop'
        to = w.organiser.user.email
        send_email(status, to, w)
        message = w.academic.institution_name +" has completed "+w.foss.foss+" training dated "+w.trdate.strftime("%Y-%m-%d")
    if request.GET['status'] == 'accept':
        #delete admin notification
        try:
            EventsNotification.objects.get(academic_id = w.academic_id, categoryid = w.id, status = 0).delete()
        except Exception, e:
            print e
        message = "Training Manager has approved your "+w.foss.foss+" training request dated "+w.trdate.strftime("%Y-%m-%d")
    if request.GET['status'] == 'reject':
        message = "Training Manager has rejected your "+w.foss.foss+" training request dated "+w.trdate.strftime("%Y-%m-%d")
    #update logs
    update_events_log(user_id = user.id, role = 2, category = 0, category_id = w.id, academic = w.academic_id, status = status)
    update_events_notification(user_id = user.id, role = 2, category = 0, category_id = w.id, academic = w.academic_id, status = status, message = message)
    if w.status == 4:
        messages.success(request, "Training has been completed. For downloading the learner's certificate click on View Participants ")
        return HttpResponseRedirect('/software-training/training/'+role+'/completed/')
    elif w.status == 5:
        messages.success(request, "Training has been rejected ")
        return HttpResponseRedirect('/software-training/training/'+role+'/rejected/')
    elif w.status == 2:
        messages.success(request, "Training has been approved ")
        return HttpResponseRedirect('/software-training/training/'+role+'/approved/')

@login_required
def training_permission(request):
    user = request.user
    if not (user.is_authenticated() and (is_resource_person(user) or is_event_manager(user))):
        raise Http404('You are not allowed to view this page')
        
    permissions = Permission.objects.select_related().all()
    form = TrainingPermissionForm()
    if request.method == 'POST':
        form = TrainingPermissionForm(request.POST)
        if form.is_valid():
            wp = Permission()
            wp.permissiontype_id = form.cleaned_data['permissiontype']
            wp.user_id = form.cleaned_data['user']
            wp.state_id = form.cleaned_data['state']
            wp.assigned_by_id = user.id
            if form.cleaned_data['district']:
                wp.district_id = form.cleaned_data['district']
            if form.cleaned_data['institute']:
                wp.institute_id = form.cleaned_data['institute']
            elif form.cleaned_data['institutiontype']:
                wp.institute_type_id = form.cleaned_data['institutiontype']
            elif form.cleaned_data['university']:
                wp.university_id = form.cleaned_data['university']
            wp.save()
            return HttpResponseRedirect("/software-training/training/permission/")
    
    context = {}
    context.update(csrf(request))
    context['form'] = form
    context['collection'] = permissions
    return render(request, 'events/templates/accessrole/workshop_permission.html', context)
    
@login_required
def accessrole(request):
    user = request.user
    state =  list(AcademicCenter.objects.filter(state__in = Permission.objects.filter(user=user, permissiontype_id=1).values_list('state_id')).values_list('id'))
    district = list(AcademicCenter.objects.filter(district__in = Permission.objects.filter(user=user, permissiontype_id=2, district_id__gt=0).values_list('district_id')).values_list('id'))
    university = list(AcademicCenter.objects.filter(university__in = Permission.objects.filter(user=user, permissiontype_id=3, university_id__gt=0).values_list('university_id')).values_list('id'))
    institution_type = list(AcademicCenter.objects.filter(institution_type__in = Permission.objects.filter(user=user, permissiontype_id=4, institute_type_id__gt=0).values_list('institute_type_id')). values_list('id'))
    institute = list(AcademicCenter.objects.filter(id__in = Permission.objects.filter(user=user, permissiontype_id=5, institute_id__gt=0).values_list('institute_id')).values_list('id'))
    all_academic_ids = list(set(state) | set(district) | set(university) | set(institution_type) | set(institute)) 
    workshops = Training.objects.filter(academic__in = all_academic_ids)
    context = {'collection':workshops}
    return render(request, 'events/templates/accessrole/workshop_accessrole.html', context)

@login_required
def training_attendance(request, wid):
    user = request.user
    onlinetest_user = ''
    psform = ParticipantSearchForm()
    sform = TrainingScanCopyForm()
    if not (user.is_authenticated() and (is_organiser(user))):
        raise Http404('You are not allowed to view this page')
    try:
        training = Training.objects.get(pk = wid) 
        if training.status == 4:
            return HttpResponseRedirect("/software-training/training/" + str(training.id) + "/participant/")
    except Exception, e:
        print e
        raise Http404('Page not found ')
    #todo check request user and training organiser same or not
    if request.method == 'POST':
        if 'submit-mark-attendance' in request.POST:
            users = request.POST
            if users:
                #set all record to 0 if status = 1
                TrainingAttendance.objects.filter(training_id = wid, status = 1).update(status = 0)
                training.status = 3
                training.save()
                for u in users:
                    if not (u =='submit-mark-attendance' or u == 'csrfmiddlewaretoken'):
                        try:
                            wa = TrainingAttendance.objects.get(mdluser_id = users[u], training_id = wid)
                            print wa.id, " => Exits"
                        except:
                            wa = TrainingAttendance()
                            wa.training_id = wid
                            wa.mdluser_id = users[u]
                            wa.status = 0
                            wa.save()
                            print wa.id, " => Inserted"
                        if wa:
                            #todo: if the status = 2 check in moodle if he completed the test set status = 3 (completed)
                            w = TrainingAttendance.objects.get(mdluser_id = wa.mdluser_id, training_id = wid)
                            w.status = 1
                            w.save()
                message = training.academic.institution_name+" has submited training attendance"
                update_events_log(user_id = user.id, role = 2, category = 0, category_id = training.id, academic = training.academic_id,  status = 6)
                update_events_notification(user_id = user.id, role = 2, category = 0, category_id = training.id, academic = training.academic_id, status = 6, message = message)
                
                messages.success(request, "Thank you for uploading the Attendance. Now make sure that you cross check and verify the details before submiting.")
        if 'search-participant' in request.POST:
            psform = ParticipantSearchForm(request.POST)
            onlinetest_user = search_participant(psform)
        
        if 'add-participant' in request.POST:
            add_participant(request, wid, 'Training')
        
        if 'submit-attendance' in request.POST:
            training.status = 1
            training.save()
        
        if 'submit-scaned-copy' in request.POST:
                form = TrainingScanCopyForm(request.POST, request.FILES)
                file_type = ['application/pdf']
                if 'scan_copy' in request.FILES:
                    if request.FILES['scan_copy'].content_type in file_type:
                        file_path = settings.MEDIA_ROOT + 'training/'
                        try:
                            os.mkdir(file_path)
                        except Exception, e:
                            print e
                        file_path = settings.MEDIA_ROOT + 'training/'+wid+'/'
                        try:
                            os.mkdir(file_path)
                        except Exception, e:
                            print e
                        full_path = file_path + wid +".pdf"
                        fout = open(full_path, 'wb+')
                        f = request.FILES['scan_copy']
                        # Iterate through the chunks.
                        for chunk in f.chunks():
                            fout.write(chunk)
                        fout.close()
                        messages.success(request, "Waiting for Training Manager approval.")
                    else:
                        messages.success(request, "Choose a PDF File")
                else:
                    messages.success(request, "Choose a PDF File.")
        
    participant_ids = list(TrainingAttendance.objects.filter(training_id = wid).values_list('mdluser_id'))
    mdlids = []
    wp = {}
    for k in participant_ids:
        mdlids.append(k[0])
    if mdlids:
        wp = MdlUser.objects.filter(id__in = mdlids)
    context = {}
    context['psform'] = psform
    context['sform'] = sform
    context['collection'] = wp
    context['onlinetest_user'] = onlinetest_user
    context['training'] = training
    context['file_path'] = '/media/training/'+wid+'/'+wid+'.pdf'
    context.update(csrf(request))
    return render(request, 'events/templates/training/attendance.html', context)


@login_required
def training_participant(request, wid=None):
    user = request.user
    if not (user.is_authenticated() and (is_resource_person(user) or is_event_manager(user) or is_organiser(user))):
        raise Http404('You are not allowed to view this page')
    can_download_certificate = 0
    if wid:
        try:
            wc = Training.objects.get(id=wid)
        except:
            raise Http404('Page not found')
        if wc.status == 4:
            workshop_mdlusers = TrainingAttendance.objects.using('default').filter(training_id = wid, status__gt = 0).values_list('mdluser_id')
        else:
            workshop_mdlusers = TrainingAttendance.objects.using('default').filter(training_id = wid).values_list('mdluser_id')
        ids = []
        for wp in workshop_mdlusers:
            ids.append(wp[0])
            
        wp = MdlUser.objects.using('moodle').filter(id__in=ids)
        if user == wc.organiser.user and wc.status == 4:
            can_download_certificate = 1
        context = {
            'collection' : wp,
            'wc' : wc,
            'can_download_certificate':can_download_certificate,
            'file_path' : '/media/training/'+wid+'/'+wid+'.pdf',
        }
        return render(request, 'events/templates/training/participant.html', context)


def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))
    
    
def training_participant_ceritificate(request, wid, participant_id):
    #response = HttpResponse(content_type='application/pdf')
    #response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    # Create the PDF object, using the response object as its "file."
    #p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    #p.drawString(200, 500, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    #p.showPage()
    #p.save()
    #return response
    # Using ReportLab to insert image into PDF
    
    #store Certificate details
    
    certificate_pass = ''
    if wid and participant_id:
        try:
            w = Training.objects.get(id = wid)
            mdluser = MdlUser.objects.get(id = participant_id)
            wcf = None
            # check if user can get certificate
            wa = TrainingAttendance.objects.get(training_id = w.id, mdluser_id = participant_id)
            if wa.status < 1:
                raise Http404('Page not found')
            if wa.password:
                certificate_pass = wa.password
                wa.count += 1
                wa.status = 3
                wa.save()
            else:
                certificate_pass = str(mdluser.id)+id_generator(10-len(str(mdluser.id)))
                wa.password = certificate_pass
                wa.status = 3
                wa.count += 1
                wa.save()
        except:
            raise Http404('Page not found')
        
    response = HttpResponse(mimetype='application/pdf')
    filename = (mdluser.firstname+'-'+w.foss.foss+"-Participant-Certificate").replace(" ", "-");
    
    response['Content-Disposition'] = 'attachment; filename='+filename+'.pdf'
    imgTemp = StringIO()
    imgDoc = canvas.Canvas(imgTemp)

    # Title 
    imgDoc.setFont('Helvetica', 40, leading=None)
    imgDoc.drawCentredString(415, 480, "Certificate of Learning")
    
    #date
    imgDoc.setFont('Helvetica', 18, leading=None)
    imgDoc.drawCentredString(211, 115, custom_strftime('%B {S} %Y', w.trdate)) 

    #password
    imgDoc.setFillColorRGB(211, 211, 211)
    imgDoc.setFont('Helvetica', 10, leading=None)
    imgDoc.drawString(10, 6, certificate_pass)
    #imgDoc.drawString(100, 100, 'transparent')
    

    # Draw image on Canvas and save PDF in buffer
    imgPath = settings.MEDIA_ROOT +"sign.jpg"
    imgDoc.drawImage(imgPath, 600, 100, 150, 76)    ## at (399,760) with size 160x160

    #paragraphe
    text = "This is to certify that <b>"+mdluser.firstname +" "+mdluser.lastname+"</b> participated in the <b>"+w.foss.foss+"</b> training organized at <b>"+w.academic.institution_name+"</b> by  <b>"+w.organiser.user.first_name + " "+w.organiser.user.last_name+"</b> on <b>"+custom_strftime('%B {S} %Y', w.trdate)+"</b> with course material provided by the Talk To A Teacher project at IIT Bombay.<br /><br />A comprehensive set of topics pertaining to <b>"+w.foss.foss+"</b> were covered in the workshop. This training is offered by the Spoken Tutorial project, IIT Bombay, funded by National Mission on Education through ICT, MHRD, Govt., of India."
    
    centered = ParagraphStyle(name = 'centered',
        fontSize = 16,  
        leading = 30,  
        alignment = 0,  
        spaceAfter = 20)

    p = Paragraph(text, centered)
    p.wrap(650, 200)
    p.drawOn(imgDoc, 4.2 * cm, 7 * cm)

    imgDoc.save()

    # Use PyPDF to merge the image-PDF into the template
    page = PdfFileReader(file(settings.MEDIA_ROOT +"Blank-Certificate.pdf","rb")).getPage(0)
    overlay = PdfFileReader(StringIO(imgTemp.getvalue())).getPage(0)
    page.mergePage(overlay)

    #Save the result
    output = PdfFileWriter()
    output.addPage(page)
    
    #stream to browser
    outputStream = response
    output.write(response)
    outputStream.close()

    return response
    
@login_required
def test_request(request, role, rid = None):
    ''' Test request by organiser '''
    user = request.user
    if not (user.is_authenticated() and ( is_organiser(user) or is_resource_person(user) or is_event_manager(user))):
        raise Http404('You are not allowed to view this page')
    context = {}
    if request.method == 'POST':
        form = TestForm(request.POST, user = request.user)
        if form.is_valid():
            dateTime = request.POST['tdate'].split(' ')
            t = Test()
            if rid:
                t = Test.objects.get(pk = rid)
            else:
                t.organiser_id = user.organiser.id
                t.academic = user.organiser.academic
            t.test_category_id = request.POST['test_category']
            
            if int(request.POST['test_category']) == 1:
                t.training_id = request.POST['workshop']
            if int(request.POST['test_category']) == 2:
                t.training_id = request.POST['training']
            if int(request.POST['test_category']) == 3:
                t.training_id = None
            
            t.invigilator_id = request.POST['invigilator']
            t.foss_id = request.POST['foss']
            t.tdate = dateTime[0]
            t.ttime = dateTime[1]
            t.save()
            t.department.clear()
            for dept in form.cleaned_data.get('department'):
                t.department.add(dept)
            
            #update logs
            message = t.academic.institution_name+" has made a test request for "+t.foss.foss+" on "+t.tdate
            if rid:
                message = t.academic.institution_name+" has updated test for "+t.foss.foss+" on  dated "+t.tdate
            update_events_log(user_id = user.id, role = 0, category = 1, category_id = t.id, academic = t.academic_id, status = 0)
            update_events_notification(user_id = user.id, role = 0, category = 1, category_id = t.id, academic = t.academic_id, status = 0, message = message)
            
            return HttpResponseRedirect("/software-training/test/"+role+"/pending/")
            
    form = TestForm(user = request.user)
    if rid:
        t = Test.objects.get(pk = rid)
        form = TestForm(user = t.organiser.user, instance = t)
    messages.info(request, "Upgrade the browser with latest version on all the systems before the test. Please note: Confirm Invigilator availability and acceptance to invigilate before adding his name in this form.")
    context = {'role' : role, 'status' : 'request'}
    context.update(csrf(request))
    context['form'] = form
    return render(request, 'events/templates/test/form.html', context)

@login_required
def test_list(request, role, status):
    """ Organiser test index page """
    user = request.user
    if not (user.is_authenticated() and ( is_organiser(user) or is_invigilator(user) or is_resource_person(user) or is_event_manager(user))):
        raise Http404('You are not allowed to view this page')
        
    status_dict = {'pending': 0, 'waitingforinvigilator': 1, 'approved' : 2, 'ongoing': 3, 'completed' : 4, 'rejected' : 5, 'reschedule' : 2}
    if status in status_dict:
        context = {}
        collectionSet = None
        todaytest = None
        if is_event_manager(user) and role == 'em':
            if status == 'ongoing':
                collectionSet = Test.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), status = status_dict[status], tdate = datetime.datetime.now().strftime("%Y-%m-%d"))
            else:
                collectionSet = Test.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), status = status_dict[status])
        elif is_resource_person(user) and role == 'rp':
            if status == 'ongoing':
                collectionSet = Test.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), status = status_dict[status], tdate = datetime.datetime.now().strftime("%Y-%m-%d"))
            else:
                collectionSet = Test.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), status = status_dict[status])
        elif is_organiser(user) and role == 'organiser':
            if status == 'ongoing': 
                collectionSet = Test.objects.filter((Q(status = 2) | Q(status = 3)), organiser__user = user , tdate = datetime.datetime.now().strftime("%Y-%m-%d"))
            elif status == 'approved':
                collectionSet = Test.objects.filter(organiser__user = user, status = status_dict[status], tdate__gt=datetime.date.today())
            else:
                collectionSet = Test.objects.filter(organiser__user = user, status = status_dict[status])
        elif is_invigilator(user) and role == 'invigilator':
            if status == 'ongoing':
                collectionSet = Test.objects.filter((Q(status = 2) | Q(status = 3)), tdate = datetime.date.today(), invigilator_id = user.invigilator.id)
                messages.info(request, "Click on the Attendance link below to see the participant list. To know more Click Here.")
            elif status == 'approved':
                collectionSet = Test.objects.filter(invigilator_id=user.invigilator.id, status = status_dict[status], tdate__gt=datetime.date.today())
            else:
                todaytest = datetime.datetime.now().strftime("%Y-%m-%d")
                collectionSet = Test.objects.filter(invigilator_id=user.invigilator.id, status = status_dict[status])
        
        if collectionSet == None:
            raise Http404('You are not allowed to view this page')
            
        header = {
            1: SortableHeader('academic__state', True, 'State'),
            2: SortableHeader('academic', True, 'Institution'),
            3: SortableHeader('foss', True, 'FOSS'),
            4: SortableHeader('tdate', True, 'Date'),
            5: SortableHeader('Participants', False),
            6: SortableHeader('Action', False)
        }
        raw_get_data = request.GET.get('o', None)
        collection = get_sorted_list(request, collectionSet, header, raw_get_data)
        ordering = get_field_index(raw_get_data)
        
        collection = TestFilter(request.GET, queryset=collection)
        context['form'] = collection.form
        
        page = request.GET.get('page')
        collection = get_page(collection, page)
        
        context['collection'] = collection
        context['header'] = header
        context['ordering'] = ordering
        
        context['status'] = status
        context['role'] = role
        context['todaytest'] = todaytest
        context['can_manage'] = user.groups.filter(Q(name="Event Manager") |  Q(name="Resource Person"))
        context.update(csrf(request))
        return render(request, 'events/templates/test/index.html', context)
    else:
        raise Http404('Page not found ')

@login_required
@csrf_exempt
def test_approvel(request, role, rid):
    """ Resource person: confirm or reject training """
    user = request.user
    status = 0
    message = None
    alert = None
    logrole = 0
    try:
        t = Test.objects.get(pk=rid)
        if request.GET['status'] == 'accept':
            status = 1
            message = "The Training Manager has approved "+t.foss.foss+" test dated "+t.tdate.strftime("%Y-%m-%d")
            alert = "Test has been approved"
            #send email
            send_email('Instructions to be followed before conducting the test-organiser', t.organiser.user.email, t)
            send_email('Instructions to be followed before conducting the test-invigilator', t.invigilator.user.email, t)
            
            logrole = 2
        if request.GET['status'] == 'invigilatoraccept':
            message = "The Invigilator "+t.organiser.user.first_name +" "+t.organiser.user.last_name+" has approved "+t.foss.foss+" test dated "+t.tdate.strftime("%Y-%m-%d")
            status = 2
            logrole = 1
            alert = "Test has been approved"
        if request.GET['status'] == 'ongoing':
            status = 3
        if request.GET['status'] == 'completed':
            status = 4
            logrole = 1
            alert = "Test has been Completed"
            message = t.academic.institution_name +" has completed "+t.foss.foss+" test dated "+t.tdate.strftime("%Y-%m-%d")
        if request.GET['status'] == 'rejected':
            message = "The Training Manager has rejected "+t.foss.foss+" test dated "+t.tdate.strftime("%Y-%m-%d")
            status = 5
            logrole = 2
            alert = "Test has been rejected"
        if request.GET['status'] == 'invigilatorreject':
            message = "The Invigilator "+t.organiser.user.first_name +" "+t.organiser.user.last_name+" has rejected "+t.foss.foss+" test dated "+t.tdate.strftime("%Y-%m-%d")
            status = 6
            logrole = 1
            alert = "Test has been rejected"
    except Exception, e:
        print e
        raise Http404('Page not found ')
        
    #if status = 2:
    #    if not (user.is_authenticated() and w.academic.state in State.objects.filter(resourceperson__user_id=user) and ( is_event_manager(user) or is_resource_person(user))):
    #        raise PermissionDenied('You are not allowed to view this page')
    if status == 1:
        t.appoved_by_id = user.id
        t.workshop_code = "TC-"+str(t.id)
    if status == 4:
        testatten = TestAttendance.objects.filter(test_id=t.id, status__lt=2)
        if testatten:
            messages.error(request, "Students are processing the test. Check the status for each students!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        t.participant_count = TestAttendance.objects.filter(test_id=t.id).count()

    t.status = status
    t.save()
    
    #events log
    #message = user.first_name+" "+user.last_name+" has accepted your "+t.foss.foss+" Test"
    update_events_log(user_id = user.id, role = logrole, category = 1, category_id = t.id, academic = t.academic_id, status = status)
    update_events_notification(user_id = user.id, role = logrole, category = 1, category_id = t.id, academic = t.academic_id, status = status, message = message)
    messages.success(request, alert)
    if request.GET['status'] == 'completed':
        return HttpResponseRedirect('/software-training/test/'+role+'/completed/')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def test_attendance(request, tid):
    user = request.user
    test = None
    onlinetest_user = ''
    form = ParticipantSearchForm()
    try:
        test = Test.objects.get(pk=tid)
        test.status = 3
        test.save()
    except:
        raise Http404('Page not found ')
    print test.foss_id
    if request.method == 'POST':
        users = request.POST
        if users:
            #set all record to 0 if status = 1
            if 'submit-attendance' in users:
                TestAttendance.objects.filter(test_id = tid, status = 1).update(status = 0)
                for u in users:
                    if not (u == 'csrfmiddlewaretoken' or u == 'submit-attendance'):
                        try:
                            ta = TestAttendance.objects.get(mdluser_id = users[u], test_id = tid)
                            if ta.status > 1:
                                continue
                        except:
                            fossmdlcourse = FossMdlCourses.objects.get(foss_id = test.foss_id)
                            ta = TestAttendance()
                            ta.test_id = test.id
                            ta.mdluser_id = users[u]
                            ta.mdlcourse_id = fossmdlcourse.mdlcourse_id
                            ta.mdlquiz_id = fossmdlcourse.mdlquiz_id
                            ta.mdlattempt_id = 0
                            ta.status = 0
                            ta.save()
                        if ta:
                            #todo: if the status = 2 check in moodle if he completed the test set status = 3 (completed)
                            t = TestAttendance.objects.get(mdluser_id = ta.mdluser_id, test_id = tid)
                            fossmdlcourse = FossMdlCourses.objects.get(foss_id = test.foss_id)
                            t.mdlcourse_id = fossmdlcourse.mdlcourse_id
                            t.mdlquiz_id = fossmdlcourse.mdlquiz_id
                            t.status = 1
                            t.save()
                            #enroll to the course
                            #get the course enrole id
                            #todo: If mark absent delete enrolement
                            mdlenrol = None
                            try:
                                mdlenrol = MdlEnrol.objects.get(enrol='self', courseid = fossmdlcourse.mdlcourse_id )
                                print "Role Exits"
                            except Exception, e:
                                print "MdlEnrol => ", e
                                print "No self enrolement for this course"
                            
                            if mdlenrol:
                                try:
                                    MdlUserEnrolments.objects.get(enrolid = mdlenrol.id, userid = ta.mdluser_id)
                                    print "MdlUserEnrolments Exits"
                                    #update dateTime
                                except Exception, e:
                                    print "MdlUserEnrolments => ", e
                                    MdlRoleAssignments.objects.create(roleid = 5, contextid = 16, userid = ta.mdluser_id, timemodified = datetime.datetime.now().strftime("%s"), modifierid = ta.mdluser_id, itemid = 0, sortorder = 0)
                                    MdlUserEnrolments.objects.create(enrolid = mdlenrol.id, userid = ta.mdluser_id, status = 0, timestart = datetime.datetime.now().strftime("%s"), timeend = 0, modifierid = ta.mdluser_id, timecreated = datetime.datetime.now().strftime("%s"), timemodified = datetime.datetime.now().strftime("%s"))
            
            if 'search-participant' in request.POST:
                form = ParticipantSearchForm(request.POST)
                onlinetest_user = search_participant(form)
                        
            if 'add-participant' in request.POST:
                add_participant(request, tid, 'Test')
            
            message = test.academic.institution_name+" has submited Test attendance dated "+test.tdate.strftime("%Y-%m-%d")
            update_events_log(user_id = user.id, role = 1, category = 1, category_id = test.id, academic = test.academic_id, status = 8)
            update_events_notification(user_id = user.id, role = 1, category = 1, category_id = test.id, academic = test.academic_id, status = 8, message = message)
            messages.success(request, "Thank you for uploading the Attendance. Now make sure that you cross check and verify the details before submiting.") 
    mdlids = []
    participant_ids = []
    online_participant_ids = list(TestAttendance.objects.filter(test_id = test.id).values_list('mdluser_id'))
    for k in online_participant_ids:
        mdlids.append(k[0])
        
    if test.test_category_id == 1:
        participant_ids = list(TrainingAttendance.objects.filter(training_id = test.training_id).values_list('mdluser_id'))
    elif test.test_category_id == 2:
        participant_ids = list(TrainingAttendance.objects.filter(training_id = test.training_id).values_list('mdluser_id'))
    else:
        participant_ids = list(TestAttendance.objects.filter(test_id = test.id).values_list('mdluser_id'))

    wp = None
    for k in participant_ids:
        mdlids.append(k[0])
    if mdlids:
        wp = MdlUser.objects.filter(id__in = mdlids)
    #check can close the test
    testatten = TestAttendance.objects.filter(test_id=test.id, status__lte=2)
    enable_close_test = True
    if testatten:
        enable_close_test = None
    context = {}
    context['collection'] = wp
    context['test'] = test
    context['form'] = form
    context['onlinetest_user'] = onlinetest_user
    context['enable_close_test'] = enable_close_test
    context.update(csrf(request))
    messages.info(request, "Instruct the students to Register and Login on the Online Test link of Spoken Tutorial. Click on the checkbox so that usernames of all the students who are present for the test are marked, then click the submit button. Students can now proceed for the Test.")
    return render(request, 'events/templates/test/attendance.html', context)

@login_required
def test_participant(request, tid=None):
    user = request.user
    can_download_certificate = 0
    if tid:
        try:
            t = Test.objects.get(id=tid)
        except:
            raise Http404('Page not found')
            
        test_mdlusers = TestAttendance.objects.using('default').filter(test_id=tid).values_list('mdluser_id')
        ids = []
        print test_mdlusers
        for tp in test_mdlusers:
            ids.append(tp[0])
            
        tp = MdlUser.objects.using('moodle').filter(id__in=ids)
        #if t.status == 4 and (user == t.organiser or user == t.invigilator):
        #    can_download_certificate = 1
        context = {'collection' : tp, 'test' : t, 'can_download_certificate':can_download_certificate}
        return render(request, 'events/templates/test/test_participant.html', context)

def test_participant_ceritificate(request, wid, participant_id):
    #response = HttpResponse(content_type='application/pdf')
    #response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    # Create the PDF object, using the response object as its "file."
    #p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    #p.drawString(200, 500, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    #p.showPage()
    #p.save()
    #return response
    # Using ReportLab to insert image into PDF
    
    #store Certificate details
    
    certificate_pass = ''
    if wid and participant_id:
        try:
            w = Test.objects.get(id = wid)
            mdluser = MdlUser.objects.get(id = participant_id)
            ta = TestAttendance.objects.get(test_id = w.id, mdluser_id = participant_id)
            mdlgrade = MdlQuizGrades.objects.get(quiz = ta.mdlquiz_id, userid = participant_id)
            if ta.status < 1 or round(mdlgrade.grade, 1) < 40 or not w.invigilator:
                raise Http404('Page not found')
                
            if ta.password:
                certificate_pass = ta.password 
                ta.count += 1
                ta.status = 4
                ta.save() 
            else: 
                certificate_pass = str(mdluser.id)+id_generator(10-len(str(mdluser.id)))
                ta.password = certificate_pass 
                ta.status = 4
                ta.count += 1
                ta.save()
        except Exception, e:
            print e
            raise Http404('Page not found')
    response = HttpResponse(mimetype='application/pdf')
    filename = (ta.mdluser_firstname+'-'+ta.mdluser_lastname+"-Participant-Certificate").replace(" ", "-");
    
    response['Content-Disposition'] = 'attachment; filename='+filename+'.pdf'
    imgTemp = StringIO()
    imgDoc = canvas.Canvas(imgTemp)

    # Title 
    #imgDoc.setFont('Helvetica', 40, leading=None)
    #imgDoc.drawCentredString(415, 480, "Certificate for Completion of c ")
    
    imgDoc.setFont('Helvetica', 18, leading=None)
    imgDoc.drawCentredString(211, 115, custom_strftime('%B {S} %Y', w.tdate))
    
    #password
    imgDoc.setFillColorRGB(211, 211, 211)
    imgDoc.setFont('Helvetica', 10, leading=None)
    imgDoc.drawString(10, 6, certificate_pass)
    #imgDoc.drawString(100, 100, 'transparent')
    

    # Draw image on Canvas and save PDF in buffer
    imgPath = settings.MEDIA_ROOT +"sign.jpg"
    imgDoc.drawImage(imgPath, 600, 100, 150, 76)    ## at (399,760) with size 160x160
    
    #paragraphe
    text = "This is to certify that <b>"+ta.mdluser_firstname +" "+ta.mdluser_lastname+"</b> has sucessfully completed <b>"+w.foss.foss+"</b> test organized at <b>"+w.academic.institution_name+"</b> by <b>"+w.invigilator.user.first_name+"</b>  with course material provided by the Take To A Teacher project at IIT Bombay.  <br /><br /><p>pasing on online exam, conducted remotly from IIT Bombay, is a pre-requisite for completing this training. <b>"+w.organiser.user.first_name + " "+w.organiser.user.last_name+"</b> at <b>"+w.academic.institution_name+"</b> invigilated this examination. This training is offered by the <b>Spoken Tutorial project, IIT Bombay, funded by National Mission on Education through ICT, MHRD, Govt of India.</b></p>"
    
    centered = ParagraphStyle(name = 'centered',
        fontSize = 16,  
        leading = 30,  
        alignment = 0,  
        spaceAfter = 20)

    p = Paragraph(text, centered)
    p.wrap(700, 200)
    p.drawOn(imgDoc, 4.2 * cm, 6 * cm)
    
    #paragraphe
    text = "Certificate for Completion of "+w.foss.foss+" Training"
    
    centered = ParagraphStyle(name = 'centered',
        fontSize = 40,  
        leading = 50,  
        alignment = 1,  
        spaceAfter = 20)

    p = Paragraph(text, centered)
    p.wrap(500, 200)
    p.drawOn(imgDoc, 6.2 * cm, 16 * cm)

    imgDoc.save()

    # Use PyPDF to merge the image-PDF into the template
    page = PdfFileReader(file(settings.MEDIA_ROOT +"Blank-Certificate.pdf","rb")).getPage(0)
    overlay = PdfFileReader(StringIO(imgTemp.getvalue())).getPage(0)
    page.mergePage(overlay)

    #Save the result
    output = PdfFileWriter()
    output.addPage(page)
    
    #stream to browser
    outputStream = response
    output.write(response)
    outputStream.close()

    return response

@csrf_exempt
def training_subscribe(request, events, eventid = None, mdluser_id = None):
    try:
        mdluser = MdlUser.objects.get(id = mdluser_id)
        if events == 'test':
            try:
                TestAttendance.objects.create(test_id=eventid, mdluser_id = mdluser_id, mdluser_firstname = mdluser.firstname, mdluser_lastname = mdluser.lastname)
            except Exception, e:
                print e
                pass
            messages.success(request, "You have sucessfully subscribe to the "+events+"")
            return HttpResponseRedirect('/participant/index/#Upcoming-Test')
        elif events == 'training':
            try:
                TrainingAttendance.objects.create(training_id=eventid, mdluser_id = mdluser_id)
            except Exception, e:
                print e
                pass
            messages.success(request, "You have sucessfully subscribe to the "+events+"")
            return HttpResponseRedirect('/participant/index/#Upcoming-Training')
        else:
            raise Http404('Page not found')
    except:
        raise Http404('Page not found')
    
    return HttpResponseRedirect('/participant/index/')

@login_required
def organiser_invigilator_index(request, role, status):
    """ Resource person: List all inactive organiser under resource person states """
    #todo: filter to diaplay block and active user
    active = status
    user = request.user
    context = {}
    if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page')
    if status == 'active':
        status = 1
    elif status == 'inactive':
        status = 0
    elif status == 'blocked':
        status = 2
    else:
        raise Http404('Page not found ')
        
    user = User.objects.get(pk=user.id)

    header = {
        1: SortableHeader('academic__state', True, 'State'),
        2: SortableHeader('academic', True, 'Institution'),
        3: SortableHeader('user__username', True, 'Name'),
        4: SortableHeader('created', True, 'Created'),
        5: SortableHeader('Action', False)
    }
    
    if role == 'organiser':
        try:
            collectionSet = Organiser.objects.select_related().filter(academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)), status=status)
            
            raw_get_data = request.GET.get('o', None)
            collection = get_sorted_list(request, collectionSet, header, raw_get_data)
            ordering = get_field_index(raw_get_data)
            
            collection = OrganiserFilter(request.GET, queryset=collection)
            context['form'] = collection.form
            
            page = request.GET.get('page')
            collection = get_page(collection, page)
        except Exception, e:
            print e
            collection = {}
    elif role == 'invigilator':
        try:
            collectionSet = Invigilator.objects.select_related().filter(academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)), status=status)
            
            raw_get_data = request.GET.get('o', None)
            collection = get_sorted_list(request, collectionSet, header, raw_get_data)
            ordering = get_field_index(raw_get_data)
            
            collection = InvigilatorFilter(request.GET, queryset=collection)
            context['form'] = collection.form
            
            page = request.GET.get('page')
            collection = get_page(collection, page)

        except Exception, e:
            print e
            collection = {}
    else:
        raise Http404('Page not found ')
            
    context['header'] = header
    context['ordering'] = ordering
    context['collection'] = collection
    context['status'] = active
    context['role'] = role
    context.update(csrf(request))
    return render(request, 'events/templates/organiser_invigilator_index.html', context)

        
def update_events_log(user_id, role, category, category_id, academic, status):
    if category == 0:
        try:
            TrainingLog.objects.create(user_id = user_id, training_id = category_id, role = role, academic_id = academic, status = status)
        except Exception, e:
            print "Training Log =>",e
    elif category == 1:
        try:
            TestLog.objects.create(user_id = user_id, test_id = category_id, role = role, academic_id = academic, status = status)
        except Exception, e:
            print "Test Log => ",e
    else:
        print "************ Error in events log ***********"
        
def update_events_notification(user_id, role, category, category_id, status, academic, message):
    try:
        EventsNotification.objects.create(user_id = user_id, role = role, category = category, categoryid = category_id, academic_id = academic, status = status, message = message)
    except Exception, e:
        print "Error in Events Notification => ", e

#Ajax Request and Responces
@csrf_exempt
def ajax_ac_state(request):
    """ Ajax: Get University, District, City based State selected """
    if request.method == 'POST':
        state = request.POST.get('state')
        data = {}
        if request.POST.get('fields[district]'):
            district = District.objects.filter(state=state).order_by('name')
            tmp = ''
            for i in district:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
                
            if(tmp):
                data['district'] = '<option value = None> -- None -- </option>'+tmp
            else:
                data['district'] = tmp
            
        if request.POST.get('fields[city]'):
            city = City.objects.filter(state=state).order_by('name')
            tmp = ''
            for i in city:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
                
            if(tmp):
                data['city'] = '<option value = None> -- None -- </option>'+tmp
            else:
                data['city'] = tmp
            
        if request.POST.get('fields[university]'):
            university = University.objects.filter(state=state).order_by('name')
            tmp = ''
            for i in university:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
            if(tmp):
                data['university'] = '<option value = None> -- None -- </option>'+tmp
            else:
                data['university'] = tmp
        
        return HttpResponse(json.dumps(data), mimetype='application/json')
        
@csrf_exempt
def ajax_ac_location(request):
    """ Ajax: Get the location based on district selected """
    if request.method == 'POST':
        district = request.POST.get('district')
        location = Location.objects.filter(district=district).order_by('name')
        tmp = '<option value = None> -- None -- </option>'
        for i in location:
            tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
        return HttpResponse(json.dumps(tmp), mimetype='application/json')

@csrf_exempt
def ajax_district_data(request):
    """ Ajax: Get the location based on district selected """
    data = {}
    if request.method == 'POST':
        tmp = ''
        district = request.POST.get('district')
        if request.POST.get('fields[location]'):
            location = Location.objects.filter(district_id=district).order_by('name')
            tmp = '<option value = None> -- None -- </option>'
            for i in location:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
            data['location'] = tmp
        
        if request.POST.get('fields[institute]'):
            collages = AcademicCenter.objects.filter(district=district).order_by('institution_name')
            tmp = '<option value = None> -- None -- </option>'
            for i in collages:
                tmp +='<option value='+str(i.id)+'>'+i.institution_name+'</option>'
            data['institute'] = tmp
        
    return HttpResponse(json.dumps(data), mimetype='application/json')

@csrf_exempt
def ajax_ac_pincode(request):
    """ Ajax: Get the pincode based on location selected """
    if request.method == 'POST':
        location = request.POST.get('location')
        location = Location.objects.get(pk=location)
        return HttpResponse(json.dumps(location.pincode), mimetype='application/json')

@csrf_exempt
def ajax_district_collage(request):
    """ Ajax: Get the Colleges (Academic) based on District selected """
    if request.method == 'POST':
        district = request.POST.get('district')
        collages = AcademicCenter.objects.filter(district=district).order_by('institution_name')
        tmp = None
        if collages:
            tmp = '<option value = None> -- None -- </option>'
            for i in collages:
                tmp +='<option value='+str(i.id)+'>'+i.institution_name+'</option>'
        return HttpResponse(json.dumps(tmp), mimetype='application/json')

@csrf_exempt
def ajax_state_collage(request):
    """ Ajax: Get the Colleges (Academic) based on District selected """
    if request.method == 'POST':
        state = request.POST.get('state')
        collages = AcademicCenter.objects.filter(state=state).order_by('institution_name')
        tmp = None
        if collages:
            tmp = '<option value = None> -- None -- </option>'
            for i in collages:
                tmp +='<option value='+str(i.id)+'>'+i.institution_name+'</option>'
        return HttpResponse(json.dumps(tmp), mimetype='application/json')

@csrf_exempt
def ajax_dept_foss(request):
    """ Ajax: Get the dept and foss based on training selected """
    data = {}
    if request.method == 'POST':
        tmp = ''
        category =  int(request.POST.get('fields[type]'))
        print category
        print request.POST
        if category == 1:
            print request.POST
            training = request.POST.get('workshop')
            if request.POST.get('fields[dept]'):
                dept = Department.objects.filter(training__id = training).order_by('name')
                for i in dept:
                    tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
                data['dept'] = tmp
            
            if request.POST.get('fields[foss]'):
                training = Training.objects.filter(pk=training).order_by('name')
                tmp = '<option value = None> -- None -- </option>'
                if training:
                    tmp +='<option value='+str(training[0].foss.id)+'>'+training[0].foss.foss+'</option>'
                data['foss'] = tmp
        elif category == 0:
            workshop = request.POST.get('workshop')
            if request.POST.get('fields[dept]'):
                dept = Department.objects.filter(training__id = workshop).order_by('name')
                for i in dept:
                    tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
                data['dept'] = tmp
            
            if request.POST.get('fields[foss]'):
                workshop = Training.objects.filter(pk=workshop)
                tmp = '<option value = None> -- None -- </option>'
                if workshop:
                    tmp +='<option value='+str(workshop[0].foss.id)+'>'+workshop[0].foss.foss+'</option>'
                data['foss'] = tmp
        else:
            dept = Department.objects.all().order_by('name')
            for i in dept:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
            data['dept'] = tmp
            
            tmp = '<option value = None> -- None -- </option>'
            foss = FossCategory.objects.all(status = 1)
            for i in foss:
                tmp +='<option value='+str(i.id)+'>'+i.foss+'</option>'
            data['foss'] = tmp
    return HttpResponse(json.dumps(data), mimetype='application/json')

@csrf_exempt
def ajax_language(request):
    """ Ajax: Get the Colleges (Academic) based on District selected """
    if request.method == 'POST':
        foss = request.POST.get('foss')
        language = FossAvailableForWorkshop.objects.select_related().filter(foss_id=foss)
        tmp = '<option value = None> -- None -- </option>'
        for i in language:
            tmp +='<option value='+str(i.language.id)+'>'+i.language.name+'</option>'
        return HttpResponse(json.dumps(tmp), mimetype='application/json')
        
@csrf_exempt
def test(request):
    return render_to_response('events/templates/test/test.html', { 'foo': 123, 'bar': 456 })
