from .views_global import *

def update_sec_questions(request):
    if request.user.is_authenticated:
        if 'inputSecQ1' in request.POST and 'inputSecQ2' in request.POST and 'inputSecQ3' in request.POST:
            # update in UserAnswers table
            u = get_object_or_404(UserData, username=request.user.username)
            ua = get_object_or_404(UserAnswers, data=u)
            ua.answer1 = request.POST.get('inputSecQ1')
            ua.answer2 = request.POST.get('inputSecQ2')
            ua.answer3 = request.POST.get('inputSecQ3')
            ua.save()
            messages.info(request, 'Your security questions have been successfully updated')

def change_password(request):
    if request.user.is_authenticated:
        if 'inputOldPassword' in request.POST and 'inputNewPassword' in request.POST and check_password(request.POST.get('inputOldPassword'), request.user.password):
            # update in User table
            u = get_object_or_404(User, username=request.user.username)
            u.set_password(request.POST.get('inputNewPassword'))
            u.save()
            # update in UserData table
            u = get_object_or_404(UserData, username=request.user.username)
            u.password = request.POST.get('inputNewPassword')
            u.save()
            # re-authenticate the user with the new creds
            user = authenticate(username=request.user.username, password=u.password)
            if user is not None:
                login(request, user)
            messages.info(request, 'Your password has been successfully changed')
        else:
            messages.warning(request, 'Your old password has been entered incorrectly')

def get_context(request, get_all_users):
    context = {}
    userdata = get_object_or_404(UserData, username=request.user.username)
    if get_all_users:
        allusers = UserData.objects.filter(school=userdata.school).values('username', 'first_name', 'last_name', 'is_admin')
        context['allusers'] = allusers
    try:
        useranswers = get_object_or_404(UserAnswers, data=userdata)
        context['useranswers'] = useranswers
    except:
        pass # pass for the superuser, other users should have the useranswers
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
        context = get_context(request, True)
        return render(request, 'user/wallet.html', context)
    return goto_login(request, "wallet")

def save_coins(request, ud):
    try:
        honorary_coins  = int(request.POST.get('honoraryCoins'))
        permanent_coins = int(request.POST.get('permanentCoins'))
        if honorary_coins < 0 or permanent_coins < 0:
            messages.warning(request, 'Both honorary or earned have to be >= 0')
            return
    except:
        messages.warning(request, 'Both honorary or earned coins have to be integers >= 0')
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
            inputCode = str(request.POST.get('inputCode')).lower()
            if "<script" in inputCode:
                # bug bounty
                run_bug_bounty(request, ud, 'reflected_XSS', 'Congrats! You found a programming bug called reflected cross-site scripting! This bug would allow you to execute malicious javascript code in browsers.', 'https://excess-xss.com/')
                # end bug bounty
            # if the code was not redeemed by this user before, only then give coins to the user
            was_redeemed_counter = CodeRedeemer.objects.filter(username=request.user.username, code=inputCode).count()
            if was_redeemed_counter > 0:
                messages.warning(request, 'You have already redeemed this code before!')
            else:
                # if the code exists
                code_counter = Code.objects.filter(allowed_hash=inputCode, school=ud.school)
                if code_counter:
                    real_code = code_counter[0]
                    # cancel if the code is not an award
                    if real_code.name != "award":
                        messages.warning(request, 'Wrong code! Only reward codes can be redeemed')
                    else:
                        money_earned = real_code.value
                        # add coins to the user
                        ud.permanent_coins = ud.permanent_coins + money_earned
                        ud.save()
                        if not real_code.infinite:
                            real_code.delete()
                        # record that the code has been redeemed by this particular user
                        code_record = CodeRedeemer(username=request.user.username, code=inputCode)
                        code_record.save()
                        messages.info(request, 'The code is successfully redeemed, you got ' + str(money_earned) + '!')
                        # record the code on the blockchain
                        tl = TransferLogs(sender='GenCyber Team', receiver=ud.username, amount=money_earned, school=ud.school, hash=hashlib.sha1(str(time.time()).encode()).hexdigest())
                        tl.save()
                else:
                    # bug bounty
                    if inputCode == "$broken-auth":
                        run_bug_bounty(request, ud, 'broken_authentication', 'You found broken authentication! Great job.', 'https://www.owasp.org/index.php/Top_10-2017_A2-Broken_Authentication')
                    # end bug bounty
                    else:
                        messages.warning(request, 'Wrong code!')
        return HttpResponseRedirect(reverse('user:wallet'))
    return goto_login(request, "wallet")

