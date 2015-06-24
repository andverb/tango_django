from django.conf.urls import url
from rango import views
from rango.views import UsersList
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^category/(?P<category_name_slug>[\w-]+)$', views.category, name='category'), ## [\w-]+ instead \w+ bcz '-' wasnt match
    url(r'^add_category/$', views.add_category, name='add_category'),
    url(r'^category/(?P<category_name_slug>[\w-]+)/add_page/$', views.add_page, name='add_page'),
    #url(r'^register/$', views.register, name='register'), # ADD NEW PATTERN!
    #url(r'^login/$', views.user_login, name='login'),
    #url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^restricted/', views.restricted, name='restricted'),
    url(r'^rango/goto/(?P<page_id>\d+)$', views.track_url, name='goto'),
    url(r'^profile/(?P<user_id>\d+)$', views.profile, name='profile'),
    #url(r'^profile/username(?P<user_slug>[\w-]+)$', views.profile, name='profile'),

    ## TODO add slugify and nickname to user profile
    url(r'^userslist/$', UsersList.as_view(), name='userslist'),

]

