from kodi_six import xbmc, xbmcaddon, xbmcgui

__addon_id__= 'script.grab.fanart'
__Addon = xbmcaddon.Addon(__addon_id__)

def data_dir():
    return __Addon.getAddonInfo('profile')

def addon_dir():
    return __Addon.getAddonInfo('path')

def log(message,loglevel=xbmc.LOGDEBUG):
    xbmc.log(__addon_id__ + "-" + __Addon.getAddonInfo('version') +  ": " + message,level=loglevel)

def showNotification(message):
    xbmcgui.Dialog().notification(getString(30010),message,time=4000,icon=xbmc.translatePath(__Addon.getAddonInfo('path') + "/resources/media/icon.png"))

def getSetting(name):
    return __Addon.getSetting(name)

def setSetting(name,value):
    __Addon.setSetting(name,value)
    
def getString(string_id):
    return __Addon.getLocalizedString(string_id)
