#
# Gedcom 6.0 Parser
#
# Copyright (C) 2015 The Museum of the Jewish People
# Copyright (C) 2012 Madeleine Price Ball
# Copyright (C) 2005 Daniel Zappala (zappala [ at ] cs.byu.edu)
# Copyright (C) 2005 Brigham Young University
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
from __future__ import unicode_literals
import re


class Element:
    """ Gedcom element

    Each line in a Gedcom file is an element with the format

    level [pointer] tag [value]

    where level and tag are required, and pointer and value are
    optional.  Elements are arranged hierarchically according to their
    level, and elements with a level of zero are at the top level.
    Elements with a level greater than zero are children of their
    parent.

    A pointer has the format @pname@, where pname is any sequence of
    characters and numbers.  The pointer identifies the object being
    pointed to, so that any pointer included as the value of any
    element points back to the original object.  For example, an
    element may have a FAMS tag whose value is @F1@, meaning that this
    element points to the family record in which the associated person
    is a spouse.  Likewise, an element with a tag of FAMC has a value
    that points to a family record in which the associated person is a
    child.
    See a Gedcom file for examples of tags and their values.

    """
    year_re = re.compile("[\d]{4}")

    def __init__(self, level, pointer, tag, value):
        """ Initialize an element.
        You must include a level, pointer, tag, and value. Normally
        initialized by the Gedcom parser, not by a user.
        """
        # basic element info
        self.level = level
        self.pointer = pointer
        self.tag = tag
        self.value = value
        # structuring
        self.children = []
        self.parent = None

    @property
    def is_individual(self):
        """ Check if this element is an individual """
        return self.tag == "INDI"

    @property
    def is_family(self):
        """ Check if this element is a family """
        return self.tag == "FAM"

    @property
    def name(self):
        """ Return a person's names as a tuple: (first,last) """
        first = ""
        last = ""
        if not self.is_individual:
            return (first, last)
        for e in self.children:
            if e.tag == "NAME":
                # some older Gedcom files don't use child tags but instead
                # place the name in the value of the NAME tag
                if e.value != "":
                    name = e.value.split('/')
                    if len(name) > 0:
                        first = name[0].strip()
                        if len(name) > 1:
                            last = name[1].strip()
                else:
                    for c in e.children:
                        if c.tag == "GIVN":
                            first = c.value
                        if c.tag == "SURN":
                            last = c.value
        return (first, last)

    @property
    def gender(self):
        """ The gender of a person in string format """
        gender = ""
        if not self.is_individual:
            return gender
        for e in self.children:
            if e.tag == "SEX":
                gender = e.value
        return gender

    @property
    def private(self):
        """ Whether the person is marked private in boolean format """
        private = False
        if not self.is_individual:
            return False
        for e in self.children:
            if e.tag == "PRIV":
                private = e.value
                if private == 'Y':
                    private = True
        return private

    @property
    def birth(self):
        """ Return the birth tuple of a person as (date,place) """
        date = ""
        place = ""
        source = ()
        if not self.is_individual:
            return (date, place, source)
        for e in self.children:
            if e.tag == "BIRT":
                for c in e.children:
                    if c.tag == "DATE":
                        date = c.value
                    if c.tag == "PLAC":
                        place = c.value
                    if c.tag == "SOUR":
                        source = source + (c.value,)
        return (date, place, source)

    @property
    def birth_year(self):
        """ Return the birth year of a person in integer format """
        date = ""
        if not self.is_individual:
            return date
        for e in self.children:
            if e.tag == "BIRT":
                for c in e.children:
                    if c.tag == "DATE":
                        years = self.year_re.findall(c.value)
                        break;
        try:
            year = int(years[0])
        except:
            return None

        if year > 3000:
            year -= 3760

        return year

    @property
    def death(self):
        """ Return the death tuple of a person as (date,place) """
        date = ""
        place = ""
        source = ()
        if not self.is_individual:
            return (date, place)
        for e in self.children:
            if e.tag == "DEAT":
                for c in e.children:
                    if c.tag == "DATE":
                        date = c.value
                    if c.tag == "PLAC":
                        place = c.value
                    if c.tag == "SOUR":
                        source = source + (c.value,)
        return (date, place, source)

    @property
    def death_year(self):
        """ The death year of a person in integer format """
        date = ""
        if not self.is_individual:
            return date
        for e in self.children:
            if e.tag == "DEAT":
                for c in e.children:
                    if c.tag == "DATE":
                        years = self.year_re.findall(c.value)
                        break;
        try:
            year = int(years[0])
        except:
            return None

        if year > 3000:
            year -= 3760

        return year

    @property
    def burial(self):
        """ The burial tuple of a person as (date,place) """
        date = ""
        place = ""
        source = ()
        if not self.is_individual:
            return (date, place)
        for e in self.children:
            if e.tag == "BURI":
                for c in e.children:
                    if c.tag == "DATE":
                        date = c.value
                    if c.tag == "PLAC":
                        place = c.value
                    if c.tag == "SOUR":
                        source = source + (c.value,)
        return (date, place, source)

    @property
    def census(self):
        """ list of census tuples (date, place) for an individual. """
        census = []
        if not self.is_individual:
            raise ValueError("Operation only valid for elements with INDI tag")
        for pdata in self.children:
            if pdata.tag == "CENS":
                date = ''
                place = ''
                source = ''
                for indivdata in pdata.children:
                    if indivdata.tag == "DATE":
                        date = indivdata.value
                    if indivdata.tag == "PLAC":
                        place = indivdata.value
                    if indivdata.tag == "SOUR":
                        source = source + (indivdata.value,)
                census.append((date, place, source))
        return census

    @property
    def last_updated(self):
        """ Return the last updated date of a person as (date) """
        date = ""
        if not self.is_individual:
            return (date)
        for e in self.children:
            if e.tag == "CHAN":
                for c in e.children:
                    if c.tag == "DATE":
                        date = c.value
        return (date)

    @property
    def occupation(self):
        """ Return the occupation of a person as (date) """
        occupation = ""
        if self.is_individual:
            for e in self.children:
                if e.tag == "OCCU":
                    occupation = e.value
        return occupation

    @property
    def deceased(self):
        """ Whether a person is deceased """
        if not self.is_individual:
            return False
        for e in self.children:
            if e.tag == "DEAT":
                return True
        return False

    def add_child(self, element):
        """ Add a child element to this element """
        self.children.append(element)

    def add_parent(self, element):
        """ Add a parent element to this element """
        self.parent = element

    def criteria_match(self, criteria):
        """ Check in this element matches all of the given criteria.
        The criteria is a colon-separated list, where each item in the

        list has the form [name]=[value]. The following criteria are supported:

        surname=[name]
             Match a person with [name] in any part of the surname.
        name=[name]
             Match a person with [name] in any part of the given name.
        birth=[year]
             Match a person whose birth year is a four-digit [year].
        birthrange=[year1-year2]
             Match a person whose birth year is in the range of years from
             [year1] to [year2], including both [year1] and [year2].
        death=[year]
        deathrange=[year1-year2]
        """

        # error checking on the criteria
        try:
            for crit in criteria.split(':'):
                key, value = crit.split('=')
        except:
            return False
        match = True
        for crit in criteria.split(':'):
            key, value = crit.split('=')
            if key == "surname" and self.name[1].find(name) == -1:
                match = False
            elif key == "name" and self.name[0].find(name) == -1:
                match = False
            elif key == "birth":
                try:
                    year = int(value)
                    if not self.birth_year == year:
                        match = False
                except:
                    match = False
            elif key == "birthrange":
                try:
                    year1, year2 = value.split('-')
                    year1 = int(year1)
                    year2 = int(year2)
                    if year1 <= self.birth_year <= year2:
                        match = False
                except:
                    match = False
            elif key == "death":
                try:
                    year = int(value)
                    if not self.death_year == year:
                        match = False
                except:
                    match = False
            elif key == "deathrange":
                try:
                    year1, year2 = value.split('-')
                    year1 = int(year1)
                    year2 = int(year2)
                    if year1 <= self.death_year <= year2:
                        match = False
                except:
                    match = False

        return match

    def __unicode__(self):
        """ Format this element as its original string """
        result = str(self.level)
        if self.pointer != "":
            result += ' ' + self.pointer
        result += ' ' + self.tag
        if self.value != "":
            result += ' ' + self.value
        return result
