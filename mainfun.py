# *********  WEB CRAWLER *************
# VERSION 1.0  
# Ajinkya Deshmukh
# ajinkyad13@gmail.com
# **********************************

'''
0. url and data stored for coressponfing url (title , meta chara also) ... anchor saved before only
1. url get from page
2. normalized them (lower case , http ,relative to absolute )
3. check for done before or not
	if done => add anchor only , anchor window 
        else => add to visited 
       		checks robots.txt
        	if => exclusion .. add url and set data as "Robot denied !!!" and add anchor  also add  to visited
                else => url ( create a empty object with anchor no data  ... bz before it processed via queue if another came can add anchor text to it )
                	Add to site queue dictionary 
4.check urlfetcher queue lenght 
	if => it is empty  refill it with site queue dictionary 
        else => 
        	see time last or put it aside time diff =2 sec 
        	try : fetch url exception : broken urls  

STOPING CONDITION => after N(e.g. 10) url dont tc urls into url dictionary and empty all dictionary and put into queue and finish that queue
'''

'''
data
'''
import re
import datetime as dt
from bs4 import BeautifulSoup
import urllib2
from urlparse import urlparse
from urlparse import urljoin
from reppy.cache import RobotsCache
robots = RobotsCache()         ## creating object for cache robots.txt


'''
url data
'''

class Url_class  :
    def __init__(self , url ):
		self.url = url
		self.anchor = []
                self.anchor_win = []
                self.title = ""
                self.urldata = "" 
    def add_anchor(self,anchortext,ancwintext):
    	self.anchor.append(anchortext)
        self.anchor_win.append(ancwintext)
    def add_title(self,titletext):
        self.title =  titletext 
    def dataadd  (self,datatext):
        self.urldata = datatext



url_fecher_queue = []   #['http://asd.com/ddd','http://asd.com/fff']
visited_site_url = {}	 # {'http://asd.com':['http://asd.com/ddd','http://asd.com/fff'] , ... }
data_url = {}             #{site : [urlobject1 , .... ]}  ##urrl object => url,anchor,anchor window,metachar,main text
site_last_time_visit ={}       # {'http://asd.com':time(), .... }
site_current_url_remain = {}   # {'http://asd.com':['http://asd.com/ddd','http://asd.com/fff'] , ... }

'''ALL USER DEFINED DATA READING  '''
def user_defined():
#open file and read what he want for focused crawling    
    FILE_READ_DATA = open( "data", "r" )
    linedata = ""
    for linethis in FILE_READ_DATA:
        linedata = linedata + linethis 
    clearline = re.sub('\s+',' ',linedata)
    listretpls =  filter(None, clearline.lower().split(" "))
    return listretpls

'''ALL USER DEFINED DEPTH DATA READING  '''
def user_defined_depth():
#open file and read what he want for focused crawling    
    FILE_READ_DATA = open( "depth", "r" )
    linedata = ""
    for linethis in FILE_READ_DATA:
        linedata = linethis 
        break      ## First line read only ... depth number
    clearline = re.sub('\s+','',linedata)  ## replace by null string not " "
    listretpls =  filter(None, clearline.lower().split(" "))
    return int(listretpls[0])
    
def user_defined_pages():
#open file and read what he want for focused crawling    
    FILE_READ_DATA = open( "page", "r" )
    linedata = ""
    for linethis in FILE_READ_DATA:
        linedata = linethis 
        break      ## First line read only ... depth number
    clearline = re.sub('\s+','',linedata)  ## replace by null string not " "
    listretpls =  filter(None, clearline.lower().split(" "))
    return int(listretpls[0])
    
    


'''Seed reader .. only used for first time'''
def seed_reader():   ##return list of urls 
#read all seed normalized it and then put it into back queue 
    list_of_url = [] 
    DocumentWhole = open( "url", "r" )
    for line in DocumentWhole:
        line = line.strip('\n')
        list_of_url.append(line)
    return list_of_url


