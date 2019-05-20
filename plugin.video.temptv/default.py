﻿# -*- coding: UTF-8 -*-
# Based on Ultimate IPTV by Whitecream.

import re, os, sys, urllib, urllib2, requests, socket, gzip
import xbmc, xbmcaddon, xbmcgui, xbmcplugin

Addon = xbmcaddon.Addon
AddonInfo = Addon().getAddonInfo
AddonID = AddonInfo('id')
AddonIcon = AddonInfo('icon')
AddonFanArt = AddonInfo('fanart')
addon = xbmcaddon.Addon(id=AddonID)
profileDir = addon.getAddonInfo('profile')
profileDir = xbmc.translatePath(profileDir).decode("utf-8")
if not os.path.exists(profileDir):
    os.makedirs(profileDir)
cookiePath = os.path.join(profileDir, 'cookies.lwp')
addon_handle = int(sys.argv[1])
socket.setdefaulttimeout(10)
urlopen = urllib2.urlopen
Request = urllib2.Request
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
headers = {'User-Agent': USER_AGENT, 'Accept': '*/*', 'Connection': 'keep-alive'}
adult = addon.getSetting('Show_Adult')

import userlists
MenuList = 'https://textuploader.com/1dsk7/raw'
ChannelzList = 'https://textuploader.com/1d90b/raw'
DayPro = 'https://textuploader.com/1ds64/raw'


def MAIN():
    addDir('English', userlists.english, 2, AddonIcon)
    addDir('27/7', userlists.hour24, 2, AddonIcon)
    addDir('Kids', userlists.kids, 2, AddonIcon)
    addDir('Sports', userlists.sports, 2, AddonIcon)
    addDir('News', userlists.news, 2, AddonIcon)
    addDir('Music', userlists.music, 2, AddonIcon)
    addDir('UK', userlists.List2, 2, AddonIcon)
    if adult == 'true':
        addDir('Lust', userlists.adult, 2, AddonIcon)
    #addDir('MORELISTS', '', 5, AddonIcon)
    addDir('[B] Settings [/B]', 'url', 4, AddonIcon, Folder=False)
    addDir('Refresh', '', 6, AddonIcon, Folder=False)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def laguages():
    addDir('Afghanistan', ChannelzList, 1, AddonIcon)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def MORELISTS():
    addDir('MenuList', MenuList, 2, AddonIcon)
    addDir('ChannelzList', ChannelzList, 1, AddonIcon)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def REFRESH():
    xbmc.executebuiltin('Container.Refresh')


def addDir(name, url, mode, iconimage, Folder=True):
    if url.startswith('plugin'):
        u = url
    else:
        u = (sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name))
    ok = True
    status = ""
    try:
        siteup = requests.get(url, timeout=1)
        if siteup.status_code == 200:
            status = " [COLOR green]online[/COLOR]"
        elif siteup.status_code == 404:
            status = " [COLOR red]offline[/COLOR]"
    except:
        status = " [COLOR red]offline[/COLOR]"
    if mode == 4 or mode == 5 or mode == 6:
        status = ""
    liz = xbmcgui.ListItem(name+status, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setArt({'thumb': iconimage, 'icon': iconimage})
    liz.setArt({'fanart': AddonFanArt})
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz, isFolder=Folder)
    return ok


def addPlayLink(name, url, mode, iconimage):
    u = (sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name))
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setArt({'thumb': iconimage, 'icon': iconimage})
    # liz.setProperty('IsPlayable', 'true')
    liz.setInfo(type="Video", infoLabels={"Title": name})
    video_streaminfo = {'codec': 'h264'}
    liz.addStreamInfo('video', video_streaminfo)
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz, isFolder=False)
    return ok


def getHtml(url, referer=None, hdr=None, data=None):
    if not hdr:
        req = Request(url, data, headers)
    else:
        req = Request(url, data, hdr)
    if referer:
        req.add_header('Referer', referer)
    if data:
        req.add_header('Content-Length', len(data))
    response = urlopen(req, timeout=20)
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
        f.close()
    else:
        data = response.read()    
    response.close()
    return data


def parsem3u(html):
    match = re.compile('#.+? tvg-logo="(.+?)" .+,(.+?)\n(.+?)\n').findall(html)
    count = 0
    for channelicon, name, url in match:
        url = url.replace('\r', '')
        status = ""
        # try:
        #    siteup = urllib.urlopen(url).getcode()
        #    status = " [COLOR red]offline[/COLOR]" if siteup != 200 else " [COLOR green]online[/COLOR]"
        # except: status = " [COLOR red]offline[/COLOR]"
        addPlayLink(name+status, url, 3, channelicon)
        count += 1
    return count


def PAGE(url):
    html = getHtml(url)
    iptvlinks = re.compile("=(.+?)=(.+?)=", re.DOTALL | re.IGNORECASE).findall(html)
    for name, link in iptvlinks:
        status = ""
        # try:
            # siteup = urllib.urlopen(link).getcode()
            # status = " [COLOR red]offline[/COLOR]" if siteup != 200 else " [COLOR green]online[/COLOR]"
        # except: status = " [COLOR red]offline[/COLOR]"
        addDir(name+status, link, 2, AddonIcon)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def LIST(url):
    try:
        m3u = getHtml(url)
        parsem3u(m3u)
    except:
        addDir('Nothing found', '', '', '', Folder=False)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def PLAY(url, title):
    playmode = int(addon.getSetting('playmode'))
    iconimage = xbmc.getInfoImage("ListItem.Thumb")
    if playmode == 0:
        stype = ''
        if '.ts' in url:
            stype = 'TSDOWNLOADER'
        elif '.m3u' in url:
            stype = 'HLSRETRY'
        if stype:
            from F4mProxy import f4mProxyHelper
            f4mp = f4mProxyHelper()
            xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)
            f4mp.playF4mLink(
                url, name, proxy=None, use_proxy_for_chunks=False, maxbitrate=0, simpleDownloader=False,
                auth=None, streamtype=stype,setResolved=False, swf=None, callbackpath="", callbackparam="",
                iconImage=iconimage)
            return
    listitem = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    listitem.setInfo('video', {'Title': name})
    listitem.setProperty("IsPlayable", "true")
    xbmc.Player().play(url, listitem)


def OPENSETTINGS():
    addon.openSettings()
    xbmc.executebuiltin('Container.Refresh')


def getParams():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if params[len(params) - 1] == '/':
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


params = getParams()
url = None
name = None
mode = None
img = None
try:
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    name = urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass
try:
    img = urllib.unquote_plus(params["img"])
except:
    pass


if mode is None or mode == 0:
    MAIN()
elif mode == 1:
    PAGE(url)
elif mode == 2:
    LIST(url)
elif mode == 3:
    PLAY(url, name)
elif mode == 4:
    OPENSETTINGS()
elif mode == 5:
    MORELISTS()
elif mode == 6:
    REFRESH()