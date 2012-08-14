from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms
from django.contrib.admin.views.decorators import staff_member_required
import math
from django.conf import settings
from django.utils import importlib
from myobj.models import uClasses, objProperties, get_space_model, TABLE_SPACE
from myobj.forms import FormUClasses, FormobjProperties, actionsetparam, designUI
from myobj import conf as MYCONF
from myobj import utils
from myobj import install as INSTALLCONF
from django.forms.models import modelformset_factory

def vi_proc_list(request):
    standartproc = MYCONF.vi_proc(request)
    return standartproc

def expcsv(file,nameclass,idclass=None):
    import csv
    if(nameclass == 'uobjects'): classobj = uClasses.objects.get(id=idclass)
    listrow = []
    if(file.__class__.__name__ == 'dict'):
        listnameparams = file['names']
        itcsv = file['values']
    else:
        itcsv = csv.reader(file)
        listnameparams = itcsv.next()
    
    for row in itcsv:
        dictr = {}
        indx = 0
        for pr in listnameparams:
            dictr[pr] = row[indx]
            indx += 1
        listrow.append(dictr)
    
    if(nameclass == 'uclasses'):
        typenewobj = uClasses
    elif(nameclass == 'objproperties'):
        typenewobj = objProperties
    elif(nameclass == 'uobjects'):
        typenewobj = get_space_model(idclass, getlines=False)
    
    iselemmtm = False
    

    errors = []
    for rowdict in listrow:
        listelemmtm = []
        dictpropobj = {}
        newobj = typenewobj()
        
        if(nameclass == 'uobjects'): newobj.uclass = classobj
        
        for named in rowdict:
            namedreal = named
            if(nameclass == 'uobjects'):
                if(named.find('headerp__') == -1):
                    dictpropobj[named] = rowdict[named]
                    continue
                else:
                    namedreal = named.replace('headerp__', '')
            try:
                if(newobj.__getattribute__(namedreal).__class__.__name__ == 'bool'):
                    rowdict[named] = True if (rowdict[named] == 'True') else False
                newobj.__setattr__(namedreal,rowdict[named])
            except ValueError:
                listelemmtm.append(named)
        if(len(listelemmtm) > 0): iselemmtm = True
        
        try:
            newobj.save()
        except Exception as e:
            dicter = {'line': str(rowdict), 'err': str(e)}
            errors.append(dicter)
        else:
            for namedmtm in listelemmtm:
                lmodel = newobj.__getattribute__(namedmtm).model
                links = lmodel.objects.filter(codename__in=rowdict[namedmtm].split(','))
                newobj.__setattr__(namedmtm,links)
            
            if(nameclass == 'uobjects'):
                newobj.propertiesdict = dictpropobj
        try:
            newobj.save()
        except Exception as e:
            dicter = {'line': str(rowdict), 'err': str(e)}
        
    if(len(errors) == 0):
        return []
    else:
        return errors

def vi_proc_form(request):
    standartproc = MYCONF.vi_proc(request)
    standartproc['myfields'] = {'minmax': [namefield[0] for namefield in MYCONF.TYPES_MYFIELDS_CHOICES if namefield[0] in MYCONF.MAXMIN_MYFIELDS]}
    return standartproc

def getclasslinksall(idclass):
    objectclass = uClasses.objects.get(id=idclass)
    classlinksall = objectclass.getspace(getlinksall=True)
    return classlinksall

