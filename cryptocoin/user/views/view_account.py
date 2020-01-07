from .views_global import *
import re


def update_sec_questions(request):
    if request.user.is_authenticated:
        if 'inputSecQ1' in request.POST and 'inputSecQ2' in request.POST and 'inputSecQ3' in request.POST:
            # update in UserAnswers table
            u = get_object_or_404(UserData, username=request.user.username)
            ua = get_object_or_404(UserAnswers, data=u)
            ua.answer1 = request.POST.get('inputSecQ1')
            ua.answer2 = request.POST.get('inputSecQ2')
            ua.answer3 = request.POST.get('inputSecQ3')
            if validate_on_save(request, ua, 'Your security questions have been successfully updated'):
                ua.save()


def change_password(request):
    if request.user.is_authenticated:
        if 'inputOldPassword' in request.POST and 'inputNewPassword' in request.POST and check_password(request.POST.get('inputOldPassword'), request.user.password):
            if len(request.POST.get('inputNewPassword')) > 100:
                messages.warning(request, 'I see how it goes... Well, try to play with maxlength somewhere else ;-). Your password has not been changed.')
            else:
                # update in User table
                u = get_object_or_404(User, username=request.user.username)
                u.set_password(request.POST.get('inputNewPassword'))
                if validate_on_save(request, u):
                    u.save()
                    # update in UserData table
                    u = get_object_or_404(UserData, username=request.user.username)
                    u.password = request.POST.get('inputNewPassword')
                    u.save()
                    # re-authenticate the user with the new creds
                    user = authenticate(username=request.user.username, password=u.password)
                    if user is not None:
                        request.session.set_expiry(settings.SESSION_EXPIRY_TIME)
                        login(request, user)
                    messages.info(request, 'Your password has been successfully changed')
        else:
            messages.warning(request, 'Your old password has been entered incorrectly')


