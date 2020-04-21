from django.shortcuts import get_object_or_404, render
from ..models import UserData, UserAnswers, Code, TransferLogs, MarketItem, Cart, Achievement, PassRecQuestions, CodeRedeemer, School, PortalSetting, Bugs, SEQuesAnsw, SECorrectAnswer, Feedback
import hashlib, time
from random import randint
from django.db.models import Sum, Min
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from math import ceil

# imports for image
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

# imports for Groups
from django.contrib.auth.models import Group

# imports for Pagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# imports from settings
from django.conf import settings

# imports for account_creation
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse

# imports for login and logout
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

# imports for driplets game
import json
from django.http import Http404, HttpResponseNotFound
import base64

# import for on-save object validation
from django.core.exceptions import ValidationError

import re
import os

# change the image url for the trial to access the static instead of media directory
def convert_urls_in_trial_and_no_image(school_name: str, items: list, context: dict):
    context['istrial'] = re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', school_name)
    for item in items:
        item.image_file.url_final = item.image_file.url.replace('/media', '') if context['istrial'] else item.image_file.url
        if 'no-image.jpg' in item.image_file.url:
            item.image_file.url_final = '/static/user/img/no-image.jpg'


def paginate_list(request, input, cutout_length):
    paginator = Paginator(input, cutout_length)
    page = request.GET.get('page')
    if not page: page = 1
    return paginator.get_page(page)


def validate_on_save(request, obj, message_on_success=''):
    try:
        obj.full_clean()
    except ValidationError as e:
        output = "Trying to break stuff, huh? ;-P Well, here is the message that will tell you what you are doing wrong: "
        for k, v in enumerate(e.message_dict.items()):
            output += str(v)
        messages.warning(request, output)
        try:
            ud = get_object_or_404(UserData, username=request.user.username)
        except:
            pass
        else:
            # bug bounty
            run_bug_bounty(request, ud, 'bug#4:overflow_max_length', 'Congrats! You found a programming bug, overflowing the maximum length allowed to be saved in the SQL database! This bug could potentially reveal sensitive information and could be exploited to crash the system.', 'https://www.owasp.org/index.php/Testing_for_Input_Validation')
            # end bug bounty
        return False
    else:
        if message_on_success != '':
            messages.info(request, message_on_success)
        return True


def goto_login(request, page_name):
    return render(request, 'user/login.html', {
        'error_message': "You need to login or register to enter the " + page_name,
    })


def run_bug_bounty(request, ud, bug_name, bug_message, link):
    award_amount = 0
    try:
        if get_object_or_404(PortalSetting, name='bug_bounty_enabled', school=ud.school).value == "true":
            bug, created = Bugs.objects.get_or_create(name=bug_name, user_data=ud, school=ud.school, link=link)
            if created:
                award_amount = int(get_object_or_404(PortalSetting, name='bug_bounty_award_amount', school=ud.school).value)
                bug.reward = award_amount
                ud.permanent_coins = ud.permanent_coins + award_amount
                ud.save()
                bug.save()
                # record the bug bounty transaction in the blockchain
                tl = TransferLogs(sender='GenCyber Team (bugs)', receiver=ud.username, amount=award_amount, school=ud.school, hash=hashlib.sha1(str(time.time()).encode()).hexdigest())
                tl.save()
            messages.warning(request, bug_message + ' We have rewarded you ' + str(bug.reward) + ' GenCyberCoins for that! One-time only :)')
            # counting the number of bugs from extras -> bug-bounty.html
            with open('./user/templates/user/extras/bug-bounty.html') as bug_bounty_html:
                # -3 compensates for the extra lines that were added for not available challenges if market is off
                num_bugs = bug_bounty_html.read().count('<li class=\"sublead\">') - 3
            reward_coins = 2 * int(PortalSetting.objects.get(name="bug_bounty_award_amount", school=ud.school).value)
            bug_count = Bugs.objects.filter(user_data=ud, school=ud.school).count()
            if bug_count == num_bugs / 2:
                try:
                    # get achievement by name
                    activity = get_object_or_404(Achievement, name='Bug Bounty Hunter', school=ud.school)
                except:
                    pass  # if the activity does not exist, that means the admin removed it
                else:
                    if Achievement.objects.filter(user_data=ud, name='Bug Bounty Hunter').count() == 0:
                        activity.user_data.add(ud)
                        ud.permanent_coins = ud.permanent_coins + reward_coins / 2
                        ud.save()
                        sender_name = 'GenCyber Team (activity ' + str(activity.id) + ')'
                        tl = TransferLogs(sender=sender_name, receiver=ud.username, amount=reward_coins, school=ud.school, hash=hashlib.sha1(str(time.time()).encode()).hexdigest())
                        tl.save()
                        messages.info(request, "You recieved the Bug Bounty Hunter Achievement for finding at least half of the bugs on the Bug Bounty page! You earned " + str(int(reward_coins / 2)) + " coins. Check out your Account page to see this Achievement.")
            elif bug_count == num_bugs:
                try:
                    # get achievement by name
                    activity = get_object_or_404(Achievement, name='Bug Bounty Exterminator', school=ud.school)
                except:
                    pass  # if the activity does not exist, that means the admin removed it
                else:
                    if Achievement.objects.filter(user_data=ud, name='Bug Bounty Exterminator').count() == 0:
                        activity.user_data.add(ud)
                        ud.permanent_coins = ud.permanent_coins + reward_coins
                        ud.save()
                        sender_name = 'GenCyber Team (activity ' + str(activity.id) + ')'
                        tl = TransferLogs(sender=sender_name, receiver=ud.username, amount=reward_coins, school=ud.school, hash=hashlib.sha1(str(time.time()).encode()).hexdigest())
                        tl.save()
                        messages.info(request, "You recieved the Bug Bounty Exterminator Achievement for finding all of the bugs on the Bug Bounty page! You earned " + str(reward_coins) + " coins. Check out your Account page to see this Achievement.")
    except Exception as e:
        messages.warning(request, e)
        pass
    return award_amount