class optionswitch:
    def _istherelinks(self,idobj,classid):
        try:
            linksObjectsAll = getclasslinksall(classid)
            links = linksObjectsAll.objects.get(idobj=idobj,uclass=classid)
        except:
            return False
        else: return links
    def change_list(self, request, obj, proplist, dicturls, islinks = False):
        data = {}
        data['formlist'] = actionsetparam(request.POST)
        isobjects = False
        ismenu = False
        resultnosearch = False
        listAggregationLinks = []
        if(dicturls['class']=='uobjects' and islinks == False):
            isobjects = True
            objectclass = uClasses.objects.get(id=dicturls['paramslist'][1])
            if(objectclass.codename == MYCONF.CLASS_NAME_MENU):
                ismenu = True
            proplist['name'] = proplist['namep'] = MYCONF.UPARAMS_MYSPACES[objectclass.get_tablespace_display()]['vlistcolumns']
        elif(islinks == True):
            if(dicturls['class'] == 'uclasses' and dicturls['paramslist'][1] == 'classes'):
                objectclass = uClasses.objects.get(id=dicturls['paramslist'][2])
                nameclasslinksall = objectclass.getspace(getlinksall=True)
                listAggregationLinks = [objlinksall for objlinksall in TABLE_SPACE if nameclasslinksall == TABLE_SPACE[objlinksall][2]]
            
            if(dicturls['paramslist'][0] == 'linkall'): proplist['name'] = proplist['namep'] = ['id','name','uclass']
        argsord = []
        sortnamep = '-id'
        if(request.POST.has_key('order') and request.POST['order'] != ''): sortnamep = request.POST['order']
        argsord.append(sortnamep)
        if(request.POST.has_key('order2') and request.POST['order2'] != ''): argsord.append(request.POST['order'])
        
        try:
            objects = obj.objects.all().order_by(*argsord)
        except AttributeError: #is list filtered
            objects = obj.order_by(*argsord)
        if(len(listAggregationLinks) > 0):
            objects = [objectsalesses for objectsalesses in obj.objects.all() if objectsalesses.tablespace in listAggregationLinks]
        if((len(objects) > 0) and (request.POST.has_key('searchcolumn') and request.POST['searchcolumn'] != '') and (request.POST.has_key('searchstrv') and request.POST['searchstrv'] != '')):
            searchkwargs = {}
            searchkwargs[request.POST['searchcolumn'] + '__contains'] = request.POST['searchstrv']
            resultnosearch = True
            objects = objects.filter(**searchkwargs)
        
        listnochecked = []
        if(request.POST.has_key('objectsno') and request.POST['objectsno'] != ''):
            listnochecked = [str(obj) for obj in request.POST['objectsno'].split(',')]
        listchecked = []
        #links id's
        if(dicturls['paramslist'][0] == 'model' and dicturls['paramslist'][2] == 'links' and dicturls['paramslist'][6] != '0'):
            classobj = uClasses.objects.get(id=dicturls['paramslist'][4])
            objectedits = classobj.getobjects(id=dicturls['paramslist'][6])
            listchecked = objectedits[0].propertiesdict[dicturls['paramslist'][8]].split(',')
            if(request.POST.has_key('objects') and len(request.POST['objects'].split(',')) >= len(listchecked)):
                listchecked = request.POST['objects'].split(',')
        elif(request.POST.has_key('objects') and request.POST['objects'] != ''):
            listchecked = [str(obj) for obj in request.POST['objects'].split(',')]
        if(islinks):
            if(dicturls['paramslist'][4] == 'linksmodel' and dicturls['paramslist'][3] != '0'):
                if(dicturls['paramslist'][0] != 'model'):
                    objectclass = uClasses.objects.get(id=dicturls['paramslist'][1])
                    myobjlinkp = objectclass.getobjects(id=dicturls['paramslist'][3])[0]
                else:
                    mymodelconf = dicturls['paramslist'][1]
                    strnamemodul = mymodelconf.split('__')[0]
                    strnamemodel = mymodelconf.split('__')[1]
                    objworkprep = importlib.import_module(strnamemodul).__getattribute__(strnamemodel)
                    myobjlinkp = objworkprep.objects.get(id=dicturls['paramslist'][3])
                #if files
                if(dicturls['paramslist'][5] == MYCONF.NAMEUPLOADMODEL):
                    listchecked = myobjlinkp.propertiesdict[dicturls['paramslist'][6]].split(',')
                elif(hasattr(myobjlinkp.__getattribute__(dicturls['paramslist'][6]),'model')):
                    listchecked.extend([str(dictobj['id']) for dictobj in myobjlinkp.__getattribute__(dicturls['paramslist'][6]).values('id')])
            elif(dicturls['class']=='objproperties'):
                listchecked.extend([str(dictobj['id']) for dictobj in uClasses.objects.get(id=dicturls['paramslist'][2]).__getattribute__('properties').values('id')])
            else:
                thislinks = self._istherelinks(dicturls['paramslist'][1], dicturls['paramslist'][3])
                if(dicturls['class']=='uclasses'):
                    if(dicturls['paramslist'][0] == 'link'):
                        if(thislinks):
                            listchecked.extend([str(dictobj['uclass']) for dictobj in thislinks.links.values('uclass').distinct()])
                    else:
                        listchecked.extend([str(dictobj['id']) for dictobj in uClasses.objects.get(id=dicturls['paramslist'][2]).__getattribute__('aggregation').values('id')])
                elif(dicturls['paramslist'][0] == 'linkall'):
                    if(thislinks):
                        listchecked.extend([str(dictobj['id']) for dictobj in thislinks.links.values('id')])
        if(len(listchecked) > 0):
            if(data['formlist'].data.has_key('objects')):
                data['formlist'].data['objects'] = ','.join(set(listchecked + data['formlist'].data['objects'].split(',')))
            else:
                data['formlist'] = actionsetparam(initial={'objects': ','.join(listchecked)})
        leftmen = ''
        htmltr = ''
        excludelist = []
        checkedall = ''
        if(request.POST.has_key('exclude') and request.POST['exclude'] == '1'):
            checkedall = 'checked="checked"'
            excludelist = request.POST['objects'].split(',')
        htmltr += '<tr class="head"><td id="allcheck"><input type="checkbox"' + checkedall + ' /></td>' + "".join(['<td>%s</td>' % str(nameprop) for nameprop in proplist['namep']]) + '</tr>'
        cssclasslink = 'classlinks' if islinks else ''
        def _sortmen(listquery,nlist,parent=0,leftp=''):
            parenttmp = ''
            for obj in listquery:
                if(obj.propertiesdict['parent_elnav_system'] == parent):
                    if(parent != 0 and parenttmp != parent):
                        leftp += '---'
                    obj.__setattr__('leftp',leftp)
                    nlist.append(obj)
                    parenttmp = parent
                    nlist = _sortmen(listquery,nlist,int(obj.id),leftp)
            return nlist
        
        if(ismenu):
            nlist = []
            objects = _sortmen(objects,nlist)
            
        else:
            startlenobjects = len(objects)
            countelem = MYCONF.COUNTPAGEELEMENTS
            countlinks = int(math.ceil(startlenobjects / float(MYCONF.COUNTPAGEELEMENTS)))
            try:
                indexpx = dicturls['paramslist'].index('page')
                indexpage = int(dicturls['paramslist'][indexpx + 1]) - 1
            except:
                indexpage = 0
                indexpx = dicturls['paramslist'].index('')
            else:
                if(indexpage == '1'): indexpage = 0
            if(countlinks < indexpage): indexpage = countlinks - 1
            
            startpg = countelem * indexpage
            endpg = countelem * (indexpage + 1)
            
            objects = objects[startpg:endpg]
            
        pagination = ''
        optiontop = ''
        for obj in objects:
            if(ismenu):
                leftmen = ''
                if(obj.leftp != ''): leftmen = obj.leftp
            htmltr += '<tr class="' + cssclasslink + ( ' click' if ((str(obj.id) in listchecked and (checkedall == '')) or ((checkedall != '') and (str(obj.id) not in excludelist)) ) else '' ) + '"><td><input type="checkbox" name="idob_' + str(obj.id) + '" ' + ( 'checked="checked"' if ((((str(obj.id) in listchecked) and checkedall == '') or ((checkedall != '') and str(obj.id) not in listchecked)) and (str(obj.id) not in listnochecked)) else '' ) + ' /></td>' + "".join(['<td>' + (leftmen if (nameprop=='name') else '') + '%s</td>' % (obj.__getattribute__(nameprop[0]).__getattribute__(nameprop[1]) if (isinstance(nameprop, tuple)) else obj.__getattribute__(nameprop)) for nameprop in proplist['name'] if nameprop]) + '</tr>'
        if((len(objects) == 0 or dicturls['paramslist'][0] == 'install') and resultnosearch == False):
            inhtml = ''
            urlactnone = '/' + dicturls['myadm'] + '/' + dicturls['class'] + '/class/' + dicturls['paramslist'][1] + '/obj/0' if (dicturls['class'] == 'uobjects') else '/' + dicturls['myadm'] + '/' + dicturls['class'] + '/0'
            value_in = 'add new element'
            if(dicturls['paramslist'][0] == 'link'):
                urlactnone = '/' + dicturls['myadm'] + '/' + dicturls['class'] + '/linksobj/classes/' + dicturls['paramslist'][3]
                value_in = 'select aggregation'
            elif(dicturls['paramslist'][0] == 'install'):
                value_in = 'install the system'
                inhtml = '<script>$("#addnewelementbutton").click(function() { document.forms["actnameurl"].nameurl.value = "install"; document.forms["actnameurl"].submit(); return false })</script>'
            elif(dicturls['paramslist'][0] == 'model' or dicturls['paramslist'][4] == 'linksmodel'):
                modelnamelink = dicturls['paramslist'][5]
                if(dicturls['paramslist'][4] != 'linksmodel'):
                    modelnamelink = dicturls['paramslist'][1]
                elif(dicturls['paramslist'][4] == 'linksmodel' and dicturls['paramslist'][0] == 'class'):
                    modelnamelink = dict([nameparam for nameparam in MYCONF.UPARAMS_MYSPACES[dicturls['paramslist'][5]]['editcolumns'] if isinstance(nameparam,tuple)])[dicturls['paramslist'][6]]
                urlactnone = '/' + dicturls['myadm'] + '/' + dicturls['class'] + '/model/' + modelnamelink + '/obj/0'
                del modelnamelink
                inhtml = ''
            else:
                if(dicturls['paramslist'][0] == 'linkall'):
                    urlactnone = '/' + dicturls['myadm'] + '/' + dicturls['class'] + '/class/' + dicturls['paramslist'][5] + '/obj/0'
                inhtml = '&nbsp<input id="expcsv" type="button" value="expotr csv" /><script>$("#expcsv").click(function() { $(".clcsvexp a:first").trigger("click"); })</script>'
            htmltr = '<tr><td colspan="'+ str(len(proplist['name']) + 1) +'"><form action="'+ urlactnone +'"><input id="addnewelementbutton" type="submit" value="' + value_in + '" />'+ inhtml +'</form></td></tr>'
        else:
            optiontop = ''
            ordersnamep = []
            ordersnamep.extend(proplist['namep'])
            ordersnamep.extend(['-' + namep for namep in proplist['namep']])
            ordersname = []
            ordersname.extend(proplist['name'])
            ordersname.extend(['-' + (namep[0] if (isinstance(namep, tuple)) else namep) for namep in proplist['name']])
            
            searchnamecolumn = '<div id="sotrtypeobj-searchc">search column: <select id="searchncol" name="searchncol">' + ''.join(['<option ' + ( 'selected="selected"' if (request.POST.has_key('searchcolumn') and request.POST['searchcolumn'] == (namep[0] if (isinstance(namep, tuple)) else namep)) else '') + ' value="' + ((namep[0] + '__' + namep[1]) if (isinstance(namep, tuple)) else namep) + '">' + proplist['namep'][proplist['name'].index(namep)] + '</option>' for namep in proplist['name']]) + '</select></div>'
            searchstropt = searchnamecolumn + '<div id="search-opt">search: <input name="searchstr" type="text" value="' + (request.POST['searchstrv'] if (request.POST.has_key('searchstrv') and request.POST['searchstrv']) else '') + '" /></div>'
            selectin = '<div id="sotrtypeobj-sort"><b>|</b><span id="actsort2" class="altlink">sort:</span> <select id="select-filter-sort">' + ''.join(['<option ' + ( 'selected="selected"' if (request.POST.has_key('order') and request.POST['order'] == (namep[0] if (isinstance(namep, tuple)) else namep) or (request.POST.has_key('searchcolumn') == False and sortnamep == (namep[0] if (isinstance(namep, tuple)) else namep))) else '') + ' value="' + (namep[0] if (isinstance(namep, tuple)) else namep) + '">' + ordersnamep[ordersname.index(namep)] + '</option>' for namep in ordersname]) + '</select></div>'
            selectin2 = '<div id="sotrtypeobj-sort2">sort2: <select id="select-filter-sort2"><option value="">--</option>' + ''.join(['<option ' + ( 'selected="selected"' if (request.POST.has_key('order2') and request.POST['order2'] == (namep[0] if (isinstance(namep, tuple)) else namep)) else '') + ' value="' + (namep[0] if (isinstance(namep, tuple)) else namep) + '">' + ordersnamep[ordersname.index(namep)] + '</option>' for namep in ordersname]) + '</select></div>'
            excludebl = ''
            if(request.POST.has_key('objects') and request.POST['objects'] != ''):
                excludebl = '<div id="selectobj-sel"><span id="buttonviewobj-sel" class="altlink">selected</span><div id="selobjectsblock-sel">' + request.POST['objects'] + '</div></div>'
            optiontop = '<div class="topoption"><form id="psevdfopt" name="psevdfopt">' + excludebl + selectin2 + selectin + searchstropt + '</form><div class="clear-bothblock">&nbsp;</div></div>'
            
            if(ismenu == False and MYCONF.COUNTPAGEELEMENTS < startlenobjects):
                urlpage = '/' + dicturls['myadm'] + '/' + dicturls['class'] +  (('/' + '/'.join(dicturls['paramslist'][0:indexpx]) + '/') if (indexpx > 0) else '/') + 'page/'
                
                pagination = utils.pagination(indexpage,countlinks,startlenobjects,MYCONF.COUNTPAGEELEMENTSLEFT,urlpage)
        
        htmltr = '<table>' + optiontop + htmltr + '</table>' + pagination
        data['table'] = htmltr
        return data
    def change_form(self, object, request, idobjurl):
        
        if(object is uClasses or object is objProperties):
            if(object is uClasses):
                objformclass = FormUClasses
            elif(object is objProperties):
                objformclass = FormobjProperties
                
            fields_form = MYCONF.FORMS_ELEMENT_EDIT[idobjurl['class']]
            dictparamsform = {}
            if(idobjurl['paramslist'][0] != '0'):
                objmodel = object.objects.get(id=idobjurl['paramslist'][0])
                for name_attr in fields_form:
                        dictparamsform[name_attr] = objmodel.__getattribute__(name_attr)
                objform = objformclass(dictparamsform)
            else:
                objmodel = object()
                objform = objformclass()
            
            if(request.POST.has_key('onsubmit') and request.POST['onsubmit'] != ''):
                issystemobj = False
                exclist = INSTALLCONF.listadminclassview if (object is uClasses) else INSTALLCONF.listadminpropsview
                if(objmodel.codename in exclist):
                    issystemobj = True
                dictparamsform = {}
                for name_attr in fields_form:
                    dictparamsform[name_attr] = request.POST.get(name_attr,False)
                if(issystemobj == True): objform = ''
                else: objform = objformclass(dictparamsform)
                if(objform != '' and objform.is_valid()):
                    for name_attr in fields_form:
                        objmodel.__setattr__(name_attr,request.POST.get(name_attr,False))
                    try:
                        objmodel.save()
                    except Exception as e:
                        objform.__setattr__('excepterr', str(e))
                    else:
                         objform = ''
            
        elif(idobjurl['class'] == 'uobjects'):
            objectclass = None
            if(idobjurl['paramslist'][0] == 'model'):
                elemseditlist = MYCONF.STRUCT_MODELS[idobjurl['paramslist'][1]]['editcolumns']
                ObjFormSet = modelformset_factory(object, fields=tuple(elemseditlist))
                formset = ObjFormSet(queryset=object.objects.none())
                
                if(MYCONF.STRUCT_MODELS[idobjurl['paramslist'][1]].has_key('links')):
                    ObjFormSetTestf = modelformset_factory(object, fields=tuple([nameparam[0] for nameparam in MYCONF.STRUCT_MODELS[idobjurl['paramslist'][1]]['links']]))
                    formsetsearchf = ObjFormSetTestf(queryset=object.objects.none())
                
                listelemimage = []
                
                objectcurrent = object()
                dictparamsinit = {}
                #links standatr model
                many_and_foreign_dict = {}
                jsparamht = {}
                if(idobjurl['paramslist'][3] != '0'):
                    objectedit = object.objects.get(id=idobjurl['paramslist'][3])
                if(MYCONF.STRUCT_MODELS[idobjurl['paramslist'][1]].has_key('links')):
                    for nameparammodel in MYCONF.STRUCT_MODELS[idobjurl['paramslist'][1]]['links']:
                        valuelink = utils.getlinks(objectedit,nameparammodel[0]) if idobjurl['paramslist'][3] != '0' else ''
                        if(idobjurl['paramslist'][1].find('__') != -1):
                            nameelemmodellink = dict(MYCONF.STRUCT_MODELS[idobjurl['paramslist'][1]]['links'])[nameparammodel[0]]
                        else:
                            nameelemmodellink = idobjurl['paramslist'][1]
                        jsparamht[nameparammodel[0]] = nameelemmodellink + '___' + nameparammodel[0]
                        many_and_foreign_dict[nameparammodel[0]] = valuelink
                        if(request.POST.has_key(nameparammodel[0] + '__prev_')):
                            many_and_foreign_dict[nameparammodel[0] + '__prev_'] = request.POST[nameparammodel[0] + '__prev_']
                        else:
                            many_and_foreign_dict[nameparammodel[0] + '__prev_'] = valuelink
                            
                if(len(many_and_foreign_dict) > 0):
                    dictparamsinit = dict(dictparamsinit.items() + many_and_foreign_dict.items())
                if(idobjurl['paramslist'][3] != '0'):
                    objectcurrent = object.objects.get(id=idobjurl['paramslist'][3])
                for elemedit in elemseditlist:
                    dictparamsinit[elemedit] = objectcurrent.__getattribute__(elemedit)
                nameclassobj = objectcurrent.__class__.__name__
                #if files
                if(nameclassobj == MYCONF.NAMEUPLOADMODEL.split('__')[1] and idobjurl['paramslist'][3] != '0'):
                    dictparamsinit['patch_name_file'] = objectcurrent.dfile.name
                
                addinitial = {}
                if(request.POST.has_key('params')):
                    addinitial[request.POST['params']] = {'objects': request.POST['objects'], 'idobj': request.POST['idobj'], 'objectsno': request.POST['objectsno'], 'exclude':  request.POST['exclude'], 'nameparam':  request.POST['idobjparentobj']}
                if(len(addinitial) > 0):
                    nameparam = request.POST['params']
                    if(isinstance(addinitial[nameparam],dict)):
                        strnamemodul = nameparam.split('__')[0]
                        strnamemodel = nameparam.split('__')[1]
                        mymodel = importlib.import_module(strnamemodul).__getattribute__(strnamemodel)
                        #links
                        ismtm = False
                        try:
                            #mtm
                            if(hasattr(objectcurrent.__getattribute__(addinitial[nameparam]['nameparam']),'model')):
                                ismtm = True
                            #link mtm None
                        except ValueError:
                            ismtm = True
                        #link fj
                        except DoesNotExist:
                            ismtm = False
                        if(ismtm == True and addinitial[nameparam]['objects']!= ''):
                            myobjscheck = addinitial[nameparam]['objects'].split(',')
                            myobjschecknon = []
                            if(addinitial[nameparam]['objectsno'] != ''):
                                myobjschecknon = addinitial[nameparam]['objectsno'].split(',')
                            if(addinitial[nameparam]['exclude'] == '1'):
                                objectdeleting = mymodel.objects.exclude(id__in = myobjschecknon)
                            else:
                                objectdeleting = mymodel.objects.filter(id__in = myobjscheck)
                            
                            dictparamsinit[addinitial[nameparam]['nameparam']] = ",".join([str(dictp['id']) for dictp in objectdeleting.values('id')])
                        else:
                            dictparamsinit[addinitial[nameparam]['nameparam']] = addinitial[nameparam]['idobj']
                        del mymodel, ismtm
                    #no link
                    else:
                        dictparamsinit[nameparam] = addinitial[nameparam]
                objform = formset.form(initial=dictparamsinit)
                prevsaved = {}
                def fieldsformpr(objform, mtm_a_fk_dict):
                    if(len(jsparamht) > 0):
                        objform.__setattr__('mtomfk',jsparamht)
                    for elemparammodel in many_and_foreign_dict:
                        if(elemparammodel.find('__prev_') == -1):
                            if(request.POST.has_key(elemparammodel) and request.POST[elemparammodel] != ''):
                                prevsaved[elemparammodel] = request.POST[elemparammodel]
                            objform.fields[elemparammodel] = forms.CharField(required = (formsetsearchf.forms[0].fields[elemparammodel].required))
                        else:
                            objform.fields[elemparammodel] = forms.CharField(widget=forms.HiddenInput,required = False)
                if(len(many_and_foreign_dict) > 0):
                    fieldsformpr(objform,many_and_foreign_dict)
                if(dictparamsinit.has_key('patch_name_file') == True):
                    objform.fields['patch_name_file'] = forms.CharField()
                for namecfield in objform.fields:
                    if(objform.fields[namecfield].__class__.__name__ == 'FileField'):
                        listelemimage.append(namecfield)
                        objform.fields[namecfield] = forms.FileField(required = False)
                if(request.POST.has_key('onsubmit') and request.POST['onsubmit'] != ''):
                    objform = formset.form(request.POST)
                    for namecfield in objform.fields:
                        if(objform.fields[namecfield].__class__.__name__ == 'FileField' and ((hasattr(request,'FILES') and len(request.FILES) > 0) or idobjurl['paramslist'][3]!='0')):
                            listelemimage.append(namecfield)
                            objform.fields[namecfield] = forms.FileField(required = False)
                    fieldsformpr(objform,many_and_foreign_dict)
                    if(objform.is_valid()):
                        for nameelemmodel in elemseditlist:
                            if(nameelemmodel not in listelemimage):
                                objectcurrent.__setattr__(nameelemmodel, request.POST[nameelemmodel])
                            elif(request.FILES.has_key(nameelemmodel)):
                                objectcurrent.__setattr__(nameelemmodel,request.FILES[nameelemmodel])
                        if(request.POST.has_key('patch_name_file') and request.POST['patch_name_file']!='' and hasattr(objectcurrent,'dfile') and objectcurrent.dfile.name!=request.POST['patch_name_file']):
                            utils.renamefile(objectcurrent.dfile,setname=request.POST['patch_name_file'])
                        elif(hasattr(objectcurrent,'dfile')):
                            utils.renamefile(objectcurrent.dfile,isrand=True)
                        dictidsaveskey = {}
                        if(dict(MYCONF.STRUCT_MODELS[idobjurl['paramslist'][1]]).has_key('links') == True):
                            listmtmfork = dict(MYCONF.STRUCT_MODELS[idobjurl['paramslist'][1]]['links'])
                            for modelparamstr in prevsaved:
                                if(many_and_foreign_dict.has_key(modelparamstr + '__prev_')):
                                    typeokcomp = False
                                    if(prevsaved[modelparamstr].find(',') != -1):
                                        typeokcomp = utils.comparelist(prevsaved[modelparamstr].split(','), many_and_foreign_dict[modelparamstr + '__prev_'].split(','))
                                    else:
                                        typeokcomp = bool(prevsaved[modelparamstr] == many_and_foreign_dict[modelparamstr + '__prev_'])
                                    if(typeokcomp): continue
                                strnamemodul = dict(listmtmfork)[modelparamstr].split('__')[0]
                                strnamemodel = dict(listmtmfork)[modelparamstr].split('__')[1]
                                objids = request.POST[modelparamstr]
                                if(objectcurrent.id == None and utils.ismtmfield(objectcurrent,modelparamstr) == True):
                                    dictidsaveskey[modelparamstr] = importlib.import_module(strnamemodul).__getattribute__(strnamemodel).objects.filter(id__in=objids.split(','))
                                    continue
                                if(hasattr(objectcurrent,modelparamstr) and hasattr(objectcurrent.__getattribute__(modelparamstr),'model')):
                                    objectcurrent.__setattr__(modelparamstr,importlib.import_module(strnamemodul).__getattribute__(strnamemodel).objects.filter(id__in=objids.split(',')))
                                else:
                                    objectcurrent.__setattr__(modelparamstr,importlib.import_module(strnamemodul).__getattribute__(strnamemodel).objects.get(id=objids))
                            if(len(dictidsaveskey) > 0):
                                objectcurrent.save()
                                for nameparammtm in dictidsaveskey:
                                    objectcurrent.__setattr__(nameparammtm,dictidsaveskey[nameparammtm])
                        objectcurrent.save()
                        
                        objform = ''
            elif(idobjurl['paramslist'][4] != 'design'):
                if(idobjurl['paramslist'][3] != '0'):
                    objmodel = object.objects.get(id=idobjurl['paramslist'][3])
                else:
                    objmodel = object()
                valuesparamsn = ()
                if(request.POST.has_key('idobjparentobj') and request.POST['idobjparentobj'] != ''):
                    valuesparamsn = (request.POST['nameprop'], request.POST['objects'])
                objform = objmodel.getform(idClass=idobjurl['paramslist'][1], addvalue = valuesparamsn)
                if(request.POST.has_key('onsubmit') and request.POST['onsubmit'] != '' and request.POST.has_key('params') == False):
                    objform = objmodel.getform(request.POST,idClass=idobjurl['paramslist'][1],save=True)
                    
                    if(objform.is_valid()): objform = ''
                elif(request.POST.has_key('params') and request.POST['params'] != ''):
                    addinit = {}
                    addinit[request.POST['params']] = {'objects': request.POST['objects'], 'idobj': request.POST['idobj'], 'objectsno': request.POST['objectsno'], 'exclude':  request.POST['exclude'], 'model': request.POST['model']}
                    objform = objmodel.getform(idClass=idobjurl['paramslist'][1],addinitial=addinit)
                if(objform != ''):
                    objform.__setattr__('typesprops',objmodel.typesprops())
            else: objectclass = uClasses.objects.get(id=idobjurl['paramslist'][1])
            if(objectclass != None and objectclass.codename == MYCONF.CLASS_NAME_MENU and idobjurl['paramslist'][4] == 'design'):
                pref_nview = '_view'
                pref_ntemplate = '_template'
                from django.template import Context, loader, VariableNode
                dictparamsform = {}
                cheseelnone = (0,'---')
                objformclass = designUI
                objectnav = objectclass.getobjects(id=idobjurl['paramslist'][3])[0]
                allObjectsTemplates = dict([(str(obj.id), obj) for obj in uClasses.objects.get(name='template_system').getobjects(namesvprop=[MYCONF.PROP_PATCH_TEMPLATE_SYS])])
                allObjectsViews = dict([(str(obj.id), obj) for obj in uClasses.objects.get(name='views_system').getobjects()])
                
                linkstemplatesnav = objectnav.links('template_system',False,namesvprop=[MYCONF.PROP_PATCH_TEMPLATE_SYS])
                linksHandlesSysDict = dict([(objhandle.name, objhandle) for objhandle in objectnav.links('handle_system')])
                
                classHandle = uClasses.objects.get(codename='handle_system')
                
                iddesigntemplate = 0
                if(linkstemplatesnav != False):
                    iddesigntemplate = str(linkstemplatesnav.id)
                
                dictparamsform['templates'] = iddesigntemplate
                for handl in linksHandlesSysDict:
                    objview = linksHandlesSysDict[handl].links('views_system',False)
                    objtemp = linksHandlesSysDict[handl].links('template_system',False)
                    if(objview is not False):
                        dictparamsform[handl + pref_nview] = str(objview.id)
                    if(objtemp is not False):
                        dictparamsform[handl + pref_ntemplate] = str(objtemp.id)
                
                objform = objformclass(dictparamsform)
                
                dicttemplatesall = [cheseelnone] + [(numhash, allObjectsTemplates[numhash].name + ':' + allObjectsTemplates[numhash].propertiesdict[MYCONF.PROP_PATCH_TEMPLATE_SYS]) for numhash in allObjectsTemplates]
                objform.fields['templates'] = forms.ChoiceField(dicttemplatesall, required=False)
                
                dictviewsall = [cheseelnone] + [(numhash, allObjectsViews[numhash].name) for numhash in allObjectsViews]
                
                if(iddesigntemplate != 0):
                    tempt = loader.get_template(linkstemplatesnav.propertiesdict[MYCONF.PROP_PATCH_TEMPLATE_SYS])
                    
                    #if there are handles
                    names_token = []
                    for variable in tempt.nodelist.get_nodes_by_type(VariableNode):
                        token = variable.filter_expression.token
                        indh = token.find('|handle:')
                        if(indh != -1):
                            names_token.append(token[1:indh-1])
                    
                    for handle_name in names_token:
                        objform.fields[handle_name + pref_nview] = forms.ChoiceField(dictviewsall, required=False)
                        objform.fields[handle_name + pref_ntemplate] = forms.ChoiceField(dicttemplatesall, required=False)
                    
                
                if(request.POST.has_key('onsubmit') and (objform.is_valid() and request.POST['onsubmit'] != '')):
                    if(iddesigntemplate != request.POST['onsubmit']):
                        #If the new pattern
                        if(iddesigntemplate != 0):
                            objectnav.linksedit('remove',allObjectsTemplates[iddesigntemplate])
                        if(request.POST['templates'] != '0'):
                            objectnav.linksedit('add',allObjectsTemplates[request.POST['templates']])
                            objectnav.save()
                    
                    if(iddesigntemplate):
                        newHandlesList = []
                        for namekeyform in request.POST:
                            if(namekeyform.find(pref_nview) != -1):
                                namehandle = namekeyform[0:namekeyform.find(pref_nview)]
                                #if there is no my handle
                                if(linksHandlesSysDict.has_key(namehandle) == False):
                                    objHandle = classHandle.initobj(name=namehandle)
                                    objHandle.save()
                                    linksHandlesSysDict[namehandle] = objHandle
                                    newHandlesList.append(objHandle)
                                if(request.POST[namekeyform] == '0'):
                                    linksHandlesSysDict[namehandle].linksedit('clear', ClassName='views_system')
                                else:
                                    linksHandlesSysDict[namehandle].linksedit('add', allObjectsViews[request.POST[namekeyform]],ManyToOny = True)
                                linksHandlesSysDict[namehandle].save()
                            elif(namekeyform.find(pref_ntemplate) != -1):
                                namehandle = namekeyform[0:namekeyform.find(pref_ntemplate)]
                                #if there is no my handle
                                if(linksHandlesSysDict.has_key(namehandle) == False):
                                    objHandle = classHandle.initobj(name=namehandle)
                                    objHandle.save()
                                    linksHandlesSysDict[namehandle] = objHandle
                                    newHandlesList.append(objHandle)
                                if(request.POST[namekeyform] == '0'):
                                    linksHandlesSysDict[namehandle].linksedit('clear', ClassName='template_system')
                                else:
                                    linksHandlesSysDict[namehandle].linksedit('add', allObjectsTemplates[request.POST[namekeyform]],ManyToOny = True)
                                linksHandlesSysDict[namehandle].save()
                            
                        if(len(newHandlesList) > 0):
                            objectnav.linksedit('add', newHandlesList)
                            objectnav.save()
                    objform = ''
        
        return objform 

