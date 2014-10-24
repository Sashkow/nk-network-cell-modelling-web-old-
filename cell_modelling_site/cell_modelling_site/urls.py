from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cell_modelling_site.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
	#url(r'^graphs/(?P<N>\d+)/(?P<K>\d+)',include('graphs.urls')),
	url(r'^graphs/',include('graphs.urls')),
	url(r'^admin/', include(admin.site.urls)),
)
