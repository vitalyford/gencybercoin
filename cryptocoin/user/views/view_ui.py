from .views_global import *


def update_header(request):
    if request.user.is_authenticated and request.method == 'POST' and 'brand' in request.POST and 'title' in request.POST:
        ud = get_object_or_404(UserData, username=request.user.username)
        if ud.is_admin:
            brand = request.POST.get('brand').strip()
            title = request.POST.get('title').strip()
            school = get_object_or_404(School, name=ud.school.name)
            if brand != '': school.brand = brand
            if title != '': school.title = title
            if validate_on_save(request, school): school.save()
    return HttpResponseRedirect(reverse('user:index'))
