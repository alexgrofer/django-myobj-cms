from django.template.loader import get_template
from django.http import HttpResponseRedirect
from django.conf import settings
from myobj import conf as MYCONF
from django.template import Context, Template
from django import template
from django.utils import importlib
from myobj import utils
register = template.Library()
from django.db import connection
import time
@register.filter(name='handle')

def handle(value, paramscms):
    start_time = time.time()
    if(hasattr(handle, 'tracingstr') == False): handle.tracingstr = ''
    if(hasattr(handle, 'loadmodul') == False): handle.loadmodul = {}
    handle.countiter = (handle.countiter + 1) if hasattr(handle, 'countiter') else 1
    handle.handlesnav = handle.handlesnav if hasattr(handle, 'handlesnav') else paramscms['itemnav'].links('handle_system')
    handle.handleobj = handle.handleobj if hasattr(handle, 'handleobj') else dict([(objh.name, {'view': objh.links('views_system',False),'grouplist': [objgroup.name for objgroup in objh.links('views_system',False).links('group_system')] if objh.links('views_system',False) != False else [],'template': objh.links('template_system',False)}) for objh in handle.handlesnav.select_related().all()])
    html = ''
    tracing = ''
    #permission
    if(len(handle.handleobj) == 0 or handle.handleobj.has_key(value) == False): return ''
    blokview = True
    for idmygroup in paramscms['request'].mygrouplist:
        if(idmygroup in handle.handleobj[value]['grouplist']):
            blokview = False
            break
    #if there are no groups that show
    if(blokview == True and len(handle.handleobj[value]['grouplist']) != 0): return ''
    viewobj = handle.handleobj[value]['view']
    if(viewobj != False):
        
        templateobj = handle.handleobj[value]['template']
        patchtemplate = False
        if(templateobj != False):
            patchtemplate = templateobj.propertiesdict['patch_tamplate_system']
        
        namemodul = viewobj.propertiesdict['importmodul_system']
        nameview = viewobj.propertiesdict['nameimport_view_system']
        
        startlenq = len(connection.queries)
        ERRVIEW = False
        try:
            if(handle.loadmodul.has_key(namemodul) == False):
                getmodul = importlib.import_module(namemodul)
                handle.loadmodul[namemodul] = getmodul
            
            linkfunk = handle.loadmodul[namemodul].__getattribute__(nameview)
            try:
                datacontext = linkfunk(**paramscms)
            except:
                ERRVIEW = True
            
            if(paramscms['HttpResponseRedirect']['link'] == None and isinstance(datacontext,HttpResponseRedirect)):
                paramscms['HttpResponseRedirect']['link'] = datacontext
            
            querydictend = connection.queries
            strsqlq = ''
            if(settings.DEBUG == True and MYCONF.DEBUGSQL == True):
                timeallsql = 0
                for sqlline in querydictend[startlenq:]:
                    timeallsql += float(sqlline['time'])
                if(len(querydictend[startlenq:]) > 0):
                    strsqlq = "'SQL': [\n\t" + "\n\t".join(["{'time': '" + dictp['time'] + "', 'sql': '" + dictp['sql'] + "'}," for dictp in querydictend[startlenq:]]) + "\n], 'countQ': " + str(len(querydictend[startlenq:])) + ", 'timeQ': " + str(timeallsql)
            if(templateobj != False):
                t = get_template(patchtemplate)
                renderhtml = t.render(Context({'datacontext': datacontext}))
            else:
                renderhtml = str(datacontext)
            html = renderhtml
            #tracing
            end_time = time.time()
            tracing = "\n{'view': 'nview: " + namemodul + "." + nameview + "(L" + str(viewobj.id) + "), ntempl: " + str(patchtemplate) + "(L" + (str(templateobj.id) if templateobj else '') + "), time: " + str(("%.3f" % (end_time - start_time))) + "', \n" + strsqlq + "\n},"
            handle.tracingstr += tracing
        except Exception as e:
            if(settings.DEBUG == True):
                del handle.countiter, handle.handlesnav, handle.handleobj, handle.tracingstr, handle.loadmodul
                if(ERRVIEW == True):
                    return linkfunk(**paramscms)
                else:
                    raise
            else:
                html = ''
    
    if(handle.countiter == paramscms['counthand']):
        if(settings.DEBUG == True):
            html += "<script>var tracingsys = [" + handle.tracingstr + "];</script>"
        del handle.countiter, handle.handlesnav, handle.handleobj, handle.tracingstr, handle.loadmodul
    
    return html