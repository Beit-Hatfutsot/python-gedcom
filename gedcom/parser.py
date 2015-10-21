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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# Please see the GPL license at http://www.gnu.org/licenses/gpl.txt
#
# This code based on work from Zappala, 2005.
# To contact the Zappala, see http://faculty.cs.byu.edu/~zappala
from __future__ import unicode_literals
import re
from element import Element


class Gedcom:
    """Parses and manipulates GEDCOM 5.5 format data

    For documentation of the GEDCOM 5.5 format, see:
    http://homepages.rootsweb.ancestry.com/~pmcbride/gedcom/55gctoc.htm

    This parser reads and parses a GEDCOM file.
    Elements may be accessed via:
      - a list (all elements, default order is same as in file)
      - a dict (only elements with pointers, which are the keys)
    """

    def __init__(self, fd):
        """ Initialize a GEDCOM data object. You must supply a Gedcom file."""
        self.as_list = []
        self.as_dict = {}
        self.top_element = Element(-1, "", "TOP", "")
        self.parse(fd)

    def parse(self, fd):
        """Open and parse file path as GEDCOM 5.5 formatted data."""
        line_num = 1
        last_elem = self.top_element
        for line in fd.read().split('\n')[:-1]:
            last_elem = self.parse_line(line_num, line, last_elem)
            line_num += 1

    def parse_line(self, line_num, line, last_elem):
        """Parse a line from a GEDCOM 5.5 formatted document.

        Each line should have the following (bracketed items optional):
        level + ' ' + [pointer + ' ' +] tag + [' ' + line_value]
        """
        ged_line_re = (
            # Level must start with nonnegative int, no leading zeros.
            '^\s*(0|[1-9]+[0-9]*) ' +
            # Pointer optional, if it exists it must be flanked by '@'
            '(@[^@]+@ |)' +
            # Tag must be alphanumeric string
            '([A-Za-z0-9_]+)' +
            # Value optional, consists of anything after a space to end of line
            '\s*(.*)\r$'
            )
        if re.match(ged_line_re, line):
            line_parts = re.match(ged_line_re, line).groups()
        else:
            errmsg = ("Line %d of document violates GEDCOM format" % line_num +
                      "\nSee: http://homepages.rootsweb.ancestry.com/" +
                      "~pmcbride/gedcom/55gctoc.htm")
            raise SyntaxError(errmsg)

        level = int(line_parts[0])
        pointer = line_parts[1].rstrip(' ')
        tag = line_parts[2]
        value = line_parts[3].lstrip(' ')

        # Check level: should never be more than one higher than previous line.
        if level > last_elem.level + 1:
            errmsg = ("Line %d of document violates GEDCOM format" % line_num +
                      "\nLines must be no more than one level higher than " +
                      "previous line.\nSee: http://homepages.rootsweb." +
                      "ancestry.com/~pmcbride/gedcom/55gctoc.htm")
            raise SyntaxError(errmsg)

        # Create element. Store in list and dict, create children and parents.
        element = Element(level, pointer, tag, value)
        self.as_list.append(element)
        if pointer != '':
            self.as_dict[pointer] = element

        # Start with last element as parent, back up if necessary.
        parent_elem = last_elem
        while parent_elem.level > level - 1:
            parent_elem = parent_elem.parent
        # Add child to parent & parent to child.
        parent_elem.add_child(element)
        element.add_parent(parent_elem)
        return element

    # Methods for analyzing individuals and relationships between individuals

    def marriages(self, individual):
        """ Return list of marriage tuples (date, place) for an individual. """
        marriages = []
        if not individual.is_individual:
            raise ValueError("Operation only valid for elements with INDI tag")
        # Get and analyze families where individual is spouse.
        fams_families = self.families(individual, "FAMS")
        for family in fams_families:
            for famdata in family.children:
                if famdata.tag == "MARR":
                    for marrdata in famdata.children:
                        date = ''
                        place = ''
                        if marrdata.tag == "DATE":
                            date = marrdata.value
                        if marrdata.tag == "PLAC":
                            place = marrdata.value
                        marriages.append((date, place))
        return marriages

    def marriage_years(self, individual):
        """ Return list of marriage years (as int) for an individual. """
        dates = []
        if not individual.is_individual:
            raise ValueError("Operation only valid for elements with INDI tag")
        # Get and analyze families where individual is spouse.
        fams_families = self.families(individual, "FAMS")
        for family in fams_families:
            for famdata in family.children:
                if famdata.tag == "MARR":
                    for marrdata in famdata.children:
                        if marrdata.tag == "DATE":
                            date = marrdata.value.split()[-1]
                            try:
                                dates.append(int(date))
                            except ValueError:
                                pass
        return dates

    def marriage_year_match(self, individual, year):
        """ Check if one of the marriage years of an individual matches
        the supplied year.  Year is an integer. """
        years = self.marriage_years(individual)
        return year in years

    def marriage_range_match(self, individual, year1, year2):
        """ Check if one of the marriage year of an individual is in a
        given range.  Years are integers.
        """
        years = self.marriage_years(individual)
        for year in years:
            if year >= year1 and year <= year2:
                return True
        return False

    def families(self, individual, family_type="FAMS"):
        """ Return family elements listed for an individual. 

        family_type can be FAMS (families where the individual is a spouse) or
        FAMC (families where the individual is a child). If a value is not
        provided, FAMS is default value.
        """
        if not individual.is_individual:
            raise ValueError("Operation only valid for elements with INDI tag.")
        families = []
        for child in individual.children:
            if (child.tag == family_type):
                family = child.value
                if family in self.as_dict and self.as_dict[family].is_family:
                    families.append(self.as_dict[family])
        return families

    def get_ancestors(self, indi, anc_type="ALL"):
        """ Return elements corresponding to ancestors of an individual

        Optional anc_type. Default "ALL" returns all ancestors, "NAT" can be
        used to specify only natural (genetic) ancestors.
        """
        if not indi.is_individual:
            raise ValueError("Operation only valid for elements with INDI tag.")
        parents = self.get_parents(indi, anc_type)
        ancestors = parents
        for parent in parents:
            ancestors = ancestors + self.get_ancestors(parent)
        return ancestors

    def get_parents(self, indi, parent_type="ALL"):
        """ Return elements corresponding to parents of an individual
        
        Optional parent_type. Default "ALL" returns all parents. "NAT" can be
        used to specify only natural (genetic) parents. 
        """
        if not indi.is_individual:
            raise ValueError("Operation only valid for elements with INDI tag.")
        parents = []
        famc_families = self.families(indi, "FAMC")
        for family in famc_families:
            if parent_type == "NAT":
                for famrec in family.children:
                    if famrec.tag == "CHIL" and famrec.value == indi.pointer:
                        for chilrec in famrec.children:
                            if chilrec.value == "Natural":
                                if chilrec.tag == "_FREL":
                                    parents = (parents + 
                                               self.get_family_members(family, "WIFE"))
                                elif chilrec.tag == "_MREL":
                                    parents = (parents +
                                               self.get_family_members(family, "HUSB"))
            else:
                parents = parents + self.get_family_members(family, "PARENTS")
        return parents

    def find_path_to_anc(self, desc, anc, path=None):
        """ Return path from descendant to ancestor. """
        if not desc.is_individual and anc.is_individual:
            raise ValueError("Operation only valid for elements with IND tag.")
        if not path:
            path = [desc]
        if path[-1].pointer == anc.pointer:
            return path
        else:
            parents = self.get_parents(desc, "NAT")
            for par in parents:
                potential_path = self.find_path_to_anc(par, anc, path + [par])
                if potential_path:
                    return potential_path
        return None

    def get_family_members(self, family, mem_type="ALL"):
        """Return array of family members: individual, spouse, and children.

        Optional argument mem_type can be used to return specific subsets.
        "ALL": Default, return all members of the family
        "PARENTS": Return individuals with "HUSB" and "WIFE" tags (parents)
        "HUSB": Return individuals with "HUSB" tags (father)
        "WIFE": Return individuals with "WIFE" tags (mother)
        "CHIL": Return individuals with "CHIL" tags (children)
        """
        if not family.is_family:
            raise ValueError("Operation only valid for elements with FAM tag.")
        family_members = [ ]
        for elem in family.children:
            # Default is ALL
            is_family = (elem.tag == "HUSB" or
                         elem.tag == "WIFE" or
                         elem.tag == "CHIL")
            if mem_type == "PARENTS":
                is_family = (elem.tag == "HUSB" or
                             elem.tag == "WIFE")
            elif mem_type == "HUSB":
                is_family = (elem.tag == "HUSB")
            elif mem_type == "WIFE":
                is_family = (elem.tag == "WIFE")
            elif mem_type == "CHIL":
                is_family = (elem.tag == "CHIL")
            if is_family and elem.value in self.as_dict:
                family_members.append(self.as_dict[elem.value])
        return family_members

    # Other methods

    def print_gedcom(self):
        """Write GEDCOM data to stdout."""
        for element in self.as_list:
            print(element)


class GedcomParseError(Exception):
    """ Exception raised when a Gedcom parsing error occurs
    """
    def __init__(self, value):
        self.value = value


    def __str__(self):
        return repr(self.value)