def init_portal_settings(school):
    # settings for:
    # allow/disallow ordering items on the market
    market_enabled, m_created = PortalSetting.objects.get_or_create(name="market_enabled", school=school)
    if m_created:
        market_enabled.save()
    # allow/disallow ajax for the market
    ajax_enabled, aj_created = PortalSetting.objects.get_or_create(name="ajax_enabled", school=school)
    if aj_created:
        ajax_enabled.value = "true"
        ajax_enabled.save()
    # allow/disallow bug bounty
    bug_bounty_enabled, b_created = PortalSetting.objects.get_or_create(name="bug_bounty_enabled", school=school)
    if b_created:
        bug_bounty_enabled.value = "true"
        bug_bounty_enabled.save()
    # set the amount of coins for the bug bounty
    bug_bounty_award_amount, ba_created = PortalSetting.objects.get_or_create(name="bug_bounty_award_amount", school=school)
    if ba_created:
        bug_bounty_award_amount.value = "20"  # default value in coins
        bug_bounty_award_amount.save()
    # allow/disallow social engineering exercise
    se_enabled, se_created = PortalSetting.objects.get_or_create(name="se_enabled", school=school)
    if se_created:
        se_enabled.value = "true"
        se_enabled.save()
    # set the amount of coins for social engineering
    se_award_amount, sea_created = PortalSetting.objects.get_or_create(name="se_award_amount", school=school)
    if sea_created:
        se_award_amount.value = "20"  # default value in coins
        se_award_amount.save()
    # set how may top-students can order items in any given time
    top_students_number, ts_created = PortalSetting.objects.get_or_create(name="top_students_number", school=school)
    if ts_created:
        top_students_number.value = "3"  # default value of 3 top-students can order at the same time
        top_students_number.save()
    # set the value for the queue auto-expansion
    queue_wait_period, qw_created = PortalSetting.objects.get_or_create(name="queue_wait_period", school=school)
    if qw_created:
        queue_wait_period.value = "1"  # default value of 1 min
        queue_wait_period.save()
    # allow/disallow pagination on the market page
    pagination_enabled, pa_created = PortalSetting.objects.get_or_create(name="pagination_enabled", school=school)
    if pa_created:
        pagination_enabled.value = "true"
        pagination_enabled.save()
    # set the maximum allowed amount to transfer by students
    amount_allowed_to_send, aats_created = PortalSetting.objects.get_or_create(name="amount_allowed_to_send", school=school)
    if aats_created:
        amount_allowed_to_send.value = "5"  # default value in coins
        amount_allowed_to_send.save()
    # define the program type, camp is default
    program_type, program_type_created = PortalSetting.objects.get_or_create(name="program_type", school=school)
    if program_type_created:
        program_type.value = "camp"
        program_type.save()


def get_portal_settings(school):
    context = {}
    init_portal_settings(school)
    ps = PortalSetting.objects.filter(school=school)
    for s in ps:
        context[s.name] = s.value
    return context


def init_default_achievements(school, request):
    # create achievements for reconnaissance questions and bug bounty when school is created
    image_path = 'static/user/img/default-achievements/'
    activity_recon = Achievement(name='Social Engineering Ninja', description='You answered all of the Reconnaissance questions!', image_file=image_path + 'recon-ninja.png', school=school)
    activity_bug = Achievement(name='Bug Bounty Exterminator', description='You found all of the bugs on the Bug Bounty page!', image_file=image_path + 'bug.png', school=school)
    activity_halfbug = Achievement(name='Bug Bounty Hunter', description='You found at least half of the bugs on the Bug Bounty page!', image_file=image_path + 'bug.png', school=school)
    activity_recon.save()
    activity_bug.save()
    activity_halfbug.save()


def get_all_market_data(request, ud):
    marketdata = MarketItem.objects.filter(school=ud.school)
    if request.user.groups.filter(name='gcadmin').exists():
        marketdata = marketdata.order_by('name')
    else:
        marketdata = marketdata.order_by('-tier', 'id')
    available_coins = ud.permanent_coins
    context = {'marketdata': marketdata, 'available_coins': available_coins}
    return context
