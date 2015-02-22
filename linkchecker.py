#!/usr/bin/env python
import pbs as sh
import os
import commands
import sys
import urllib2

class linkchecker(object):
    def __init__(self):
        self.urlhostnames = {}
        self.tracing = {}
        self.printdebug = True 

    def debug(self, text):
        if self.printdebug:
            print "DEBUG:", text

    def hostexist(self, url):
        hostname = self.hostfromurl(url)
        self.debug("Hostname: " + hostname)
        checkhost = ""
        try:
            checkhost = str(sh.host(hostname))
                    except Exception as ex:
            print "no host", ex
        self.debug("Reply from host command: " + checkhost)
        if "not found" in checkhost or checkhost == "":
            return False
        else:
            return True

    def isurl(self, url):
        if url in self.urlhostnames:
            return True
        else:
            if "." in url:
                urlparts = url.split("/")
                if (urlparts[0] == "http:" or urlparts[0] == "https:"):
                    return True
                else:
                    return False

    def urlexist(self, url):
        check = urllib2.urlopen(headrequest(url))
        if check.getcode() == 200:
            return True
        else:
            print "Meldung vom Webserver:", check.getcode()
            return False

    def hostfromurl(self, url):
        urlparts = url.split("/")
        if url in self.urlhostnames:
            return self.urlhostnames[url]
        else:
            if self.isurl(url):
                host = urlparts[2]
                self.urlhostnames[url] = host
                return host
            else:
                print "Kein valider URL erkannt!"

    def urlspeed(self, url):
        hostname = self.hostfromurl(url)
        pingresult = ""
        try:
            pingresult = sh.ping("-c1", hostname)
        except Exception as ex:
            self.debug(ex)
        pingresult = pingresult.split("\n")
        resultlen = len(pingresult)
        for pingline in pingresult:
            if "time=" in pingline:
                pinglineparts = pingline.split(" ")
                measure = pinglineparts.pop()
                pingtime = pinglineparts.pop().replace("time=", "")
                return float(pingtime)

    def hostip(self, url):
        hostname = self.hostfromurl(url)
        hostanswer = sh.host(hostname)  
        hostip = ""
        if "not found" in hostanswer:
            hostip = "nf"
        else:
            self.debug(hostanswer)
            hostanswer = hostanswer.split("\n")
            hostanswer = hostanswer[0].split(" ")
            hostip = hostanswer[3]
        return hostname, hostip

    def trace(self, url):
        hostname = self.hostfromurl(url)
        if url in self.tracing:
            return hostname, self.tracing[url]
        else:
            hosttrace = sh.traceroute(hostname)
            hosttrace = hosttrace.split("\n")  
            hops = len(hosttrace) - 2
            self.tracing[url] = hops 
            return hostname, hops

    def checkall(self, url, savefile=""):
        if self.hostexist(url):
            if savefile == "": 
                if self.urlexist(url):
                    print "Webadresse", url, "ist vorhanden."
                else:
                    print "Huch? Wo ist denn", url, "abgeblieben?"
                responsetime = "Antwortzeit von " + self.hostfromurl(url) + ": " + str(self.urlspeed(url))
                print responsetime
                hostname, hostip = self.hostip(url)
                if hostip == "nf":
                    print "Diesen Host gibt es nicht."
                else:
                    print "Die IP zu " + hostname + " lautet: '" + hostip.strip() + "'."
                # hostname, hops = self.trace(url)
                # print "Von hier aus sind es", hops, "Hops bis", hostname
                return True
            else:
                outfile = open(savefile, "a")
                if self.urlexist(url):
                    outtext = "Webadresse " + url + " ist vorhanden.\n"
                    outfile.write(outtext)
                    else:
                    outtext = "Huch? Wo ist denn " + url + " abgeblieben?\n"
                    outfile.write(outtext)
                responsetime = "Antwortzeit von " + self.hostfromurl(url) + ": " + str(self.urlspeed(url))
                outfile.write(responsetime)
                hostname, hostip = self.hostip(url)
                if hostip == "nf":
                    outtext = "Diesen Host gibt es nicht.\n"
                else:
                    outtext = "Die IP zu " + hostname + " lautet: '" + hostip.strip() + "'.\n"
                outfile.write(outtext)
                # hostname, hops = self.trace(url)
                # outtext = "Von hier aus sind es " + str(hops) + " Hops bis " + hostname + ".\n\n"
                # outfile.write(outtext)
                outfile.close()
                return True
        else:
            pass

class headrequest(urllib2.Request):
    def get_method(self):
        return "HEAD"


myLinkchecker = linkchecker()
url = ""
savefile = ""  
sourcefile = ""
do = False

argcount = 0
for pars in sys.argv:
    if pars[0] == "-":
        if pars == "-u":
            url = sys.argv[argcount+1]
        elif pars == "-f":
            savefile = sys.argv[argcount+1]
        elif pars == "-l":
            sourcefile = sys.argv[argcount+1]
        elif pars == "-h":
            print "-f Filename: filename for saving"
            print "-h: this help"
            print "-l Filename: use list of URLs in this file for checking"
            print "-u URL: check this URL"
    argcount += 1    

if savefile != "":
    if os.path.isfile(savefile):
        os.remove(savefile)

if sourcefile == "":
    if url != "" and savefile != "":
        do = myLinkchecker.checkall(url, savefile)
    elif url != "" and savefile == "":
        do = myLinkchecker.checkall(url)  
    elif url == "":
        print "No URL given. Nothing to do."
else:
    sf = open(sourcefile)
    urllist = sf.read()  
    sf.close()
    urllist = urllist.split("\n")
    for url in urllist:
        if myLinkchecker.isurl(url):
            if savefile == "":
                myLinkchecker.checkall(url)
            else:
                myLinkchecker.checkall(url, savefile)
        else:
            outtext = "'" + url + "' does not exist!"
            if savefile == "":
                print outtext 
            else:
                pass
    
if do:
    print "Done."
