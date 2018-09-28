from gluon.html import *
from gluon.sqlhtml import SQLTABLE
from gluon.sql import Rows
from itertools import groupby


class ReportTable():

    def __init__(self,
                 rows,
                 grouping=None,  # {'field':'id','function': lambda row,v: ''}
                 sumary={},
                 footer={},
                 col_widths=[],
                 width='100%',
                 truncate=30):
        self.rows = rows
        self.grouping = grouping
        self.sumary = sumary
        self.footer = footer
        self.col_widths = col_widths
        self.width = width
        self.truncate = truncate
        self.tablenames = list(set(map(lambda c: c.split('.')[0], rows.colnames)))
        self.joined = len(self.tablenames) > 1
        self.groups = []
        self._summaries = []
        self._header = None
        self._footer = None

    def slice_rows(self, rows, field, function):
        ts, fs = field.split('.')
        if self.joined:
            rows = rows.sort(lambda row: row[ts][fs])
        else:
            rows = rows.sort(lambda row: row[fs])
        groups = []
        for key, group in groupby(rows, function):
            groups.append((key, Rows(db=rows.db,
                                     records=list(group),
                                     colnames=rows.colnames,
                                     fields=rows.fields)))
        return groups

    def table_rows(self, rows, truncate):
        table = SQLTABLE(rows, truncate=truncate)
        trs = table.element('tbody').elements('tr')
        return trs

    def table_header(self, rows, col_widths):
        ths = []
        dal = rows.db
        if not len(col_widths) > 0:
            col_widths = [100 / len(rows)] * len(rows)
        for i, col in enumerate(rows.colnames):
            table, field = col.split('.')
            ths.append(TH(dal[table][field].label, _width='%i%%' % col_widths[i]))
        return THEAD(TR(ths))

    def rows_sumary(self, rows, functions={}):
        results = [0] * len(rows.colnames)
        for row in rows:
            for i, col in enumerate(rows.colnames):
                if col in functions:
                    results[i] = functions[col](row, results[i])
                else:
                    results[i] = ' '
        width = 100 / len(results)
        tr = TR([TD(r, _width='%i%%' % width, _class='sumary') for r in results])
        return tr

    def generate(self):
        if self.grouping:
            slices = self.slice_rows(self.rows, self.grouping['field'], self.grouping['function'])
        else:
            slices = [('', self.rows)]
        self._header = self.table_header(self.rows, self.col_widths)
        self._groups = []
        for key, slice in slices:
            self._groups.extend(self.table_rows(slice, self.truncate))
            summary = self.rows_sumary(slice, self.sumary)
            self._summaries.append(summary)
            self._groups.append(summary)
        if len(self.footer) > 0:
            self._footer = self.rows_sumary(self.rows, self.footer)
            self._groups.append(self._footer)
        return TABLE(self._header, TBODY(self._groups), _width=self.width)