'''Data store to already created object when site marked as visited'''
def datastorer(site , at_given_url):      # return beautifulsoup object                   *** # at exception return 0 
# on that url that page text saved , title , meta character also saved  
# beautiful soap used for url
# try and catch used (broken url)
# url stored in dictionary and returns for further use of link on that page
# modify time visit of that site 
    listofobject = data_url[site] 
    list_of_one_object =  filter(lambda x: x.url ==at_given_url , listofobject)
    object_url = list_of_one_object[0]
    ##open page and give to beautiful soup
    try :
        req = urllib2.Request(at_given_url)
        req.add_unredirected_header('User-Agent', 'StudentBot')      ## Bot name  ... StudentBot
        objecturllib = urllib2.urlopen(req )
        site_last_time_visit[site] = dt.datetime.now()               ## site visited now so time is updated 
        htmlcode  =  objecturllib.read()
        #============== STORING FILE IN FOLDER =============
        html_code_file = open("segment/"+site,"a")
        html_code_file.write(at_given_url)
        html_code_file.write('\n\n')
        html_code_file.write(str(htmlcode))
        html_code_file.write('\n\n\n\n')
        html_code_file.write("#===========================================================================================================#")
        html_code_file.write('\n\n\n\n')
        html_code_file.close()
        #============== STORING FILE ENDS ==================
        soupobject = BeautifulSoup(htmlcode)
        nouse = [xjs.extract() for xjs in soupobject.findAll(['script', 'style'])]    ## remove all javascript and css from body NOUSE OF THAT
        #soupnormalized = soupobject.prettify()
        #print soupnormalized
        if soupobject.title : 
            ##print soupobject.title.string 
            object_url.add_title(soupobject.title.string) 
        ##print soupobject.body.get_text().encode('utf-8') ##printing purpose utf8 conversion 
        object_url.dataadd(soupobject.body.get_text())
        return  soupobject
    except Exception :
        object_url.dataadd("Error : Url is broken !!!")
        return 0 
    #print object_url.url.encode('utf-8')           
    #print object_url.title.encode('utf-8')               
    #print object_url.urldata.encode('utf-8')
    



'''Returns all page on given page '''
def all_url_on_given_page(beautful_soap_string):   # return [[url,anchor,anchorwindow],[url,anchor,anchorwindow],.... ]  
#give all urls on given page 
#normalized them using below defination
#return all url,achor text , anchor text window 
    temp_list = [] 
    for link in beautful_soap_string.find_all('a'):             ## for all a
         if link.get('href') :                  ## only contain href
             ref_anchorwindow = ''
             ref_link = link.get('href')
             ref_anchor = link.string
             if link.previousSibling : 
                 ref_anchorwindow = link.previousSibling.string     ##******** CORRECT THIS AFTERWARDS  *******************
             make_list = [ref_link, ref_anchor,ref_anchorwindow]
##***** DONT MAKE URL LOWER... OTHERWISE IT WILL NOT WORK ... FOLDER ARE CASE SENSATIVE .... ONLY SITE URL AFTERWARDS MAKE SMALL
             temp_list.append(make_list)
    return temp_list



#========== FOCUSED CRAWLER ============================
#*******************************************************


def focused_links (list_of_links):
#****************** MAKE LOWER ANCHOR TEXT ************************ >>>>IN PREVIOSE ONLY
    list_ret = [ ]
    for evry_link_list in list_of_links :
        if evry_link_list[1] : 
            anchor_for_that_url = evry_link_list[1].lower()    ## remove lower from here and put that in datastorer function
            words_in_that_anchor = filter(None, anchor_for_that_url.split(" "))
            if len(list(set(LIST_OF_WORDS_USER) & set(words_in_that_anchor))):
                list_ret.append(evry_link_list)
    return list_ret



#*******************************************************
#=============== FOCUSED CRAWLER ENDS HERE ==============

'''Site normalized before further processong '''
def sitenamenormalization(baseurl , one_url_at_a_time): ## baseurl is one used for datastored , and one url from all url returns from that page
# return final url provided         

