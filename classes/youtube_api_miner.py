import gdata.youtube.service
import re

srv = gdata.youtube.service.YouTubeService()

def get_youtube_playlist(playlist_url):
    playlist_id = playlist_extract_id(playlist_url)
    feed = srv.GetYouTubePlaylistVideoFeed(playlist_id=playlist_id)
    title = feed.title.text
    subtitle = feed.subtitle.text
    #ci = CourseInfo(title=title, description=subtitle)
    #ci.save()
    for i, entry in enumerate(feed.entry):
        title = entry.title.text    
        #link = entry.link # list of links
        if entry.location:
            location = entry.location.text
        content = entry.content.text
        link = entry.link[0].href
        #cis = CourseInfoSession(title=title, session_number=i+1, conent)
        #cis.save()
        #cisv = CourseInfoSessionVideo(course_info_session=url, url=link)
        #cisv.save()

        
    
def playlist_extract_id(playlist_url):
    # /p=([aA_]+)[\&|$]/
    m = re.search('p=([a-zA-Z0-9]+)', playlist_url)
    try:
        return m.group(1)
    except:
        pass