def controller(request, object, dicturls):
    action_request = actionsetparam(request.POST)
    #is_validate
    dictparams = action_request.data
    paramp = ''
    if(dictparams['nameurl'] == 'urladd'):
        addparam = ''
        if(dicturls['class'] == 'uobjects'):
            if(dictparams['model'] == ''):
                objectclass = uClasses.objects.get(id=dictparams['idclass'])
                if(objectclass.codename == MYCONF.CLASS_NAME_MENU):
                    addparam = dictparams['idobj']
                paramp = dicturls['class'] + '/' + 'class/' + str(dictparams['idclass']) + '/obj/0/' + str(addparam)
            else:
                paramp = dicturls['class'] + '/model/' + dictparams['model'] + '/obj/0/'
        else:
            paramp = dicturls['class'] + '/' + '0'
    elif(dictparams['nameurl'] == 'urledit'):
        if(dictparams['model'] != ''):
            paramp = dicturls['class'] + '/model/' + dictparams['model'] + '/obj/' + str(dictparams['idobj'])
        elif(dicturls['class'] == 'uobjects'):
            paramp = dicturls['class'] + '/class/' + str(dictparams['idclass']) + '/obj/' + str(dictparams['idobj'])
        else:
            paramp = dicturls['class'] + '/' + str(dictparams['idobj'])
    elif(dictparams['nameurl'] == 'urlremove' and dictparams['objects'] != ''):
        if(dicturls['class']=='uclasses' or dicturls['class']=='objproperties'):
            exclist = INSTALLCONF.listadminclassview if (dicturls['class']=='uclasses') else INSTALLCONF.listadminpropsview
            object = object.objects.exclude(codename__in=exclist)
        
        myobjscheck = dictparams['objects'].split(',')
        myobjschecknon = []
        if(dictparams['objectsno'] != ''):
            myobjschecknon = dictparams['objectsno'].split(',')
        if(dictparams['exclude'] == '1'):
            if(dicturls['class']!='uobjects'):
                objectdeleting = object.exclude(id__in = myobjschecknon)
            else:
                objectdeleting = object.objects.exclude(id__in = myobjschecknon)
        else:
            if(dicturls['class']!='uobjects'):
                objectdeleting = object.filter(id__in = myobjscheck)
            else:
                objectdeleting = object.objects.filter(id__in = myobjscheck)
        
        for obj in objectdeleting: obj.delete()
        paramp = dicturls['class']
        if(dictparams['params'] == 'isobjtrue'):
            paramp = 'uobjects/class/' + str(dictparams['idclass'])
        elif(dictparams.has_key('model') and dictparams['model']!=''):
            paramp = 'uobjects/model/' + dictparams['model']
    
    elif(dictparams['nameurl'] == 'urlpropclass'):
        return HttpResponseRedirect('/' + dicturls['myadm'] + '/objproperties/linksobj/classes/' + str(dictparams['idobj']))
    elif(dictparams['nameurl'] == 'urlaggregation'):
        return HttpResponseRedirect('/' + dicturls['myadm'] + '/uclasses/linksobj/classes/' + str(dictparams['idobj']))
    elif(dictparams['nameurl'] == 'urlclassobjects'):
        return HttpResponseRedirect('/' + dicturls['myadm'] + '/uobjects/class/' + str(dictparams['idobj']))
    elif(dictparams['nameurl'] == 'urladdobjectsfromclass'):
        return HttpResponseRedirect('/' + dicturls['myadm'] + '/uobjects/class/' + str(dictparams['idobj']) + '/obj/0')
    elif(dictparams['nameurl'] == 'urllinksobj'):
        return HttpResponseRedirect('/' + dicturls['myadm'] + '/uclasses/link/' + str(dictparams['idobj']) + '/class/' + str(dictparams['idclass']))
    elif(dictparams['nameurl'] == 'allclassfiltered'):
        return HttpResponseRedirect('/' + dicturls['myadm'] + '/uobjects/linkall/' + str(dictparams['idobj']) + '/class/' + str(dictparams['idclass']) + '/classes/' + str(dictparams['objects']))
    elif(dictparams['nameurl'] == 'urladdlinkobject'):
        if(dictparams['params'] == 'ismodellinklink'):
            linkobj = object.objects.get(id=dictparams['idobj'])
            listmylinks = [(str(objlink.id), objlink) for objlink in linkobj.__getattribute__(dictparams['nameprop']).all() if str(objlink.id) not in dictparams['objectsno'].split(',')]
            mylinks = [objlink[0] for objlink in listmylinks]
            mylinkscheck = []
            if(dictparams['objects'] != ''):
                mylinkscheck.extend(dictparams['objects'].split(','))
            if(dictparams['exclude'] == '1'):
                objlinks = linkobj.__getattribute__(dictparams['nameprop']).exclude(id__in = mylinkscheck)
            else:
                objlinks = linkobj.__getattribute__(dictparams['nameprop']).filter(id__in = mylinks + mylinkscheck)
            linkobj.save()
            paramp = dicturls['class'] + '/model/' + dictparams['model'] + '/obj/' + str(dictparams['idobj'])
        else:
            linksObjectsAll = getclasslinksall(dictparams['idclass'])
            linkobj = linksObjectsAll.objects.get(idobj=dictparams['idobj'], uclass=dictparams['idclass'])
            listmylinks = [(str(objlink.id), objlink) for objlink in linkobj.links.all() if str(objlink.id) not in dictparams['objectsno'].split(',')]
            mylinks = [objlink[0] for objlink in listmylinks]
            mylinkscheck = []
            if(dictparams['objects'] != ''):
                mylinkscheck.extend(dictparams['objects'].split(','))
            if(dictparams['exclude'] == '1'):
                linkobj.links = linksObjectsAll.objects.exclude(id__in = mylinkscheck)
            else:
                linkobj.links = linksObjectsAll.objects.filter(id__in = mylinks + mylinkscheck)
            linkobj.save()
            
            objectclass = uClasses.objects.get(id=dictparams['idclass'])
            if(objectclass.codename == MYCONF.CLASS_NAME_GROUP):
                paramp = 'uobjects/class/' + str(dictparams['idclass'])
            else:
                paramp = 'uclasses/link/' + str(dictparams['idobj']) + '/class/' + str(dictparams['idclass'])
    elif(dictparams['nameurl'] == 'urladdlinkclass'):
        objmodel = uClasses.objects.get(id=dictparams['idobj'])
        checklist = dictparams['objects'].split(',') if dictparams['objects'] != '' else []
        mylinkscheck = []
        if(dictparams['objects'] != ''):
            mylinkscheck.extend(dictparams['objects'].split(','))
        if(object is objProperties):
            mylinks = [str(dict['id']) for dict in objmodel.properties.values('id') if (str(dict['id']) not in dictparams['objectsno'].split(','))]
            if(dictparams['exclude'] == '1'):
                objlinks = objProperties.objects.exclude(id__in = mylinkscheck)
            else:
                objlinks = objProperties.objects.filter(id__in = mylinks + mylinkscheck)
            objmodel.properties = objlinks
        elif(object is uClasses):
            mylinks = [str(dict['id']) for dict in objmodel.aggregation.values('id') if (str(dict['id']) not in dictparams['objectsno'].split(','))]
            
            if(dictparams['exclude'] == '1'):
                objlinks = uClasses.objects.exclude(id__in = mylinkscheck)
            else:
                objlinks = uClasses.objects.filter(id__in = mylinks + mylinkscheck)
            objmodel.aggregation = objlinks
        
        objmodel.save()
        
        return HttpResponseRedirect('/' + dicturls['myadm'] + '/uclasses/')
    elif(dictparams['nameurl'] == 'csvexp' and request.FILES.get('datafile',False) != False):
        redstr = ''
        if(dicturls['class'] == 'uobjects'):
            redstr = '/class/' + str(dictparams['idclass'])
        
        errors = expcsv(request.FILES['datafile'],dicturls['class'],dictparams['idclass'])
        if(len(errors) == 0):
            return HttpResponseRedirect('/' + dicturls['myadm'] + '/' + dicturls['class'] + redstr)
        else:
            htmlerr = ''.join([ '<div>' + dicterr['line'] + '<p>' + dicterr['err'] + '</p>' + '</div><br/>' for dicterr in errors])
            return render_to_response('myadmin/change_list.html', {'myhtml': htmlerr,}, RequestContext(request, processors=[vi_proc_list]))
    elif(dictparams['nameurl'] == 'csvimp' and dictparams['objects'] != ''):
        from time import gmtime, strftime
        import csv
        listidobjcts = dictparams['objects'].split(',')
        pname = ''
        if(dicturls['class'] == 'uclasses'):
            colscsv = ['name', 'codename', 'description', 'tablespace', 'properties', 'aggregation']
            objects_export = uClasses.objects.filter(id__in = listidobjcts)
        elif(dicturls['class'] == 'objproperties'):
            colscsv = ['name', 'codename', 'description', 'myfield', 'minfield', 'maxfield', 'required', 'udefault']
            objects_export = objProperties.objects.filter(id__in = listidobjcts)
        elif(dicturls['class'] == 'uobjects'):
            classobj = uClasses.objects.get(id=dictparams['idclass'])
            pname = '_'+classobj.codename
            colscsv = [objprop.codename for objprop in classobj.properties.all()]
            colscsv.append('headerp__name')
            colscsv.extend(['headerp__' + paramheader for paramheader in MYCONF.UPARAMS_MYSPACES[classobj.get_tablespace_display()]['editcolumns']])
            objects_export = classobj.getobjects(id__in = listidobjcts)
        
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + (dicturls['class'] + pname).lower() + '_' + strftime("%d%m%y_%H%M", gmtime()) + '.csv'
        writer = csv.writer(response)
        
        writer.writerow(colscsv)
        for object in objects_export:
            colcsv = []
            for nameparamobj in colscsv:
                if(dicturls['class'] == 'uobjects' and nameparamobj.find('headerp__') == -1):
                    valueobj = object.propertiesdict[nameparamobj]
                else:
                    valueobj = object.__getattribute__(nameparamobj.replace('headerp__',''))
                
                if(valueobj.__class__.__name__ == 'ManyRelatedManager'):
                    colcsv.append( (','.join( [ str(objm['codename']) for objm in valueobj.all().values('codename') ] )) )
                elif(valueobj.__class__.__name__ != 'unicode'):
                    colcsv.append(str(valueobj))
                else:
                    colcsv.append(valueobj.encode( "utf-8" ))
            writer.writerow(colcsv)
        
        return response
    #UI
    elif(dictparams['nameurl'] == 'install'):
        errors = []
        dictprop = {'names':INSTALLCONF.PROPN,'values':INSTALLCONF.PROPL}
        errors += expcsv(dictprop, 'objproperties')
        dictclass = {'names':INSTALLCONF.ClASSN,'values':INSTALLCONF.CLASSL}
        errors += expcsv(dictclass, 'uclasses')
        if(settings.DEBUG == True):
            if(len(errors) == 0):
                html = '<p>install ok</p>'
            else:
                html = ''.join([ '<div>' + dicterr['line'] + '<p>' + dicterr['err'] + '</p>' + '</div><br/>' for dicterr in errors])
            return render_to_response('myadmin/static.html', {'myhtml': html, 'head': 'install'}, RequestContext(request, processors=[vi_proc_list]))
        else:
            return HttpResponseRedirect('/' + dicturls['myadm'] + '/uclasses/')
    elif(dictparams['nameurl'] == 'urlmovemenuobj' and dictparams['objects'] != ''):
        objctsmenu = uClasses.objects.get(id=dictparams['idclass'])
        listidobjcts = dictparams['objects'].split(',')
        #on itself can not be
        if(str(dictparams['idobj']) not in listidobjcts):
            for obj in objctsmenu.getobjects(id__in = listidobjcts):
                obj.propertiesdict['parent_elnav_system'] = dictparams['idobj']
                obj.save()
        paramp = 'uobjects/class/' + str(dictparams['idclass'])
    elif(dictparams['nameurl'] == 'urldesignnav'):
        paramp = dicturls['class'] + '/class/' + str(dictparams['idclass']) + '/obj/' + str(dictparams['idobj']) + '/design'
        
    elif(dictparams['nameurl'] == 'urlpermissionobj'):
        classview = uClasses.objects.get(codename=MYCONF.CLASS_NAME_GROUP)
        paramp = dicturls['class'] + '/linkall/' + str(dictparams['idobj']) + '/class/' + str(dictparams['idclass']) + '/classes/' + str(classview.id) + '/permission'
    elif(dictparams['nameurl'] == 'urlparamsnav'):
        classview = uClasses.objects.get(codename=MYCONF.CLASS_PARAMSNAV_SYS)
        paramp = dicturls['class'] + '/linkall/' + str(dictparams['idobj']) + '/class/' + str(dictparams['idclass']) + '/classes/' + str(classview.id) + '/params'
    
    return HttpResponseRedirect('/' + dicturls['myadm'] + '/' + str(paramp))

