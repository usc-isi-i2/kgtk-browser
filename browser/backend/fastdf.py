"""
Fast and simple dataframe implementation.
"""

import io
import csv
from operator import itemgetter
from collections import OrderedDict
import itertools

from kgtk.exceptions import KGTKException


class FastDataFrame(object):
    """
    Fast and simple dataframe implementation that mirrors the functionality we
    previously implemented via pandas.  This is less general but about 10x faster.
    """
    
    def __init__(self, columns, rows):
        """Create a dataframe with header 'columns' and data 'rows'.
        'columns' may be integers or strings and can be a single atom.
        'rows' can be any list or iterable of tuples whose arity is uniform
        and matches 'columns'.
        """
        self.columns = self.get_columns(columns)  # columns are always kept as a tuple
        self.rows = rows                          # rows can be a list, set or iterable

    def __iter__(self):
        return self.rows.__iter__()

    def __len__(self):
        return len(self.get_rows())

    def __getitem__(self, index):
        """Support indexed access to rows which requires conversion to a list format.
        """
        rows = self.rows
        if not isinstance(rows, (list, tuple)):
            rows = list(rows)
            self.rows = rows
        return rows[index]

    def empty(self):
        return len(self) == 0

    def copy(self):
        # if it is an iterable, we need to listify first, otherwise copying will exhaust the iter:
        rows = self.get_rows()
        return FastDataFrame(self.columns, rows.copy())

    def get_columns(self, columns=None):
        """Map 'columns' or the current columns onto a normalized tuple.
        'columns' may be integers or strings and can be a single atom.
        """
        columns = self.columns if columns is None else columns
        columns = (columns,) if isinstance(columns, (int, str)) else columns
        return tuple(columns)

    def get_rows(self):
        """Materialize the current set of rows as a list if necessary
        and return the result.
        """
        if not isinstance(self.rows, (list, set, tuple)):
            self.rows = list(self.rows)
        return self.rows
        
    def _get_column_indices(self, columns):
        """Convert 'columns' into a set of integer indices into 'self.columns'.
        'columns' may be integers or strings and can be a single atom.
        """
        icols = []
        for col in self.get_columns(columns):
            if isinstance(col, int):
                icols.append(col)
            else:
                icols.append(self.columns.index(col))
        return tuple(icols)

    def rename(self, colmap, inplace=False):
        """Rename some or all columns according to the map in 'colmap'.
        """
        newcols = tuple(colmap.get(c, c) for c in self.columns)
        df = inplace and self or FastDataFrame(newcols, self.rows)
        df.columns = newcols
        return df

    def project(self, columns):
        """Project rows of 'self' according to 'columns' which might be integer or string indices.
        This always creates a new dataframe as a result.  If a single column is given as an atom,
        rows will be atomic, if given as a list rows will be single-element tuples.
        """
        atomic_singletons = isinstance(columns, (int, str))
        icols = self._get_column_indices(columns)
        if len(icols) > 1 or atomic_singletons:
            return FastDataFrame(itemgetter(*icols)(self.columns), map(lambda r: itemgetter(*icols)(r), self.rows))
        else:
            # ensure single-item tuple, itemgetter converts to atom in this case:
            col = icols[0]
            return FastDataFrame(itemgetter(*icols)(self.columns), map(lambda r: (r[col],), self.rows))

    def drop_duplicates(self, inplace=False):
        """Remove all duplicate rows.  Preserve order of first appearance.
        """
        rows = list(OrderedDict.fromkeys(self.rows))
        if inplace:
            self.rows = rows
            return self
        else:
            return FastDataFrame(self.columns, rows)

    def drop_nulls(self, inplace=False):
        """Remove all rows that have at least one None value.
        """
        df = inplace and self or FastDataFrame(self.columns, None)
        df.rows = filter(lambda r: None not in r, self.rows)
        return df

    def coerce_type(self, column, type, inplace=False):
        # TO DO: for now we do this after JSON conversion
        pass

    def concat(self, *dfs, inplace=False):
        """Concatenate 'self' with all data frames 'dfs' which are assumed to have the
        same arity, column types and order, but not necessarily the same column names.
        The result uses the column names of 'self'.
        """
        columns = self.columns
        norm_dfs = [self]
        for df in dfs:
            if df is None:
                continue
            if len(columns) != len(df.columns):
                raise KGTKException('unioned frames need to have the same number of columns')
            norm_dfs.append(df)
        if len(norm_dfs) == 1:
            return inplace and self or self.copy()
        else:
            df = inplace and self or FastDataFrame(columns, None)
            df.rows = itertools.chain(*norm_dfs)
            return df
        
    def union(self, *dfs, inplace=False):
        """Concatenate 'self' with all data frames 'dfs' and remove any duplicates.
        """
        df = self.concat(*dfs, inplace=inplace)
        df = df.drop_duplicates(inplace=inplace)
        return df

    def to_list(self):
        """Return rows as a list of tuples.
        """
        self.rows = list(self.rows)
        return self.rows

    def to_string(self):
        """Return a printable string representation of this frame.
        """
        out = io.StringIO()
        csvwriter = csv.writer(out, dialect=None, delimiter='\t',
                               quoting=csv.QUOTE_NONE, quotechar=None,
                               lineterminator='\n', escapechar=None)
        csvwriter.writerow(self.columns)
        csvwriter.writerows(self.rows)
        return out.getvalue()

    def to_records_dict(self):
        """Return a list of rows each represented as a dict of column/value pairs.
        """
        columns = self.columns
        return [{k: v for k, v in zip(columns, r)} for r in self.rows]

    def to_value_dict(self):
        """Convert a single-valued values data frame into a corresponding JSON dict.
        Assumes 'self' is a binary key/value frame where each key has exactly 1 value.
        Keys are assumed to be in column 0 and values in column 1.
        """
        return {k: v for k, v in self.rows}

    def to_values_dict(self):
        """Convert a multi-valued 'values_df' data frame into a corresponding JSON dict.
        Assumes 'values_df' is a binary key/value frame where each key can have multiple values.
        Keys are assumed to be in column 0 and values in column 1.
        """
        result = {}
        for k, v in self.rows:
            result.setdefault(k, []).append(v)
        return result
