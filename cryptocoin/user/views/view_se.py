from .views_global import *

##
## social engineering pages
##

def submit_social_engineering(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        context = {}
        if request.method == 'POST':
            for key in request.POST:
                if key == 'csrfmiddlewaretoken' or key == 'submit':
                    continue
                try: # to parse out the POST params
                    question_id = int(key)
                    answer = request.POST.get(key).lower().replace(" ", "")
                except:
                    # bug bounty
                    run_bug_bounty(request, ud, 'html_editing_on_social_eng', 'Congrats! You found a programming bug on client-side input validation. This bug would allow you to break the normal flow of checking social engineering answers and show you a trace of errors on the page!', 'https://www.owasp.org/index.php/Input_Validation_Cheat_Sheet')
                    # end bug bounty
                else:
                    try: # to find the correct question that the student tried to answer
                        se_ques_answ = get_object_or_404(SEQuesAnsw, school=ud.school, id=question_id)
                    except:
                        # bug bounty
                        run_bug_bounty(request, ud, 'html_editing_on_social_eng', 'Congrats! You found a programming bug on client-side input validation. This bug would allow you to break the normal flow of checking social engineering answers and show you a trace of errors on the page!', 'https://www.owasp.org/index.php/Input_Validation_Cheat_Sheet')
                        # end bug bounty
                    else: # if there is such a question and the answer is correct, then save it
                        if se_ques_answ.answer == answer and SECorrectAnswer.objects.filter(user_data=ud, se_ques_answ=se_ques_answ).count() == 0:
                            se_correct_answer = SECorrectAnswer(user_data=ud, se_ques_answ=se_ques_answ)
                            se_correct_answer.save()
                            award_amount = int(get_object_or_404(PortalSetting, name='se_award_amount', school=ud.school).value)
                            ud.permanent_coins = ud.permanent_coins + award_amount
                            ud.save()
                            messages.info(request, "You got " + str(award_amount) + " for your \"" + se_ques_answ.answer +"\" answer!")
                            # record the SE transaction in the blockchain
                            tl = TransferLogs(sender='GenCyber Team (SE)', receiver=ud.username, amount=award_amount, school=ud.school, hash=hashlib.sha1(str(time.time()).encode()).hexdigest())
                            tl.save()
        return HttpResponseRedirect(reverse('user:extras-social-engineering'))
    return goto_login(request, "social engineering")

def extras_social_engineering(request):
    if request.user.is_authenticated:
        context = {}
        ud = get_object_or_404(UserData, username=request.user.username)
        se_enabled = get_object_or_404(PortalSetting, name='se_enabled', school=ud.school).value
        if se_enabled == "true":
            all_se_questions = SEQuesAnsw.objects.filter(school=ud.school).order_by('id')
            se_correct_answers = SECorrectAnswer.objects.filter(user_data=ud).values_list('se_ques_answ__id', flat=True)
            context['allquestions'] = all_se_questions
            context['correctanswers'] = se_correct_answers
            return render(request, 'user/extras/social-engineering.html', context)
        else:
            return HttpResponseRedirect(reverse('user:index'))
    return goto_login(request, "social engineering")

def submit_social_engineering_admin(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists():
            context = {}
            if request.method == 'POST': # if adding a new SE question/answer pair
                if "submitAdd" in request.POST:
                    question, asnwer = "", ""
                    for key in request.POST:
                        if "addQ" in key:
                            question = request.POST.get(key)
                        if "addA" in key:
                            answer = request.POST.get(key).lower().replace(" ", "")
                    if question != "" and answer != "":
                        se_ques_answ = SEQuesAnsw(question=question, answer=answer, school=ud.school)
                        se_ques_answ.save()
                    else:
                        messages.warning(request, "Question and answer fields cannot be empty")
                elif "submitEdit" in request.POST: # if editing existing questions/answers
                    for key in request.POST:
                        if "q" in key:
                            try:
                                id = int(key.replace("q", ""))
                                question = request.POST.get(key)
                                answer = request.POST.get("a" + str(id)).lower().replace(" ", "")
                                se_ques_answ = get_object_or_404(SEQuesAnsw, id=id)
                                se_ques_answ.question = question
                                se_ques_answ.answer = answer
                                se_ques_answ.save()
                            except:
                                messages.warning(request, "Don't try to mess with POST params")
                                break
                elif "remove" in request.POST: # if trying to remove a question/answer pair
                    try:
                        id = int(request.POST.get("remove"))
                        se_ques_answ = get_object_or_404(SEQuesAnsw, id=id)
                        messages.info(request, "Deleted " + se_ques_answ.question + " with answer " + se_ques_answ.answer)
                        se_ques_answ.delete()
                    except:
                        messages.warning(request, "Don't try to mess with POST params")
        return HttpResponseRedirect(reverse('user:extras-social-engineering-admin'))
    return goto_login(request, "social engineering admin")

def extras_social_engineering_admin(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists():
            context = {}
            ud = get_object_or_404(UserData, username=request.user.username)
            all_se_questions = SEQuesAnsw.objects.filter(school=ud.school).order_by('id')
            context['allquestions'] = all_se_questions
            return render(request, 'user/extras/social-engineering-admin.html', context)
        return extras_social_engineering(request)
    return goto_login(request, "social engineering")
