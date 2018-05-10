from .views_global import *
from .view_market import market

##
## management portal
##
VALID_IMAGE_EXTENSIONS = [".jpg",".jpeg",".png",".gif"]

def generate_gencyber_code():
    done = 1
    data = ""
    while done < 100:
        curr_time = str(time.localtime())
        r = randint(0, 1000)
        start = randint(0, 34)
        data = str(hashlib.sha1((str(curr_time) + str(r)).encode('utf-8')).hexdigest()[start:start + 5])
        if any(k == '0' for k in data) or any(k == 'o' for k in data):
            done = done + 1
            continue
        else:
            break
    return data

def submit_code_generator(request):
    if request.user.is_authenticated and request.method == 'POST':
        # check if the code is infinite
        is_infinite = False
        if "infinite" in request.POST:
            is_infinite = (request.POST.get('infinite') == 'on')
        context = {}
        # 'key' consists of the school id + "!" or "#" + code itself
        if request.user.is_superuser and ('inputSchool' in request.POST) and ('inputCount' in request.POST):
            school = request.POST.get('inputSchool')
            count  = int(request.POST.get('inputCount'))
            # get or create a new School, if created => initialize default PortalSettings
            s, created = School.objects.get_or_create(name=school)
            if created:
                init_portal_settings(s)
            for i in range(count):
                key = str(s.id) + "!" + generate_gencyber_code()
                c = Code(allowed_hash=key, name=school, school=s, infinite=is_infinite)
                c.save()
        elif request.user.groups.filter(name='gcadmin').exists() and ('inputCount' in request.POST):
            award_value = 0
            try:
                count = int(request.POST.get('inputCount'))
                if request.POST.get('inputValue') != "":
                    award_value = int(request.POST.get('inputValue'))
            except:
                messages.warning(request, 'Please enter a number, not a string')
            else:
                type = request.POST.get('codeType')
                special_char = "#" # by default, the code is a registration code
                if type == "award":
                    special_char = "$"
                school_gcadmin = get_object_or_404(UserData, username=request.user.username).school
                for i in range(count):
                    key = str(school_gcadmin.id) + special_char + generate_gencyber_code()
                    if type == "registration":
                         c = Code(allowed_hash=key, name=school_gcadmin.name, school=school_gcadmin, infinite=is_infinite)
                    elif type == "award":
                         c = Code(allowed_hash=key, name='award', value=award_value, school=school_gcadmin, infinite=is_infinite)
                    c.save()
        elif 'delete' in request.POST:
            if request.POST.get('delete') == "registration":
                if request.user.is_superuser:
                    Code.objects.filter(allowed_hash__contains='!').delete()
                elif request.user.groups.filter(name='gcadmin').exists():
                    school_gcadmin = get_object_or_404(UserData, username=request.user.username).school
                    Code.objects.filter(school=school_gcadmin, allowed_hash__contains='#').delete()
            elif request.POST.get('delete') == "award" and request.user.groups.filter(name='gcadmin').exists():
                school_gcadmin = get_object_or_404(UserData, username=request.user.username).school
                Code.objects.filter(school=school_gcadmin, allowed_hash__contains='$').delete()
    return HttpResponseRedirect(reverse('user:code-generator'))

def code_generator(request):
    if request.user.is_authenticated:
        context = {}
        # the following returns the list of all codes to show on the page
        if request.user.is_superuser:
            context['is_superuser'] = "true"
            schools = School.objects.all()
            codes_output = {}
            for s in schools:
                curr_school_name = s.name
                codes_output[curr_school_name] = []
                codes = Code.objects.filter(school=s)
                for c in codes:
                    if "!" in c.allowed_hash:
                        if c.infinite:
                            codes_output[curr_school_name].append(c.allowed_hash + " (inf)")
                        else:
                            codes_output[curr_school_name].append(c.allowed_hash)
            context['codes'] = codes_output
            context['admins'] = UserData.objects.filter(is_admin=True).values('first_name', 'last_name', 'school__name')
            return render(request, 'user/code-generator.html', context)
        elif request.user.groups.filter(name='gcadmin').exists():
            context['is_gcadmin'] = "true"
            school_gcadmin = get_object_or_404(UserData, username=request.user.username).school
            registration_codes = []
            award_codes = {}
            codes = Code.objects.filter(school=school_gcadmin)
            for c in codes:
                if "#" in c.allowed_hash:
                    registration_codes.append(c.allowed_hash)
                elif '$' in c.allowed_hash:
                    if c.infinite:
                        award_codes[c.allowed_hash] = str(c.value) + " (inf)"
                    else:
                        award_codes[c.allowed_hash] = c.value
            context['registration_codes'] = registration_codes
            context['award_codes'] = award_codes
            return render(request, 'user/code-generator.html', context)
    return HttpResponseRedirect(reverse('user:index'))

