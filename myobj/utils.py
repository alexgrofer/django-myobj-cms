def mumenrec(oblist,ul='ul',li='li',tagli='p'):
    strmod = '<' + ul + '>'
    for obl in oblist:
        try:
            link = obl[2]
        except:
            link = '/'
        valobj = str(obl[0])
        cssclass = obl[(len(obl) - 1)] if (len(obl) >= 3) else ''

        if(type(obl[1]) is list):
            strmod += '<' + li + ' class="' + cssclass + '"><' + tagli + '><a href="' + link + '">' + valobj + '</a></' + tagli + '>' + mumenrec(obl[1],ul,li,tagli) +'</' + li + '>'
        else:
            strmod += '<' + li + ' class="' + cssclass + '"><a href="' +obl[1]+ '">' + valobj +'</a></' + li + '>'
    strmod += '</' + ul + '>'
    return strmod

def safe_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0

def pagination(indexpage,countlinks,startlenobjects,leftrcount,urlp):
    linksp = ''
    linkspt = ''
    startleft = indexpage - leftrcount if (indexpage - leftrcount >=0) else 0
    rangenorm = range(countlinks)[startleft: leftrcount + indexpage]
    
    if(indexpage != 0):
        
        if((indexpage - leftrcount) >= 0):
            linksp += '<a class="nextleft" href="' + urlp + str(indexpage + 1 - leftrcount) + '">...</a>'
        linkspt += '<a id="prevpg" class="prev" href="' + urlp + str(indexpage) + '">&larr; Ctrl prev</a>'
    
    for i in rangenorm:
        actclassl = ''
        if(indexpage == i):
            actclassl = ' class="actionp"'
        linksp += '<a' + actclassl + ' href="' + urlp + str((i + 1)) + '">' + str((i + 1)) + '</a>'
    
    if(indexpage +1 != countlinks):
        linkspt += '<a id="nextpg" class="next" href="' + urlp + str(indexpage + 2) + '">next Ctrl &rarr;</a>'
        linksp += '<a class="nextright" href="' + urlp + str((indexpage + 2 + leftrcount)) + '">...</a>'
    
    pagination = '<div id="pagination" class="pagination"><p class="page-top">' + linkspt + '</p><p class="pagin-lenks">' + linksp + '</p></div><script>$(document).keydown(function(event){if(event.ctrlKey){if(event.keyCode == 37){if($("#prevpg").length){linkclick($("#prevpg").attr("href"))}}else if(event.keyCode == 39){if($("#nextpg").length){linkclick($("#nextpg").attr("href"))}}}})</script>'
    return pagination
def comparelist(list1,list2):
        maxlist = list1 if (len(list1) > len(list2)) else list2
        lenok = 0
        for ellist in list1:
            if(ellist in list2): lenok += 1
        return True if (lenok == len(maxlist)) else False
def getlinks(objectedit,name,listid=True):
        elements = None
        if(hasattr(objectedit,name)):
            elemvaluempar = objectedit.__getattribute__(name)
            if(hasattr(elemvaluempar,'model')):
                elements = ('' if (elemvaluempar.count() == 0) else (",".join(([str(dictp['id']) for dictp in elemvaluempar.values('id')])) if listid else elemvaluempar ))
            else:
                elements = ('' if (hasattr(elemvaluempar,'id') == False) else (str(elemvaluempar.id) if listid else elemvaluempar ))
            
        return elements

def renamefile(objfile,setname='',isrand=False):
    import os
    import random
    stmp = 'qwertyuiasdfghjzxc234'
    randname = ''.join(random.sample(stmp,len(stmp)))
    newpath = ''
    oldpath = objfile.path
    tuplepath = os.path.split(oldpath)
    if(setname!=''):
        tuplepath = os.path.split(setname)
        if(tuplepath[0]!=''):
            objfile.field.upload_to = tuplepath[0]
        newpath = os.path.join(tuplepath[0], tuplepath[1])
    elif(isrand == True): newpath = os.path.join(tuplepath[0], randname + '.' + tuplepath[1].split('.')[1])
    else:
        return False
    objfile.save(newpath,objfile)
    #os.remove(oldpath) #нудно удалять или параметр isdelete

def ismtmfield(obj,col):
    return True if (col + '_id' not in dir(obj)) else False