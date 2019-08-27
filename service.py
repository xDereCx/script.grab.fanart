import xbmc
import xbmcgui
import thread
import json
import random
import resources.lib.utils as utils

class GrabFanartService:
    current_mode = 'random'
    
    monitor = None #xbmc monitor object
    WINDOW = None #object representing the home window
    xbmc_tv = None #array for tv shows
    xbmc_movies = None #array for movie files
    xbmc_music = None #array for music artist

    tv_index = 0
    movie_index = 0
    music_index = 0
    
    def __init__(self):
        utils.log("Grab Fanart Service Started")
        
        #setup the window and file list
        self.WINDOW = xbmcgui.Window(10000)
        self.xbmc_tv = list()
        self.xbmc_movies = list()
        self.xbmc_music = list()

        #let XBMC know the script is not ready yet
        self.WINDOW.setProperty('script.grab.fanart.Ready',"")

        #start populating the arrays right away - don't use threads here
        if(utils.getSetting('mode') == '' or utils.getSetting('mode') == 'random'):
            self.grabRandom()
        else:
            self.grabRecent()
        
        #start the monitor
        self.monitor = UpdateMonitor(after_scan=self.updateMedia)
        
    def run(self):
        
        #keep this thread alive
        while(True):

            aVideo = None
            globalArt = None
            
            if(len(self.xbmc_movies) > 0):

                try:

                    self.WINDOW.setProperty('script.grab.fanart.Movie.Title',self.xbmc_movies[self.movie_index].title)
                    self.WINDOW.setProperty('script.grab.fanart.Movie.FanArt',self.xbmc_movies[self.movie_index].fan_art)
                    self.WINDOW.setProperty('script.grab.fanart.Movie.Poster',self.xbmc_movies[self.movie_index].poster)
                    self.WINDOW.setProperty('script.grab.fanart.Movie.Logo',self.xbmc_movies[self.movie_index].logo)
                    self.WINDOW.setProperty('script.grab.fanart.Movie.Plot',self.xbmc_movies[self.movie_index].plot)
                    self.WINDOW.setProperty('script.grab.fanart.Movie.Path',self.xbmc_movies[self.movie_index].path)
                
                    aVideo = self.xbmc_movies[self.movie_index]
                    globalArt = aVideo
                    
                except IndexError:
                    pass
                
                self.movie_index = self.movie_index + 1
                if(self.movie_index >= len(self.xbmc_movies)):
                    self.movie_index = 0
                
            if(len(self.xbmc_tv) > 0):

                try:
                    
                    self.WINDOW.setProperty('script.grab.fanart.TV.Title',self.xbmc_tv[self.tv_index].title)
                    self.WINDOW.setProperty('script.grab.fanart.TV.FanArt',self.xbmc_tv[self.tv_index].fan_art)
                    self.WINDOW.setProperty('script.grab.fanart.TV.Poster',self.xbmc_tv[self.tv_index].poster)
                    self.WINDOW.setProperty('script.grab.fanart.TV.Logo',self.xbmc_tv[self.tv_index].logo)
                    self.WINDOW.setProperty('script.grab.fanart.TV.Plot',self.xbmc_tv[self.tv_index].plot)
                    self.WINDOW.setProperty('script.grab.fanart.TV.Path',self.xbmc_tv[self.tv_index].path)

                    #this will only have a value when "recent" is the type
                    self.WINDOW.setProperty('script.grab.fanart.TV.Season',str(self.xbmc_tv[self.tv_index].season))
                    self.WINDOW.setProperty('script.grab.fanart.TV.Episode',str(self.xbmc_tv[self.tv_index].episode))
                    self.WINDOW.setProperty('script.grab.fanart.TV.Thumb',self.xbmc_tv[self.tv_index].thumb)
                

                    #use a tv show if blank or randomly selected is = 9 (10% chance)
                    if(aVideo == None or self.randomNum(10) == 9):
                        aVideo = self.xbmc_tv[self.tv_index]

                    #30% change of TV show on global
                    if(globalArt == None or self.randomNum(3) == 2):
                        globalArt = self.xbmc_tv[self.tv_index]
                except IndexError:
                    pass
                    
                self.tv_index = self.tv_index + 1
                if(self.tv_index >= len(self.xbmc_tv)):
                    self.tv_index = 0

            if(aVideo != None):
                
                self.WINDOW.setProperty('script.grab.fanart.Video.Title',aVideo.title)
                self.WINDOW.setProperty('script.grab.fanart.Video.FanArt',aVideo.fan_art)
                self.WINDOW.setProperty('script.grab.fanart.Video.Poster',aVideo.poster)
                self.WINDOW.setProperty('script.grab.fanart.Video.Logo',aVideo.logo)
                self.WINDOW.setProperty('script.grab.fanart.Video.Plot',aVideo.plot)
                self.WINDOW.setProperty('script.grab.fanart.Video.Path',aVideo.path)

            if(len(self.xbmc_music) > 0):

                try:
                    
                    self.WINDOW.setProperty('script.grab.fanart.Music.Artist',self.xbmc_music[self.music_index].title)
                    self.WINDOW.setProperty('script.grab.fanart.Music.FanArt',self.xbmc_music[self.music_index].fan_art)
                    self.WINDOW.setProperty('script.grab.fanart.Music.Description',self.xbmc_music[self.music_index].plot)

                    #30% of music fanart on global
                    if(globalArt == None or self.randomNum(3) == 2):
                        globalArt = self.xbmc_music[self.music_index]
                except IndexError:
                    pass

                self.music_index = self.music_index + 1
                if(self.music_index >= len(self.xbmc_music)):
                    self.music_index = 0

            if(globalArt != None):
                
                self.WINDOW.setProperty('script.grab.fanart.Global.Title',globalArt.title)
                self.WINDOW.setProperty('script.grab.fanart.Global.FanArt',globalArt.fan_art)
                self.WINDOW.setProperty('script.grab.fanart.Global.Logo',globalArt.logo)

            #let xbmc know the images are ready
            self.WINDOW.setProperty('script.grab.fanart.Ready',"true")
            
            #check if mode has changed
            if(utils.getSetting('mode') != '' and utils.getSetting('mode') != self.current_mode):
                self.updateMedia()
            
            refresh_interval = 10
            if(utils.getSetting('refresh') != ''):
                refresh_interval = float(utils.getSetting("refresh"))

            if(self.monitor.waitForAbort(refresh_interval)):
                break;

    def updateMedia(self):
        if(utils.getSetting('mode') == '' or utils.getSetting('mode') == 'random'):
            thread.start_new_thread(self.grabRandom, ())
        else:
            thread.start_new_thread(self.grabRecent, ())

    def grabRandom(self):
        utils.log("media type is: random")
        self.current_mode = 'random'
        
        media_array = self.getJSON('VideoLibrary.GetMovies','{"properties":["title","art","year","file","plot"]}')
            
        if(media_array != None and 'movies' in media_array):
            self.xbmc_movies = list()    #reset the list
            self.movie_index = 0
            
            for aMovie in media_array['movies']:
                newMedia = XbmcMedia()
                newMedia.title = aMovie['title']
                newMedia.plot = aMovie['plot']
                newMedia.path = aMovie['file']
                
                if('fanart' in aMovie['art']):
                    newMedia.fan_art = aMovie['art']['fanart']

                if('poster' in aMovie['art']):
                    newMedia.poster = aMovie['art']['poster']

                if('clearlogo' in aMovie['art']):
                    newMedia.logo = aMovie['art']['clearlogo']

                if(newMedia.verify()):
                    self.xbmc_movies.append(newMedia)
            random.shuffle(self.xbmc_movies)
            
        utils.log("found " + str(len(self.xbmc_movies)) + " movies files")
        
        media_array = self.getJSON('VideoLibrary.GetTVShows','{"properties":["title","art","year","file","plot"]}')

        if(media_array != None and 'tvshows' in media_array):
            self.xbmc_tv = list()
            self.tv_index = 0
             
            for aShow in media_array['tvshows']:
                newMedia = XbmcMedia()
                newMedia.title = aShow['title']
                newMedia.plot = aShow['plot']
                newMedia.path = aShow['file']
                
                if('fanart' in aShow['art']):
                    newMedia.fan_art = aShow['art']['fanart']

                if('poster' in aShow['art']):
                    newMedia.poster = aShow['art']['poster']

                if('clearlogo' in aShow['art']):
                    newMedia.logo = aShow['art']['clearlogo']

                if(newMedia.verify()):
                    self.xbmc_tv.append(newMedia)

            random.shuffle(self.xbmc_tv)                    

        utils.log("found " + str(len(self.xbmc_tv)) + " tv files")
        
        media_array = self.getJSON('AudioLibrary.GetArtists','{ "properties":["fanart","description"] }')

        if(media_array != None and 'artists' in media_array):
            self.xbmc_music = list()
            self.music_index = 0
            
            for aArtist in media_array["artists"]:
                newMedia = XbmcMedia()
                newMedia.title = aArtist['artist']
                newMedia.fan_art = aArtist['fanart']
                newMedia.poster = aArtist['fanart']
                newMedia.plot = aArtist['description']

                if(newMedia.verify()):
                    self.xbmc_music.append(newMedia)

            random.shuffle(self.xbmc_music)
            
        utils.log("found " + str(len(self.xbmc_music)) + " music files")
        
    def grabRecent(self):
        utils.log("media type is: recent")
        self.current_mode = 'recent'
        
        media_array = self.getJSON('VideoLibrary.GetRecentlyAddedMovies','{"properties":["title","art","year","file","plot"], "limits": {"end":10} }')
                 
        if(media_array != None and 'movies' in media_array):
            self.xbmc_movies = list()    #reset the list
            self.movie_index = 0
            
            for aMovie in media_array['movies']:
                newMedia = XbmcMedia()
                newMedia.title = aMovie['title']
                newMedia.plot = aMovie['plot']
                newMedia.path = aMovie['file']
                
                if('fanart' in aMovie['art']):
                    newMedia.fan_art = aMovie['art']['fanart']

                if('poster' in aMovie['art']):
                    newMedia.poster = aMovie['art']['poster']

                if('clearlogo' in aMovie['art']):
                    newMedia.logo = aMovie['art']['clearlogo']

                if(newMedia.verify()):    
                    self.xbmc_movies.append(newMedia)
                    
            random.shuffle(self.xbmc_movies)

        utils.log("found " + str(len(self.xbmc_movies)) + " movie files")
        
        media_array = self.getJSON('VideoLibrary.GetRecentlyAddedEpisodes','{"properties":["showtitle","art","file","plot","season","episode"], "limits": {"end":10} }')

        if(media_array != None and 'episodes' in media_array):
            self.xbmc_tv = list()
            self.tv_index = 0
            
            for aShow in media_array['episodes']:
                newMedia = XbmcMedia()
                newMedia.title = aShow['showtitle']
                newMedia.plot = aShow['plot']
                newMedia.season = aShow['season']
                newMedia.episode = aShow['episode']
                newMedia.path = aMovie['file']
                
                if('tvshow.fanart' in aShow['art']):
                    newMedia.fan_art = aShow['art']['tvshow.fanart']

                if('tvshow.poster' in aShow['art']):
                    newMedia.poster = aShow['art']['tvshow.poster']

                if('tvshow.clearlogo' in aShow['art']):
                    newMedia.logo = aShow['art']['tvshow.clearlogo']

                if('thumb' in aShow['art']):
                    newMedia.thumb = aShow['art']['thumb']

                if(newMedia.verify()):
                    self.xbmc_tv.append(newMedia)

            random.shuffle(self.xbmc_tv)

        utils.log("found " + str(len(self.xbmc_tv)) + " tv files")
        
        media_array = self.getJSON('AudioLibrary.GetRecentlyAddedAlbums','{ "properties":["artist","fanart"], "limits": {"end":10} }')

        if(media_array != None and 'albums' in media_array):
            self.xbmc_music = list()
            self.music_index = 0
            
            for aArtist in media_array["albums"]:
                newMedia = XbmcMedia()
                newMedia.title = ",".join(aArtist['artist'])
                newMedia.fan_art = aArtist['fanart']
                newMedia.poster = aArtist['fanart']
                
                if(newMedia.verify()):
                    self.xbmc_music.append(newMedia)

            random.shuffle(self.xbmc_music)

        utils.log("found " + str(len(self.xbmc_music)) + " music files")
        
    def getJSON(self,method,params):
        json_response = xbmc.executeJSONRPC('{ "jsonrpc" : "2.0" , "method" : "' + method + '" , "params" : ' + params + ' , "id":1 }')

        jsonobject = json.loads(json_response.decode('utf-8','replace'))
       
        if('result' in jsonobject):
            return jsonobject['result']
        else:
            utils.log("no result " + str(jsonobject))
            return None

    def randomNum(self,size):
        #return random number from 0 to x-1
        return random.randint(0,size -1)


class XbmcMedia:
    title = ''
    fan_art = ''
    poster = ''
    logo = ''
    plot = ''
    season = ''
    episode = ''
    thumb = ''
    path = ''
    
    def verify(self):
        result = True

        if(self.title == '' or self.fan_art == '' or self.poster == ''):
            result = False

        return result

class UpdateMonitor(xbmc.Monitor):
    #function to run after DB operations
    after_scan = None
     
    def __init__(self,*args,**kwargs):
        xbmc.Monitor.__init__(self)
        self.after_scan = kwargs['after_scan']

    def onScanFinished(self,library):
        self.after_scan()

    def onCleanFinished(self, library):
        self.after_scan()
        
GrabFanartService().run()
