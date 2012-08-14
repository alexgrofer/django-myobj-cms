from django.db import models
from myobj import conf as MYCONF
from myobj import utils
from django.forms.models import modelformset_factory
from django import forms
from django.utils import importlib
from django.contrib.auth.models import User
#propertiesObject
class objProperties(models.Model):
    name = models.CharField(max_length=255)
    codename = models.CharField(max_length=30,unique=True)
    description = models.CharField(max_length=255,blank=True)
    myfield = models.PositiveSmallIntegerField(choices=MYCONF.TYPES_MYFIELDS_CHOICES, default=1)
    minfield = models.CharField(max_length=4,blank=True)
    maxfield = models.CharField(max_length=4,blank=True)
    required = models.BooleanField(blank=True)
    udefault = models.CharField(max_length=255,blank=True)
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = MYCONF.PROJECT_NAME + '_ucms_objproperties'
        verbose_name = 'Properties'
        

#userClasses
class uClasses(models.Model):
    name = models.CharField(max_length=255)
    codename = models.CharField(max_length=30,unique=True)
    description = models.CharField(max_length=255,blank=True)
    tablespace = models.PositiveSmallIntegerField(choices=MYCONF.MYSPACE_TABLES_CHOICES, default=1)
    properties = models.ManyToManyField(objProperties,blank=True)
    aggregation = models.ManyToManyField("self",blank=True)
    objectsqueryset = []
    _getclasslinksall = None
    _getclasslines = None
    _getclassheader = None
    def getspace(self,getlines=False,getlinksall=False):
        if(getlinksall == False):
            if(getlines==True and self._getclasslines != None):
                return self._getclasslines
            elif(getlines==False and self._getclassheader != None):
                return self._getclassheader
        elif(self._getclasslinksall != None):
            return self._getclasslinksall
        
        classget = get_space_model(getlines=getlines, getlinksall=getlinksall, tablespace=self.tablespace)
        if(getlinksall == True and self._getclasslinksall == None):
            self._getclasslinksall = classget
        else:
            if(getlines == True and self._getclasslines == None):
                self._getclasslines = classget
            elif(getlines == False and self._getclassheader == None):
                self._getclassheader = classget
        return classget
    def getobjects(self, namesvprop=[], *args, **kwargs):
        modelheader = get_space_model(getlines=False, tablespace=self.tablespace)
        newkwargs = {'uclass': str(self.id)}
        newkwargs = dict(newkwargs.items() + kwargs.items())
        self.objectsqueryset = modelheader.objects.filter(**newkwargs).select_related()
        tempprop = self.properties.all()
        templinesdict = {}
        if(len(namesvprop) > 0 and self.objectsqueryset.count() > 0):
            okparamfilt = [str(propobj.id) for propobj in tempprop if propobj.codename in namesvprop]
            nameheadermodel = self.objectsqueryset[0].__class__.__name__.lower()
            dictparamf = {}
            dictparamf[nameheadermodel + '__id__in'] = [str(dictobj.id) for dictobj in self.objectsqueryset]
            dictparamf['property__id__in'] = okparamfilt
            templinesall = self.getspace(True).objects.select_related().filter(**dictparamf)
            templinesallval = dict([(str(objline['id']), str(objline[nameheadermodel + '__id'])) for objline in templinesall.values('id',nameheadermodel + '__id')])
            for objline in templinesall:
                try:
                    templinesdict[templinesallval[str(objline.id)]].append(objline)
                except:
                    templinesdict[templinesallval[str(objline.id)]] = [objline]
        for objqs in self.objectsqueryset:
            objqs.propertiesclass = tempprop
            if(len(namesvprop) > 0 and templinesdict.has_key(str(objqs.id))):
                objqs.templines = templinesdict[str(objqs.id)]
        return self.objectsqueryset
    def initobj(self,**kwargs):
            objectheaher = self.getspace()
            myobj = objectheaher(uclass=self,**kwargs)
            return myobj
    def delete(self):
        #del objects
        objects = self.getobjects()
        if(len(objects) > 0):
            for obj in self.getobjects().all(): obj.delete()
        
        self.aggregation.clear()
        super(uClasses, self).delete()
        
    def getobjprop(self,paramcurrentsclass={}, *args, **kwargs):
        if(len(self.objectsqueryset) == 0 or len(paramcurrentsclass) > 0): self.getobjects(**paramcurrentsclass)
        if(len(self.objectsqueryset) == 0): return []
        nameheadermodel = self.objectsqueryset[0].__class__.__name__.lower()
        namefieldprops = dict([(objprop.codename, objprop.myfield) for objprop in self.properties.all()])
        newkwargs = {}
        for keyw in kwargs:
            findparam = keyw.split('__',1)
            fieldlookups = '__' + findparam[1] if (len(findparam) > 1) else ''
            newkwargs[MYCONF.TYPES_COLUMNS[dict(MYCONF.TYPES_MYFIELDS)[dict(MYCONF.TYPES_MYFIELDS_CHOICES)[namefieldprops[findparam[0]]]]] + fieldlookups] = kwargs[keyw]
            
        modellines = get_space_model(getlines=True, tablespace=self.tablespace)
        lines = modellines.objects.select_related().filter(**newkwargs)
        listidclassobjects = [obj.id for obj in self.objectsqueryset]
        listobjectslinks = []
        for objline in lines:
            listobjectslinks.extend([str(object.id) for object in objline.__getattribute__(nameheadermodel + '_set').all()])
        myobjects = self.objectsqueryset.filter(id__in=set(listobjectslinks))
        return myobjects

        
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = MYCONF.PROJECT_NAME + '_ucms_uclasses'
        verbose_name = 'Classes'
        

