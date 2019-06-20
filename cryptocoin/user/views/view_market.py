from .views_global import *


def submit_cart(request):
    if request.user.is_authenticated:
        for key in request.POST:
            ud = get_object_or_404(UserData, username=request.user.username)
            # allow to add items in the cart to only top players, also check if market is enabled
            market_enabled = get_object_or_404(PortalSetting, name="market_enabled", school=ud.school).value
            if "add" in str(key) and market_enabled == "true":
                players = get_top_players(request, ud)
                if players['top_player'] == "true":
                    try:
                        c = ud.cart.market_items.all()
                    except:
                        c = Cart(user_data=ud)
                        c.save()
                        messages.warning(request, 'You cart has not been created before for some reason. It exists now though so try to order again!')
                        break
                    try:
                        md = get_object_or_404(MarketItem, id=int(key.replace("add", "")), school=ud.school)
                    except:
                        messages.warning(request, 'Hmm, trying to mess with us, huh. Nope ;-)')
                        break
                    if md.quantity <= 0:
                        messages.warning(request, 'Sorry, we are out of stock for ' + md.name)
                        break
                    program_type = get_object_or_404(PortalSetting, school=ud.school, name='program_type').value
                    # if the program is classroom then check for the wrong tier as user validation
                    '''if program_type == 'classroom':
                        if md.tier > ud.tier:
                            # bug bounty
                            run_bug_bounty(request, ud, 'server_side_input_validation', 'Congrats! You found a programming bug on server-side validation. This bug would allow you to get the item that you are not supposed to get!', 'https://www.owasp.org/index.php/Input_Validation_Cheat_Sheet')
                            # end bug bounty
                            break'''
                    already_bought = c.filter(name=md.name).count()
                    if already_bought > 0:
                        messages.warning(request, 'Sorry, we have limited supply, you can buy only one ' + md.name)
                        break
                    # get the price from the submitted item depending on the program type
                    try:
                        if program_type == 'classroom':
                            item_price = md.cost_permanent
                            if int(request.POST.get('checkers')) != md.cost_permanent:
                                raise
                        else:  # if program type is camp or any other one
                            item_price = int(request.POST.get('checkers'))
                            if item_price < 0:
                                raise
                            # resetting the price to a random one
                            set_market_prices([md], ud)
                            item_price = md.cost_permanent
                    except:
                        # bug bounty
                        run_bug_bounty(request, ud, 'bug#11:client_side_input_validation', 'Congrats! You found a programming bug on client-side/hidden-field input validation. This bug would allow you to get the money back for the item you have just bought => direct profit!', 'https://www.owasp.org/index.php/Input_Validation_Cheat_Sheet')
                        # end bug bounty
                        break
                    # save only if the user can afford it in the cart
                    if item_price <= ud.permanent_coins:  # + cart.cost_permanent <= available_coins:
                        md.cost_permanent = item_price
                        ud.cart.market_items.add(md)
                        ud.cart.save()
                        # reduce quantity by 1
                        md.quantity = md.quantity - 1
                        md.save()
                        ud.permanent_coins = ud.permanent_coins - item_price
                        ud.items_bought = ud.items_bought + 1
                        # in classroom, users can buy only once per turn, so set the tier back to 0
                        if program_type == 'classroom':
                            ud.tier = 0
                        ud.save()
                    else:
                        messages.warning(request, 'You cannot afford ' + md.name)
                    break
                else:
                    # bug bounty
                    run_bug_bounty(request, ud, 'bug#12:race_condition_when_ordering', 'Congrats! You found a programming bug on adding an item when it was not your turn! This bug would allow you to add any item regardless of your turn in the queue.', 'https://www.owasp.org/index.php/Testing_for_Race_Conditions_%28OWASP-AT-010%29')
                    # end bug bounty
    if 'page' in request.GET:
        return HttpResponseRedirect(reverse('user:market') + "?page=" + request.GET.get('page'))
    return HttpResponseRedirect(reverse('user:market'))


