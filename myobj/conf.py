from myobj import utils
from django.conf import settings
DEBUGSQL = True
PROJECT_NAME = (settings.ROOT_URLCONF).split('.')[0]
MYSPACE_TABLES_CHOICES = (
    (1, 'my'),
    (2, 'system'),
    ### START EXAMP ###
    #(3, 'exampleheaders'),
    ### END EXAMP ###
)

UPARAMS_MYSPACES = {
    'my': {'vlistcolumns': ['id','name'], 'editcolumns': ['name','content','sort']},
    'system': {'vlistcolumns': ['id','name'], 'editcolumns': ['name','sort']},
    ### START EXAMP ###
    #'exampleheaders': {'vlistcolumns': ['id','name'], 'editcolumns': ['name',('locations','myobj.models__examplelocationhome'),('sales','myobj.models__examplesellers')]},
    ### END EXAMP ###
}

NAMEUPLOADMODEL = 'myobj.models__systemuploadsfiles'

STRUCT_MODELS = {
    ### START EXAMP ###
    #'myobj.models__examplelocationhome':
    #    {'editcolumns': ['name','locat_chois'], 'vlistcolumns': ['id','name','locat_chois'], 'links': [('aggregation', 'myobj.models__examplelocationhome')]},
    #'myobj.models__examplesellers':
    #    {'editcolumns': ['name','description'], 'vlistcolumns': ['id','name'], 'links': [('locations', 'myobj.models__examplelocationhome')]},
    ### END EXAMP ###
    NAMEUPLOADMODEL: 
        {'editcolumns': ['name','dfile'], 'vlistcolumns': ['id','name','dfile']},
}

FORMS_ELEMENT_EDIT = {
    'uclasses': ['name','codename','description','tablespace'],
    'objproperties': ['name','codename','description','myfield','minfield','maxfield','required', 'udefault'],
    'uobjects': [],
}

#names columns MODEL lines
TYPES_COLUMNS = {
    'char': 'upcharfield',
    'text': 'uptextfield',
    'integer': 'upintegerfield',
    'float': 'upfloatfield',
    'time': 'uptimefield',
    'date': 'updatefield',
}

TYPES_MYFIELDS_CHOICES = (
    (1, 'str'),
    (2, 'text'),
    (3, 'int'),
    (4, 'float'),
    (5, 'html'),
    (6, 'date'),
    (7, 'time'),
    (8, 'url'),
    (9, 'ip'),
    (10, 'email'),
    (11, 'bool'),
    (12, 'files'),
)

TYPES_MYFIELDS = (
    ('str', 'char'),
    ('text', 'text'),
    ('int', 'integer'),
    ('float', 'float'),
    ('html', 'text'),
    ('date', 'date'),
    ('time', 'time'),
    ('url', 'char'),
    ('ip', 'char'),
    ('email', 'char'),
    ('bool', 'char'),
    ('files', 'text'),

)

NAVENTRY = 'ru/'

MAXMIN_MYFIELDS = [1,2,3,4] #TYPES_MYFIELDS_CHOICES
nameadmin_patch = 'admin'
UPLOADMEDIA_PATCH = 'ucmsfiles'

listtopmen = [
    (
        'OOAD',
        [('classes', [('add','/' + nameadmin_patch + '/myobj/uclasses/0')],'/' + nameadmin_patch + '/myobj/uclasses/'), ('properties', [('add','/' + nameadmin_patch + '/myobj/objproperties/0')],'/' + nameadmin_patch + '/myobj/objproperties'),('objects','/' + nameadmin_patch + '/myobj/uobjects')],
        '/' + nameadmin_patch + '/myobj/uclasses/'
    ),
    (
        'templates',
        [('views','/' + nameadmin_patch + '/myobj/uobjects/class/views_system')],
        '/' + nameadmin_patch + '/myobj/uobjects/class/template_system'
    ),    (
        'navigation',
        [('params','/' + nameadmin_patch + '/myobj/uobjects/class/params_system')],
        '/' + nameadmin_patch + '/myobj/uobjects/class/menu_system'
    ),
    (
        'sys',
        [('model', [(namemodel, '/' + nameadmin_patch + '/myobj/uobjects/model/' + namemodel) for namemodel in STRUCT_MODELS.keys()], ''), ('permission','/' + nameadmin_patch + '/myobj/uobjects/class/group_system')],
    )
]
#('add','/' + nameadmin_patch + '/uobjects/model/')
sntui = [('add','urladd'), ('remove','urlremove'), ('edit','urledit'), ('csv', [('export', 'csvexp', 'clcsvexp'), ('import', 'csvimp')], '')]

TYPES_DEF_CLASSES = {
    'uclasses': 
{
    'namenormal': 'Classes',
    'userui': sntui + [('properties', 'urlpropclass', 'classlinkm'), ('objects', [('add','urladdobjectsfromclass')], 'urlclassobjects', 'classlinkm'), ('aggregation', 'urlaggregation', 'classlinkm')], 
    'name': ['id', 'name', 'codename', 'description', 'tablespace'], 
    'namep': ['id', u'name', u'code name', u'description', u'table space'], 
    'namecont': u'Classes'
},
    'objproperties': 
{
    'namenormal': 'Properties',
    'userui': sntui,
    'name': ['id', 'name', 'codename', 'description', ],
    'namep': ['id', u'name', u'code name', u'code name'],
    'namecont': u'Properties'
},
    'uobjects': 
{
    'namenormal': 'Objects', 
    'userui': sntui + [('links', 'urllinksobj', 'classlinkm')], 
    'name': [], 
    'namep': [], 
    'namecont': u'Objects'
}
}

CLASS_NAME_MENU = 'menu_system'
CLASS_NAME_VIEWS = 'views_system'
CLASS_NAME_GROUP = 'group_system'
CLASS_NAME_HANDLE = 'handle_system'
PROP_NAME_PARENT_MENU = 'parent_elnav_system'
PROP_PATCH_TEMPLATE_SYS = 'patch_tamplate_system'
CLASS_PARAMSNAV_SYS = 'params_system'

def vi_proc(request):
    urlpath = [s for s in request.path.split('/') if s!='']
    paramslisturl = [pr for pr in request.path_info.split('/') if pr != '']
    dicturls = {
        'myadm': paramslisturl[0] + '/' +paramslisturl[1],
        'class': paramslisturl[2],
        'paramslist': paramslisturl[3:] + ['']
    }
    return {
        'urls': dicturls,
        'topmenu': utils.mumenrec(listtopmen)
    }
#return list id, add class group 'adminsite', 'notauthorized', 'staff', 'superuser'
def getusergrouplist(requestobj=None):
    groups = []
    if(requestobj.user.is_authenticated()): 
        groups.append('authorized')
        if(requestobj.user.is_staff): groups.append('staff')
        if(requestobj.user.is_superuser): groups.append('superuser')
    else: groups.append('notauthorized')
    if(requestobj.user.groups.count() > 0):
        groups.extend([objgrp.name for objgrp in requestobj.user.groups.all()])
    return groups
    
COUNTPAGEELEMENTS = 200
COUNTPAGEELEMENTSLEFT = 10