#lower case 
#normalizes site name www.asd.com => http://asd.com
# relative to absolute /ddd => http://asd.com/ddd
#same page remove 
## REFER TO URL STUDY  ##
    if baseurl.startswith('http://'):
        baseurl = baseurl[7:]
    if baseurl.startswith('https://'):
        baseurl = baseurl[8:]
    if baseurl.startswith('www.'):
        baseurl = baseurl[4:]

    flag_of_one_url_http = 0     
    if one_url_at_a_time.startswith('http://'):
        one_url_at_a_time = one_url_at_a_time[7:]
        flag_of_one_url_http = 1
    if one_url_at_a_time.startswith('https://'):
        one_url_at_a_time = one_url_at_a_time[8:]
        flag_of_one_url_http = 1
    if one_url_at_a_time.startswith('www.'):
        one_url_at_a_time = one_url_at_a_time[4:]
        flag_of_one_url_http = 1 

    if (flag_of_one_url_http==1):    
        one_url_at_a_time = "http://" + one_url_at_a_time

    modified_base_url = 'http://'+baseurl
    joinedurl = urljoin( modified_base_url,one_url_at_a_time )   ##join url
    joined_url_parsed  = urlparse( joinedurl)                    ## parsed ... remove query from urls 
    finalurl = joined_url_parsed.scheme+"://" + joined_url_parsed.netloc.lower() + joined_url_parsed.path
    return finalurl.strip('/')             ##last element / no use and making duplicatswith / and without /               ## case insensative



'''Check for duplicate '''
def url_checker_dupli(site , normalized_absolute_url ):
#checks is url used first time or used before
#checks in visited_site_url dictionary at key site and in list for normalized_absolute_url
#check site is dere ot not in dictionary .... !!!!
#return 0 or 1 accordingly
# mark visited by adding url and site accordingly dere or not 
    if visited_site_url.has_key(site):
        if normalized_absolute_url in visited_site_url[site]:
            return 0     ## duplicate 
        else :
            visited_site_url[site].append(normalized_absolute_url)  ## added as visited
            new_obj_url = Url_class( normalized_absolute_url)
            data_url[site].append(new_obj_url)                      ## blank dataobject created for that url and added 
            return new_obj_url      ## site is present but url is new 
    else : 
        visited_site_url[site] = []
        data_url[site] = []
        visited_site_url[site].append(normalized_absolute_url)
        new_obj_url = Url_class( normalized_absolute_url)
        data_url[site].append(new_obj_url)   
        #print "all new"
        return new_obj_url          ## site also ... no url offcourse



''' If duplicate url then ... and add to object created already '''
def add_anchor_only(site, url , anchor , anchor_window):
#add anchor of given url bz it done before jst add anchor  AND anchor window
#add in data_url dictionary at key site and in list for normalized_absolute_url
    all_url_rel = data_url[site]
    list_of_one_url_of_site =  filter(lambda mm: mm.url == url ,all_url_rel )
    one_url_gotted_obj = list_of_one_url_of_site[0] 
    one_url_gotted_obj.add_anchor(anchor , anchor_window)



  
'''*** MERGED IN URL DUPLICATE CLASS ... IT WILL CHECK IF NOT CREATE AND RETURN 1 IF DERE JST RETURN 0  .. both url and site check  
# Mark as visited and create object
def url_visited(site, url_provided):                       #return nothing 
#mark that url as visited and create object for it 
#add to both dictionary data_url and visited_site_url
# check site in dictionary there or not ... if not add sitte to dictionary  
'''


'''Robot call checker'''
def robots_checker(url_provided):   #return 0: denied 1 : granted
#check robots for that url call 
  try : 
    if robots.allowed(url_provided, '*'):   ## put user agent name instead of *
        return 1
    else : 
        return 0 
  except Exception : 
        return -1                # ************* site doesn't exists  


'''If robots denied'''
def denied_robots_call(site, url , anchor , anchor_window):
#add data="Robots denied" , anchor and anchor window to already created object 
#DONT ADD TO QUEUE OF SITE 
    list_of_object_derived = data_url[site] 
    list_of_one_object =  filter(lambda dd: dd.url == url ,  list_of_object_derived)
    object_url_gotted = list_of_one_object[0]
    object_url_gotted.add_title("ROBOTS DENIED")    ## ASK MADAM ... title of denied urls 
    object_url_gotted.add_anchor( anchor , anchor_window)
    object_url_gotted.dataadd("ROBOTS DENIED")     ## ASK MADAM CONFIRM  .... GOOGLE SHOWS LIKE THAT
    #print object_url_gotted.anchor
    #print object_url_gotted.anchor_win
    #print object_url_gotted.url
    #print object_url_gotted.title
    #print object_url_gotted.urldata