def transfer(request):
    if not request.user.is_authenticated:
        return goto_login(request, "transfer")
    # gcadmins are also counselors => college students/helpers
    # at the end of gencyber, K-12 students can give the leftover coins
    # to the counselors to bet on the best one, just for fun
    max_amount_allowed_to_send = settings.MAX_AMOUNT_ALLOWED_TO_SEND
    sender = get_object_or_404(UserData, username=request.user.username)
    try:
        receiver = UserData.objects.get(username=request.POST.get('inputTransfer'), school=sender.school)
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
        if amount_not_integer: # if all but the first character are not digits
            messages.warning(request, 'You can send only integer values!')
        elif amount < 0 or coins < 0:
            messages.warning(request, 'You can send only positive integer values!')
            # bug bounty
            run_bug_bounty(request, sender, 'transfer_negative_amount', 'Congrats! You found a programming bug on sending a negative amount of money to someone! This bug would allow you to drain honorary coins from any user to your account without them knowing it.', 'https://www.owasp.org/index.php/Input_Validation_Cheat_Sheet')
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
                        else:
                            receiver.permanent_coins = receiver.permanent_coins + amount
                            sender.permanent_coins = sender.permanent_coins - amount
                        receiver.save()
                        sender.save()
                        # log the sender/receiver and timestamp only if amount > 0
                        if amount > 0:
                            tl = TransferLogs(sender=sender.username, receiver=receiver.username, amount=amount, school=sender.school, hash=hashlib.sha1(str(time.time()).encode()).hexdigest())
                            tl.save()
                            messages.info(request, 'You sent ' + str(amount) + ' to ' + receiver.username + '!')
    return HttpResponseRedirect(reverse('user:wallet'))

def user_login_process(request):
    username = request.POST.get('inputUsername')
    password = request.POST.get('inputPassword')
    user = authenticate(username=username, password=password)
    if user is not None:
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
        # end bug bounty
        return render(request, 'user/login.html', {'error_message': "Invalid login! Try again.",})

def check_fields(request):
    if not 'inputUsername' in request.POST or not 'inputPassword' in request.POST:
        return False
    uname = request.POST.get('inputUsername')
    pswd = request.POST.get('inputPassword')
    if uname.strip() == "" or pswd.strip() == "":
        return False
    return True

def account_creation(request):
    # check if the registration code is valid
    code = str(request.POST.get('inputCode')).lower()
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
    questions = PassRecQuestions.objects.all()
    context = {'username': uname, 'password': pswd, 'first_name': fname, 'last_name': lname, 'q1': q1, 'q2': q2, 'q3': q3, 'a1': a1, 'a2': a2, 'a3': a3, 'code': code, 'questions': questions}
    try:
        if not "#" in code and not "!" in code:
            raise
        school_id = Code.objects.filter(allowed_hash=code)[0].school
    except:
        context['error_message'] = "Registration code is not valid! Check it again or contact the GenCyber Squad for help."
        return render(request, 'user/register.html', context)
    # check for duplicates
    user_with_the_same_name = UserData.objects.filter(username=uname)
    if user_with_the_same_name.count() > 0 or uname == "admin":
        context['error_message'] = "Sorry, a user named \"" + uname + "\" already exists. Try again =P"
        return render(request, 'user/register.html', context)
    if not check_fields(request):
        context['error_message'] = "Username and password cannot be empty."
        return render(request, 'user/register.html', context)
    # if there is no duplicate user, then continue
    try:
        # create an authenticated account and assign it a group
        user = User.objects.create_user(username=uname, first_name=fname, last_name=lname, email='dummy@email.coin', password=pswd)
        # if the code belongs to gcadmin, else it belongs to gcstudent
        if "!" in code:
            group, _ = Group.objects.get_or_create(name='gcadmin')
        else:
            group, _ = Group.objects.get_or_create(name='gcstudent')
        user.groups.add(group)
        user.save()

        # add the user data to gencybercoin db
        is_admin = False
        if group.name == "gcadmin":
            is_admin = True
        ud = UserData(username=uname, first_name=fname,
            last_name=lname, password=pswd, is_admin=is_admin, school=school_id)
        ud.save()
        c = Cart(user_data=ud)
        c.save()
        ua = UserAnswers(data=ud, answer1=a1,
            answer2=a2,
            answer3=a3, question1=q1,
            question2=q2, question3=q3)
        ua.save()
        if not Code.objects.get(allowed_hash=code).infinite:
            Code.objects.filter(allowed_hash=code)[0].delete()

        user = authenticate(username=uname, password=pswd)
        login(request, user)
    except:
        return render(request, 'user/register.html', {'error_message': "Something went wrong, whoops. Please contact the GenCyber Team.",})
    else:
        return HttpResponseRedirect(reverse('user:account'))