def get_cart(request, ud):
    context = {}
    curr_sum = 0
    try:
        c = ud.cart.market_items.all()
    except:
        context['error_message'] = "Your cart does not exist, we will create one for you"
        c = Cart(user_data=ud)
        c.save()
        return context
    if c.count() > 0:
        curr_sum = int(c.aggregate(cost=Sum('cost_permanent'))['cost'])
    context['total'] = str(curr_sum)
    return context


def remove_cart_item(request, key, ud):
    market_enabled = get_object_or_404(PortalSetting, name="market_enabled", school=ud.school).value
    if market_enabled == "false":
        return
    try:
        c = ud.cart
        id = int(key.replace("remove", ""))
        # bug bounty
        if c.market_items.filter(id=id).count() == 0:
            run_bug_bounty(request, ud, 'bug#13:refresh_on_remove', 'Congrats! You found a programming bug on refreshing (resubmitting) the page after you removed an item from the cart! This bug would allow you to get the money back as many times as you want for the item you have just removed. Also, it would add more available items in the market itself.', 'https://en.wikipedia.org/wiki/Replay_attack')
            return
        # end bug bounty
        md = get_object_or_404(MarketItem, id=id)
        c.market_items.remove(md)
    except:
        return
    c.save()
    md.quantity = md.quantity + 1
    md.save()
    ud.permanent_coins = ud.permanent_coins + md.cost_permanent
    ud.items_bought = ud.items_bought - 1
    ud.save()


def set_market_prices(marketdata, ud):
    # this can be refactored to speed up (something to think about later)
    # this commented part is an algorithm that takes into account all top_players
    '''users = UserData.objects.filter(school=ud.school, is_admin=False, username__in=top_players).order_by('-permanent_coins')
    min_coins, max_coins = 0, 0
    min = users.aggregate(Min('permanent_coins'))['permanent_coins__min']
    min_coins = min // 4
    max_coins = min // 2'''
    # take into account the current's user available coins
    available_coins = ud.permanent_coins
    min_coins = available_coins // 4
    max_coins = available_coins // 2
    for m in marketdata:
        m.cost_permanent = randint(min_coins, max_coins)


def market_queue(request):
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        context = get_top_players(request, ud)
        context['cart_size'] = ud.cart.market_items.count()
        context['status'] = "success"
        return JsonResponse(context)
    return goto_login(request, "market")


def market(request):
    context = {}
    if request.user.is_authenticated:
        ud = get_object_or_404(UserData, username=request.user.username)
        # take care of removing an item from the cart in the camp
        program_type = get_object_or_404(PortalSetting, school=ud.school, name='program_type').value
        if request.method == 'POST' and program_type == 'camp':
            for key in request.POST:
                if "remove" in str(key):
                    remove_cart_item(request, key, ud)
                    break
        # get the cart
        context.update(get_cart(request, ud))
        items_in_the_cart = ud.cart.market_items.all()
        context['cart'] = items_in_the_cart
        context.update(get_top_players(request, ud))
        context.update(get_portal_settings(ud.school))
        if context['ajax_enabled'] == "true" and context['market_enabled'] == "true":
            if context['top_player'] == "false":
                if program_type == 'classroom':
                    messages.info(request, 'You will be able to order next time you get to the top-' + context['top_students_number'])
                else:
                    messages.info(request, 'The queue will automatically notify you when it is your turn to order')
            else:
                messages.info(request, 'Order NOW!')
        # pagination setup
        all_market_data = get_all_market_data(request, ud)
        context['available_coins'] = all_market_data['available_coins']
        if context['pagination_enabled'] == "true":
            paginator = Paginator(all_market_data['marketdata'], 20)
            page = request.GET.get('page')
            if not page: page = 1
            # bug bounty
            if context['bug_bounty_enabled'] == "true":
                try:
                    page_int = int(page)
                    if page_int < 1 or page_int > paginator.num_pages:
                        raise
                except:
                    context['available_coins'] += run_bug_bounty(request, ud, 'bug#10:local_file_inclusion', 'Congrats! You found a programming bug that can cause a local file inclusion. This bug would allow you to potentially read every file on the server!', 'https://www.owasp.org/index.php/Testing_for_Local_File_Inclusion')
            # end bug bounty
            items = paginator.get_page(page)
            if program_type == 'camp':
                set_market_prices(items, ud)
            context['marketdata'] = items
        else:
            if program_type == 'camp':
                set_market_prices(all_market_data['marketdata'], ud)
            context['marketdata'] = all_market_data['marketdata']
        return render(request, 'user/market.html', context)
    return goto_login(request, "market")


