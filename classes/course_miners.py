import urllib
from BeautifulSoup import BeautifulSoup
import hashlib
import pickle
import xml

#url_download_cache_db = pickle.load(open('data.pkl', 'rb'))

def get_attr(linkattrs, attr):
    ln = filter(lambda (x,y): x == attr, linkattrs)
    return ln[0][1]

def save_pickle():
    out = open('data.pkl', 'wb')
    pickle.dump(url_download_cache_db, out)
    out.close()

def disk_cache_urlopen_read(url):
    """ Caches contents of url to disk """
    try:
        html = urllib.urlopen(url).read()
    except IOError: # sometimes connection fails from slamming too hard
        time.sleep(3)
        html = urllib.urlopen(url).read()

#    try:
#        disk_location = url_download_cache_db[url]
#    except KeyError:
#        try:
#            html = urllib.urlopen(url).read()
#        except IOError: # sometimes connection fails from slamming too hard
#            time.sleep(3)
#            html = urllib.urlopen(url).read()
#        filename = hashlib.sha1(html).hexdigest()
#        disk_location = 'mine_db/' + filename
#        url_download_cache_db[url] = disk_location
#        fp = open(disk_location, 'w')
#        fp.write(html)
#        fp.close()
#    fp = open(disk_location)
#    ret = fp.read()
#    fp.close()
#    return ret
    return html

def mit_ocw_load_course_db():
    mit_ocw_course_url = 'http://ocw.mit.edu/OcwWeb/web/courses/courses/index.htm'
    mit_ocw_course_html = disk_cache_urlopen_read(mit_ocw_course_url)#urllib.urlopen(mit_ocw_course_url).read()
    soup = BeautifulSoup(mit_ocw_course_html)

    course_db = []
    all_anchors = soup.findAll('a')
    for anchor in all_anchors:
        href_filter = filter(lambda (x,y): x == 'href', anchor.attrs)
        if len(href_filter) == 1 and href_filter[0][1].find('CourseHome') > 0:
            name = anchor.childGenerator().next()
            url = href_filter[0][1]
            parent = anchor.parent
            number = parent.previous
            date = anchor.next.next.next
            course_db.append((name, url, number, date))
    return course_db

def mit_ocw_load_table_from_page(course_url):
    course_html = disk_cache_urlopen_read(course_url)
    soup = BeautifulSoup(course_html)
    dtables = soup.findAll('table')
    tables = []
    for table in dtables:
        if table.findAll('table'):
            continue
        rows = []
        schema = []
        for row in table.findAll('tr'):
            for th in row.findAll('th'):
                schema.append(th.renderContents())
            tds = []
            for td in row.findAll('td'):
                tds.append(td.renderContents())
            if len(tds) > 0:
                rows.append(tds)
        tables.append((schema, rows))
    return tables

def mit_ocw_grab_instructors(course_html):
    try:
        soup = BeautifulSoup(course_html)
        chpstaff = soup.find('div', {'class': 'chpstaff'})
        try:
            return [prof.renderContents() for prof in chpstaff.findAll('p')]
        except AttributeError:
            return ''
    except Exception:
        return ''

def mit_ocw_grab_description(course_html):
    try:
        soup = BeautifulSoup(course_html)
        desc = soup.find('div', {'id': 'Description'})
        return desc.renderContents()
    except Exception:
        return ''
            
import re
def stanford_load_course_db():
    courses = [('Programming Methodology', 'CS106A'),
        ('Programming Abstractions', 'CS106B'),
        ('Programming Paradigms', 'CS107'),
        ('Introduction to Robotics', 'CS223A'),
        ('Natural Language Processing', 'CS224N'),
        ('Machine Learning', 'CS229'),
        ('The Fourier Transform and its Applications', 'EE261'),
        ('Introduction to Linear Dynamical Systems', 'EE263'),
        ('Convex Optimization I', 'EE364A'),
        ('Convex Optimization II', 'EE364B ')]
    courseurls = ['http://see.stanford.edu/see/courseinfo.aspx?coll=824a47e1-135f-4508-a5aa-866adcae1111',
            'http://see.stanford.edu/see/courseinfo.aspx?coll=11f4f422-5670-4b4c-889c-008262e09e4e', 
            'http://see.stanford.edu/see/courseinfo.aspx?coll=2d712634-2bf1-4b55-9a3a-ca9d470755ee',
            'http://see.stanford.edu/see/courseinfo.aspx?coll=86cc8662-f6e4-43c3-a1be-b30d1d179743',
            'http://see.stanford.edu/see/courseinfo.aspx?coll=63480b48-8819-4efd-8412-263f1a472f5a',
            'http://see.stanford.edu/see/courseinfo.aspx?coll=348ca38a-3a6d-4052-937d-cb017338d7b1',
            'http://see.stanford.edu/see/courseinfo.aspx?coll=84d174c2-d74f-493d-92ae-c3f45c0ee091',
            'http://see.stanford.edu/see/courseinfo.aspx?coll=17005383-19c6-49ed-9497-2ba8bfcfe5f6',
            'http://see.stanford.edu/see/courseinfo.aspx?coll=2db7ced4-39d1-4fdb-90e8-364129597c87',
            'http://see.stanford.edu/see/courseinfo.aspx?coll=523bbab2-dcc1-4b5a-b78f-4c9dc8c7cf7a']
    db = []
    instructors = []
    descriptions = []
    prereqs = []
    topics = []
    for i, url in enumerate(courseurls):
        html = disk_cache_urlopen_read(url)
        soup = BeautifulSoup(html)
        title_unf = soup.find('h1').renderContents()
        title = title_unf.split("<br />")[1]
        tblWrap = soup.find('div', {'id': 'tableWrapper'})
        desc = tblWrap.find('p').renderContents()
        desc = desc.replace('<br />','\n')
        topic_l = desc.find('Topics: ')
        prereq_l = desc.find('Prerequisites: ')
        if topic_l > -1 and topic_l < prereq_l:
            dsc = desc[:topic_l]
        elif prereq_l > -1:
            dsc = desc[:prereq_l]
        else:
            dsc = desc
        print dsc
        prereqs.append('')
        descriptions.append(dsc)
            
        sidelinks = soup.find('div', {'id': 'contentBoxWrapper2'}).findAll('a')
        instructor_pos = html.find('Instructor:')
        instructor = html[instructor_pos + 11:]
        instructor = instructor[:instructor.find('<')]
        insp = instructor.split(', ')
        instructor = insp[1] + insp[0]
        instructors.append(instructor)
        for link in sidelinks:
            if not re.search('Lectur', link.renderContents()):
                continue
            href_filter = filter(lambda (x,y): x == 'href', link.attrs)
            if not href_filter:
                print 'error'
                continue
            side_html = disk_cache_urlopen_read(href_filter[0][1])
            side_soup = BeautifulSoup(side_html)
            if re.search('Lectures', link.renderContents()):
                lectures = []
                lectures_url = href_filter[0][1]
                #p = re.compile('Course Meetings: (\d+)').match(side_html)
                #course_meetings = int(p.group(1))
                for row in side_soup.findAll('tr'):
                    if row.findAll('th'):
                        jsurl = filter(lambda (x,y): x=='href', row.find('a').attrs)[0][1]
                        url = jsurl[23:-3]
                        # url is saved with description on the next row
                    else:
                        main_url = url
                        lis = row.findAll('li')
                        desc = lis[0].renderContents()[25:]
                        trans_html, trans_pdf = lis[1].findAll('a')
                        links = row.find('center')
                        link_dict = {'HTML Transcript': trans_html['href'], 'PDF Transcript': trans_pdf['href'], 'SEE player': main_url}
                        for a in links.findAll('a'):
                            link_url = a['href']
                            print link_url
                            link_url_cr = link_url.find('\r')
                            if link_url_cr == -1:
                                link_dict[a.next] = link_url
                            else:
                                link_dict[a.next] = link_url[:link_url_cr]
                        out_dict = {'description': desc, 'links': link_dict}
                        lectures.append(out_dict)
        db.append(lectures)
    return courses, instructors, db, courseurls, descriptions, prereqs

