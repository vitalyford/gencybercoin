from django import template
from django.contrib.auth.models import Group
from user.models import PortalSetting, UserData

register = template.Library()


@register.filter(name='group_number_equals')
def has_group(user, group):
    try:
        ud = UserData.objects.get(username=user.username)
        for s in group:
            if ud.group_number == s['group_number']:
                return True
        return False
    except:
        return False


@register.filter(name='check_atlantis')
def student_mode(user):
    ud = UserData.objects.get(username=user.username)
    return bool(ud.team_number)


@register.filter(name='student_mode')
def student_mode(user):
    ud = UserData.objects.get(username=user.username)
    student_mode = ud.school.student_mode_for_admins
    return student_mode


@register.filter(name='is_admin')
def is_admin(user):
    try:
        return UserData.objects.get(username=user.username).is_admin
    except:
        return False


@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
        ud = UserData.objects.get(username=user.username)
        if ud.is_admin:
            student_mode = ud.school.student_mode_for_admins
            if student_mode:
                return False
        return True if group in user.groups.all() else False
    except:
        return False


@register.filter(name='has_bug_bounty')
def has_bug_bounty(user):
    try:
        ud = UserData.objects.get(username=user.username)
        bug_bounty_enabled = PortalSetting.objects.get(school=ud.school, name="bug_bounty_enabled").value
        if bug_bounty_enabled == "true":
            return True
    except:
        pass
    return False


@register.filter(name='has_se')
def has_se(user):
    try:
        ud = UserData.objects.get(username=user.username)
        se_enabled = PortalSetting.objects.get(school=ud.school, name="se_enabled").value
        if se_enabled == "true":
            return True
    except:
        pass
    return False


@register.filter(name='get_school')
def get_school(user):
    try:
        ud = UserData.objects.get(username=user.username)
        return ud.school.name
    except:
        pass
    return ""


@register.filter(name='get_brand')
def get_school(user):
    try:
        ud = UserData.objects.get(username=user.username)
        return ud.school.brand
    except:
        pass
    return ""


@register.filter(name='get_title')
def get_school(user):
    try:
        ud = UserData.objects.get(username=user.username)
        return ud.school.title
    except:
        pass
    return ""