def submit_nominations_admin(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists():
            all_is_good = True
            selectedStudents   = request.POST.getlist('selectedStudents')
            selectedActivities = request.POST.getlist('selectedActivities')
            if selectedStudents and selectedActivities:
                for a in selectedActivities:
                    for s in selectedStudents:
                        try:
                            ud = get_object_or_404(UserData, id=int(s))
                            activity = get_object_or_404(Achievement, id=int(a))
                        except:
                            messages.warning(request, 'ERROR: Student with id=' + s + ' or activity with id=' + a + ' has not been added')
                            all_is_good = False
                        else:
                            activity.user_data.add(ud)
                if all_is_good:
                    messages.info(request, 'All students and activities have been successfully assigned')
                else:
                    messages.warning(request, 'Some of the students or activities have not been assigned')
    return HttpResponseRedirect(reverse('user:nominations-admin'))

def nominations_admin(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists():
            context = {}
            context['achievements'] = Achievement.objects.filter(school=ud.school).order_by('name')
            context['students'] = UserData.objects.filter(school=ud.school).order_by('first_name', 'last_name').values('first_name', 'last_name', 'username', 'id')
            return render(request, 'user/nominations-admin.html', context)
    return HttpResponseRedirect(reverse('user:index'))

def add_new_achievements_item(request, ud):
    try:
        name     = request.POST.get('itemName')
        descr    = request.POST.get('itemDescr')
        image_file = ""
        if 'imageNew' in request.FILES:
            image_name = request.FILES['imageNew'].name.lower()
            if any([image_name.endswith(e) for e in VALID_IMAGE_EXTENSIONS]):
                image_file = request.FILES['imageNew']
                try:
                    im = Image.open(image_file)
                    im.verify()
                    image_file = save_image(request, ud, image_file, "New")
                except:
                    image_file = ""
                    messages.warning(request, 'Images should be images when you upload them, non-image files are not allowed')
            else:
                messages.warning(request, 'Only jpg, jpeg, png, and gif are allowed to be uploaded')
    except:
        messages.warning(request, 'Please check the restrictions: quantity >= 0 and 1 <= tier <= 10')
        return
    try:
        if image_file == "" or not image_file: # use defaults for image_file
            activity_item = Achievement(name=name, description=descr, school=ud.school)
        else:
            activity_item = Achievement(name=name, description=descr, image_file=image_file, school=ud.school)
    except:
        messages.warning(request, 'Something went wrong with the new activity, it has not been added')
    else:
        activity_item.save()
        messages.info(request, name + ' has been added')

def submit_achievements_admin(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists():
            context = {}
            if request.method == 'POST':
                try:
                    if "addNewItem" in request.POST:
                        add_new_achievements_item(request, ud)
                    else:
                        name, descr, id, update_remove = "", "", -1, ""
                        for key in request.POST:
                            if "name" in key:
                                name = request.POST.get(key)
                            elif "descr" in key:
                                descr = request.POST.get(key)
                            elif "update" in key:
                                update_remove = "update"
                                try:
                                    id = int(request.POST.get(key))
                                except:
                                    id = -1
                                    pass
                            elif "remove" in key:
                                update_remove = "remove"
                                try:
                                    id = int(request.POST.get(key))
                                except:
                                    id = -1
                                    pass
                        if id >= 0:
                            activity_item = get_object_or_404(Achievement, id=id, school=ud.school)
                            if update_remove == "update":
                                activity_item.name = name
                                activity_item.description = descr
                                if ('image' + str(id)) in request.FILES:
                                    image_name = request.FILES['image' + str(id)].name.lower()
                                    if any([image_name.endswith(e) for e in VALID_IMAGE_EXTENSIONS]):
                                        # validate image before saving
                                        image_file = request.FILES['image' + str(id)]
                                        try:
                                            im = Image.open(image_file)
                                            im.verify()
                                            image_file = save_image(request, ud, image_file, str(id))
                                            if activity_item.image_file.url != "/media/no-image.jpg":
                                                activity_item.image_file.delete()
                                            activity_item.image_file = image_file
                                        except:
                                            messages.warning(request, 'Images should be images when you upload them, non-image files are not allowed')
                                    else:
                                        messages.warning(request, 'Only jpg, jpeg, png, and gif are allowed to be uploaded')
                                activity_item.save()
                            elif update_remove == "remove":
                                messages.info(request, 'Activity item ' + activity_item.name + ' has been deleted')
                                if activity_item.image_file.url != "/media/no-image.jpg":
                                    activity_item.image_file.delete()
                                activity_item.delete()
                except:
                    messages.warning(request, 'Wrong format of the item')
            return HttpResponseRedirect(reverse('user:achievements-admin'))
        return market(request)
    return HttpResponseRedirect(reverse('user:index'))

def achievements_admin(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists():
            context = {}
            achievements = Achievement.objects.filter(school=ud.school).order_by('id')
            context['achievements'] = achievements
            return render(request, 'user/achievements-admin.html', context)
    return HttpResponseRedirect(reverse('user:index'))

def market_admin(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists():
            context = {}
            all_market_data = get_all_market_data(request, ud)
            pagination_enabled = get_object_or_404(PortalSetting, name='pagination_enabled', school=ud.school)
            if pagination_enabled.value == "true":
                paginator = Paginator(all_market_data['marketdata'], 20)
                page = request.GET.get('page')
                if not page: page = 1
                context['marketdata'] = paginator.get_page(page)
            else:
                context = all_market_data
            context['pagination_enabled'] = pagination_enabled.value
            return render(request, 'user/market-admin.html', context)
        return market(request)
    return HttpResponseRedirect(reverse('user:index'))

def crop_image(image, x, y, w, h):
    size = 300, 300
    cropped_image = image.crop((x, y, w + x, h + y))
    cropped_image.thumbnail(size, Image.ANTIALIAS)
    #rotated_image = cropped_image.rotate(r)
    #cropped_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
    return cropped_image

def image_upload_market(ud, filename):
    image_path = '{school}/market/{filename}'.format(school=ud.school.id, filename=filename)
    return image_path

def save_image(request, ud, image_file, id):
    im = Image.open(image_file)
    im_io = BytesIO()
    try:
        width, height = im.size
        x = int(request.POST.get('inputX' + id))
        y = int(request.POST.get('inputY' + id))
        w = int(request.POST.get('inputWidth' + id))
        h = int(request.POST.get('inputHeight' + id))
        if x < 0 or x > width or y < 0 or y > height or w < 0 or w > width - x or h < 0 or h > height - y:
            raise
    except:
        return image_file
    else:
        im = crop_image(im, x, y, w, h)
        format = image_file.name.split(".")[-1].lower()
        if format == "jpg":
            format = "jpeg"
        im.save(im_io, format=format, quality=100)
        im_content = ContentFile(im_io.getvalue(), image_file.name)
    return im_content

def add_new_market_item(request, ud):
    try:
        name     = request.POST.get('itemName')
        descr    = request.POST.get('itemDescr')
        quantity = int(request.POST.get('itemQuantity'))
        if quantity < 0:
            raise
        tier = int(request.POST.get('itemTier'))
        if tier < 1 or tier > 10:
            raise
        image_file = ""
        if 'imageNew' in request.FILES:
            image_name = request.FILES['imageNew'].name.lower()
            if any([image_name.endswith(e) for e in VALID_IMAGE_EXTENSIONS]):
                image_file = request.FILES['imageNew']
                try:
                    im = Image.open(image_file)
                    im.verify()
                    image_file = save_image(request, ud, image_file, "New")
                except Exception as e:
                    image_file = ""
                    messages.warning(request, 'Images should be images when you upload them, non-image files are not allowed')
                    messages.warning(request, e)
            else:
                messages.warning(request, 'Only jpg, jpeg, png, and gif are allowed to be uploaded')
    except:
        messages.warning(request, 'Please check the restrictions: quantity >= 0 and 1 <= tier <= 10')
        return
    try:
        if image_file == "" or not image_file: # use defaults for image_file
            marketitem = MarketItem(name=name, description=descr, quantity=quantity, tier=tier, school=ud.school)
        else:
            marketitem = MarketItem(name=name, description=descr, quantity=quantity, tier=tier, image_file=image_file, school=ud.school)
    except:
        messages.warning(request, 'Something went wrong with the new market item, it has NOT been added')
    else:
        marketitem.save()
        messages.info(request, name + ' has been added')

def submit_market_admin(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists():
            context = {}
            if request.method == 'POST':
                try:
                    if "addNewItem" in request.POST:
                        add_new_market_item(request, ud)
                    else:
                        name, quantity, tier, descr, id, update_remove = "", 0, 0, "", -1, ""
                        for key in request.POST:
                            if "name" in key:
                                name = request.POST.get(key)
                            elif "quantity" in key:
                                try:
                                    quantity = int(request.POST.get(key))
                                    if quantity < 0:
                                        raise
                                except:
                                    raise ValueError('Wrong format of quantity')
                            elif "tier" in key:
                                try:
                                    tier = int(request.POST.get(key))
                                    if tier < 1 or tier > 10:
                                        raise
                                except:
                                    raise ValueError('Wrong format of tier')
                            elif "descr" in key:
                                descr = request.POST.get(key)
                            elif "update" in key:
                                update_remove = "update"
                                try:
                                    id = int(request.POST.get(key))
                                except:
                                    id = -1
                                    pass
                            elif "remove" in key:
                                update_remove = "remove"
                                try:
                                    id = int(request.POST.get(key))
                                except:
                                    id = -1
                                    pass
                        if id >= 0:
                            market_item = get_object_or_404(MarketItem, id=id, school=ud.school)
                            if update_remove == "update":
                                market_item.name = name
                                market_item.description = descr
                                market_item.tier = tier
                                market_item.quantity = quantity
                                if ('image' + str(id)) in request.FILES:
                                    image_name = request.FILES['image' + str(id)].name.lower()
                                    if any([image_name.endswith(e) for e in VALID_IMAGE_EXTENSIONS]):
                                        # validate image before saving
                                        image_file = request.FILES['image' + str(id)]
                                        try:
                                            im = Image.open(image_file)
                                            im.verify()
                                            image_file = save_image(request, ud, image_file, str(id))
                                            if market_item.image_file.url != "/media/no-image.jpg":
                                                market_item.image_file.delete()
                                            market_item.image_file = image_file
                                        except:
                                            messages.warning(request, 'Images should be images when you upload them, non-image files are not allowed')
                                    else:
                                        messages.warning(request, 'Only jpg, jpeg, png, and gif are allowed to be uploaded')
                                market_item.save()
                            elif update_remove == "remove":
                                messages.info(request, 'Market item ' + market_item.name + ' has been deleted')
                                if market_item.image_file.url != "/media/no-image.jpg":
                                    market_item.image_file.delete()
                                market_item.delete()
                except:
                    messages.warning(request, 'Wrong format of the item')
            return HttpResponseRedirect(reverse('user:market-admin'))
        return market(request)
    return HttpResponseRedirect(reverse('user:index'))

def update_setting(request, ud, portal_setting):
    # enabling portal_setting
    enabled = str(request.POST.get(portal_setting) == 'on').lower()
    ps = get_object_or_404(PortalSetting, school=ud.school, name=portal_setting)
    if ps.value != enabled:
        ps.value = enabled
        ps.save()

def submit_settings_admin(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists():
            context = {}
            if 'save' in request.POST:
                # enabling market for students
                update_setting(request, ud, 'market_enabled')
                # enabling ajax
                update_setting(request, ud, 'ajax_enabled')
                # enabling bug bounty for students
                update_setting(request, ud, 'bug_bounty_enabled')
                # setting up bug bounty award for students
                if 'bug_bounty_award_amount' in request.POST:
                    try:
                        bug_bounty_award_amount = int(request.POST.get('bug_bounty_award_amount'))
                        if bug_bounty_award_amount <= 0:
                            raise
                    except:
                        messages.warning(request, 'The reward amount has to be an integer greater than 0')
                    else:
                        ba = get_object_or_404(PortalSetting, school=ud.school, name='bug_bounty_award_amount')
                        ba.value = str(bug_bounty_award_amount)
                        ba.save()
                # enabling social engineering for students
                update_setting(request, ud, 'se_enabled')
                # setting up social engineering award for students
                if 'se_award_amount' in request.POST:
                    try:
                        se_award_amount = int(request.POST.get('se_award_amount'))
                        if se_award_amount <= 0:
                            raise
                    except:
                        messages.warning(request, 'The reward amount has to be an integer greater than 0')
                    else:
                        sea = get_object_or_404(PortalSetting, school=ud.school, name='se_award_amount')
                        sea.value = str(se_award_amount)
                        sea.save()
                # setting how many students can order at the same time
                if 'top_students_number' in request.POST:
                    try:
                        top_students_number = int(request.POST.get('top_students_number'))
                        if top_students_number <= 0:
                            raise
                    except:
                        messages.warning(request, 'The max student queue number has to be an integer greater than 0')
                    else:
                        ts = get_object_or_404(PortalSetting, school=ud.school, name='top_students_number')
                        ts.value = str(top_students_number)
                        ts.save()
                # setting how many students will be added to the queue if no orders have been made
                if 'queue_wait_period' in request.POST:
                    try:
                        queue_wait_period = float(request.POST.get('queue_wait_period'))
                    except:
                        messages.warning(request, 'The queue wait period has to be an integer greater than 0')
                    else:
                        qw = get_object_or_404(PortalSetting, school=ud.school, name='queue_wait_period')
                        qw.value = str(queue_wait_period)
                        qw.save()
                # enabling pagination
                update_setting(request, ud, 'pagination_enabled')
    return HttpResponseRedirect(reverse('user:settings-admin'))

def settings_admin(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists():
            context = get_portal_settings(ud.school)
            return render(request, 'user/settings-admin.html', context)
        return render(request, 'user/account.html', {})
    return HttpResponseRedirect(reverse('user:index'))

def student_carts_admin(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists():
            students = UserData.objects.filter(school=ud.school, is_admin=False)
            carts = {}
            for s in students:
                # try-except in case if cart does not exists
                try:
                    carts[s.first_name + " " +s.last_name + " (aka " + s.username + ")"] = s.cart.market_items.all().values_list('name', flat=True)
                except:
                    pass
            context = {'carts': carts}
            return render(request, 'user/student-carts-admin.html', context)
        return render(request, 'user/account.html', {})
    return HttpResponseRedirect(reverse('user:index'))

def submit_student_manager_admin(request):
    if request.user.is_authenticated and request.method == 'POST':
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists() and 'hiddenDelete' in request.POST:
            if request.POST.get('hiddenDelete') == "All":
                TransferLogs.objects.all().delete()
                CodeRedeemer.objects.all().delete()
                UserData.objects.all(~Q(username=ud.username)).delete()
                User.objects.all(~Q(username=ud.username)).delete()
                messages.info(request, 'All user data except yours have been deleted')
            else:
                try:
                    id = int(request.POST.get('hiddenDelete'))
                except:
                    messages.warning(request, 'User ID should be an integer')
                else:
                    try:
                        deleteUser = get_object_or_404(UserData, id=id)
                        username = deleteUser.username
                    except:
                        messages.warning(request, 'User ID does not exist')
                    else:
                        TransferLogs.objects.filter(Q(sender=username) | Q(receiver=username)).delete()
                        CodeRedeemer.objects.filter(username=username).delete()
                        deleteUser.delete()
                        get_object_or_404(User, username=username).delete()
                        messages.info(request, 'The user ' + username + ' and all user\'s data have been deleted')
    return HttpResponseRedirect(reverse('user:student-manager-admin'))

def student_manager_admin(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists():
            userdata = UserData.objects.filter(school=ud.school).order_by('first_name', 'last_name')
            context = {'userdata': userdata, 'curr_user': ud}
            return render(request, 'user/student-manager-admin.html', context)
    return HttpResponseRedirect(reverse('user:index'))

def change_mode_admin(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists():
            ud.school.student_mode_for_admins = not ud.school.student_mode_for_admins
            ud.school.save()
            return HttpResponseRedirect(reverse('user:index'))
    return HttpResponseRedirect(reverse('user:index'))

def show_feedback_admin(request):
    context = {}
    if request.user.is_superuser:
        feedback = Feedback.objects.all()
        count = feedback.count() // 2
        context['feedbackFirst'] = feedback[:count]
        context['feedbackSecond'] = feedback[count:]
        return render(request, 'user/show-feedback-admin.html', context)
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        if request.user.groups.filter(name='gcadmin').exists():
            feedback = Feedback.objects.filter(school=ud.school)
            count = feedback.count() // 2
            context['feedbackFirst'] = feedback[:count]
            context['feedbackSecond'] = feedback[count:]
            return render(request, 'user/show-feedback-admin.html', context)
    return HttpResponseRedirect(reverse('user:index'))
