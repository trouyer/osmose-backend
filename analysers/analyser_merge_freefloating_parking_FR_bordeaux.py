#!/usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Frédéric Rodrigo 2014                                      ##
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

from .Analyser_Merge import Analyser_Merge, Source, SHP, Load, Mapping, Select, Generate


class Analyser_Merge_FreeFloating_Parking_FR_bm(Analyser_Merge):
    def __init__(self, config, logger = None):
        Analyser_Merge.__init__(self, config, logger)
        self.missing_official = self.def_class(item = 8160, id = 1, level = 3, tags = ['merge', 'parking', 'cycle'],
            title = T_f('{0} free floating parking not integrated', 'BM'))

        self.init(
            'https://opendata.bordeaux-metropole.fr/explore/dataset/st_freefloating_p',
            'Emplacement freefloating Bordeaux Métropole',
            SHP(Source(attribution = 'Bordeaux Métropole', millesime = '04/2020',
                fileUrl = 'https://opendata.bordeaux-metropole.fr/explore/dataset/st_freefloating_p/download/?format=shp&timezone=Europe/Berlin&lang=fr', zip = 'st_freefloating_p.shp')),
            Load(("ST_X(geom)",), ("ST_Y(geom)",)),
            Mapping(
                select = Select(
                    types = ["nodes"],
                    tags = {"amenity": "bicycle_rental"}),
                osmRef = "ref",
                conflationDistance = 50,
                generate = Generate(
                    static1 = {
                        "amenity": "bicycle_rental",
                        "bicycle_parking": "floor",
                        "bicycle": "yes",
                        "rollerboard": "yes"},
                    static2 = {"source": self.source},
                    mapping1 = {
                        "ref": "gid",
                        "scooter": lambda res: "yes" if res["typologie"] is "VTS" else "no"
                        })))
