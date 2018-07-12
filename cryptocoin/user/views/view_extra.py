from .views_global import *

##
## extras pages info
##

def extras_cryptocurrency(request):
    if request.user.is_authenticated:
        return render(request, 'user/extras/cryptocurrency.html', {})
    return goto_login(request, "cryptocurrency")

def extras_bug_bounty(request):
    if request.user.is_authenticated:
        return render(request, 'user/extras/bug-bounty.html', {})
    return goto_login(request, "bug bounty")

def extras_blockchain(request):
    if request.user.is_authenticated:
        context = {}
        ud = get_object_or_404(UserData, username=request.user.username)
        transfers = TransferLogs.objects.filter(school=ud.school).order_by('-id')
        if transfers.count() > 0:
            curr_day = ""
            for log in transfers:
                if ud.is_admin:
                    if log.sender != "GenCyber Team":
                        sender_name = get_object_or_404(UserData, username=log.sender)
                        log.sender = sender_name.first_name + " " + sender_name.last_name
                    if log.receiver != "GenCyber Team":
                        receiver_name = get_object_or_404(UserData, username=log.receiver)
                        log.receiver = receiver_name.first_name + " " + receiver_name.last_name
                else:
                    # anonymize the usernames
                    sender_name = log.sender
                    receiver_name = log.receiver
                    log.sender = "".join((sender_name[0], "*" * len(sender_name[1:])))
                    log.receiver = "".join((receiver_name[0], "*" * len(receiver_name[1:])))
                # fix the dates
                log.day = log.date.strftime("%A, %B %d")
                log.date = log.date.strftime("%B %d, %Y, %I:%M:%S %p").replace(' 0', ' ')
                if curr_day != log.day:
                    curr_day = log.day
                    log.switch_next_day = True
                else:
                    log.switch_next_day = False
                context['transfers'] = transfers
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
        return render(request, 'user/extras/hall-of-fame.html', context)
    return goto_login(request, "hall of fame")

def submit_extras_feedback(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if "message" in request.POST:
            try:
                message = request.POST.get('message')
                f = Feedback(school=ud.school, message=message)
                f.save()
                if "<script" in message.lower():
                    # bug bounty
                    run_bug_bounty(request, ud, 'stored_XSS', 'Congrats! You found a programming bug called stored cross-site scripting! This bug would allow you to execute malicious javascript code in browsers.', 'https://excess-xss.com/')
                    # end bug bounty
            except Exception as e:
                messages.warning(request, 'Something went wrong, your feedback has not been recorded')
            else:
                messages.info(request, 'Your feedback has been recorded. Thank you so much!')
    return HttpResponseRedirect(reverse('user:extras-feedback'))

def extras_feedback(request):
    if request.user.is_authenticated:
        return render(request, 'user/extras/feedback.html', {})
    return HttpResponseRedirect(reverse('user:index'))
