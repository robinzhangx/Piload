from django.conf.urls import patterns, include, url
from rest_framework import routers
from piload import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'task', views.TaskViewSet)
router.register(r'status', views.StatusViewSet)
router.register(r'download', views.DownloadViewSet, 'download')

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'app.views.home', name='home'),
    # url(r'^app/', include('app.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^add$', views.add_task_view, name='add_task_view'),
    url(r'^submit$', views.submit_task_view, name='submit_task_view'),
    url(r'^update$', views.update_status_view, name='update_status_view'),
    url(r'^logout$', views.logout_view, name='logout_view'),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token'),
)