#linesObject
class AbsBaseLines(models.Model):
    property = models.ForeignKey(objProperties)
    uptextfield = models.TextField(blank=True)
    upcharfield = models.CharField(max_length=255,blank=True)
    uptimefield = models.TimeField(blank=True,null=True)
    updatefield = models.DateField(blank=True,null=True)
    upintegerfield = models.IntegerField(blank=True,null=True)
    upfloatfield = models.FloatField(blank=True,null=True)
    class Meta:
        abstract = True

class systemObjLines(AbsBaseLines):
    class Meta:
        db_table = MYCONF.PROJECT_NAME + '_ucms_systemobjlines'
class myObjLines(AbsBaseLines):
    class Meta:
        db_table = MYCONF.PROJECT_NAME + '_ucms_myobjlines'

class AbsBaseLinksObjects(models.Model):
    idobj = models.IntegerField(blank=False)
    name = models.CharField(max_length=255)
    uclass = models.ForeignKey(uClasses)
    links = models.ManyToManyField("self",blank=True)
    class Meta:
        abstract = True

class linksObjectsSystem(AbsBaseLinksObjects):
    class Meta:
        db_table = MYCONF.PROJECT_NAME + '_ucms_linksobjectssystem'

class linksObjectsAll(AbsBaseLinksObjects):
    class Meta:
        db_table = MYCONF.PROJECT_NAME + '_ucms_linksobjectsall'

