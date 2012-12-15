http://alexgro.github.com/django-myobj-cms/
================

django-myobj-cms
================

1. django-admin.py startproject mysite (If this is a new project)

2. python manage.py startapp myobj

3. Edit the 'urls.py'

from django.conf.urls.defaults import patterns, include
from myobj import conf as MYCONF
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
```python
urlpatterns = patterns('',
    (r'^' + MYCONF.NAVENTRY, include(MYCONF.PROJECT_NAME + '.myobj.urls')), # /ru/1 or /1, '1' - obj nav
    (r'^admin/myobj/', include(MYCONF.PROJECT_NAME + '.myobj.urls')),
    
    (r'^admin/', include(admin.site.urls)),
)
```
The entry point (MYCONF.NAVENTRY) may be empty or edited, by default, 'ru'

4. copy the files in the project

5. Put 'django.contrib.admin' and 'mysite.myobj' in your INSTALLED_APPS setting

6. python manage.py syncdb

7. go http://sitename/admin/myobj/uobjects/class/menu_system (or /admin/myobj/uclasses/install), and click install