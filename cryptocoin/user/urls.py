from django.conf.urls import url
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from . import views

app_name = 'user'

urlpatterns = [
    url(r'^gcsuperuser/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^5ebe2294ecd0e0f08eab7690d2a6ee69$', views.secret, name='secret'),
    #url(r'^driblets/$', views.driblets, name='driblets'),
    url(r'^register/$', views.register, name='register'),
    url(r'^wallet/$', views.wallet, name='wallet'),
    url(r'^update/header/$', views.update_header, name='update-header'),
    url(r'^wallet/submit/$', views.submit_wallet, name='submit-wallet'),
    url(r'^account-creation/$', views.account_creation, name='account-creation'),
    url(r'^account/$', views.user_account, name='account'),
    url(r'^account/submit/$', views.submit_user_account, name='submit-account'),
    url(r'^account/transfer/$', views.transfer, name='transfer'),
    url(r'^password-recovery/$', views.password_recovery, name='password-recovery'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^login-process/$', views.user_login_process, name='login-process'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^market/$', views.market, name='market'),
    url(r'^market/queue/$', views.market_queue, name='market-queue'),
    url(r'^market/submit-cart/$', views.submit_cart, name='submit-cart'),
    url(r'^manage/change-mode-admin/$', views.change_mode_admin, name='change-mode-admin'),
    url(r'^manage/code-generator/$', views.code_generator, name='code-generator'),
    url(r'^manage/submit-code-generator/$', views.submit_code_generator, name='submit-code-generator'),
    url(r'^manage/nominations-admin/$', views.nominations_admin, name='nominations-admin'),
    url(r'^manage/submit-nominations-admin/$', views.submit_nominations_admin, name='submit-nominations-admin'),
    url(r'^manage/achievements-admin/$', views.achievements_admin, name='achievements-admin'),
    url(r'^manage/submit-achievements-admin/$', views.submit_achievements_admin, name='submit-achievements-admin'),
    url(r'^manage/market-admin/$', views.market_admin, name='market-admin'),
    url(r'^manage/market-admin/submit$', views.submit_market_admin, name='submit-market-admin'),
    url(r'^manage/settings-admin/$', views.settings_admin, name='settings-admin'),
    url(r'^manage/submit-settings-admin/$', views.submit_settings_admin, name='submit-settings-admin'),
    url(r'^manage/student-carts-admin/$', views.student_carts_admin, name='student-carts-admin'),
    url(r'^manage/student-manager-admin/$', views.student_manager_admin, name='student-manager-admin'),
    url(r'^manage/submit-student-manager-admin/$', views.submit_student_manager_admin, name='submit-student-manager-admin'),
    url(r'^manage/show-feedback-admin/$', views.show_feedback_admin, name='show-feedback-admin'),
    url(r'^manage/submit-feedback-admin/$', views.submit_feedback_admin, name='submit-feedback-admin'),
    url(r'^manage/pdf-codes-admin/$', views.pdf_codes_admin, name='pdf-codes-admin'),
    url(r'^extras/cryptocurrency/$', views.extras_cryptocurrency, name='extras-cryptocurrency'),
    url(r'^extras/bug-bounty/$', views.extras_bug_bounty, name='extras-bug-bounty'),
    url(r'^extras/hall-of-fame/$', views.extras_hall_of_fame, name='extras-hall-of-fame'),
    url(r'^extras/social-engineering/$', views.extras_social_engineering, name='extras-social-engineering'),
    url(r'^extras/social-engineering-admin/$', views.extras_social_engineering_admin, name='extras-social-engineering-admin'),
    url(r'^extras/social-engineering/submit/$', views.submit_social_engineering, name='submit-social-engineering'),
    url(r'^extras/social-engineering-admin/submit/$', views.submit_social_engineering_admin, name='submit-social-engineering-admin'),
    url(r'^extras/blockchain/$', views.extras_blockchain, name='extras-blockchain'),
    url(r'^extras/feedback/$', views.extras_feedback, name='extras-feedback'),
    url(r'^extras/submit-feedback/$', views.submit_extras_feedback, name='submit-extras-feedback'),
    url(r'^.*$', RedirectView.as_view(permanent=False, url='/')),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
