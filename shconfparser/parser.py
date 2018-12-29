#!/usr/bin/python

import re, os
from collections import OrderedDict

__author__ = "Kiran Kumar Kotari"
__date__ = "$Date: 2015-12-28 19:45:47 +0530 (Mon, 28 Dec 2015) $"
__copyright__ = "Copyright 2015-18, MIT"
__credits__ = ["Kiran Kumar Kotari"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Kiran Kumar Kotari"
__email__ = "kotarikirankumar@gmail.com"
__status__ = "3 - Alpha"

class Parser:
    def __init__(self):
        self.data = OrderedDict()
        self.table = []
        self.header_pattern = r''
        self.header_names = []
        self.column_indexes = []

    def _space_level(self, line):
        return len(line) - len(line.lstrip(' '))

    def _convert_to_dict(self, tree, level=0):
        temp_dict = OrderedDict()
        for i, node in enumerate(tree):
            try:
                next_node = tree[i+1]
            except IndexError:
                next_node = {'level': -1}

            if node['level'] > level:
                continue
            if node['level'] < level:
                return temp_dict

            if next_node['level'] == level:
                temp_dict[node['key']] = 'None'
            elif next_node['level'] > level:
                temp_dict[node['key']] = self._convert_to_dict(tree[i+1:], level=next_node['level'])
            else:
                temp_dict[node['key']] = 'None'
                return temp_dict
        return temp_dict

    def _fetch_header(self, lines):
        pattern = re.compile(self.header_pattern)
        for i, line in enumerate(lines):
            result = pattern.match(line)
            if result: return i
        return 0

    def _fetch_column_position(self, header):
        position = []
        for header_name in self.header_names:
            position.append(header.find(header_name))
        return position

    def _fetch_table_column(self, line, start, end, key, data):
        col_data = str(line[start:end]).strip()
        if col_data: data[key] = col_data

    def _fetch_table_row(self, line, data, table):
        if len(line) < self.column_indexes[-1]:
            data[self.header_name[0]] = line.strip()
            return data

        for i, column_index in enumerate(self.column_indexes):
            try:
                start, end = column_index, self.column_indexes[i+1]
                self._fetch_table_column(line, start, end, self.header_names[i], data)
            except IndexError:
                continue
        self._fetch_table_column(line, start=self.column_indexes[-1], end=-1, key=self.header_names[-1], data=data)
        table.append(data)
        data = {}
        return data

    def _fetch_table_data(self, lines, header_index):
        table, data = [], {}
        for i in range(header_index + 1, len(lines)):
            if '#' in lines[i]:
                break
            data = self._fetch_table_row(lines[i], data, table)
        return table

    def parse_tree(self, lines):
        data = list()
        for i, line in enumerate(lines):
            space = self._space_level(line.rstrip())
            line = line.strip()
            if line != '!' and line != '' and line != 'end':
                data.append({'key': line, 'level': space})
        self.data = self._convert_to_dict(data)
        return self.data

    def parse_data(self, lines):
        self.data = OrderedDict()
        for line in lines:
            line = line.rstrip()
            self.data[line] = 'None'
        return self.data

    def parse_table(self, lines, header_names):
        self.table_lst = []
        self.header_names = header_names
        self.header_pattern = ' +'.join(header_names)
        header_index = self._fetch_header(lines)
        self.column_indexes = self._fetch_column_position(lines[header_index])
        self.table_lst = self._fetch_table_data(lines, header_index)
        return self.table_lst