#headersObject
class AbsBaseHeaders(models.Model):
    _flagAutoAddedLinks = True
    uclass = models.ForeignKey(uClasses) #как может быть объект без класса ?)_
    __propertiesdict = {}
    __typespropsdict = {}
    #modelandtuple = (modul,model) or QuerySet
    def setlinks(self,nameparam,modelandtupleorqueryset,objids=None):
        if(isinstance(modelandtupleorqueryset,tuple)):
            if(self.id == None and utils.ismtmfield(self,nameparam) == True):
                return importlib.import_module(modelandtupleorqueryset[0]).__getattribute__(modelandtupleorqueryset[1]).objects.filter(id__in=objids.split(','))
            if(hasattr(self,nameparam) and hasattr(self.__getattribute__(nameparam),'model')):
                if(objids == ''): self.__getattribute__(nameparam).clear()
                else: self.__setattr__(nameparam,importlib.import_module(modelandtupleorqueryset[0]).__getattribute__(modelandtupleorqueryset[1]).objects.filter(id__in=objids.split(',')))
            else:
                if(objids == ''): self.__setattr__(nameparam, None)
                else: self.__setattr__(nameparam,importlib.import_module(modelandtupleorqueryset[0]).__getattribute__(modelandtupleorqueryset[1]).objects.get(id=objids))
        else:
            self.__setattr__(nameparam,modelandtupleorqueryset)
        return False
        
    def getlinks(objectedit,name,listid=True):
            return utils.getlinks(objectedit,name,listid)
        
    def getform(self,postgetp={},idClass=None,save=False,addinitial = {}, addvalue = ()):
        if(self.id == None):
            objectclass = uClasses.objects.get(id=idClass)
            self.uclass = objectclass
            namespace = objectclass.get_tablespace_display()
        else:
            namespace = self.uclass.get_tablespace_display()
        fields_form = [nameparam for nameparam in MYCONF.UPARAMS_MYSPACES[namespace]['editcolumns'] if not isinstance(nameparam,tuple)]
        
        headerspace = self.uclass.getspace()
        ObjFormSet = modelformset_factory(headerspace, fields=tuple(fields_form))
        formset = ObjFormSet(queryset=headerspace.objects.none())
        
        ObjFormSetTestf = modelformset_factory(headerspace, fields=tuple([nameparam[0] for nameparam in MYCONF.UPARAMS_MYSPACES[namespace]['editcolumns'] if isinstance(nameparam,tuple)]))
        formsetsearchf = ObjFormSetTestf(queryset=headerspace.objects.none())
        many_and_foreign_dict = {}
        listmtmfork = [nameparam for nameparam in MYCONF.UPARAMS_MYSPACES[namespace]['editcolumns'] if isinstance(nameparam,tuple)]
        jsparamht = {}
        for nameparammodel in listmtmfork:
            valuelink = self.getlinks(nameparammodel[0])
            jsparamht[nameparammodel[0]] = namespace + '__' + nameparammodel[0]
            many_and_foreign_dict[nameparammodel[0]] = valuelink
            if(postgetp.has_key(nameparammodel[0] + '__prev_')):
                many_and_foreign_dict[nameparammodel[0] + '__prev_'] = postgetp[nameparammodel[0] + '__prev_']
            else:
                many_and_foreign_dict[nameparammodel[0] + '__prev_'] = valuelink
        
        dictproperties = self.propertiesdict
        dictmodules = {}
        if(len(many_and_foreign_dict) > 0):
            dictproperties = dict(dictproperties.items() + many_and_foreign_dict.items())
        dicttypesprops = self.typesprops()
        prevsaved = {}
        if(len(postgetp) > 0):
            for keyname in dictproperties:
                if(postgetp.get(keyname, False) != False and many_and_foreign_dict.has_key(keyname) and keyname.find('__prev_') == -1):
                    prevsaved[keyname] = postgetp[keyname]
                    dictproperties[keyname] = postgetp[keyname]
                elif(postgetp.get(keyname, False) != False):
                    if(dicttypesprops.has_key(keyname) and postgetp[keyname]=='' and (dicttypesprops[keyname] in ['int','float','date','time'])):
                        dictproperties[keyname] = None
                    else:
                        dictproperties[keyname] = postgetp[keyname]
                else:
                    dictproperties[keyname] = False
            self.propertiesdict = dictproperties
            
            for nameparmodel in fields_form:
                self.__setattr__(nameparmodel, postgetp.get(nameparmodel,False))
                dictproperties[nameparmodel] = postgetp.get(nameparmodel,False)
        else:
            
            for nameparmodel in fields_form:
                dictproperties[nameparmodel] = self.__getattribute__(nameparmodel)
        if(len(addvalue) > 0):
            dictproperties[addvalue[0]] = addvalue[1]
        if(len(addinitial) > 0):
            for nameparam in addinitial:
                if(isinstance(addinitial[nameparam],dict)):
                    if(addinitial[nameparam]['model'] != MYCONF.NAMEUPLOADMODEL):
                        strnamemodul = dict(listmtmfork)[nameparam].split('__')[0]
                        strnamemodel = dict(listmtmfork)[nameparam].split('__')[1]
                    #if files
                    else:
                        strnamemodul = MYCONF.NAMEUPLOADMODEL.split('__')[0]
                        strnamemodel = MYCONF.NAMEUPLOADMODEL.split('__')[1]
                    mymodel = importlib.import_module(strnamemodul).__getattribute__(strnamemodel)
                    #links
                    ismtm = False
                    try:
                        #mtm
                        if(hasattr(self.__getattribute__(nameparam),'model')):
                            ismtm = True
                        #link mtm None
                    except ValueError:
                        ismtm = True
                    #link fj
                    except :
                        ismtm = False
                    if((ismtm == True and addinitial[nameparam]['objects']!= '') or addinitial[nameparam]['model'] == MYCONF.NAMEUPLOADMODEL):
                        myobjscheck = addinitial[nameparam]['objects'].split(',')
                        myobjschecknon = []
                        if(addinitial[nameparam]['objectsno'] != ''):
                            myobjschecknon = addinitial[nameparam]['objectsno'].split(',')
                        if(addinitial[nameparam]['exclude'] == '1'):
                            objectdeleting = mymodel.objects.exclude(id__in = myobjschecknon)
                        else:
                            objectdeleting = mymodel.objects.filter(id__in = myobjscheck)
                        
                        dictproperties[nameparam] = ",".join([str(dictp['id']) for dictp in objectdeleting.values('id')])
                    else:
                        dictproperties[nameparam] = addinitial[nameparam]['idobj']
                    del mymodel, ismtm
                #no link
                else:
                    dictproperties[nameparam] = addinitial[nameparam]
        objform = formset.form(dictproperties)
        if(self.id == None and len(postgetp) == 0):
            objform = formset.form(initial=dictproperties)
        if(len(jsparamht) > 0):
            objform.__setattr__('mtomfk',jsparamht)
        for myprop in self.uclass.properties.values('codename', 'myfield', 'minfield', 'maxfield', 'required'):
            #switch field for myfield
            dict_myfield = dict(MYCONF.TYPES_MYFIELDS_CHOICES)
            
            minparam = None if (utils.safe_int(myprop['minfield']) == 0) else int(myprop['minfield'])
            maxparam = None if (utils.safe_int(myprop['maxfield']) == 0) else int(myprop['maxfield'])
            
            if(dict_myfield[myprop['myfield']] == 'str'): switchfield = forms.CharField(min_length = minparam, max_length=maxparam, required=bool(myprop['required']))
            elif(dict_myfield[myprop['myfield']] == 'text'): switchfield = forms.CharField(widget = forms.Textarea, min_length = minparam, max_length = maxparam, required=bool(myprop['required']))
            elif(dict_myfield[myprop['myfield']] == 'html'): switchfield = forms.CharField(widget = forms.Textarea, min_length = minparam, max_length = maxparam, required=bool(myprop['required']))
            elif(dict_myfield[myprop['myfield']] == 'int'): switchfield = forms.IntegerField(min_value = minparam, max_value = maxparam, required = bool(myprop['required']))
            elif(dict_myfield[myprop['myfield']] == 'float'): switchfield = forms.FloatField(min_value = minparam, max_value = maxparam, required = bool(myprop['required']))
            elif(dict_myfield[myprop['myfield']] == 'date'): switchfield = forms.DateField(widget = forms.DateInput, required = bool(myprop['required']))
            elif(dict_myfield[myprop['myfield']] == 'time'): switchfield = forms.TimeField(widget = forms.TimeInput, required = bool(myprop['required']))
            elif(dict_myfield[myprop['myfield']] == 'url'): switchfield = forms.URLField(required = bool(myprop['required']))
            elif(dict_myfield[myprop['myfield']] == 'ip'): switchfield = forms.IPAddressField(required = bool(myprop['required']))
            elif(dict_myfield[myprop['myfield']] == 'email'): switchfield = forms.EmailField(required = bool(myprop['required']))
            elif(dict_myfield[myprop['myfield']] == 'bool'): switchfield =  forms.BooleanField(required = bool(myprop['required']))
            elif(dict_myfield[myprop['myfield']] == 'files'): switchfield = forms.CharField(min_length = minparam, max_length = maxparam, required=bool(myprop['required']))
            
            objform.fields[myprop['codename']] = switchfield
        if(len(many_and_foreign_dict) > 0):
            for elemparammodel in many_and_foreign_dict:
                if(elemparammodel.find('__prev_') == -1):
                    objform.fields[elemparammodel] = forms.CharField(required = (formsetsearchf.forms[0].fields[elemparammodel].required))
                else:
                    objform.fields[elemparammodel] = forms.CharField(widget=forms.HiddenInput,required = False)
        #save
        dictidsaveskey = {}
        if(objform.is_valid() and len(postgetp) > 0 and save == True):
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
                
                linksobj = self.setlinks(modelparamstr,(strnamemodul,strnamemodel),prevsaved[modelparamstr])
                if(linksobj != False):
                    dictidsaveskey[modelparamstr] = linksobj
            if(len(dictidsaveskey) > 0):
                self.save()
                for nameparammtm in dictidsaveskey:
                    self.setlinks(nameparammtm,modelandtupleorqueryset=dictidsaveskey[nameparammtm])
            self.save()
        
        return objform
    propertiesclass = []
    templines = []
    def getpropforcibly(self):
        dictp = {}
        if(len(self.propertiesclass) == 0):
            self.propertiesclass = self.uclass.properties.all()
        try:
            if(len(self.templines) == 0):
                self.templines = self.lines.select_related().all()
            listidproplines = dict([(str(line.property.id),line) for line in self.templines])
            for objprop in self.propertiesclass:
                if(str(objprop.id) in listidproplines.keys()):
                    name_column_lines = MYCONF.TYPES_COLUMNS[dict(MYCONF.TYPES_MYFIELDS)[dict(MYCONF.TYPES_MYFIELDS_CHOICES)[objprop.myfield]]]
                    dictp[objprop.codename] = listidproplines[str(objprop.id)].__getattribute__(name_column_lines)
                else:
                    dictp[objprop.codename] = objprop.udefault
                self.__typespropsdict[objprop.codename] = dict(MYCONF.TYPES_MYFIELDS_CHOICES)[objprop.myfield]
        except:
            for objprop in self.propertiesclass:
                dictp[objprop.codename] = objprop.udefault
                self.__typespropsdict[objprop.codename] = dict(MYCONF.TYPES_MYFIELDS_CHOICES)[objprop.myfield]
        return dictp
    @property
    def propertiesdict(self):
        if(len(self.__propertiesdict) == 0  or self.id == None):
            self.__propertiesdict = self.getpropforcibly()
        
        return self.__propertiesdict
    @propertiesdict.setter
    def propertiesdict(self, value):
        self.__propertiesdict = value
        
    def typesprops(self):
        if(len(self.__typespropsdict) == 0): self.__propertiesdict = self.getpropforcibly()
        return self.__typespropsdict
        
    def therelinks(f):
        def tmp(*args, **kwargs):
            try:
                classlinks = args[0].uclass.getspace(getlinksall=True)
                classlinks.objects.get(idobj=str(args[0].id),uclass=str(args[0].uclass.id))
            except: return []
            else:
                return f(*args, **kwargs)
        return tmp
    
    @therelinks
    def links(self, classname, asall = True, namesvprop=[]):
        dictparam = {}
        dictparam['uclass__id' if str(classname).isdigit() else 'uclass__codename'] = classname

        listidobjects = [objlink.idobj for objlink in self.uclass.getspace(getlinksall=True).objects.get(idobj=self.id,uclass=self.uclass).links.all().filter(**dictparam)]
        dictparaminclass = {}
        dictparaminclass['id' if str(classname).isdigit() else 'codename'] = classname
        objclass = uClasses.objects.get(**dictparaminclass)
        objects = objclass.getobjects(id__in = listidobjects,namesvprop=namesvprop)
        return objects if (asall == True) else (objects[0] if (len(objects) > 0) else False)
    
    def _getlinks(self):
        mylinkobject = self.uclass.getspace(getlinksall=True).objects.get(idobj=self.id,uclass=self.uclass)
        return mylinkobject.links
    #type options 'add', 'clear', 'remove'
    @therelinks
    def linksedit(self,type,objects=None,ClassName='',ManyToOny = False):
        if(type == 'clear'):
            if(ClassName != ''):
                self.linksedit('remove', self.links(ClassName))
            else:
                self._getlinks().clear()
        else:
            if(objects.__class__.__name__ != 'QuerySet' and isinstance(objects, list) == False): objects = [objects]
            if(len(objects) > 0):
                first = objects[0]
                classname = first.uclass
                objectslinks = self.uclass.getspace(getlinksall=True).objects.filter(idobj__in=[object.id for object in objects],uclass=classname)
                if(ManyToOny == True):
                    self.linksedit('clear', ClassName=classname.name)
                    self._getlinks().__getattribute__(type)(objectslinks[0])
                else:    
                    self._getlinks().__getattribute__(type)(*objectslinks.all())
        
    def delete(self):
        #del lines
        self.lines.all().delete()
        #del links
        try:
            thislink = self.uclass.getspace(getlinksall=True).objects.get(idobj=self.id,uclass=self.uclass)
            thislink.links.clear()
            thislink.delete()
        except: pass
        
        super(AbsBaseHeaders, self).delete()
    
    def _manuallyCreateManuallyLink(self):
        try:
            objlinks = self.uclass.getspace(getlinksall=True).objects.get(idobj=self.id,uclass=self.uclass)
            objlinks.name = self.name
            objlinks.save()
        #if the object does not create a table of links to
        except:
            classlinkall = self.uclass.getspace(getlinksall=True)
            objl = classlinkall(idobj=self.id,name=self.name,uclass=self.uclass)
            objl.save()
            return 1 #is new obj
        else:
            return 0
        
    def save(self, *args, **kwargs):
        super(AbsBaseHeaders, self).save(*args, **kwargs)
        if(len(self.__propertiesdict) > 0):
            linksobject = [str(prop.property.id) for prop in self.lines.all()]
            modellines = self.lines.model
            for propclass in self.uclass.properties.all():
                if(propclass.codename in self.__propertiesdict.keys()):
                    name_column_lines = MYCONF.TYPES_COLUMNS[dict(MYCONF.TYPES_MYFIELDS)[dict(MYCONF.TYPES_MYFIELDS_CHOICES)[propclass.myfield]]]
                    valuepr = self.__propertiesdict[propclass.codename]
                    if(name_column_lines == 'upintegerfield' and valuepr == ''):
                        valuepr = None
                    if(str(propclass.id) in linksobject):
                        object_lines = self.lines.get(property__id=propclass.id)
                        object_lines.__setattr__(name_column_lines,valuepr)
                        object_lines.save()
                    else:
                        new_object_lines = modellines()
                        new_object_lines.property = propclass
                        new_object_lines.__setattr__(name_column_lines,valuepr)
                        new_object_lines.save()
                        self.lines.add(new_object_lines)
        if(self._flagAutoAddedLinks == True): self._manuallyCreateManuallyLink()
    
    def __unicode__(self):
        return self.name
    class Meta:
        abstract = True