def get_top_players(request, ud):
    context = {}
    program_type = get_object_or_404(PortalSetting, school=ud.school, name='program_type').value
    if program_type == "classroom":
        # get all users depending on the program type, admins and superuser do not count
        users = UserData.objects.filter(school=ud.school, is_admin=False, tier__gt=0).order_by('-permanent_coins')
        top_users = []
        context['top_player'] = "false"
        for user in users:
            top_users.append(user.username)
            # just in case if a cart has not been created yet
            c, created = Cart.objects.get_or_create(user_data=user)
            if created: c.save()
            # assign the top player to the current user if possible
            if user.username == request.user.username:
                context['top_player'] = "true"
                context['player_tier'] = user.tier
        context['top_players'] = top_users
        # top_students_number = get_object_or_404(PortalSetting, school=ud.school, name="top_students_number")
        # queue_capacity = int(top_students_number.value)
        context['top_students_number'] = users.count()
    else:  # for camp and all others
        return camp_top_players(request, ud)
    return context


def camp_top_players(request, ud):
    context = {}
    # get all users depending on the program type, admins and superuser do not count
    users = UserData.objects.filter(is_admin=False, school=ud.school).order_by('items_bought', '-permanent_coins')
    total_users = users.count()
    context['top_player'] = "false"
    if total_users > 0:
        top_users = []
        try:
            top_students_number = get_object_or_404(PortalSetting, school=ud.school, name="top_students_number")
            queue_capacity = int(top_students_number.value)
        except:
            queue_capacity = 3
        # find top-(n+3) students
        roof = min(total_users, max(queue_capacity, 3) + 3)
        # check if someone started ordering
        someone_started_ordering = False
        try:  # just in case if a cart has not been created yet
            latest_time = users[0].cart.date
        except:
            for user in users:
                c, created = Cart.objects.get_or_create(user_data=user)
                if created: c.save()
            latest_time = users[0].cart.date
        user_with_the_latest = users[0]
        for user in users:
            if user.cart.market_items.count() > 0:
                someone_started_ordering = True
                latest_time = max(user.cart.date, latest_time)
                user_with_the_latest = user
        # find top players
        already_increased_queue_capacity = False
        for i in range(0, roof):
            top_users.append(users[i].username)
            # allow top-n students to order market items
            if i < queue_capacity and users[i].username == request.user.username:
                context['top_player'] = "true"
            # if previous top users did not order anything within X min, allow 2 more users to order
            if (i + 1) == roof and queue_capacity < total_users and not already_increased_queue_capacity and someone_started_ordering:
                # get the queue auto-expansion wait period
                try:
                    queue_wait_period = float(get_object_or_404(PortalSetting, school=ud.school, name="queue_wait_period").value)
                except:
                    queue_wait_period = 1
                if queue_wait_period >= 0 and (timezone.now() - latest_time).total_seconds() > queue_wait_period * 60:
                    user_with_the_latest.cart.date = timezone.now()
                    user_with_the_latest.cart.save()
                    already_increased_queue_capacity = True
                    roof += 2
                    queue_capacity += 2
                    top_students_number.value = str(queue_capacity)
                    top_students_number.save()
        context['top_players'] = top_users
        context['top_students_number'] = queue_capacity
    return context
