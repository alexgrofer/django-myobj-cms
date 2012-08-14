from django.conf.urls.defaults import *
from myobj import conf as MYCONF

urlpatterns = patterns(MYCONF.PROJECT_NAME + '.myobj.views',
    (r'^(?P<type>' + '|'.join(MYCONF.TYPES_DEF_CLASSES.keys()) + ')/(?P<params>.*)','options.get_url'),
    #site
    (r'^(?P<namem>[0-9a-z]*)/(?P<params>.*)','getsite.getpage'),
)
