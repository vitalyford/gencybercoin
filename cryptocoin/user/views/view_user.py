from .views_global import *


def handler404(request):
    return render(request, 'user/extras/404.html', status=404)


def index(request):
    if request.user.is_authenticated:
        return render(request, 'user/index.html', {})
    return goto_login(request, "GenCyberCoin Portal")


def get_questions():
    return {'questions': PassRecQuestions.objects.all()}


def register(request):
    if request.user.is_authenticated:
        return render(request, 'user/index.html', {})
    return render(request, 'user/register.html', get_questions())


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('user:index'))


def driblets(request):
    if request.user.is_authenticated:
        if 'data' in request.POST:
            r = request.POST.get('data')[:-7]
            r = base64.b64decode(r).decode('utf-8')
            r = r.replace('\"', '')
            # print(r)
            received_list = str(r).split(':')
            if len(received_list) == 3:
                # print("Base64 success:" + received_list[1] + " total: " + received_list[2] + "done")
                try:
                    amount = 30
                    success = float(int(received_list[1]))
                    total = float(int(received_list[2]))
                    if total == 0:
                        return HttpResponseNotFound('<h1>Page not found</h1>')
                    percent = success / total
                    if percent >= 0 and percent <= 100:
                        amount = amount * percent
                        u = get_object_or_404(UserData, username=request.user.username)
                        if int(amount) > u.driplets_score:
                            u.permanent_coins = u.permanent_coins + int(amount) - u.driplets_score
                            u.driplets_score = int(amount)
                        u.save()
                except TypeError:
                    return HttpResponseNotFound('<h1>Page not found</h1>')
            else:
                return HttpResponseNotFound('<h1>Page not found</h1>')
    response_data = {'status': "success"}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def user_login(request):
    return render(request, 'user/login.html')


def password_recovery(request):
    # check if the user already entered the username to recover the password for
    context = {}
    if 'inputUsername' not in request.POST:
        return render(request, 'user/password-recovery.html', context)
    try:
        # check if username exists and show questions to the user
        username = request.POST.get('inputUsername')
        ud = get_object_or_404(UserData, username=username)
        if not ud.school:
            context['error_message'] = "Congrats! You had to look into the source code on the GitHub page to figure out this one! Developers sometimes accidentally release passwords, and hackers diligently go through the sources to find those sensitive data leaks. The code to redeem is $superuser-leak-is-danger"
            return render(request, 'user/password-recovery.html', context)
    except:
        context['error_message'] = "Username does not exist, and it is case-sensitive by the way"
    else:
        # if username exists, then pull the questions out
        context['username'] = username
        useranswers = get_object_or_404(UserAnswers, data=ud)
        context['useranswers'] = useranswers
        if 'inputQ1' in request.POST and 'inputQ2' in request.POST and 'inputQ3' in request.POST:
            # count the correct answers
            try:
                answers = [useranswers.answer1.lower() == str(request.POST.get('inputQ1')).lower(), useranswers.answer2.lower() == str(request.POST.get('inputQ2')).lower(), useranswers.answer3.lower() == str(request.POST.get('inputQ3')).lower()]
            except:
                context['error_message'] = "No security questions are found for this user"
            else:
                # login the user if 2 or more answers are correct
                if sum(answers) > 1:
                    user = authenticate(username=request.POST.get('inputUsername'), password=useranswers.data.password)
                    request.session.set_expiry(settings.SESSION_EXPIRY_TIME)
                    login(request, user)
                    # useranswers.was_hacked = useranswers.was_hacked + 1
                    # useranswers.save()
                    return HttpResponseRedirect(reverse('user:index'))
                context['error_message'] = "Only " + str(sum(answers)) + " answers are correct, try again"
    return render(request, 'user/password-recovery.html', context)


def secret(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        # bug bounty
        run_bug_bounty(request, ud, 'bug#1:sensitive_data_exposure', 'Congrats! You found a secret page that programmers sometimes forget about. This kind of bugs may expose sensitive data.', 'https://www.owasp.org/index.php/Top_10-2017_A3-Sensitive_Data_Exposure')
        # end bug bounty
        return render(request, 'user/extras/secret.html', {})
    return HttpResponseRedirect(reverse('user:index'))