render = optionswitch()

@staff_member_required
def get_url(request, *args, **kwargs):
    paramslisturl = [pr for pr in request.path_info.split('/') if pr != '']
    dicturls = {
        'myadm': paramslisturl[0] + '/' +paramslisturl[1],
        'class': paramslisturl[2],
        'paramslist': paramslisturl[3:] + ['','','','','']
    }
    template_render = ''
    params_render = {}
    proplistALL = MYCONF.TYPES_DEF_CLASSES[kwargs['type']]
    StrHeader = dicturls['class']
    def _gethclass(idclass):
        objectclass = dict([(str(objcl.id), objcl) for objcl in uClasses.objects.all()])
        return '&nbsp;>&nbsp; class: <a href="' + '/' + dicturls['myadm'] + '/' + dicturls['class'] + '/class/' + str(objcl.id) + '/' + '">' + objectclass[idclass].name + '</a>'
    
    objreqcont = RequestContext(request, processors=[vi_proc_list])
    
    addition_men = []
    addition_men.extend(MYCONF.TYPES_DEF_CLASSES[kwargs['type']]['userui'])
    islinks = True if (dicturls['paramslist'][0] == 'linksobj' or dicturls['paramslist'][0] == 'linkall' or dicturls['paramslist'][0] == 'link') else False
    #switch model class
    if(kwargs['type'] == 'uclasses'):
        objwork = uClasses
        if(dicturls['paramslist'][1] == 'classes' and dicturls['paramslist'][2] != ''):
            StrHeader += _gethclass(dicturls['paramslist'][2])
            addition_men.append(('add aggregation', 'urladdlinkclass','classaddlinkm'))
            
        #for links objects
        if(dicturls['paramslist'][0] == 'link' and dicturls['paramslist'][2] == 'class'):
            StrHeader += _gethclass(dicturls['paramslist'][3])
            objwork = uClasses.objects.get(id=dicturls['paramslist'][3]).aggregation.all()
            addition_men.append(('filter link object id - ' + dicturls['paramslist'][1], 'allclassfiltered','filtclassobj'))
    elif(kwargs['type'] == 'objproperties'):
        objwork = objProperties
        if(dicturls['paramslist'][1] == 'classes' and dicturls['paramslist'][2] != ''):
            StrHeader += _gethclass(dicturls['paramslist'][2])
            addition_men.append(('add prop', 'urladdlinkclass','classaddlinkm'))
        
    elif(kwargs['type'] == 'uobjects'):
        if(dicturls['paramslist'][1].isdigit()):
            StrHeader += _gethclass(dicturls['paramslist'][3] if (dicturls['paramslist'][0]=='linkall') else dicturls['paramslist'][1])
        if(dicturls['paramslist'][0]==''):
            return HttpResponseRedirect('/' + dicturls['myadm'] + '/uclasses/')
        elif(dicturls['paramslist'][0]=='linkall' and dicturls['paramslist'][5] != ''):
            linksObjectsAll = getclasslinksall(dicturls['paramslist'][3])
            objwork = linksObjectsAll.objects.filter(uclass__id__in=dicturls['paramslist'][5].split(','))
            addition_men.append(('set link', 'urladdlinkobject','classaddlinkm'))
            if(dicturls['paramslist'][6]=='permission' or dicturls['paramslist'][6]=='params'):
                StrHeader += _gethclass(dicturls['paramslist'][5])
                addition_men = [('add rights', 'urladdlinkobject','classaddlinkm')]
        elif((dicturls['paramslist'][0]=='model' and dicturls['paramslist'][1] != '') or (dicturls['paramslist'][0] == 'action' and (request.POST.has_key('model') and request.POST['model'] != ''))):
        #show objects standart model
            mymodelconf = dicturls['paramslist'][1] if dicturls['paramslist'][4] != 'linksmodel' else dicturls['paramslist'][5]
            if(request.POST.has_key('model') and request.POST['model'] != ''): mymodelconf = request.POST['model']
            params_modul = mymodelconf.split('__')
            strnamemodul = params_modul[0]
            strnamemodel = params_modul[1]
            objwork = importlib.import_module(strnamemodul).__getattribute__(strnamemodel)
            if(dicturls['paramslist'][4] == 'linksmodel'):
                    if(MYCONF.STRUCT_MODELS.has_key(dicturls['paramslist'][5])):
                        testobjworknames = MYCONF.STRUCT_MODELS[dicturls['paramslist'][5]]['vlistcolumns']
                    else:
                        testobjworknames = ['id']
            else:
                testobjworknames = MYCONF.STRUCT_MODELS[mymodelconf]['vlistcolumns']
            proplistALL = {'name': testobjworknames,'namep': testobjworknames}
            addition_men = []
            if(dicturls['paramslist'][4] != 'linksmodel'):
                addition_men = [('add','urladd'), ('remove','urlremove'), ('edit','urledit')]
            if(dicturls['paramslist'][2] == 'links' or dicturls['paramslist'][4] == 'linksmodel'):
                addition_men.append(('add rights', 'urladdlinkobject','classaddlinkm'))
            islinks = True
        elif((dicturls['paramslist'][0]=='class' and dicturls['paramslist'][1] != '') or (dicturls['paramslist'][0] == 'action' and (request.POST.has_key('idclass') and request.POST['idclass'] != ''))):
            from myobj.install import CLASSL
            if(dicturls['paramslist'][1] in [listcl[0] for listcl in CLASSL]):
                try:
                    classind = str(uClasses.objects.get(codename=str(dicturls['paramslist'][1])).id)
                except :
                    if(dicturls['paramslist'][1] in [listcl[0] for listcl in CLASSL]):
                        return HttpResponseRedirect('/' + dicturls['myadm'] + '/uclasses/install')
                else:
                    return HttpResponseRedirect('/' + dicturls['myadm'] + '/' + dicturls['class'] + '/class/' + classind + '/')
            
            spaceheaders = get_space_model(request.POST['idclass'] if (request.POST.has_key('idclass') and request.POST['idclass'] != '') else dicturls['paramslist'][1], getlines=False)
            
            if(dicturls['paramslist'][0]=='class' and dicturls['paramslist'][1] != '' and dicturls['paramslist'][2] != 'obj'):
                if(dicturls['paramslist'][1].isdigit()):
                    
                    objectclass = uClasses.objects.get(id=str(dicturls['paramslist'][1]))
                    if(objectclass.codename == MYCONF.CLASS_NAME_MENU):
                        addition_men.append(('move', 'urlmovemenuobj', 'classaddlinkm'))
                        addition_men.append(('design', 'urldesignnav','classaddlinkm'))
                        addition_men.append(('params', 'urlparamsnav','classaddlinkm'))
                    elif(objectclass.codename == MYCONF.CLASS_NAME_VIEWS):
                        addition_men.append(('permission', 'urlpermissionobj', 'classaddlinkm'))
                    
                    objwork = spaceheaders.objects.filter(uclass=dicturls['paramslist'][1])
                else:
                    objwork = spaceheaders.objects.filter(uclass__codename=str(dicturls['paramslist'][1]))
            else:
                if(dicturls['paramslist'][4] == 'linksmodel'):
                    
                    if(dicturls['paramslist'][5] != MYCONF.NAMEUPLOADMODEL):
                        dictlistlink = {}
                        for elemlink in MYCONF.UPARAMS_MYSPACES[dicturls['paramslist'][5]]['editcolumns']:
                            if(isinstance(elemlink, tuple)):
                                dictlistlink[elemlink[0]] = elemlink[1]
                        strnamemodul = dictlistlink[dicturls['paramslist'][6]].split('__')[0]
                        strnamemodel = dictlistlink[dicturls['paramslist'][6]].split('__')[1]
                    #if files
                    else:
                        strnamemodul = MYCONF.NAMEUPLOADMODEL.split('__')[0]
                        strnamemodel = MYCONF.NAMEUPLOADMODEL.split('__')[1]
                    objwork = importlib.import_module(strnamemodul).__getattribute__(strnamemodel)
                    testobjworknames = (objwork().__dict__.keys())
                    proplistALL = {'name': testobjworknames,'namep': testobjworknames}
                    addition_men = [('add rights', 'urladdobjectform','classaddlinkm')]
                    islinks = True
                else:
                    objwork = spaceheaders
    #and edit object
    if(dicturls['paramslist'][4] != 'linksmodel' and ((kwargs['type'] == 'uobjects' and dicturls['paramslist'][0]=='model' and dicturls['paramslist'][3].isdigit()) or dicturls['paramslist'][0].isdigit() or (kwargs['type'] == 'uobjects' and dicturls['paramslist'][0]=='class' and dicturls['paramslist'][1].isdigit() and dicturls['paramslist'][2]=='obj' and dicturls['paramslist'][3].isdigit()))):
        objreqcont = RequestContext(request, processors=[vi_proc_form])
        rhtml = render.change_form(objwork, request, dicturls)
        if(rhtml == ''):
            requrl = ''
            if(dicturls['class'] == 'uobjects'):
                if(dicturls['paramslist'][4]=='design'):
                    requrl = '/' + dicturls['myadm'] + '/' + dicturls['class'] + '/' + '/'.join([str(elurl) for elurl in dicturls['paramslist'][0:5]])
                elif(dicturls['paramslist'][0]=='model'):
                    requrl = '/' + dicturls['myadm'] + '/' + dicturls['class'] + '/model/' + dicturls['paramslist'][1]
                else:
                    requrl = '/' + dicturls['myadm'] + '/' + dicturls['class'] + '/class/' + dicturls['paramslist'][1] + ( ('/obj/' + dicturls['paramslist'][3]) if dicturls['paramslist'][3]!='0' else '' )
            else:
                requrl = '/' + dicturls['myadm'] + '/' + dicturls['class']
            
            return HttpResponseRedirect(requrl)
        
        template_render = 'myadmin/change_form.html'
        params_render = {'namecont': MYCONF.TYPES_DEF_CLASSES[kwargs['type']]['namecont'], 'header': StrHeader, 'myhtml': rhtml}
    elif(dicturls['paramslist'][0] == 'action'):
        return controller(request, objwork, dicturls)
    else:
        rhtml = render.change_list(request, objwork, proplistALL, dicturls, islinks)
        template_render = 'myadmin/change_list.html'
        params_render = {'namecont': MYCONF.TYPES_DEF_CLASSES[kwargs['type']]['namecont'], 'header': StrHeader, 'myhtml': rhtml, 'uimenu': utils.mumenrec(addition_men)}
    
    return render_to_response(template_render, params_render, objreqcont)