## Youtube

import gdata.youtube.service
import re

srv = gdata.youtube.service.YouTubeService()

def youtube_playlist_to_data(playlist_url):
    playlist_id = playlist_extract_id(playlist_url)
    feed = srv.GetYouTubePlaylistVideoFeed(playlist_id=playlist_id)
    title = feed.title.text
    subtitle = feed.subtitle.text
    if not subtitle:
        subtitle = ' ' # temp hack
    for i, entry in enumerate(feed.entry):
        title = entry.title.text    
        if entry.location:
            location = entry.location.text
        content = entry.content.text
        link = entry.link[0].href
    return {'title': title, 'description': subtitle, 'links': feed.entry, 'url':playlist_url,}



def youtube_playlist_to_course(playlist_url):
    playlist_id = playlist_extract_id(playlist_url)
    feed = srv.GetYouTubePlaylistVideoFeed(playlist_id=playlist_id)
    title = feed.title.text
    if feed.subtitle:
        subtitle = feed.subtitle.text
    else:
        subtitle = ' '
    from classes.models import CourseInfo, Session, CourseInfoSession, SessionLink
    ci = CourseInfo(title=title, description=subtitle)
    ci.url = 'http://www.youtube.com/view_play_list?p=' + playlist_id
    ci.save()
    for i, entry in enumerate(feed.entry):
        title = entry.title.text    
        if entry.location:
            location = entry.location.text
        if entry.content:
            content = entry.content.text
        else:
            content = ' '
        link = entry.link[0].href
        session = Session(title=title, description=content, video_url=link)
        session.save()
        cis = CourseInfoSession(course_info=ci, session=session, session_number=i+1)
        cis.save()
        #cisv = SessionLink(course_info_session=session, url=link)
        #cisv.save()
    return ci

def youtube_user_playlist_extractor(username):
    playlists = []
    si = 1 
    while len(playlists) == (si-1):
        xml_uri = 'http://gdata.youtube.com/feeds/api/users/%s/playlists/?max-results=50&start-index=%d' % (username, si)
        xml_data = urllib.urlopen(xml_uri).read()
        dom_parser = xml.dom.minidom.parseString(xml_data).firstChild
        for node in dom_parser.childNodes:
            if node.nodeName == 'entry':
                for cn in node.childNodes:
                    if cn.nodeName == 'yt:playlistId':
                        playlists.append(cn.firstChild.nodeValue)
        si += 50
    return playlists


#def youtube_url_to_session
#def handle
def playlist_extract_id(playlist_url):
    # /p=([aA_]+)[\&|$]/
    m = re.search('p=([a-zA-Z0-9]+)', playlist_url)
    try:
        return m.group(1)
    except:
        return playlist_url

#def 

def fetch_youtube_video(video_url):
    id_start = video_url.find('v=') + 2
    if id_start > 0: 
        id_end = video_url[id_start:].find('&') + id_start
        print video_url[id_start:]
        if id_end < id_start:
            id_end = len(video_url)
        print id_start, id_end, video_url[id_start:id_end]
        vid = srv.GetYouTubeVideoEntry(video_id=video_url[id_start:id_end])
        print vid.title.text
        return {'title': vid.title.text, 'description': vid.content.text}
    else:
        vid = srv.GetYouTubeVideoEntry(video_id=video_url)
        return {'title': vid.title.text, 'description': vid.content.text}