''' If not denied by robots call ''' 
def add_to_site_queue_dict(site, url):
#add to dictionary of queue sitewise
#first check site name present in dictionary or not if not create new key and empty list 
#if present append to site list 

##IF CHECK SITE PRESENT OR NOT 
##IF PRESENT JUST ADD TO QUEUE
##ELSE ADD SITE AND MAKE QUEUE BY MAKING LIST
    if site_current_url_remain.has_key(site):
        site_current_url_remain[site].append(url)
    else :
        site_current_url_remain[site] = [url , ]


'''Back queue lenght is less than 3'''
def back_queue_feeder():
#fill back queue 
#check queue lenght if greater than 3 dont do anything
#if smaller then go through all dictionary site_current_url_remain keys pop 1 element (remove from queue)
#if list remaining 1 element then pop and delete that list and key from dictionary

# if dictionary is empty then ????    ...end of crawl 
    if len(url_fecher_queue)== 0  : 
        if len(site_current_url_remain):
                  dellist = []
                  for eachsite in site_current_url_remain : 
                        if len(site_current_url_remain[eachsite]) > 1 :
                            tempvar = site_current_url_remain[eachsite].pop(0)
                            url_fecher_queue.append(tempvar)
                        else : 
                            tempvar = site_current_url_remain[eachsite].pop(0)
                            url_fecher_queue.append(tempvar)
                            dellist.append(eachsite)
                  for del_each in dellist : 
                      del (site_current_url_remain[del_each])
        else : 
                    print " ===============  QUEUE FINISHED RESULTS ============= \n "

                    print "URL FECTER QUEUE"
                    print url_fecher_queue

                    print "\n\n\n\n"

                    print "VISITED SITE URL"
                    print visited_site_url

                    print "\n\n\n\n"

                    print "DATA URL"
                    print data_url

                    print "\n\n\n\n"

                    print "SITE TIME"
                    print site_last_time_visit

                    print "\n\n\n\n"

                    print "URL REMAINED"
                    print site_current_url_remain

                    print "\n\n\n\n"

                    for data_con in data_url:
                        print data_con
                        for  dataobj in data_url[data_con]: 
                                    print dataobj.url.encode('utf-8')  
                                    print dataobj.anchor
                                    print dataobj.anchor_win  
                                    print dataobj.title.encode('utf-8') 
                                    print dataobj.urldata.encode('utf-8')        
                                    print "=============\n"
                    print "*****************************\n"          


                    print "Url visited"
                    print urllistvisted

                    print "Depth List"
                    print LIST_DEPTH_REC



                    print "Site Queue Finished ... Stopping Crawling"
                    exit()
    #else : 
    #    print "No need to feed"


'''Before url fetched check this time '''
def time_checker(site_name):
#checks time and return 0 or 1 accordingly what to do 
#checks last visit
#check site present or not ** very first task . then if present . not present create . ****time last visit remained in above dataadder function
    
    if site_last_time_visit.has_key(site_name):   ## site visited previously
        time_when_vistied = site_last_time_visit[site_name]
        time_now  =  dt.datetime.now()
        difference_delta_obj  = time_now - time_when_vistied  
        if difference_delta_obj.days > 0 or difference_delta_obj.seconds >=2 :             #========= PUTTED 2 SECOND GAP +++ ARY HERE IF U WANT DIFFERENT +++++ 
            return 1   ## time is greater than 2 seconds  .... no problem
        else :
            return 0   ## not rite time last time visited is less than 2 seconds
    else : 
        ## do nothing datastorer create when he load the site url  .. he store site last time 
        return 1    ## fine never visited so go ahead 