class systemObjHeaders(AbsBaseHeaders):
    lines = models.ManyToManyField(systemObjLines,blank=True) #без строк можно создать
    
    #user params
    name = models.CharField(max_length=255)
    sort = models.IntegerField(blank=True,null=True,default=0)
    class Meta:
        db_table = MYCONF.PROJECT_NAME + '_ucms_systemobjheaders'
class myObjHeaders(AbsBaseHeaders):
    lines = models.ManyToManyField(myObjLines,blank=True) #без строк можно создать
    #user params
    name = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    sort = models.IntegerField(blank=True,null=True,default=0)
    class Meta:
        db_table = MYCONF.PROJECT_NAME + '_ucms_myobjheaders'

class systemuploadsfiles(models.Model):
    name = models.CharField(max_length=255)
    dfile = models.FileField(upload_to=MYCONF.UPLOADMEDIA_PATCH)
    class Meta:
        db_table = MYCONF.PROJECT_NAME + '_ucms_uploadfiles'

### START example models #########################################################################################################################
#TYPELOCATION_CHOICES = (
#    (1, 'country'),
#    (2, 'sity'),
#)
#class examplelocationhome(models.Model):
#    name = models.CharField(max_length=25)
#    locat_chois = models.PositiveSmallIntegerField(choices=TYPELOCATION_CHOICES)
#    aggregation = models.ManyToManyField("self",blank=True)
#    class Meta:
#        db_table = MYCONF.PROJECT_NAME + '_examplelocationhome'
#class examplesellers(models.Model):
#    name = models.CharField(max_length=25)
#    description = models.CharField(max_length=255)
#    locations = models.ManyToManyField(examplelocationhome)
#    class Meta:
#        db_table = MYCONF.PROJECT_NAME + '_examplesellers'
#class exampleHeadersLines(AbsBaseLines):
#    class Meta:
#        db_table = MYCONF.PROJECT_NAME + '_ucms_exampleheaderslines'
#class exampleHeaders(AbsBaseHeaders):
#    lines = models.ManyToManyField(exampleHeadersLines,blank=True)
#    
#    name = models.CharField(max_length=25)
#    locations = models.ManyToManyField(examplelocationhome,blank=True)
#    sales = models.ForeignKey(examplesellers)
#    class Meta:
#        db_table = MYCONF.PROJECT_NAME + '_ucms_exampleheaders'
### END example models #########################################################################################################################

# MYSPACE_TABLES_CHOICES conf.py mirror dict spaces (header,lines)
TABLE_SPACE = {
    1: (myObjHeaders, myObjLines, linksObjectsAll), #(1, 'my') MYSPACE_TABLES_CHOICES
    2: (systemObjHeaders, systemObjLines, linksObjectsSystem), #(2, 'system') MYSPACE_TABLES_CHOICES
    #3: (exampleHeaders, exampleHeadersLines, linksObjectsAll), #add your space #3: (exampleHeaders, exampleHeadersLines),
}
def get_space_model(idnameclass=None, getlines=False, getlinksall=False, tablespace=None): # getlines is False then return Headers
    if(tablespace):
        tablespaceid = tablespace
    elif(str(idnameclass).isdigit()):
        tablespaceid = uClasses.objects.get(id=str(idnameclass)).tablespace
    else:
        tablespaceid = uClasses.objects.get(codename=str(idnameclass)).tablespace
    typlespace = TABLE_SPACE.get(tablespaceid, False)
    if(getlinksall != False):
        return typlespace[2]
    else:
        return typlespace[1 if getlines else 0]