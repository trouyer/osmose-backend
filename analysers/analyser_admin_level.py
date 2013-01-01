#! /usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Etienne Chové <chove@crans.org> 2009                       ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

from analyser_sax import Analyser_Sax

from modules import OsmoseLog

###########################################################################

class DataHandler:
    def __init__(self):
        self.ways = {}
        self.rels = {}
    def WayCreate(self, data):
        if data[u"tag"].get(u"boundary", None) <> u"administrative":
            return
        self.ways[data["id"]] = data
    def RelationCreate(self, data):
        if data[u"tag"].get(u"boundary", None) <> u"administrative":
            return
        self.rels[data["id"]] = data

###########################################################################

class Analyser_Admin_Level(Analyser_Sax):

    def __init__(self, config, logger = OsmoseLog.logger()):
        Analyser_Sax.__init__(self, config, logger)

    ################################################################################

    def _load_plugins(self):
        self._Err = {}
        self._Err[1] = { "item": 6050,
                         "level": 1,
                         "desc": { "en": "Wrong administrative level",
                                   "fr": "Mauvais niveau administratif"}
                       }

    ################################################################################

    def _run_analyse(self):

        o = DataHandler()

        ## get relations
        self.logger.log("get ways data")
        self.parser.CopyWayTo(o)
        wdta = o.ways

        ## get ways id
        self.logger.log("get relations data")
        self.parser.CopyRelationTo(o)
        rdta = o.rels

        del o

        ## find admin level
        way_to_level = {}
        rel_to_level = {}
        for wid in wdta:
            way_to_level[wid] = 99
        for rid in rdta:
            rel_to_level[rid] = 99

        self.logger.log("check admin level - relations")
        for rid in rdta:

            try:
                level = int(rdta[rid]["tag"]["admin_level"])
            except:
                # find node in relation
                wid = [x["ref"] for x in rdta[rid]["member"] if x["type"]=="way"]
                if not wid:
                    continue
                wid = wid[0]
                wta = self.WayGet(wid)
                if not wta["nd"]:
                    continue
                nid = wta["nd"][0]
                nta = self.NodeGet(nid)
                if not nta:
                    continue
                # add error to xml
                self._outxml.startElement("error", {"class":"1"})
                self._outxml.Element("text", {"lang":"fr", "value":"admin_level illisible"})
                self._outxml.Element("text", {"lang":"en", "value":"admin_level unreadable"})
                self._outxml.RelationCreate(rdta[rid])
                self._outxml.Element("location", {"lat":str(nta["lat"]),"lon":str(nta["lon"])})
                self._outxml.endElement("error")
                continue

            for m in rdta[rid][u"member"]:
                if m[u"type"] == u"way":
                    if m[u"ref"] in way_to_level:
                        way_to_level[m[u"ref"]] = min(way_to_level[m[u"ref"]], level)
                if m[u"type"] == u"relation":
                    if m[u"ref"] in rel_to_level:
                        rel_to_level[m[u"ref"]] = min(rel_to_level[m[u"ref"]], level)

        ##
        self.logger.log("check admin level - ways")
        for wid in wdta:

            try:
                level = int(wdta[wid]["tag"]["admin_level"])
            except:
                self._outxml.startElement("error", {"class":"1"})
                self._outxml.Element("text", {"lang":"fr", "value":"admin_level illisible"})
                self._outxml.Element("text", {"lang":"en", "value":"admin_level unreadable"})
                self._outxml.WayCreate(wdta[wid])
                n =  self.NodeGet(wdta[wid]["nd"][0])
                if n:
                    self._outxml.Element("location", {"lat":str(n["lat"]),"lon":str(n["lon"])})
                self._outxml.endElement("error")
                continue

            if way_to_level[wid] not in [99, level]:
                self._outxml.startElement("error", {"class":"1"})
                self._outxml.Element("text", {"lang":"fr", "value":"admin_level devrait être %d"%way_to_level[wid]})
                self._outxml.Element("text", {"lang":"en", "value":"admin_level should be %d"%way_to_level[wid]})
                self._outxml.WayCreate(wdta[wid])
                n = self.NodeGet(wdta[wid]["nd"][0])
                if n:
                    self._outxml.Element("location", {"lat":str(n["lat"]),"lon":str(n["lon"])})
                self._outxml.endElement("error")
                continue

    ################################################################################

    def _close_plugins(self):
        pass
 
    ################################################################################