def get_context(request, get_all_users):
    context = {}
    userdata = get_object_or_404(UserData, username=request.user.username)
    if get_all_users:
        allusers = UserData.objects.filter(school=userdata.school).values('id', 'first_name', 'last_name', 'is_admin', 'username').order_by('first_name', 'last_name')
        context['allusers'] = allusers
    try:
        useranswers = get_object_or_404(UserAnswers, data=userdata)
        context['useranswers'] = useranswers
    except:
        pass  # pass for the superuser, other users should have the useranswers
    context['userdata'] = userdata
    return context


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def user_account(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        context = get_context(request, False)
        achievements = ud.achievement_set.all()
        for a in achievements:
            try:
                sender_name = 'GenCyber Team (activity ' + str(a.id) + ')'
                total_rewarded = TransferLogs.objects.filter(sender=sender_name, receiver=ud.username).aggregate(Sum('amount'))['amount__sum']
                if not total_rewarded:
                    raise
            except:
                a.reward = 0
            else:
                a.reward = total_rewarded
        context['achievements'] = achievements
        return render(request, 'user/account.html', context)
    return goto_login(request, "account")


def submit_user_account(request):
    if request.user.is_superuser:
        if 'inputNewPassword' in request.POST:
            change_password(request)
    elif request.user.is_authenticated:
        if 'inputNewPassword' in request.POST:
            change_password(request)
        elif 'inputSecQ1' in request.POST and 'inputSecQ2' in request.POST and 'inputSecQ3' in request.POST:
            update_sec_questions(request)
    return HttpResponseRedirect(reverse('user:account'))


def wallet(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        context = get_context(request, True)
        try:
            amount_allowed_to_send = int(get_object_or_404(PortalSetting, school=ud.school, name='amount_allowed_to_send').value)
            if amount_allowed_to_send < 0:
                raise
        except:
            amount_allowed_to_send = 2
        context.update({'amount_allowed_to_send': amount_allowed_to_send})
        return render(request, 'user/wallet.html', context)
    return goto_login(request, "wallet")


def save_coins(request, ud):
    try:
        honorary_coins  = int(request.POST.get('honoraryCoins'))
        permanent_coins = int(request.POST.get('permanentCoins'))
        if honorary_coins < 0 or permanent_coins < 0:
            messages.warning(request, 'Both appreciation and earned coins have to be >= 0')
            return
    except:
        messages.warning(request, 'Both appreciation and earned coins have to be integers >= 0')
    else:
        ud.honory_coins    = honorary_coins
        ud.permanent_coins = permanent_coins
        ud.save()


def submit_wallet(request):
    if request.user.is_authenticated:
        if 'saveCoins' in request.POST:
            ud = get_object_or_404(UserData, username=request.user.username)
            if ud.is_admin:
                save_coins(request, ud)
        if 'inputCode' in request.POST:
            ud = get_object_or_404(UserData, username=request.user.username)
            inputCode = str(request.POST.get('inputCode')).lower().strip()
            if "<script" in inputCode:
                # bug bounty
                run_bug_bounty(request, ud, 'bug#5:reflected_XSS', 'Congrats! You found a programming bug called reflected cross-site scripting! This bug would allow you to execute malicious javascript code in browsers.', 'https://excess-xss.com/')
                # end bug bounty
            # if the code was not redeemed by this user before, only then give coins to the user
            was_redeemed_counter = CodeRedeemer.objects.filter(user_data=ud, code=inputCode).count()
            if was_redeemed_counter > 0:
                messages.warning(request, 'You have already redeemed this code before!')
            else:
                # if the code exists
                try:
                    real_code = get_object_or_404(Code, allowed_hash=inputCode, school=ud.school)
                except:
                    # bug bounty
                    if inputCode == "$broken-auth":
                        run_bug_bounty(request, ud, 'bug#2:broken_authentication', 'You found broken authentication! Great job.', 'https://www.owasp.org/index.php/Top_10-2017_A2-Broken_Authentication')
                    elif inputCode == "$wonder-why-wonder-how":
                        run_bug_bounty(request, ud, 'bug#15:weak_hash', 'You found a way to crack the weak hash, most likely via a dictionary attack!', 'https://en.wikipedia.org/wiki/Dictionary_attack')
                    elif inputCode == "$security-txt-policy!":
                        run_bug_bounty(request, ud, 'bug#3:security.txt', 'You found security.txt page! This is a useful location to remember when you are working on real bug bounty hunting. Good luck!', 'https://securitytxt.org/')
                    elif inputCode == "$good-old-404-error":
                        run_bug_bounty(request, ud, 'bug#14:404_error', 'You learned about 404 errors! This is a page that is typically shown on the website when you are trying to access a page that does not exist.', 'https://en.wikipedia.org/wiki/HTTP_404')
                    elif inputCode == "$csrf-failure-takeover#":
                        run_bug_bounty(request, ud, 'bug#17:csrf_failure', 'You learned about Cross-Site Request Forgery! This is an attack that allows to send legitimate-looking requests on your behalf to banks, social websites, etc.', 'https://medium.com/@charithra/introduction-to-csrf-a329badfca49')
                    elif inputCode == "$superuser-leak-is-danger":
                        run_bug_bounty(request, ud, 'bug#18:github_data_exposure', 'You learned about not exposing sensitive data via public resources. Make sure that when you develop code, you do not accidentally publish keys, passwords, or your granny\'s address.', 'https://nakedsecurity.sophos.com/2019/03/25/thousands-of-coders-are-leaving-their-crown-jewels-exposed-on-github/')
                    # end bug bounty
                    else:
                        messages.warning(request, 'Wrong code!')
                else:
                    # cancel if the code is not an award
                    if real_code.name != "award":
                        messages.warning(request, 'Wrong code! Only reward codes can be redeemed')
                    else:
                        money_earned = real_code.value
                        # add coins to the user
                        ud.permanent_coins = ud.permanent_coins + money_earned
                        ud.save()
                        # record that the code has been redeemed by this particular user
                        code_record = CodeRedeemer(user_data=ud, code=inputCode)
                        code_record.save()
                        # delete the code unless it is set to infinite
                        if not real_code.infinite:
                            real_code.delete()
                        messages.info(request, 'The code is successfully redeemed, you got ' + str(money_earned) + '!')
                        # record the code on the blockchain
                        sender_name = 'GenCyber Team (' + inputCode + ')'
                        tl = TransferLogs(sender=sender_name, receiver=ud.username, amount=money_earned, school=ud.school, hash=hashlib.sha1(str(time.time()).encode()).hexdigest())
                        tl.save()
        return HttpResponseRedirect(reverse('user:wallet'))
    return goto_login(request, "wallet")


def transfer(request):
    if not request.user.is_authenticated:
        return goto_login(request, "transfer")
    # gcadmins are also counselors => college students/helpers
    # at the end of gencyber, K-12 students can give the leftover coins
    # to the counselors to bet on the best one, just for
    sender = get_object_or_404(UserData, username=request.user.username)
    # check password match for non-admins
    if not sender.is_admin:
        if 'userPassword' not in request.POST:
            return HttpResponseRedirect(reverse('user:wallet'))
        if not check_password(request.POST.get('userPassword'), request.user.password):
            messages.warning(request, 'Wrong password, try again')
            return HttpResponseRedirect(reverse('user:wallet'))
    try:  # settings.MAX_AMOUNT_ALLOWED_TO_SEND
        max_amount_allowed_to_send = int(get_object_or_404(PortalSetting, school=sender.school, name='amount_allowed_to_send').value)
        if max_amount_allowed_to_send < 0:
            raise
    except:
        max_amount_allowed_to_send = 2
    try:
        receiver = UserData.objects.get(id=request.POST.get('inputTransfer'), school=sender.school)
    except:
        messages.warning(request, 'Select the user to send the money to')
    else:
        amount_str = request.POST.get('inputAmount')
        if receiver.is_admin:
            max_amount_allowed_to_send = 100000
            coins = sender.honory_coins
        elif sender.is_admin:
            max_amount_allowed_to_send = 100000
            coins = sender.permanent_coins
        else:
            coins = sender.permanent_coins
        amount_not_integer = False
        try:
            amount = int(amount_str)
        except:
            amount_not_integer = True
        if amount_not_integer:  # if all but the first character are not digits
            messages.warning(request, 'You can send only integer values!')
        elif amount < 0 or coins < 0:
            messages.warning(request, 'You can send only positive integer values!')
            # bug bounty
            run_bug_bounty(request, sender, 'bug#7:transfer_negative_amount', 'Congrats! You found a programming bug on sending a negative amount of money to someone! This bug would allow you to drain honorary coins from any user to your account without them knowing it.', 'https://www.owasp.org/index.php/Input_Validation_Cheat_Sheet')
            # end bug bounty
        else:
            if receiver is not None:
                if amount > coins:
                    messages.warning(request, 'Wanted to send more money than you can afford? Gotcha! =P')
                else:
                    # check if the sender has previously moved money to receiver
                    if amount != 0 and not receiver.is_admin and not sender.is_admin and TransferLogs.objects.filter(sender=sender.username, receiver=receiver.username, school=sender.school).count() > 0:
                        messages.warning(request, 'You have already sent money to this user, sorry, budget cuts do not allow sending more =(')
                    else:
                        if amount > max_amount_allowed_to_send:
                            amount = max_amount_allowed_to_send
                            messages.warning(request, 'Sorry, you can send only up to ' + str(max_amount_allowed_to_send) + ' coins at a time, we changed it to ' + str(max_amount_allowed_to_send) + ' because of the budget cuts =(')
                        if receiver.is_admin:
                            receiver.honory_coins = receiver.honory_coins + amount
                            sender.honory_coins = sender.honory_coins - amount
                        elif receiver.username != sender.username:
                            receiver.permanent_coins = receiver.permanent_coins + amount
                            sender.permanent_coins = sender.permanent_coins - amount
                        receiver.save()
                        sender.save()
                        # bug bounty
                        if receiver.username == sender.username:
                            run_bug_bounty(request, sender, 'bug#9:html_editing_on_transfer', 'Congrats! You found an easter egg! This is not really a dangerous bug but you had to tweak something in the HTML code, so you get a reward.', 'https://www.owasp.org/index.php/Input_Validation_Cheat_Sheet')
                        # end bug bounty
                        # log the sender/receiver and timestamp only if amount > 0
                        if amount > 0:
                            tl = TransferLogs(sender=sender.username, receiver=receiver.username, amount=amount, school=sender.school, hash=hashlib.sha1(str(time.time()).encode()).hexdigest())
                            tl.save()
                            # show username if sent by a student, show first/last name if sent by/to admin
                            if receiver.is_admin or sender.is_admin:
                                messages.info(request, 'You sent ' + str(amount) + ' to ' + receiver.first_name + " " + receiver.last_name + '!')
                            else:
                                messages.info(request, 'You sent ' + str(amount) + ' to ' + receiver.username + '!')
    return HttpResponseRedirect(reverse('user:wallet'))


def user_login_process(request):
    username = request.POST.get('inputUsername')
    password = request.POST.get('inputPassword')
    user = authenticate(username=username, password=password)
    if user is not None:
        request.session.set_expiry(settings.SESSION_EXPIRY_TIME)
        login(request, user)
        # redirect to a home page if not a superuser
        if not request.user.is_superuser:
            return HttpResponseRedirect(reverse('user:index'))
        else:
            return HttpResponseRedirect(reverse('user:code-generator'))
    else:
        # bug bounty
        if username == "admin" and password == "forgot_my_password":
            return render(request, 'user/extras/broken-admin.html', {})
        elif username == "wonderwoman" and password == "dontforget":
            return render(request, 'user/extras/wonderwoman.html', {})
        # end bug bounty
        return render(request, 'user/login.html', {'error_message': "Invalid login! Try again."})


def check_fields(request):
    if 'inputUsername' not in request.POST or 'inputPassword' not in request.POST:
        return False
    uname = request.POST.get('inputUsername')
    pswd = request.POST.get('inputPassword')
    if uname.strip() == "" or pswd.strip() == "":
        return False
    return True


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def init_default_reconnaissance(school):
    # hardcoding the reconnaissance questions and corresponding answers
    qa = {}
    qa['Which cryptographic hash function has been broken by Google?'] = 'sha1'
    qa['What was bought as the first purchase ever made using Bitcoin?'] = 'pizza'
    qa['What online game has exposed hundreds of millions of users to being secretly recorded and hacked during play in 2019?'] = 'fortnite'
    for question, answer in qa.items():
        se_ques_answ = SEQuesAnsw(question=question, answer=answer, school=school)
        se_ques_answ.save()


def init_default_market(school):
    # hardcoding the market items
    items = []

    items.append(MarketItem(name='Rubber Ducky', description='USB drive that pretends to be a keyboard', quantity=1000000, tier=5, school=school))
    items.append(MarketItem(name='WiFi Pineapple', description='Device to pentest WiFi', quantity=1000000, tier=10, school=school))

    for item in items:
        item.save()


def account_creation(request):
    # check if the registration code is valid
    code = str(request.POST.get('inputCode')).lower().strip()
    uname = request.POST.get('inputUsername')
    fname = request.POST.get('inputFirstname')
    lname = request.POST.get('inputLastname')
    pswd = request.POST.get('inputPassword')
    q1 = request.POST.get('inputQ1')
    q2 = request.POST.get('inputQ2')
    q3 = request.POST.get('inputQ3')
    a1 = request.POST.get('inputA1')
    a2 = request.POST.get('inputA2')
    a3 = request.POST.get('inputA3')
    isTrial = (request.POST.get('trial') == 'on')
    questions = PassRecQuestions.objects.all()
    context = {'username': uname, 'password': pswd, 'first_name': fname, 'last_name': lname, 'q1': q1, 'q2': q2, 'q3': q3, 'a1': a1, 'a2': a2, 'a3': a3, 'code': code, 'questions': questions}
    if isTrial: # assign IP addr as the code because trial is selected
        code = get_client_ip(request)
        # get or create a new School, if created => initialize default PortalSettings
        school_id, created = School.objects.get_or_create(name=code)
        if created:
            school_id.title += " | " + code
            school_id.save()
            init_portal_settings(school_id)
            PortalSetting.objects.filter(name="market_enabled", school=school_id).update(value="true")
            init_default_reconnaissance(school_id)
            init_default_market(school_id)
    else:
        try:
            if "#" not in code and "!" not in code:
                raise
            school_id = Code.objects.filter(allowed_hash=code)[0].school
        except:
            context['error_message'] = "Registration code is not valid! Check it again or contact the GenCyber Squad for help."
            return render(request, 'user/register.html', context)
    # check for intentionally long input
    all_input = [len(uname), len(fname), len(lname), len(pswd), len(q1), len(q2), len(q3), len(a1), len(a2), len(a3)]
    if all(a < 90 for a in all_input):
        # check for duplicates
        user_with_the_same_name = User.objects.filter(username=uname)
        if user_with_the_same_name.count() > 0 or uname == "admin" or uname == "wonderwoman":
            context['error_message'] = "Sorry, a user named \"" + uname + "\" already exists. Try again =P"
            return render(request, 'user/register.html', context)
        if not check_fields(request):
            context['error_message'] = "Username and password cannot be empty."
            return render(request, 'user/register.html', context)
        # validate the username
        pattern = re.compile(r'^[\w.@+-]+$')
        if pattern.match(uname) is None:
            context['error_message'] = "Enter a valid username. This value may contain only letters, numbers, space, and @/./+/-/_ characters."
            return render(request, 'user/register.html', context)
        # if there is no duplicate user, then continue
        # create an authenticated account and assign it a group
        try:
            user = User.objects.create_user(username=uname, first_name=fname, last_name=lname, email='dummy@email.coin', password=pswd)
        except:
            messages.warning(request, 'Do not mess with the username, first name, last name, and password :) Try to mess with other fields, those are better')
            return HttpResponseRedirect(reverse('user:register'))
        # if the code belongs to gcadmin, else it belongs to gcstudent
        if "!" in code and not isTrial:
            group, _ = Group.objects.get_or_create(name='gcadmin')
        else:
            group, _ = Group.objects.get_or_create(name='gcstudent')
        user.groups.add(group)

        if validate_on_save(request, user): user.save()
        else: return HttpResponseRedirect(reverse('user:register'))

        # add the user data to gencybercoin db
        is_admin = True if group.name == "gcadmin" else False
        ud = UserData(username=uname, first_name=fname, last_name=lname, password=pswd, is_admin=is_admin, school=school_id)

        if validate_on_save(request, ud): ud.save()
        else:
            user.delete()
            return HttpResponseRedirect(reverse('user:register'))

        c = Cart(user_data=ud)

        if validate_on_save(request, c): c.save()
        else:
            user.delete()
            ud.delete()
            return HttpResponseRedirect(reverse('user:register'))

        ua = UserAnswers(data=ud, answer1=a1, answer2=a2, answer3=a3, question1=q1, question2=q2, question3=q3)

        if validate_on_save(request, ua):
            ua.save()
            if not isTrial and not Code.objects.get(allowed_hash=code).infinite:
                Code.objects.filter(allowed_hash=code)[0].delete()

            user = authenticate(username=uname, password=pswd)
            request.session.set_expiry(settings.SESSION_EXPIRY_TIME)
            login(request, user)
            return HttpResponseRedirect(reverse('user:account'))
        else:
            c.delete()
            user.delete()
            ud.delete()

        messages.warning(request, 'Trying to break stuff, huh? Well, see the messages above, they will tell you what you are doing wrong ;-)')
        return HttpResponseRedirect(reverse('user:register'))
    else:
        context['error_message'] = "Good try. Really. But you do not want to mess with the maxlength here :-)"
        return render(request, 'user/register.html', context)
