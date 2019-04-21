from .views_global import *
import re

#
# social engineering pages
#


def verify_se_question(correct_answer_line, user_answer):
    user_answer = user_answer.lower()
    correct_answers = correct_answer_line.split(";")
    for correct_answer in correct_answers:
        # clean up the user answer and leave only whitespace
        user_answer = re.sub(r'[^\w\s]', '', user_answer)
        user_answer_words = user_answer.split()
        for i, word in enumerate(user_answer_words):
            prev = correct_answer
            correct_answer = correct_answer.replace(word, '')
            if prev == correct_answer: break
            if correct_answer == '':
                return True if i + 1 == len(user_answer_words) else False
    return False


def submit_social_engineering(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.method == 'POST':
            for key in request.POST:
                if key == 'csrfmiddlewaretoken' or key == 'submit':
                    continue
                try:  # to parse out the POST params
                    question_id = int(key)
                    answer = request.POST.get(key).lower()  # .replace(" ", "")
                except:
                    # bug bounty
                    run_bug_bounty(request, ud, 'bug#8:html_editing_on_social_eng', 'Congrats! You found a programming bug on client-side input validation. This bug would allow you to break the normal flow of checking social engineering answers and show you a trace of errors on the page!', 'https://www.owasp.org/index.php/Input_Validation_Cheat_Sheet')
                    # end bug bounty
                else:
                    try:  # to find the correct question that the student tried to answer
                        se_ques_answ = get_object_or_404(SEQuesAnsw, school=ud.school, id=question_id)
                    except:
                        # bug bounty
                        run_bug_bounty(request, ud, 'bug#8:html_editing_on_social_eng', 'Congrats! You found a programming bug on client-side input validation. This bug would allow you to break the normal flow of checking social engineering answers and show you a trace of errors on the page!', 'https://www.owasp.org/index.php/Input_Validation_Cheat_Sheet')
                        # end bug bounty
                    else:  # if there is such a question and the answer is correct, then save it
                        # if se_ques_answ.answer == answer and SECorrectAnswer.objects.filter(user_data=ud, se_ques_answ=se_ques_answ).count() == 0:
                        if verify_se_question(se_ques_answ.answer, answer) and SECorrectAnswer.objects.filter(user_data=ud, se_ques_answ=se_ques_answ).count() == 0:
                            se_correct_answer = SECorrectAnswer(user_data=ud, se_ques_answ=se_ques_answ)
                            se_correct_answer.save()
                            award_amount = int(get_object_or_404(PortalSetting, name='se_award_amount', school=ud.school).value)
                            ud.permanent_coins = ud.permanent_coins + award_amount
                            ud.save()
                            messages.info(request, "You got " + str(award_amount) + " for your \"" + se_ques_answ.answer + "\" answer!")
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


def extras_osint_ninjas(request):
    if request.user.is_authenticated:
        context = {}
        ud = get_object_or_404(UserData, username=request.user.username)

        # get the user data to show the ranking
        userdata = UserData.objects.filter(school=ud.school, is_admin=False).values('id', 'first_name', 'last_name')
        context['usercount'] = userdata.count()

        # get the recon questions and the number of correct answers
        se_tasks = SEQuesAnsw.objects.filter(school=ud.school).order_by('id')
        context['school_name'] = ud.school.name
        context['se_tasks_counts'] = {}
        for se_task in se_tasks:
            context['se_tasks_counts'][se_task.question] = se_task.secorrectanswer_set.filter(user_data__is_admin=False).count()

        # identify how many questions every user answered correctly
        usercount_who_answered_all_questions = 0
        total_task_number = len(context['se_tasks_counts'])
        for u in userdata:
            u['answers'] = SECorrectAnswer.objects.filter(user_data__id=u['id']).count()
            if u['answers'] == total_task_number:
                usercount_who_answered_all_questions = usercount_who_answered_all_questions + 1
        context['percentage_who_answered_all_questions'] = 0
        if context['usercount'] != 0:
            context['percentage_who_answered_all_questions'] = int((float(usercount_who_answered_all_questions) / float(context['usercount'])) * 100.0)
        context['userdata'] = userdata

        return render(request, 'user/extras/osint-ninjas.html', context)
    return goto_login(request, "OSINT masters")


def submit_social_engineering_admin(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists():
            if request.method == 'POST':  # if adding a new SE question/answer pair
                if "submitAdd" in request.POST:
                    question, answer = "", ""
                    for key in request.POST:
                        if "addQ" in key:
                            question = request.POST.get(key)
                        if "addA" in key:
                            answer = request.POST.get(key)  # .lower().replace(" ", "")
                            answer = re.sub(r'[^\w;]', '', answer.lower())
                    if question != "" and answer != "":
                        se_ques_answ = SEQuesAnsw(question=question, answer=answer, school=ud.school)
                        if validate_on_save(request, se_ques_answ): se_ques_answ.save()
                    else:
                        messages.warning(request, "Question and answer fields cannot be empty")
                elif "submitEdit" in request.POST:  # if editing existing questions/answers
                    for key in request.POST:
                        if "q" in key:
                            try:
                                id = int(key.replace("q", ""))
                                question = request.POST.get(key)
                                answer = request.POST.get("a" + str(id)).lower().replace(" ", "")
                                answer = re.sub(r'[^\w;]', '', answer)
                                se_ques_answ = get_object_or_404(SEQuesAnsw, id=id)
                                se_ques_answ.question = question
                                se_ques_answ.answer = answer
                                se_ques_answ.save()
                            except:
                                messages.warning(request, "Don't try to mess with POST params")
                                break
                elif "remove" in request.POST:  # if trying to remove a question/answer pair
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