def url_splitter(fullurl):  ## in main this require bz every url function require site name and url 
##url splitted returns two parts 1.main domain 2. full url 
    site_and_rel   = urlparse( fullurl ) 
    return site_and_rel.netloc.lower()    ## site name without http ... :)  ..... ##**** PROBLEM ON FTP PROTOCOL


'''Give url  to fetch '''
def url_giver():
# returns one url that want to fetch 
# check time before giving 
#if time is less then pop another one and push this one back to queue   (if 1 or 2 element is remaining then)
# return url 


## time checking and feeder covered here  .... 

    if len(url_fecher_queue) == 0 : 
        back_queue_feeder()
    while True :
        jstforhold = ""
        current_pop_url = url_fecher_queue.pop(0)
        site_of_given_url = url_splitter(current_pop_url)
        value_return = time_checker(site_of_given_url)
        if value_return==1 : 
            jstforhold = current_pop_url 
            break 
        else : 
            url_fecher_queue.insert(10 ,current_pop_url )                 ## **** TIME NOT MATCH THEN 10 th position insert .... 
    return jstforhold




## DONT NEED TO CHECK TIME AND QUEUE FEEDER .... TAKEN CARE BY URL_GIVER


#===========DEPTH IMPLEMENTATION======================
#==========*********************=====================
## depth calculation for crawling

def create_depth_list (user_given_no):   ## create depth empty list 
## e.g. depth 4 === [ [],[],[],[]  ] ## for each depth one list
## add 1 to user given because first is zero and taken by seeds
    LIST_DEPTH_REC = [[] for x in range(user_given_no + 1)]
    return LIST_DEPTH_REC

def add_to_depth (one_full_url , depth_number): ## adding given urls to depth
## depth number provides info about in which depth we want to add
    LIST_DEPTH_REC[ depth_number].append(one_full_url) 


def check_depth (full_absolute_url): ## returning 1 if depth is not boundary depth AND 0 when depth is boundary depth 
    for current_list in  LIST_DEPTH_REC:
        if full_absolute_url in current_list : 
            break 
    depth_of_url = LIST_DEPTH_REC.index(current_list)
    if depth_of_url == USER_GIVEN_NO : 
        return [0,depth_of_url]
    else :
        return [1,depth_of_url]




#==========*********************=====================
#===========DEPTH IMPLEMENTATION FINISHED======================



#======================= MAIN ++++++ =============================
url_list = seed_reader()
LIST_OF_WORDS_USER = user_defined()  
USER_GIVEN_NO = user_defined_depth()    ## Number of depth max user want to crawl
LIST_DEPTH_REC = create_depth_list(USER_GIVEN_NO)     ## list where records are stored
depth_of_current = 0 



for one_url_in_list in url_list : 
    site_base_name  = url_splitter(one_url_in_list)
    res_dpli = url_checker_dupli( site_base_name , one_url_in_list)
    if res_dpli :    ## url not present 
        ret_robo  = robots_checker(one_url_in_list) ##robots check 
        if ret_robo== 1 :    ## if -1 do nothing site not present  or delete site from dictionary ***** 
            res_dpli.add_anchor("Seeds","Seeds")   ##    ASK madam ... remove bz .. other will give anchor abt seeds
            add_to_site_queue_dict(site_base_name , one_url_in_list)
            # ===== depth calculation =======
            add_to_depth (one_url_in_list , depth_of_current)
            # ===== depth calculation ends ======
        elif ret_robo == 0:  
            denied_robots_call(site_base_name , one_url_in_list , "NO ACHOR TO SEEDS","NO WINDOW TO SEEDS")
        elif ret_robo == -1 :  #*** delete site bz its not present in actual world   
            del   visited_site_url[site_base_name]
            del   data_url[site_base_name]  
    else :         ## duplicate url 
        add_anchor_only(site_base_name , one_url_in_list , "NO ACHOR TO SEEDS","NO WINDOW TO SEEDS" )
        
