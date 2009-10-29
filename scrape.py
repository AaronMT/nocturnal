#!/usr/bin/python
# output directory
output_dir = "/tmp/"

# mod_autoindex generated HTML containing builds:
index_url = "http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-trunk/"

import os
import urllib2
import simplejson as json
from sgmllib import SGMLParser

class BuildDisplay():
    def __init__(self, suffix, extension, name, css_class):
        self.suffix = suffix
        self.extension = extension
        self.name = name
        self.css_class = css_class

files_wanted = [
#               (suffix,          extension, name,                 css_class)
    BuildDisplay(".win32",        "zip",     "Windows",            "windows zip"),
    BuildDisplay(".mac",          "dmg",     "Mac",                "mac dmg"),
    BuildDisplay(".linux-i686",   "tar.bz2", "Linux Intel",        "linux bz2"),
    BuildDisplay(".linux-x86_64", "tar.bz2", "Linux 64-bit Intel", "linux bz2 x64")
]

wanted_keys = tuple([f.suffix + "." + f.extension for f in files_wanted])

def build(url, files_wanted):
    d = {}
    d['url'] = index_url + url
    d['date'] = ""
    d['size'] = ""
    for f in files_wanted:
        if d['url'].endswith(f.suffix + "." + f.extension):
            d['css_class'] = f.css_class
            d['name'] = f.name
            d['extension'] = f.extension
            d['suffix'] = f.suffix
            return d

class URLLister(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.builds = []
        self.textData = ""
            
    def start_td(self, attrs):
        self.textData = ""

    def end_td(self):
        text = self.textData.strip()

        if (self.textData.endswith(wanted_keys)):
            self.builds.append(build(text, files_wanted))
            return

        if (len(self.builds) > 0):
            if (self.builds[-1]['date'] == ""):
                self.builds[-1]['date'] = text.split()[0]
            elif (self.builds[-1]['size'] == ""):
                self.builds[-1]['size'] = text

    def handle_data(self, text):
        self.textData += text

def buildJSON(builds):
    output = []
    for f in files_wanted:
        for build in builds:
            if build['url'].endswith(f.suffix + "." + f.extension):
                output.append(build)
    return json.dumps(output, indent=0)

def buildHTML(builds):
    header = """<!DOCTYPE html>
<html>
      <head>
        <title>Firefox Nightly Builds</title>
        <style>
          li { margin-bottom: 1em; }
        </style>
      </head>
      <body>
        <h1>Firefox Nightly Builds</h1>
        <ul>\n"""
    
    footer = """
        </ul>
        
        There's <a href="http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-trunk">more stuff</a> if you don't see what you're looking for.

      </body>
</html>"""
    
    middle = ""
    for f in files_wanted:
        for build in builds:
            if build['url'].endswith(f.suffix + "." + f.extension):
                middle += '\n<li class="' + build['css_class'] + '">\n'
                middle += '<a href="' + build['url'] + '">'
                middle += build['name']
                middle += '</a>'
                middle += ' ' + build['size'] + 'B'
                middle += '  ' + build['extension']
                middle += '<br>\n'
                middle += '<small>Built on ' + build['date'] + '</small>\n'

    return header + middle + footer

def writeOutput(filename, text):
    f = open(os.path.join(output_dir, filename), 'w')
    f.write(text)
    f.close()

def main():
    f = urllib2.urlopen(index_url)
    parser = URLLister()
    parser.feed(f.read())
    f.close()
    parser.close()

    writeOutput("index.html", buildHTML(parser.builds))
    writeOutput("index.json", buildJSON(parser.builds))

if __name__ == '__main__':
    main()
