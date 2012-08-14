from django.shortcuts import render_to_response
from myobj.conf import NAVENTRY, getusergrouplist
from myobj.models import uClasses
from django.conf import settings
from django.template import loader, VariableNode, Template, Context
from django.http import HttpResponse, Http404

def getpage(request, *args, **kwargs):
    #get urls
    actionurl = [pr for pr in request.path_info.split('/') if pr != '']
    classmenu = uClasses.objects.get(codename='menu_system')
    itemnav = actionurl[1] if (NAVENTRY != '') else actionurl[0]
    for i in range(10):
        if(i+1 > len(actionurl)): actionurl.append('')
    if(str(itemnav).isdigit()):
        objmenu = classmenu.getobjects(id=itemnav)
    else:
        objmenu = classmenu.getobjprop(codename_system=itemnav)
    try: mythisnav = objmenu[0]
    except IndexError: raise Http404
    templateobj = mythisnav.links('template_system',False)
    request.__setattr__('mygrouplist', getusergrouplist(requestobj = request))
    counthandles = 0
    ObjHttpResponseCOOKIE = HttpResponse()
    tempt = loader.get_template(templateobj.propertiesdict['patch_tamplate_system'])
    for variable in tempt.nodelist.get_nodes_by_type(VariableNode):
        token = variable.filter_expression.token
        indh = token.find('|handle:')
        if(indh != -1):
            counthandles += 1
    ObjHttpResponseRedirect = {'link': None}
    mycontextdict = {'paramsreq': {'counthand': counthandles,'request': request, 'itemnav': mythisnav, 'actionurl': actionurl, 'HttpResponseRedirect': ObjHttpResponseRedirect, 'httpresponse_cookie': ObjHttpResponseCOOKIE}}
    response = render_to_response(templateobj.propertiesdict['patch_tamplate_system'], mycontextdict)
    if(ObjHttpResponseRedirect['link'] != None):
        return ObjHttpResponseRedirect['link']
    if(len(ObjHttpResponseCOOKIE.cookies) > 0):
        response.cookies = ObjHttpResponseCOOKIE.cookies
    return response