'''
#========== checking  ==========                              ## **** DONE NICE UPTIL ALL GOOD CHECK BY UN COMMETING ALL STUFF
print "URL FECTER QUEUE"
print url_fecher_queue

print "VISITED SITE URL"
print visited_site_url

print "DATA URL"
print data_url

print "SITE TIME"
print site_last_time_visit

print "URL REMAINED"
print site_current_url_remain

for data_con in data_url:
    print data_con
    for  dataobj in data_url[data_con]: 
        	print dataobj.url 
                print dataobj.anchor 
                print dataobj.anchor_win 
                print dataobj.title 
                print dataobj.urldata  



while True :
    urlgiver  = url_giver()
    print urlgiver
'''
no_of_urls = user_defined_pages()
## exit functionality remove  ..... and   delete sites which are not present when robots checker say no site by returning -1 
counter = 1 
#for now only 
urllistvisted = []
while counter <= no_of_urls :                            ## fist n number of urls only ..... 
    urlgiver  = url_giver()


    # checking its depth ===========
    list_of_info_url = check_depth (urlgiver)
    ok_or_cancel = list_of_info_url[0]
    depth_of_current = list_of_info_url[1] 
    #checking ite depth ends===========


    site_base_name  = url_splitter(urlgiver)
    soup_catcher = datastorer(site_base_name ,urlgiver )
    if soup_catcher and ok_or_cancel:                        ## ok or cancel decided by depth ... on boundary depth no further urls  
        list_of_url = all_url_on_given_page(soup_catcher)
        #FOCUSED CRAWLER ======================
        list_of_url = focused_links (list_of_url) ## VARIABLE OVERWRITTEN
        #FOCUSE CRAWLER =======================
        for one_url_list_in_all_list in list_of_url : 
            modified_abs_url = sitenamenormalization(urlgiver ,one_url_list_in_all_list[0] )
            modi_site_base =  url_splitter(modified_abs_url)
            urlretval = url_checker_dupli(modi_site_base ,modified_abs_url)
            
            if urlretval :    ## url not present 
                    ret_robo  = robots_checker(modified_abs_url) ##robots check 
                    if ret_robo== 1 :    ## if -1 do nothing site not present  or delete site from dictionary *****  
                        add_to_site_queue_dict(modi_site_base , modified_abs_url)
                        urlretval.add_anchor(one_url_list_in_all_list[1], one_url_list_in_all_list[2])   ## anchor added 
                        # ===== depth calculation =======
                        add_to_depth (modified_abs_url ,depth_of_current+1 )
                        # ===== depth calculation ends ======
                    elif ret_robo == 0:  
                        denied_robots_call(modi_site_base , modified_abs_url,one_url_list_in_all_list[1] ,one_url_list_in_all_list[2])
                    elif ret_robo == -1 :  #*** delete site bz its not present in actual world   
                        del   visited_site_url[modi_site_base]
                        del   data_url[modi_site_base]  
            else :         ## duplicate url 
                    add_anchor_only(modi_site_base , modified_abs_url, one_url_list_in_all_list[1], one_url_list_in_all_list[2] )
        
    urllistvisted.append(urlgiver) ###tatpurta 
    counter = counter + 1 





print "URL FECTER QUEUE"
print url_fecher_queue

print "\n\n\n\n"

print "VISITED SITE URL"
print visited_site_url

print "\n\n\n\n"

print "DATA URL"
print data_url

print "\n\n\n\n"

print "SITE TIME"
print site_last_time_visit

print "\n\n\n\n"

print "URL REMAINED"
print site_current_url_remain

print "\n\n\n\n"

for data_con in data_url:
    print data_con
    for  dataobj in data_url[data_con]: 
                print dataobj.url.encode('utf-8')  
                print dataobj.anchor
                print dataobj.anchor_win  
                print dataobj.title.encode('utf-8') 
                print dataobj.urldata.encode('utf-8')        
                print "=============\n"
print "*****************************\n"          

print "Url visited"
print urllistvisted

print "Depth List"
print LIST_DEPTH_REC





###  1. anchor window add  
###  2. anchor add ...change url_visited class return object ... so used to add anchor    #### DONE ... :) 
###  3. delete from dicitionary return -1 sites ... bz they are not present   #### DONE ... :) 
###  4. user -agent                                                           #### DONE ... :) 
###  5. how many levels go deeper   ### DONE :) 
###  6. focused crawler      ### DONE :)
