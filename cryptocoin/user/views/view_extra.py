from .views_global import *

#
# extras pages info
#


def csrf_failure(request, reason=""):
    return render(request, 'user/extras/csrf-failure.html', {})


def atlantis(request):
    if request.user.is_authenticated:
        if 'username' in request.POST and 'password' in request.POST:
            if request.POST.get('username').lower().strip().replace(' ', '') == 'wannacry' and request.POST.get('password').lower().strip().replace(' ', '') == 'bluekeep':
                ud = get_object_or_404(UserData, username=request.user.username)
                ud.team_number = bool(ud.team_number) ^ 1  # changing from 0 to 1 and from 1 to 0
                ud.save()
                # bug bounty
                run_bug_bounty(request, ud, 'bug#16:forgotten_form', 'Congrats! You found a hidden form that admins forgot to delete from the source code, which could result in an unexpected behavior. That could relate to old backups, forgotten files, etc. You unlocked Atlantis on this website!', 'https://www.owasp.org/index.php/Review_Old,_Backup_and_Unreferenced_Files_for_Sensitive_Information_(OTG-CONFIG-004)')
                # end bug bounty
            else:
                messages.warning(request, 'Wrong credentials')
        return render(request, 'user/extras/cryptocurrency.html', {})
    return goto_login(request, "atlantis")


def extras_cryptocurrency(request):
    if request.user.is_authenticated:
        return render(request, 'user/extras/cryptocurrency.html', {})
    return goto_login(request, "cryptocurrency")


def extras_bug_bounty(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        market_enabled = get_object_or_404(PortalSetting, name="market_enabled", school=ud.school).value
        context = {'market_enabled': market_enabled}
        return render(request, 'user/extras/bug-bounty.html', context)
    return goto_login(request, "bug bounty")


def extras_security_txt(request):
    return render(request, 'user/extras/security.html', {})


def extras_blockchain(request):
    if request.user.is_authenticated:
        context = {}
        ud = get_object_or_404(UserData, username=request.user.username)
        if ud.is_admin and request.method == 'POST' and 'selectedStudent' in request.POST:
            try:
                selectedStudentID = int(request.POST.get('selectedStudent'))
                if selectedStudentID < 0:
                    raise
                selectedStudent = get_object_or_404(UserData, id=selectedStudentID)
            except:
                transfers = TransferLogs.objects.filter(school=ud.school).order_by('-id')
            else:
                transfers = TransferLogs.objects.filter(Q(sender=selectedStudent.username) | Q(receiver=selectedStudent.username), school=ud.school).order_by('-id')
        else:
            transfers = TransferLogs.objects.filter(school=ud.school).order_by('-id')
        if transfers.count() > 0:
            curr_day = ""
            for log in transfers:
                # setting the mine/not-mine flag for the log
                log.mine = (ud.username == log.sender or ud.username == log.receiver)
                if log.mine:
                    log.student_id = ud.id
                if ud.is_admin or ud.username == log.sender or ud.username == log.receiver:
                    if "GenCyber Team" not in log.sender:
                        sender_name = get_object_or_404(UserData, username=log.sender)
                        log.sender = sender_name.first_name + " " + sender_name.last_name
                        if sender_name.is_admin:
                            log.sender += " (GenCyber Team)"
                    if "GenCyber Team" not in log.receiver:
                        receiver_name = get_object_or_404(UserData, username=log.receiver)
                        log.receiver = receiver_name.first_name + " " + receiver_name.last_name
                        if receiver_name.is_admin:
                            log.receiver += " (GenCyber Team)"
                else:
                    # anonymize the usernames
                    sender_name = log.sender
                    receiver_name = log.receiver
                    log.sender = "".join((sender_name[0], "*" * len(sender_name[1:])))
                    log.receiver = "".join((receiver_name[0], "*" * len(receiver_name[1:])))
                    # add GenCyber Team if the sender or receiver is an admin
                    try:
                        if get_object_or_404(UserData, username=sender_name).is_admin:
                            log.sender += " (GenCyber Team)"
                    except:
                        pass
                    try:
                        if get_object_or_404(UserData, username=receiver_name).is_admin:
                            log.receiver += " (GenCyber Team)"
                    except:
                        pass
                # fix the dates
                log.day = log.date.strftime("%A, %B %d")
                log.date = log.date.strftime("%B %d, %Y, %I:%M:%S %p").replace(' 0', ' ')
                if curr_day != log.day:
                    curr_day = log.day
                    log.switch_next_day = True
                else:
                    log.switch_next_day = False
            pagination_enabled = get_object_or_404(PortalSetting, name='pagination_enabled', school=ud.school)
            blockchains_per_page = 60
            if 'selectedStudent' in request.POST and selectedStudentID >= 0:
                blockchains_per_page = len(transfers)
            if pagination_enabled.value == "true":
                paginator = Paginator(transfers, blockchains_per_page)
                page = request.GET.get('page')
                if not page: page = 1
                context['transfers'] = paginator.get_page(page)
            else:
                context['transfers'] = transfers
            context['pagination_enabled'] = pagination_enabled.value
        # add users if it's the admin
        if ud.is_admin:
            allusers = UserData.objects.filter(school=ud.school).values('id', 'first_name', 'last_name', 'is_admin').order_by('first_name', 'last_name')
            context['allusers'] = allusers
        return render(request, 'user/extras/blockchain.html', context)
    return goto_login(request, "blockchain")


def extras_hall_of_fame(request):
    if request.user.is_authenticated:
        context = {}
        ud = get_object_or_404(UserData, username=request.user.username)
        bounties = Bugs.objects.filter(school=ud.school).order_by('date')
        if bounties.count() > 0:
            students = {}
            for bounty in bounties:
                # fix the time/date to the appropriate format, probably should be in the models.py instead
                bounty.date = bounty.date.strftime("%B %d, %Y, %I:%M:%S %p").replace(' 0', ' ')
                full_name = bounty.user_data.first_name + " " + bounty.user_data.last_name
                if full_name not in students:
                    students[full_name] = []
                students[full_name].append(bounty)
            # sort the students dict by the length of their bounties
            students_list = []
            for k in sorted(students, key=lambda k: len(students[k]), reverse=True):
                students_list.append({k: students[k]})
            context['students'] = students_list
        else:
            messages.warning(request, 'Nobody found any bugs yet, you can be the first one!')
        return render(request, 'user/extras/hall-of-fame.html', context)
    return goto_login(request, "hall of fame")


def submit_extras_feedback(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if "message" in request.POST:
            try:
                message = request.POST.get('message')
                f = Feedback(school=ud.school, message=message)
                if validate_on_save(request, f):
                    f.save()
                    if "<script" in message.lower():
                        # bug bounty
                        run_bug_bounty(request, ud, 'bug#6:stored_XSS', 'Congrats! You found a programming bug called stored cross-site scripting! This bug would allow you to execute malicious javascript code in browsers.', 'https://excess-xss.com/')
                        # end bug bounty
                    messages.info(request, 'Your feedback has been recorded. Thank you so much!')
            except:
                messages.warning(request, 'Something went wrong, your feedback has not been recorded')
    return HttpResponseRedirect(reverse('user:extras-feedback'))


def extras_feedback(request):
    if request.user.is_authenticated:
        return render(request, 'user/extras/feedback.html', {})
    return HttpResponseRedirect(reverse('user:index'))
