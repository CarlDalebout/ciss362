"""
All measures in cm by default!!!

linewidth  default=''
linecolor  default=black
linestyle  default=solid
"""

import math, random, os, string, re, sys
random.seed()
from math import sin, cos

from subprocess import Popen
from subprocess import PIPE
from math import *
import traceback
import string

def to_string(s):
    """ IMPORTANT: Some strings are returned as bytes. Call this to
    convert to strings.
    This has been done in the shell function. """
    if isinstance(s, bytes):
        return "".join( chr(x) for x in bytearray(s))
    else:
        return str(s)

def myround(points):
    ''' rounding to prevent overflow of accuracy '''
    #print points, type(points)
    if isinstance(points, int):
        return points
    if isinstance(points, float):
        return round(points, 2)
    elif isinstance(points, tuple):
        return tuple(myround(x) for x in points)
    elif isinstance(points, list):
        return list(myround(x) for x in points)
    #elif points == None:
    #    return None
    else:
        return points # no casting

def flatten(xss):
    # If xss = [[1,2,3],[4,5,6]], then [1,2,3,4,5,6] is returned.
    return reduce(lambda x,y:x+y, xss, [])

def removedup(xs):
    r = []
    for x in xs:
        if x not in r: r.append(x)
    return r


def randstr():
    s = ''
    for i in range(16):
        s += random.choice(string.ascii_letters)
    return s
#==============================================================================
# Convenience function to convert multiline string to 2d array
#==============================================================================
def str_to_2darray(s, sep=' '):
    lines = s.split('\n')
    lines = [_.strip() for _ in lines if _.strip() != '']
    lines = [_.split(sep) for _ in lines]
    lines = [[_.strip() for _ in row if _.strip() != ''] for row in lines]
    return lines
#==============================================================================
# tikz coordinate
#==============================================================================
def coordinate(x, y, name):
    return r'\coordinate (%s) at (%scm,%scm) {};' % (name, x, y)
                
#==============================================================================
# This is a temporary fix.
# 1. Removes "at (%s,%s)" from tikz string
# 2. Insert "left =of a" etc into tikz string
#==============================================================================
def next_to(s, # a tikz string
            name, directions):
    p = re.compile("at\s*\([0-9]*(.[0-9]*)?\s*\,\s*[0-9]*(.[0-9]*)?\s*\)")
    s =  re.sub(p, "", s)
    try:
        d,dist = directions
    except:
        d = directions
        dist = 0
    s = s.replace(']', ',%s=%scm of %s]' % (d, dist, name))
    return s

#==============================================================================
# Constants
#==============================================================================
L = 0.04 # default line width
DOUBLE_LINKED_LIST_LINEWIDTH = 0.03
SINGLE_LINKED_LIST_LINEWIDTH = 0.03
POINTER_LINEWIDTH = 0.03

#==============================================================================
# Basic utilities
#==============================================================================
def IFELSE(b, x, y):
    if b: return x
    else: return y

def RANGE(a, b=None, c=None):
    if b==None and c==None:
        a, b, c = 0, a, 1
    elif b!=None and c==None:
        c = 1
    ret = []
    x = a
    while x < b:
        ret.append(x)
        x += c
    return ret

def ceiling(x):
    return IFELSE(int(x) == x, int(x), int(x) + 1)

def floor(x):
    if int(x) == x: return int(x)
    else: return IFELSE(x >= 0, int(x), int(x) - 1)

def readfile(filename): return open(filename, 'r').read()
def writefile(filename, s): return open(filename, 'w').write(s)

#==============================================================================
# The following function will remove extraneous character in the stdout
# when you execute scons
#==============================================================================
def clean_scons_output(s):
    return s.replace(chr(27)+"[?1034h", "") # remove garbage char

#==============================================================================
# beamer
#==============================================================================
def beamerframe(title='SOME TITLE',
                fragile=True,
                allowframebreaks=False,
                s='SOME CONTENT',
          ):
    options = []
    if fragile:
        options.append('fragile')
    if allowframebreaks:
        options.append('allowframebreaks')
    if options != []:
        options = '[%s]' % (','.join(options))
    else:
        options = ''
    return r'''
\begin{frame}%(options)s
\frametitle{%(title)s}
%(s)s
\end{frame}

''' % {'title':title, 's': s, 'options':options}
    
#==============================================================================
# Basic latex utilities
#==============================================================================
def console(s='',
            filename='', # TODO: read file a file instead
            xs=[],       # DEPRECATED: Use commands
            commands=[],
            command=[],
            numbers='',
            frame='single', # TODO
            width=75, wrapmarker=''):
    return verbatim(s=s,
                    filename=filename,
                    commands=commands,
                    command=command,
                    numbers=numbers,
                    frame=frame,
                    width=width,
                    wrapmarker=wrapmarker)


def tikzpicture(s):
    return r"""\begin{tikzpicture}
%s
\end{tikzpicture}
""" % s


def center(s):
    return r"""\begin{center}
%s
\end{center}""" % s


def do_latex_example(s, center=True):
    print (console(s.strip()))
    if center:
        print (r"""\begin{center}
%s
\end{center}""" % s)
    else:
        print (r"""\begin{center}
%s
\end{center}""" % s)
        


def do_tikz_example(s):
    print (console(s.strip()))
    print (r"""\begin{center}
\begin{tikzpicture}
%s
\end{tikzpicture}
\end{center}
""" % s)

#==============================================================================
# verbatim
# It's annoying when executing latex commands that we have to choose 3 chars
# that does not appear in the text. Furthermore, hand coding the tex commands
# in the verbatim text shifts the text. This function allows you to write the
# text and then spell out what substrings should have tex command applied to.
# The function will find the 3 commandchars for you.
#
# WARNING: Note that the characters in the environment name cannot be used.
# For instance if you uses \begin{console}...\end{console}, then
# c, o, n, s, l, e
# cannot be used.
#
# WARNING: The following characters cannot use: <>-,
#
# Note that the charactes in extrachars are those that requires \ in the
# commandchars line.
#
# Example:
#   verbatim(s, [['underline', ['hello', 'world']],
#                ['redtext',   ['abc', 'def']],
#               ]
#           )
#==============================================================================
def verbatim(s='',
             filename='', # TODO: read file a file instead
             xs=[],       # DEPRECATED: Use commands
             commands=[],
             command=[],
             numbers='',
             frame='single', # TODO
             width=75, wrapmarker=''
             ):
    if xs != []: commands = xs
    if command != []: commands = [command]
    #--------------------------------------------------------------------------
    # Get file contents if necessary
    #--------------------------------------------------------------------------
    if filename != '':
        try:
            s = readfile(filename)
        except:
            return verbatim('verbatim error: Cannot read file %s' % filename)
    #--------------------------------------------------------------------------
    # Format according to width
    #--------------------------------------------------------------------------
    lines = s.split('\n')
    newlines = []
    ret = ''
    for line in lines:
        pre, line = line[:width], line[width:]
        newlines.append(pre)
        while line != '':
            pre, line = line[:width], line[width:]
            pre = wrapmarker + pre
            newlines.append(pre)
    ret += '\n'.join(newlines)
    s = ret
    #--------------------------------------------------------------------------
    # Line numbering on the left
    #--------------------------------------------------------------------------
    numbers = IFELSE(numbers in ['', None, False], '', 'numbers=%s' % numbers)
    #--------------------------------------------------------------------------
    # Frame
    #--------------------------------------------------------------------------
    frame = IFELSE(frame in ['', None, False], '', 'frame=%s' % frame)
    #--------------------------------------------------------------------------
    # Compute commandchars
    #--------------------------------------------------------------------------
    from string import ascii_letters, digits, punctuation
    #chars = list(digits + "~!@$()*_+|:;./?") # FOR SOME REASON digits HAS
                                              # PROBLEMS
    chars = list("~!@$()*_+|:;./?")
    chars = [c for c in chars if c not in "console"]
    extrachars = ['\\', '{', '}', '#', '^', '&', '[', ']']
    commandchars = {}
    for c in chars: commandchars[c] = c
    for c in extrachars: commandchars[c] = '\\' + c
    chars = chars + extrachars
    c = [x for x in chars if x not in s][:3] # 3 characters in char, not in s
    commandchars = 'commandchars=%s%s%s' % \
                   (commandchars[c[0]], commandchars[c[1]],commandchars[c[2]])
    #--------------------------------------------------------------------------
    # Perform replacement
    #--------------------------------------------------------------------------
    for item in commands:
        func, substrings = item

        if isinstance(substrings, str):
            # CASE: item looks like ['textcolor', 'hello world']
            substrings = [substrings]

        if isinstance(substrings[0], str):
            # CASE: item looks like ['textcolor', ['hello', ...]]
            for substring in substrings:
                import re
                p = re.compile('(%s)' % substring)
                done = ''
                while s != '':
                    parts = p.split(s, 1)
                    #print "parts:", parts
                    if len(parts) == 1:
                        done += s
                        s = ''
                    else:
                        left, mid, right = parts
                        done += left
                        done += r"%s%s%s%s%s" % (c[0], func, c[1], mid, c[2])
                        s = right
                s = done
        elif isinstance(substrings[0], int):
            # CASE: item looks like ['textcolor', [42,....]]
            # Two subcases:
            # SUBCASE 1: item looks like ['textcolor', [42,5,10]]
            #            This means that substring is a list of 3 numbers
            #            line number, starting column number, ending
            #            column number
            # SUBCASE 2: item looks like ['textcolor', [42, 'hello']]
            if isinstance(substrings[1], int):
                lines = s.split('\n')
                i,j,k = substrings # all ints
                substring = lines[i][j:k]
                new_substring = r"%s%s%s%s%s" % (c[0], func, c[1], substring, c[2])
                lines[i] = lines[i][:j] + new_substring + lines[i][k:] 
                s = '\n'.join(lines)
            else:
                linenumber, substring = substrings
                lines = s.split('\n')
                import re
                p = re.compile('(%s)' % substring)
                done = ''
                s = lines[linenumber]
                while s != '':
                    parts = p.split(s, 1)
                    #print "parts:", parts
                    if len(parts) == 1:
                        done += s
                        s = ''
                    else:
                        left, mid, right = parts
                        done += left
                        done += r"%s%s%s%s%s" % (c[0], func, c[1], mid, c[2])
                        s = right
                s = done
                lines[linenumber] = s
                s = '\n'.join(lines)
    return r"""\begin{console}[%s, %s, %s]
%s
\end{console}
""" % (frame, numbers, commandchars, s)

#==============================================================================
# table
#==============================================================================
def table(data,
          style=None,
          col_headings=None,
          row_headings=None,
          topleft_heading=None,
          right_row_headings=None, # NEW
          col_width=None):
    # data is a dictionary or a list of list/tuples
    #
    #
    # TODO: If col_headings not the right size, error occurs.
    
    if style == None and isinstance(data, dict):
        s = ''
        for k,v in data.items():
            s += r'%s & %s \\' % (k,v) + '\n'
        return r'''
\begin{longtable}{|r|r|}
\hline
%s
\hline
\end{longtable}
        ''' % s
    
    # Change rows of data from tuples/lists to lists and all data to string
    data = [[str(_) for _ in row] for row in data]
    
    # compute num_cols
    if col_headings == None: col_headings = []
    col_headings = [str(_) for _ in col_headings]
    num_cols = max([len(x) for x in data] + [len(col_headings)])
    if col_headings:
        col_headings = col_headings + ['' for i in range(num_cols - len(col_headings))] # add '' to col headings if nec

    # compute num_rows
    if row_headings == None: row_headings = []
    row_headings = [str(_) for _ in row_headings]
    num_rows = max([len(row_headings), len(data)])
    if row_headings:
        row_headings = row_headings + ['' for i in range(num_rows - len(row_headings))] # add '' to row headings if nec

    #if right_row_headings == None: right_row_headings = []
    #right_row_headings = [str(_) for _ in right_row_headings]
    #num_rows = max([num_rows, len(right_row_headings)])
    #if right_row_headings:
    #    right_row_headings = right_row_headings + ['' for i in range(num_rows - len(right_row_headings))] # add '' to row headings if nec
        
    # add '' so that data is (num_rows)-by-(num_cols)
    data = data + [[''] for i in range(num_rows - len(data))]
    data = [row + ['' for i in range(num_cols - len(row))] for row in data]
    
    # Put row heading entries into data
    if row_headings:
        data = [[x] + row for x,row in zip(row_headings, data)]
    #if right_row_headings:
    #    data = [row + [x] for x,row in zip(row_headings, data)]
        
    # Add col_headings and topleft_heading to data:
    # NOTE:
    # -- If col_headings is empty, then topleft_heading will not appear
    # -- If row_headings is empty, then topleft_heading will not appear
    if col_headings:
        if topleft_heading == None: topleft_heading = ''
        if row_headings:
            data.insert(0, [str(topleft_heading)] + col_headings)
        else:
            data.insert(0, col_headings)
    num_cols = len(data[0])

    #for i,row in enumerate(data):
    #    print i, row

    # Change all entries in data to strings of the same width
    widths = [0 for i in range(num_cols)]
    #print "widths:", widths
    for row in data:
        for i in range(num_cols):
            widths[i] = max([widths[i],len(row[i])])
    
    data = [[str(x).ljust(width) for x,width in zip(row,widths)] for row in data]
    
    s = ''

    for row in data:
        row = row + ['' for _ in range(num_cols - len(row))]
        row = ' & '.join([str(x) for x in row]) + r'\\ \hline' + '\n'
        s += row

    s = ''
    for i,row in enumerate(data):
        t = ' & '.join(row) + r' \\ \hline '
        if i == 0 and col_headings: # col header
            t += r'\hline '
        t += '\n'
        s += t
    if s.endswith('\n'): s = s[:-1]
    if not style:
        if row_headings:
            if col_width:
                align = '|'.join(['p{%s}|' % col_width] + ['p{%s}' % col_width for _ in range(num_cols - 1)])
            else:
                align = '|'.join(['r|'] + ['r' for _ in range(num_cols - 1)])
        else:
            align = '|'.join(['r' for _ in range(num_cols)])
        align = '|%s|' % align
    else:
        align=style
    #if row_headings:
    #    align = '|r|' + align
        
    return r'''
\begin{longtable}{%s}
\hline 
%s
\end{longtable}
        ''' % (align, s)
    
#==============================================================================
# execute(source, print_source=False, debug)
# source = python code string
#
# 1. Saves source as a file with random filename of the form [rand].tmp.py
# 2. Execute the python program and retrieves stdout, stderr, return code
# 3.
#
# Return case:
#    return stdout, stderr, return code?
#==============================================================================
def execute(source,
            print_source=False,
            debug=False,
            print_result=True, # True: print result. False: return result
            ):
    """
    source is a python program.
    1. Print s in a latex console environment.
    2. Print traceback (etc) if there are errors
    3. Insert stdout
    """
    source = source.strip()

    # Get source filename
    randstr = ''.join([random.choice(string.ascii_lowercase) for _ in range(8)])
    filename = '%s.tmp.py' % randstr

    # Save source and execute
    writefile(filename, source) # Note: source does not have filename
    cmd = 'python %s 2>stderr.txt >stdout.txt' % filename # ???? 2018/10/13
    #stdout, stderr, returncode = myexec(cmd) # seems to hang
    os.system(cmd)
    os.system('rm -f %s' % filename) # delete source file
    stderr = open('stderr.txt', 'r').read().strip()
    stdout = open('stdout.txt', 'r').read().strip()
    
    if debug or stderr != '':
        s = r"""PYTHON ERROR. See source, stderr, stdout below
%s\vspace{-.1\baselineskip}
%s\vspace{-.1\baselineskip}
%s""" % (verbatim(source), verbatim(stdout), verbatim(stderr))
    else:
        # debug == false or stderr == ''
        s = ''
        if print_source:
            s = console(source) + r'\vspace{0.5\baselineskip}' + stdout
        else:
            s = stdout
        
    if print_result:
        print (s)
    else:
        return s


def error():
    s = readfile('main.py.err').strip()
    if s == '': return ''
    return r"""
\begin{console}
ERROR FROM main.py.err:

    %s
\end{console}
    """



def minipage(s='',
             align='t',
             h=0, w=0):
    h = round(h,3)
    w = round(w,3)
    if h < 0.1: h = 0.1
    if w < 0.1: w = 0.1
    if s=='': s = r'\mbox{}' + '\n'
    return r'''
\begin{minipage}[%(align)s][%(h)scm]{%(w)scm}
%(s)s
\end{minipage}
''' % {'align':align, 'h':h, 'w':w, 's':s}


    
class Plot:
    """
    Goal
    - maintains a list of object to draw
    - maintains a tight bounding rect of all objects
    - provides debug/error window at the bottom

    This basically spits out a tikz environment in a centered
    environment.
    
    TODO:
    - Plot(pdf=True, filename='a', dir='tmp/')
    """
    def __init__(self,
                 verbose=False,
                 center=True,
                 scale=1,
                 extra=0, # extra added to the minimal grid
                 **karg   # things like linewidth, ...
                 ):      
        # named shapes (see add method)
        # is an object is added without name,
        # a name will be give ('0', '1', ...)
        # see self.auto_inc

        # Need to order tikz strings as objects are added to plot
        self.auto_inc = 0
        self.xs = {}
        self.verbose = verbose
        self.center = center
        self.extra = extra
        self.scale = scale
        self.debug = '' # a debug/status minipage?
        self.font = '' # not used yet
        self.env = karg
        self.grid = None

        self.ordered_names = [] # ADDED TO ORDER OBJECTS
         
    def add(self, shape, *arg, **karg):
        """ Note that if shape is a string, then it's just a latex
        fragment.

        TODO: Add objects instead
        """

        # Python3 change
        if 'name' in karg: # OLD: karg.has_key('name'):
            name = karg['name']
        else:
            name = self.auto_inc; self.auto_inc += 1

        if isinstance(shape, BaseNode):
            self.xs[name] = shape
        else:
            self.xs[name] = [shape, arg, karg]

        self.ordered_names.append(name) # ADDED TO ORDER OBJECTS
        
    def __iadd__(self, x):
        if isinstance(x, Grid):
            self.grid = x
        else:
            self.add(x)
        return self
    def __str__(self):
        draw_grid = False
        min_x0 = None
        min_y0 = None
        max_x1 = None
        max_y1 = None
        s = ''

        def f(): pass


        # TEMP: PUT GRID FIRST???
        # The rest computes parameters for the grid
        # Either grid params were passed in or computed.
        if self.grid:
            # If Grid() created with x0,y0,x1,y1 need to compute bounding rect.
            if self.grid.x0==0 and \
               self.grid.y0==0 and \
               self.grid.x1==0 and \
               self.grid.y1==0:
                # Compute bounding rec for grid
                min_x0 = min_y0 = max_x1 = max_y1 = None
                for value in self.xs.values():
                    if isinstance(value, BaseNode):
                        x0,y0,x1,y1 = value.leftx(), value.bottomy(), value.rightx(), value.topy()
                    else:
                        # This should be deprecated
                        x0 = y0 = x1 = y1 = 0
                        shape, arg, karg = value
                        if shape in [circle]:
                            radius = karg.get('radius', None)
                            r = karg.get('r', None)
                            if radius == None and r != None: radius = r
                            x0 = karg['x'] - radius
                            y0 = karg['y'] - radius
                            x1 = karg['x'] + radius
                            y1 = karg['y'] + radius
                        else:
                            try:
                                x0 = karg['x0']
                                y0 = karg['y0']
                                x1 = karg['x1']
                                y1 = karg['y1']
                            except:
                                pass
                    if min_x0 == None or x0 < min_x0: min_x0 = x0
                    if min_y0 == None or y0 < min_y0: min_y0 = y0
                    if max_x1 == None or x1 > max_x1: max_x1 = x1
                    if max_y1 == None or y1 > max_y1: max_y1 = y1
                if min_x0 == None: min_x0 = 0 # PROBABLY ... or max_x1 is it's not none? 
                if min_y0 == None: min_y0 = 0
                if max_x1 == None: max_x1 = 0
                if max_y1 == None: max_y1 = 0
                # adjust to integers
                min_x0 = floor(min_x0)
                min_y0 = floor(min_y0)
                max_x1 = ceiling(max_x1)
                max_y1 = ceiling(max_y1)
                s += str(Grid(x0=min_x0, y0=min_y0, x1=max_x1, y1=max_y1))
            else:
                s += str(self.grid)



        
        
        #for value in self.xs.values():
        for name in self.ordered_names: # ADDED FOR ORDERING OBJECTS
            value = self.xs[name]
            
            try:
                shape, arg, karg = value
                if type(shape) == type('') and arg == () and karg == {}:
                    s += shape
                else:
                    s += apply(shape, arg, karg)
            except:
                try:
                    s += str(value)
                except:
                    raise ValueError("str method in Plot error: %s, type:%s" % (value, type(value)))



                
        s = s.rstrip()
        # \begin{tikzpicture}[...]
        options = ''
        if self.scale != 1:
            options = "[scale=%s]" % self.scale
        latex = r"""\begin{tikzpicture}%s
%s
\end{tikzpicture}""" % (options, s)
        latex += '\n'
        if self.center:
            latex = r"""\begin{center}
%s
\end{center}""" % latex
            latex += '\n'
        if self.verbose:
            latex = r"""\begin{console}
%s
\end{console}
%s""" % (latex, latex)
        return latex


    

#==============================================================================
# BaseNode: parent of all shapes
#==============================================================================
class BaseNode:
    # Note that the width,height or x0,y0,x1,y1 specified is the
    # the boundary box. The actual content area is smaller.
    #
    # TODO: Remove x, y, w, h as computed fields
    def __init__(self,
                 name=None,
                 x=None, y=None, # center
                 w=None, h=None, # width, height
                 #
                 x0=None, y0=None, x1=None, y1=None, # bounding box
                 # Note that either w,h or x0,y0,x1,y1 is specified
                 debug=True):
        self.name = name
        if x != None:
            self.x0 = x - w/2.0
            self.x1 = x + w/2.0
            self.y0 = y - h/2.0
            self.y1 = y + h/2.0
        elif x0 != None:
            self.x0 = x0
            self.x1 = x1
            self.y0 = y0
            self.y1 = y1
        self.debug = False # debug
    def move(self, dx=0.0, dy=0.0):
        self.x0 += dx
        self.y0 += dy
        self.x1 += dx
        self.y1 += dy
    def centerx(self): return (self.x0 + self.x1)/2.0
    def centery(self): return (self.y0 + self.y1)/2.0
    def topy(self): return self.y1
    def bottomy(self): return self.y0
    def leftx(self): return self.x0
    def rightx(self): return self.x1
    def height(self): return self.y1 - self.y0
    def width(self): return self.x1 - self.x0
    def top(self): return self.centerx(), self.y1
    def bottom(self): return self.centerx(), self.y0
    def left(self): return self.x0, self.centery()
    def right(self): return self.x1, self.centery()
    def center(self): return self.centerx(), self.centery()
    def topleft(self): return self.x0, self.y1
    def topright(self): return self.x1, self.y1
    def bottomleft(self): return self.x0, self.y0
    def bottomright(self): return self.x1, self.y0
    def __str__(self):
        x0 = self.x0
        y0 = self.y0
        x1 = self.x1
        y1 = self.y1
        s = ''
        if self.debug: # add bounding box
            s += rect(x0=x0, y0=y0, x1=x1, y1=y1, color='red') # 
        return s

    def get_edge(self, node, style=""):
        """ return list of points describing edge joining self to node.
        assume down
        """
        y = (self.y0 + self.y1)/2.0
        x = (self.x0 + self.x1)/2.0
        node_y = (node.y0 + node.y1) / 2.0
        node_x = (node.x0 + node.x1) / 2.0
        if y == node_y: # CASE: same level
            if self.x1 <= node.x0:
                x0,y0 = self.right()
                x1,y1 = node.left()
            else:
                x0,y0 = self.left()
                x1,y1 = node.right()
            return [(x0,y0),(x1,y1)]
        
        if style == "":
            if y > node_y: # CASE: downward
                x0,y0 = self.bottom()
                x1,y1 = node.top()
            elif y < node_y: # CASE: up
                x0,y0 = self.top()
                x1,y1 = node.bottom()  
            return [(x0,y0),(x1,y1)]
        elif style == "ES":
            x0,y0 = self.right()
            x2,y2 = node.top()
            x1,y1 = x2,y0
            return (x0,y0),(x1,y1),(x2,y2)
        elif style == "SW":
            x0,y0 = self.bottom()
            x2,y2 = node.right()
            x1,y1 = x0,y2
            return (x0,y0),(x1,y1),(x2,y2)
        elif style == "WS":
            x0,y0 = self.left()
            x2,y2 = node.top()
            x1,y1 = x2,y0
            return (x0,y0),(x1,y1),(x2,y2)
        elif style == "broom": # leg of a broom downward
            x0,y0 = self.bottom()
            x3,y3 = node.top()
            x1,y1 = x0,(y0+y3)/2.0
            x2,y2 = x3,y1
            return (x0,y0),(x1,y1),(x2,y2),(x3,y3)

#==============================================================================
# Point
# Cleanup: can use rect with height=width=0
#==============================================================================
class Point(BaseNode):
    def __init__(self, x=0, y=0, point=None, name=None):
        if point != None:
            x, y = point
        BaseNode.__init__(self, x=x, y=y, w=0.0, h=0.0, name=name)
    def __str__(self):
        return r"\node[shape=circle,minimum size=0,inner sep=0](%s) at (%s,%s){};" % (self.name, self.x0, self.y0)
        
#==============================================================================
# Style
# Mode "tikz" objects have common attributes such as linecolor, linewidth, etc.
#
# tikz():
# Form  a string s to be used in latex tikz:
#   \draw[s]
#==============================================================================
import copy
def get_style(**arg):
    """Form  a string s to be used in latex
    \draw[s]
    """
    
    linewidth = str(arg.get('linewidth', '')).strip()
    if linewidth in ['', None]:
        linewidth = ''
    else:
        if linewidth == 'very thin':
            pass # DON'T DO ANYTHING
        else:
            if not linewidth.endswith('cm'):
                linewidth = '%scm' % linewidth
        linewidth = 'line width=%s' % linewidth

    #--------------------------------------------------------------------------
    # Color: only color, linecolor used
    #--------------------------------------------------------------------------
    color = arg.get('color', '')
    linecolor = arg.get('linecolor', '')
    if color=='' and linecolor!='': color=linecolor

    startstyle = arg.get('startstyle','')
    endstyle = arg.get('endstyle','')
    # Get rid of "dot"
    startstyle = startstyle.replace('dot', '')
    endstyle = endstyle.replace('dot', '')
    
    #--------------------------------------------------------------------------
    # Add arrow tips to linestyle
    #--------------------------------------------------------------------------
    linestyle = ''
    if startstyle.startswith('-'): startstyle = startstyle[1:]
    if startstyle == '>': startstyle = '<'
    if startstyle == '>>': startstyle = '<<'
    if startstyle == '>|': startstyle = '|<'
    if startstyle == '>>|': startstyle = '|<<'
    
    if endstyle.startswith('-'): endstyle = endstyle[1:]

    if startstyle or endstyle:
        linestyle = '%s-%s' % (startstyle, endstyle)
    else:
        linestyle = ''

    """
    if startstyle in ['>','->']:
        startstyle = '<'
        if endstyle in ['>','->']:
            linestyle = '<->'
        else:
            linestyle = '<-'
    else:
        if endstyle in ['>','->']:
            linestyle = '->'
        else:
            linestyle = ''
    """
    #--------------------------------------------------------------------------
    # arrow (tip) style
    #--------------------------------------------------------------------------
    if arg.get('arrowstyle', '') != '':
        linestyle = ','.join([linestyle, ">=triangle 60"])

    #------------------------------------------------------------------------- 
    # Add 'dashed', etc to linestyle
    #-------------------------------------------------------------------------
    if arg.get('linestyle', '') != '':
        linestyle = ','.join([linestyle, arg.get('linestyle', '')])

    xs = [str(linewidth), str(color), linestyle]
    xs = [_.strip() for _ in xs if _.strip() != '']
    return ','.join(xs)

class Style:
    def __init__(self, **arg):
        self.arg = copy.deepcopy(arg)
    def __str__(self):
        return str(self.arg)
    def tikz(self):
        return get_style(**self.arg)

#==============================================================================
# Grid
#==============================================================================
def grid(x0=0, y0=0, x1=5, y1=5,
         color='gray',
         linewidth='very thin',
         dx=1, dy=1,
         fontsize='normalsize',
         label_axes=True):
    s = ''
    for x in RANGE(x0, x1+0.00001, dx):
        s += line(x0=x,y0=y0,x1=x,y1=y1,color=color, linewidth='')
    for y in RANGE(y0, y1+0.00001, dy):
        s += line(x0=x0,y0=y,x1=x1,y1=y,color=color, linewidth='')

    if label_axes:
        for x in RANGE(x0, x1+0.00001, dx):
            if x == int(x): x = int(x)
            if x0 == int(x0): x0 = int(x0)
            #if y == int(y): y = int(y)
            if y0 == int(y0): y0 = int(y0)
            s += r"\draw(%s, %s) node [font=\ttfamily, label=below:{\%s {\texttt{%s}}}] {};" % (x, y0, fontsize, x)
            s += '\n'
        for y in RANGE(y0, y1+0.00001, dy):
            if y == int(y): y = int(y)
            if y0 == int(y0): y0 = int(y0)
            s += r"\draw(%s, %s) node [font=\ttfamily, label=left:{\%s {\texttt{%s}}}] {};" % (x0, y, fontsize, y)
            s += '\n'
    return s

class Grid(BaseNode):
    def __init__(self,
                 x0=0, y0=0, x1=0, y1=0,
                 linecolor='gray',
                 linewidth='very thin',
                 linestyle='',
                 dx=1, dy=1,
                 label_axes=True,
                 fontsize='normalsize',
                 debug=True):
        x0 = round(x0, 4)
        y0 = round(y0, 4)
        x1 = round(x1, 4)
        y1 = round(y1, 4)
        BaseNode.__init__(self,
                          x0=x0, y0=y0, x1=x1, y1=y1,
                          debug=debug)
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.linecolor = linecolor
        self.dx = dx
        self.dy = dy
        self.label_axes = label_axes
        self.fontsize = fontsize
        
    def __str__(self):
        linewidth = self.linewidth
        linestyle = self.linestyle
        linecolor = self.linecolor
        x0, y0 = self.x0, self.y0
        x1, y1 = self.x1, self.y1
        dx, dy = self.dx, self.dy
        label_axes = self.label_axes
        return grid(x0=x0, y0=y0, x1=x1, y1=y1,
                    color=linecolor, linewidth=linewidth, fontsize=self.fontsize,
                    dx=dx, dy=dy, label_axes=label_axes)
        
#==============================================================================
# Circle
#==============================================================================
def circle(x=0, y=0, center=None, r=0,
           linewidth='', linestyle='', linecolor='black',
           background='', foreground='black',
           innersep=0,
           align='t', font='',
           label='', s='',
           anchor=None,
           rotate=0,
           name=None,
           ):

    if center != None: x, y = center
    x0 = x - r
    x1 = x + r
    y0 = y - r
    y1 = y + r

    # Parameters for minipage
    radius = 0 # this is the radius for the rounded corner used in rect
               # NOT used in circle.
               
    def floatlinewidth(linewidth):
        if isinstance(linewidth, str): return 0
        else: return linewidth

    h = 2 * r - 2 * floatlinewidth(linewidth)
    w = 2 * r - 2 * floatlinewidth(linewidth)
    
    # WARNING: the x,y is the center and not the bounding rect
    
    s = s.strip()
    label = label.strip()

    d = {'x':x, 'y':y, 'h':h, 'w':w,
         'background':background, 'foreground':foreground,
         'linewidth':linewidth, 'linecolor':linecolor, 'linestyle':linestyle,
         'r':r,
         'radius':radius, 'innersep':innersep, 'align':align, 's':s}

    # CHECK: d is not used later.
    # To account for thickness of border
    import copy
    d1 = copy.deepcopy(d)
    d1['w'] = d['w'] - floatlinewidth(linewidth)
    d1['h'] = d['h'] - floatlinewidth(linewidth)
    emptypage = minipage(s='', align=d1['align'], h=d1['h'], w=d1['w'])
    d1.update({'minipage':emptypage})

    ret = ''

    # Draw boundary and interior with background color
    if background != '':
        ret += r"""
\fill[%s] (%s, %s) circle (%s);
""" % (background, x, y, r)

    # change line width
    if d1['linewidth'] == '':
        pass
    else:
        d1['linewidth'] == 'line width=%scm' % d1['linewidth']

    style = get_style(linewidth=linewidth,
                      linecolor=linecolor,
                      linestyle=linestyle)
    d1['style'] = style
    d1['name'] = name
    
    # Draw boundary with boundary color
    if linecolor != '' and linewidth != 0:
        if linestyle == 'double':
            d1['r'] = r - floatlinewidth(linewidth)
        else:
            d1['r'] = r - floatlinewidth(linewidth) / 2.0
        #d1['r'] = 0.1 # TESTING ONLY

        # TODO: HOW TO COMBINE BOTH CASE BELOW?
        # TODO: HOW TO ADD ANCHOR
        if not name:
            ret += r"\draw[%(style)s] (%(x)s, %(y)s) circle (%(r)s);" % d1
        else:
            # TO TEST
            d1['r'] = 2 * d1['r'] 
            ret += r"\node [%(style)s,minimum size=%(r)scm,draw,circle] at (%(x)s,%(y)s)(%(name)s){};" % d1

    else:
        # 2018/11/01: when linecolor == '' or linewidth == 0
        if not name:
            d1['r'] = 2 * d1['r'] 
            ret += r"\node [draw=none,%(style)s,minimum size=%(r)scm,circle] at (%(x)s,%(y)s){};" % d1
        else:
            # TO TEST
            d1['r'] = 2 * d1['r'] 
            ret += r"\node [draw=none,%(style)s,minimum size=%(r)scm,circle] at (%(x)s,%(y)s)(%(name)s){};" % d1
        
    # content
    if s != '':
        length = (r - floatlinewidth(linewidth)) / 1.414 * 2.0
        d1.update({'minipage':minipage(s=s,
                                       align=d1['align'],
                                       h=length-2*innersep, w=length-2*innersep)})
        ret += r'''\draw (%(x)s,%(y)s) node[color=%(foreground)s, inner sep=%(innersep)scm] {
 %(minipage)s
};''' % d1
    elif label != '':
        # ANCHOR FOR LABEL [??]
        if anchor in [None, '']:
            d1['label'] = label
            ret += r'\draw (%(x)s, %(y)s) node[color=%(foreground)s] {%(label)s};' \
                   % d1
        else:
            d1['label'] = label
            ret += r'\draw (%(x)s, %(y)s) node[%(anchor)s,color=%(foreground)s] {%(label)s};' \
                   % d1
            
    return ret

class Circle(BaseNode):
    def __init__(self,
                 x=0, y=0, center=None, r=0,
                 linewidth='', linestyle='', linecolor='black',
                 background='', foreground='black',
                 innersep=0,
                 font='', s='', label='',
                 name=None,
                 anchor=None,
                 debug=True):
        x, y, r = myround([x, y, r]) # ROUNDING
        if center != None: x, y = center
        BaseNode.__init__(self,
                          x=x, y=y,
                          w=2*r, h=2*r,
                          x0=x-r, y0=y-r, x1=x+r, y1=y+r,
                          debug=debug)
        self.r = r
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.linecolor = linecolor
        self.background = background
        self.foreground = foreground
        self.innersep = innersep
        self.font = font
        self.s = s
        self.label = str(label)
        self.anchor = anchor
        self.name = name
    def __str__(self):
        x, y = self.center()
        r = self.r
        s = self.s # TODO: REMOVE textsf
        label = self.label
        linewidth = self.linewidth
        linestyle = self.linestyle
        linecolor = self.linecolor
        foreground = self.foreground
        background = self.background
        innersep = self.innersep
        font = self.font
        label = self.label
        name = self.name
        anchor = self.anchor
        ret = ''
        ret += BaseNode.__str__(self)
        ret += circle(x=x, y=y, r=r,
                      linewidth=linewidth,
                      linestyle=linestyle,
                      linecolor=linecolor,
                      background=background,
                      foreground=foreground,
                      innersep=innersep,
                      font=font,
                      s=s,
                      label=label,
                      anchor=anchor,
                      name=name,
                      )
        return ret
#==============================================================================
# Ellipse
#==============================================================================
def ellipse(x0=0,y0=0,x1=0,y1=0,
            center=None, width=None, height=None,
            background='white', foreground='black',
            linewidth='', linestyle='', linecolor='black',
            innersep=0,
            align='t', font='',
            name='', label='', s='', double=False, double_distance=0.08):
    # incomplete ... see circle
    if center!=None:
        x, y = center
        w, h = width, height
    else:
        x = (x0 + x1)/2.0; y = (y0 + y1)/2.0
        w = (x1 - x0); h = (y1 - y0)

    x = round(x, 3)
    y = round(y, 3)
    w = round(w, 3)
    h = round(h, 3)
    
    s = s.strip()
    label = label.strip()

    d = {'x':x, 'y':y, 'h':h, 'w':w,
         'background':background, 'foreground':foreground,
         'linewidth':linewidth, 'linecolor':linecolor, 'linestyle':linestyle,
         'double':double,
         'innersep':innersep, 'align':align, 's':s, 'label':label}
    
    import copy
    def floatlinewidth(linewidth):
        if linewidth==None or linewidth=='': return ''
        else: return linewidth

    d1 = copy.deepcopy(d)
    d1['w'] = d['w'] # - floatlinewidth(linewidth)
    d1['h'] = d['h'] # - floatlinewidth(linewidth)
    emptypage = minipage(s='', align=d1['align'], h=d1['h'], w=d1['w'])
    d1.update({'minipage':emptypage})
    
    # change line width
    if d1['linewidth'] == '':
        pass
    elif isinstance(d1['linewidth'], float):
        d1['linewidth'] = 'line width=%scm' % d1['linewidth']
    if d1['double']:
        d1['double'] = 'double, double distance=%scm' % double_distance
    else:
        d1['double'] = ''
    style = get_style(linewidth=linewidth,
                      linecolor=linecolor,
                      linestyle=linestyle)
    d1['style'] = style
    d1['name'] = name
    ret = r'''\node[draw,shape=ellipse,
minimum height=%(h)scm,minimum width=%(w)scm,inner sep=%(innersep)s,
fill=%(background)s,
%(double)s,
%(linewidth)s, %(linestyle)s] (%(name)s) at (%(x)s,%(y)s) {%(label)s};''' % d1
    return ret

#==============================================================================
# Diamond (for ER diagram)
#==============================================================================
def diamond(center=(0,0),width=4,height=2,label='',name='',
            linewidth=0.01,background='white',innersep=0, linestyle='',
            double=False, double_distance=0.08):
    x,y = center
    d1 = {'h':height, 'w':width, 'x':x, 'y':y, 'name':name,
          'background':background,
          'label':label,'linewidth':linewidth, 'double':double}
    # change line width
    if d1['linewidth'] == '':
        pass
    elif isinstance(d1['linewidth'], float):
        d1['linewidth'] = 'line width=%scm' % d1['linewidth']
    
    if d1['double']:
        d1['double'] = 'double, double distance=%scm' % double_distance
    else:
        d1['double'] = ''
    
    d1['innersep'] = 'inner sep=0'
    ret = r'''\node[draw,shape=diamond,
    minimum height=%(h)scm,minimum width=%(w)scm,
    fill=%(background)s,
    %(innersep)s,
    %(double)s, aspect=1.5, 
    %(linewidth)s] (%(name)s) at (%(x)s,%(y)s) {%(label)s};''' % d1

    # double distance does not work ... manually draw anther diamond below
    #if d1['double']:
    #    ratio = float(d1['w']) / d1['h']
    #    d1['h'] = d1['h'] - double_distance * 2.0 / ratio
    #    d1['w'] = d1['w'] - double_distance * 2.0
    #ret += r'''\node[draw,shape=diamond,
    #minimum height=%(h)scm,minimum width=%(w)scm,
    #fill=%(background)s,
    #%(double)s,
    #%(innersep)s,
    #%(linewidth)s] (%(name)s) at (%(x)s,%(y)s) {%(label)s};''' % d1
        
    return ret
    


#==============================================================================
def tabrect(x0=0, y0=0, x1=1, y1=1,
            linewidth=L, linecolor='black', linestyle='',
            background='white', foreground='black',
            innersep=0, radius=0,
            align='t', 
            s='',
            #
            #tab data
            ):
    ret = ''
    h = 0.8
    w = 2.5
    ret += r"""
    \draw (%s,%s) node[style=rounded corners, draw, line width=1, fill=blue!40, rotate=90] {
\begin{minipage}[t][%scm]{%scm}
\begin{flushleft}
\textsf{\scriptsize INTERMEDIATE}
\end{flushleft}
\end{minipage}
};""" % (x0, y0 + w/2.0 + 1, h, w)
    ret += rect(x0=x0, y0=y0, x1=x1, y1=y1,
             linewidth=linewidth, linecolor=linecolor, linestyle=linestyle,
             background=background, foreground=foreground,
             innersep=0.2, radius=0.5,
             align=align, 
             s=s)
    return ret

#==============================================================================
# Rect
#==============================================================================
def rect(x0=None, y0=None, x1=None, y1=None,
         x=None, y=None, w=None, h=None,
         linewidth='', linecolor='black', linestyle='',
         background='', foreground='black',
         innersep=0.0, radius=0.0,
         align='t', font='',
         label='',
         s=' ',
         rotate=0,
         name=None,
         ):
        
    if x0 != None:
        x = (x0 + x1) / 2.0
        y = (y0 + y1) / 2.0
        w = (x1 - x0) - 2 * innersep
        h = (y1 - y0) - 2 * innersep

    s = str(s).strip()
    label = str(label).strip()
    
    d = {'x':x, 'y':y, 'h':h, 'w':w,
         'background':background, 'foreground':foreground,
         'linewidth':linewidth, 'linecolor':linecolor, 'linestyle':linestyle,
         'radius':radius, 'innersep':innersep, 'align':align, 's':s}

    # To account for thickness of border
    import copy
    d1 = copy.deepcopy(d)
    d1['w'] = d['w'] - IFELSE(isinstance(linewidth,str), 0, linewidth)
    d1['h'] = d['h'] - IFELSE(isinstance(linewidth,str), 0, linewidth)
    emptypage = minipage(s='', align=d1['align'], h=d1['h'], w=d1['w'])
    d1.update({'minipage':emptypage})
    d1['name'] = name
    ret = ''

    if background != '':
        ret += r'''
\draw (%(x)s, %(y)s)
  node[fill=%(background)s,rounded corners=%(radius)scm,inner sep=%(innersep)scm] {
%(minipage)s
};''' % d1

    if d1['linewidth']=='': pass
    else: d1['linewidth'] = 'line width=%scm' % d1['linewidth']

    # border
    if linewidth != 0:
        if not name:
            ret += r'''
\draw (%(x)s, %(y)s)
  node[draw, %(linewidth)s, %(linestyle)s, color=%(linecolor)s,
       rounded corners=%(radius)scm, inner sep=%(innersep)scm] {
%(minipage)s
};''' % d1
        else:
            ret += r'''
\draw (%(x)s, %(y)s)
  node[draw, %(linewidth)s, %(linestyle)s, color=%(linecolor)s,
       rounded corners=%(radius)scm, inner sep=%(innersep)scm,
       name=%(name)s] {
%(minipage)s
};''' % d1
    else:
        if not name:
            ret += r'''
\draw (%(x)s, %(y)s)
  node[draw=none, %(linewidth)s, %(linestyle)s, color=%(linecolor)s,
       rounded corners=%(radius)scm, inner sep=%(innersep)scm] {
%(minipage)s
};''' % d1
        else:
            ret += r'''
\draw (%(x)s, %(y)s)
  node[draw=none, %(linewidth)s, %(linestyle)s, color=%(linecolor)s,
       rounded corners=%(radius)scm, inner sep=%(innersep)scm,
       name=%(name)s] {
%(minipage)s
};''' % d1
    
    
            

    # content
    if s != '':
        d1.update({'minipage':minipage(s=s,
                                       align=d1['align'],
                                       h=d1['h'], w=d1['w'])})
        ret += r'''
\draw (%(x)s, %(y)s) node[color=%(foreground)s,
 inner sep=%(innersep)scm] {
 %(minipage)s
};''' % d1
    elif label != '':
        d1['label'] = label
        ret += r'\draw (%(x)s, %(y)s) node[color=%(foreground)s] {%(label)s};' % d1

    return ret



class Rect(BaseNode):
    def __init__(self,
                 x0=0, y0=0, x1=0, y1=0,
                 linewidth='', linestyle='', linecolor='black',
                 background='', foreground='black',
                 innersep=0, radius=0,
                 align='t', font='', s='', label='',
                 rotate=0,
                 debug=True,
                 name=None):
        BaseNode.__init__(self,
                          x0=x0, y0=y0, x1=x1, y1=y1,
                          debug=debug)
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.linecolor = linecolor
        self.background = background        
        self.foreground = foreground
        self.font = font
        self.s = str(s)
        self.label = str(label)
        self.innersep = innersep
        self.radius = radius
        self.align = align
        self.rotate=rotate
        self.name = name
    def __str__(self):
        x0 = self.x0
        y0 = self.y0
        x1 = self.x1
        y1 = self.y1
        align = self.align
        font = self.font
        s = self.s
        label = self.label
        linewidth = self.linewidth
        linestyle = self.linestyle
        linecolor = self.linecolor
        background, foreground = self.background, self.foreground
        innersep, radius = self.innersep, self.radius
        rotate = self.rotate
        name = self.name
        ret = ''
        ret += BaseNode.__str__(self)
        ret += rect(x0=x0, y0=y0, x1=x1, y1=y1,
                    linewidth=linewidth, linestyle=linestyle, linecolor=linecolor,
                    background=background, foreground=foreground,
                    innersep=innersep, radius=radius,
                    align=align, font=font, s=s, label=label,
                    rotate=rotate,
                    name=name)
        return ret

class BlankRect(Rect):
    # blank rect that acts as a spacing
    def __init__(self, x0=0, y0=0, x1=0, y1=0):
        Rect.__init__(self,
                      x0=x0, y0=y0, x1=x1, y1=y1,
                      linewidth=0.0, linestyle='', linecolor='',
                      background='', foreground='',
                      innersep=0, radius=0,
                      align='t', font='', s='', label='',
                      rotate=0)
    
class Rect2(Rect):
    # This is really the same as Rect except that the boundary line
    # is 1/2 in the rect and 1/2 out.
    # This is used for arrays (for instance) or anything that
    # requires overlapping boundary.
    def __init__(self,
                 x0=0, y0=0, x1=0, y1=0,
                 linewidth=L, linestyle='', linecolor='black',
                 background='', foreground='black',
                 innersep=0, radius=0,
                 align='t', font='', s='', label='',
                 rotate=0,
                 debug=True):
        Rect.__init__(self, x0=x0, y0=y0, x1=x1, y1=y1,
                      linewidth=linewidth,
                      linestyle=linestyle,
                      linecolor=linecolor,
                      background=background,
                      foreground=foreground,
                      innersep=innersep, radius=radius,
                      align=align, font=font, s=s, label=label,
                     rotate=rotate,
                      debug=debug)
    def floatlinewidth(self):
        if isinstance(self.linewidth, str): return 0
        else: return self.linewidth
    def height(self): return (self.x1 - self.x0)  + self.floatlinewidth()
    def width(self): return (self.y1 - self.y0)  + self.floatlinewidth()
    def topy(self): return self.y1 + self.floatlinewidth()/2.0
    def top(self): return self.centerx(), self.topy()
    def bottomy(self): return self.y0 - self.floatlinewidth()/2.0
    def bottom(self): return self.centerx(), self.bottomy()
    def leftx(self): return self.x0 - self.floatlinewidth()/2.0
    def left(self): return self.leftx(), self.centery()
    def rightx(self): return self.x1 + self.floatlinewidth()/2.0
    def right(self): return self.x1 + self.floatlinewidth()/2.0, self.centery()
    def topleft(self): return self.leftx(), self.topy()
    def topright(self): return self.rightx(), self.topy()
    def bottomleft(self): return self.leftx(), self.bottomy()
    def bottomright(self): return self.rightx(), self.bottomy()
    def __str__(self):
        x0, y0 = self.x0, self.y0
        x1, y1 = self.x1, self.y1
        linestyle = self.linestyle
        linecolor = self.linecolor
        background = self.background
        foreground = self.foreground
        innersep = self.innersep
        radius = self.radius
        align = self.align
        font = self.font
        s = self.s
        label = self.label
        rotate = self.rotate
        debug = self.debug
        L = self.floatlinewidth() / 2.0
        r = Rect(x0=x0-L, y0=y0-L, x1=x1+L, y1=y1+L,
                 linewidth=self.linewidth,
                 linestyle=linestyle,
                 linecolor=linecolor,
                 background=background,
                 foreground=foreground,
                 innersep=innersep, radius=radius,
                 align=align, font=font, s=s, label=label,
                 rotate=rotate,
                 debug=debug)
        return str(r)

class Rect2NoLeftRight(Rect2):
    def __init__(self,
                 x0=0, y0=0, x1=0, y1=0,
                 linewidth='', linestyle='', linecolor='black',
                 background='', foreground='black',
                 innersep=0, radius=0,
                 align='t', font='', s='', label='',
                 rotate=0,
                 debug=True):
    
        Rect2.__init__(self, x0=x0, y0=y0, x1=x1, y1=y1,
                       linewidth=linewidth, linestyle=linestyle,
                       linecolor=linecolor,
                       background=background, foreground=foreground,
                       innersep=innersep, radius=radius,
                       align=align, font=font, s=s, label=label,
                       rotate=rotate,
                       debug=debug)
    def __str__(self):
        x0, y0 = self.x0, self.y0
        x1, y1 = self.x1, self.y1
        linestyle = self.linestyle
        linewidth= self.linewidth
        linecolor = self.linecolor
        background = self.background
        foreground = self.foreground
        innersep = self.innersep
        radius = self.radius
        align = self.align
        font = self.font
        s = self.s
        label = self.label
        rotate = self.rotate
        debug = self.debug
        L = self.floatlinewidth() / 2.0
        ret = str(Line(x0=x0-L, y0=y1, x1=x1+L, y1=y1,
                     linewidth=linewidth, linestyle=linestyle,
                     linecolor=linecolor))
        ret += str(Line(x0=x0-L, y0=y0, x1=x1+L, y1=y0,
                     linewidth=linewidth, linestyle=linestyle,
                     linecolor=linecolor))
        ret += str(Rect2(x0=x0, y0=y0, x1=x1, y1=y1,
                       linewidth=0, 
                       background=background, foreground=foreground,
                       innersep=innersep, radius=radius,
                       align=align, font=font, s=s, label=label,
                       rotate=rotate,
                       debug=debug))
        return ret
        
# Containers:
#   - can have bounding box and all objects placed in box
#   - can be no bounding box (no limit) but still need to specify starting
#     x0,y0
# x,y = a reference point for drawing the collection
# rects = list of rects
# direction and align = for drawing
#
# Rects' drawn positions are with respect to (x,y)
#
# Adding to container:
#   - left-to-right, top-to-bottom (for bounding box case)
#   - left-to-right (no bounding box case)
#   - for the time being ignore right-to-left or bottom-to-top
#   - can align rects by their bottoms, middles, tops
#   - default is align by bottom
class RectContainer(BaseNode):
    def __init__(self,
                 x=0, y=0,
                 debug=False,
                 align='bottom',
                 direction='left-to-right',
                 name=None,
                 ):
        # x0,y0,x1,y1 is the rect area of this container
        BaseNode.__init__(self,
                          x0=x, y0=y, x1=x, y1=y,
                          debug=debug)
        self.rects = []
        self.x = x
        self.y = y
        self.direction = direction
        self.align = align
        self.name = name
    def layout(self):
        # First layout the rects using x,y and direction and align.
        direction = self.direction
        align = self.align
        x, y = self.x, self.y
        self.x0 = self.x1 = x
        self.y0 = self.y1 = y
        
        for r in self.rects:
            w = r.x1 - r.x0
            h = r.y1 - r.y0
        
            if direction == 'left-to-right':
                r.x0 = x
                r.x1 = x + w
                self.x1 = x = r.x1
                if self.align == 'bottom':
                    r.y0 = y
                    r.y1 = y + h
                    self.y1 = max(self.y1, r.y1)
                elif self.align == 'top':
                    r.y1 = y
                    r.y0 = y - h
                    self.y0 = min(self.y0, r.y0)
            elif direction == 'top-to-bottom':
                r.y1 = y
                r.y0 = y - h
                y = r.y0
                if self.align == 'left':
                    r.x0 = x
                    r.x1 = r.x0 + w
                    self.x1 = max(self.x1, r.x1)
                    self.y0 = r.y0
                elif self.align == 'right':
                    r.x1 = x
                    r.x0 = r.x1 - w
                    self.x0 = min(self.x0, r.x0)
                    self.y0 = r.y0
        self.x0 = min([r.x0 for r in self.rects])
        self.y0 = min([r.y0 for r in self.rects])
        self.x1 = max([r.x1 for r in self.rects])
        self.y1 = max([r.y1 for r in self.rects])
    def __iadd__(self, r):
        self.rects.append(r)
        self.layout()
        return self
    def __getitem__(self, i):
        i = int(i) # ERROR: 2021/1/28 python2-3 error. This is called with float
        return self.rects[i]
    def __setitem__(self, i, r):
        self.rects[i] = r
    def __str__(self):
        s = ''
        x0s = []; x1s = []; y0s = []; y1s = []
        for rect in self.rects:
            x0s.append(rect.left()[0])
            x1s.append(rect.right()[0])
            y0s.append(rect.bottom()[1])
            y1s.append(rect.top()[1])
            s += str(rect)
        x0 = min(x0s); x1 = max(x1s)
        y0 = min(y0s); y1 = max(y1s)
        #print "(self.name: %s" % self.name)
        if self.name != None:
            s += ';\n'
            s0 = str(Rect(x0=x0, y0=y0, x1=x1, y1=y1,
                          linewidth=0, name=self.name, label=' '))
            s += s0
        return s


def RectAdaptor(**karg):
    env = karg.get('env', {})
    env.update(karg)
    x0 = env.get('x0', 0)
    y0 = env.get('y0', 0)
    x1 = env.get('x1', 0)
    y1 = env.get('y1', 0)
    linewidth = env.get('linewidth', L)
    linestyle = env.get('linestyle', '')
    linecolor = env.get('linecolor', 'black')
    background = env.get('background', '')
    foreground = env.get('foreground', 'black')
    innersep = env.get('innersep', 0)
    radius = env.get('radius', 0)
    align = env.get('align', 't')
    font = env.get('font', '')
    s = env.get('s', '')
    rotate = env.get('rotate', 0)
    debug = env.get('debug', True)
    return Rect(x0=x0, y0=y0, x1=x1, y1=y1,
                linewidth=linewidth, linestyle=linestyle, linecolor=linecolor,
                background=background, foreground=foreground,
                innersep=innersep, radius=radius,
                align=align, font=font, s=s,
                rotate=rotate,
                debug=debug)

#==============================================================================
# Snipped Array
# TODO: Add width, height [DONE]
#==============================================================================
class SnippedArray(RectContainer):

    def __init__(self, x=0, y=0,
                 xs=[],
                 linewidth=L,
                 width=1, height=1,
                 snippedstring='...'):
        RectContainer.__init__(self, x=x, y=y)
        for i,x in enumerate(xs):
            if x != snippedstring:
                self += Rect2(x0=0, y0=0, x1=width, y1=height,
                              linewidth=linewidth,
                              label=r'{\texttt{%s}}' % x)
            else:
                if 0 < i < len(xs) - 1:
                    self += Rect2(x0=0, y0=0, x1=width*1.5, y1=height,
                                  linewidth=linewidth, label=x)
                else:
                    self += Rect2NoLeftRight(x0=0, y0=0, x1=width*1.5,
                                             y1=height, label=x,
                                             linewidth=linewidth)
        self.layout()
        
#==============================================================================
# Cross
#==============================================================================

def cross(x0, y0, x1, y1, color='', linewidth=""):
    style = get_style(linewidth=linewidth, color=color)
    return r"""
\draw[%(style)s] (%(x0)s, %(y0)s) -- (%(x1)s, %(y1)s);
\draw[%(style)s] (%(x0)s, %(y1)s) -- (%(x1)s, %(y0)s);
""" % {'x0':x0, 'y0':y0, 'x1':x1, 'y1':y1, 'style':style}

def crossed_rect(x0, y0, x1, y1, linewidth='', color=''):
    s = rect(x0, y0, x1, y1, linewidth=linewidth, color=color)
    s += line(x0, y0, x1, y1, linewidth=linewidth, color=color)
    s += line(x0, y1, x1, y0, linewidth=linewidth, color=color)
    return s

class CrossedRect2(Rect2):
    def __init__(self,
                 x0=0, y0=0, x1=0, y1=0,
                 linewidth='', linestyle='', linecolor='black',
                 background='', foreground='black',
                 innersep=0, radius=0,
                 align='t', font='', s='', label='',
                 rotate=0,
                 debug=True):
        Rect2.__init__(self,
                       x0=x0, y0=y0, x1=x1, y1=y1,
                       linewidth=linewidth, linestyle=linestyle, linecolor=linecolor,
                       background=background, foreground=foreground,
                       innersep=innersep, radius=radius,
                       align=align, font=font, s=s, label=label,
                       rotate=rotate,
                       debug=debug)
    def __str__(self):
        s = Rect2.__str__(self)
        linecolor = self.linecolor
        linewidth = self.linewidth
        (x0, y0), (x1, y1) = self.topleft(), self.bottomright()
        s += str(Line(x0, y0, x1, y1, linecolor=linecolor, linewidth=linewidth))
        (x0, y0), (x1, y1) = self.topright(), self.bottomleft()
        s += str(Line(x0, y0, x1, y1, linecolor=linecolor, linewidth=linewidth))
        return s
#==============================================================================
# Line
# label the line ... should this be parameter label or s?
#==============================================================================
def line(x0=0, y0=0, x1=0, y1=0,
         points=None,
         linecolor='black',
         linewidth='',
         linestyle = '', # solid, dash, etc
         color='', # DEPRECATED
         startstyle = '', # "->", ".", etc.
         arrowstyle = '',
         endstyle = '',
         r=0,
         names=None, # using tikz node names
         bend_left=None,
         bend_right=None,
         label=None,
         #s=None,
         anchor=None,
         controls=None,
         loop=None, # 2020/06/03: note: only when names are the same
         ):
    if color != '': linecolor = color
    if color == '' and linecolor != '': color=linecolor
    style = get_style(linewidth=linewidth,
                      color=color,
                      startstyle=startstyle,
                      linestyle=linestyle,
                      arrowstyle=arrowstyle,
                      endstyle=endstyle)

    # 2020/06/03: If the two names in names are the same, use loop
    #             But would need "loop left", "loop right", "loop above"
    #
    
    if points == None:
        points = [(x0,y0),(x1,y1)]
    if names:
        s = ["(%s)" % _ for _ in names]
    else:
        s = ["(%s,%s)" % (x,y) for x,y in points]
    #--------------------------------------------------------------------------
    # label
    #--------------------------------------------------------------------------
    if anchor == None: anchor = 'above'
    if label in ['', None]:
        label = ''
    else:
        label = 'node [%s] {%s}' % (anchor, label)
    #--------------------------------------------------------------------------
    # Form " to " with bend
    #--------------------------------------------------------------------------
    if controls == None:
        if bend_left == None and bend_right == None:
            bend_left = 0
        if bend_left:
            if loop:
                s = (" to [bend left=%s, %s] %s " % (bend_left, loop, label)).join(s)
            else:
                s = (" to [bend left=%s] %s " % (bend_left, label)).join(s)
        elif bend_right:
            if loop:
                s = (" to [bend left=%s, %s] %s " % (bend_right, loop, label)).join(s)
            else:
                s = (" to [bend right=%s] %s " % (bend_right, label)).join(s)
        else:        
            s = (" to %s " % (label,)).join(s)
    else: # use control points
        if isinstance(controls, tuple):
            controls = [controls]
        x = 'and'.join([str(_) for _ in controls])
        x = '..controls' + x + '.. ' + label
        # INCOMPLETE
        s = x.join(s)
        
    #--------------------------------------------------------------------------
    # Form label of line with anchor
    #--------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------
    # Complete the tikz command
    #--------------------------------------------------------------------------
    s = r"\draw[%s] %s;" % (style, s); s += '\n'
    #--------------------------------------------------------------------------
    # Handle case of drawing a dot at the beginning of end of line
    #--------------------------------------------------------------------------
    if isinstance(linewidth, (int, float)):
        if linewidth != 0:
            if r <= 0:
                r = 0
            elif r <= 0.5 * linewidth:
                r = 1.5 * linewidth
            else:
                pass
        else:
            r = 0.05 # hardcoded
    else:
        r = 0.05 # hardcoded
    if startstyle in ['.', 'dot']:
        x, y = points[0]
        s += circle(x=x, y=y, r=r,
                    linecolor=linecolor, background=linecolor)
    if endstyle in ['.', 'dot']:
        x, y = points[-1]
        s += circle(x=x, y=y, r=r,
                    linecolor=linecolor, background=linecolor)
    return s


def midpoint(p0, p1, ratio=0.5):
    if ratio < 0: ratio = 0.0
    if ratio > 1: ratio = 1.0
    #print ("midpoint ... p0: %s" % p0)
    #print ("midpoint ... p1: %s" % p1)
    v = [p1[0] - p0[0], p1[1] - p0[1]]
    #print ("v:" % v)
    #l = length(p0, p1)
    v = [v[0] * ratio, v[1] * ratio]
    p2 = [p0[0] + v[0], p0[1]+ v[1]]
    return p2

def length(p0, p1):
    from math import sqrt
    x0, y0 = p0
    x1, y1 = p1
    return sqrt((x1 - x0)**2 + (y1 - y0)**2)

class Line(BaseNode):
    """Line(
    x0=0, y0=0, x1=0, y1=0,
    points=None,
    linecolor='black',
    linewidth='',
    linestyle='',
    startstyle='',
    endstyle='',
    r=0,                    # radius of dot at start or end of line
)

    TODO: Path class

    """
    def __init__(self,
                 x0=0, y0=0, x1=0, y1=0,
                 points=None,
                 startstyle = '', # "->", ".", etc.
                 arrowstyle = '',
                 endstyle = '',
                 linestyle = '', # solid, dashed, etc
                 linecolor='black',
                 linewidth=L,
                 r=0,
                 names=None,
                 debug=False,
                 bend_left=None,
                 bend_right=None,
                 anchor=None,
                 label=None,
                 controls=None,
                 loop=None, # 2020/06/03
    ):
        points = myround(points) # WARNING: rounding ... need to test more
        #print ("points: %s" % points)
        if points not in [None, []]:
            x0 = min([i for i,j in points])
            x1 = max([i for i,j in points])
            y0 = min([j for i,j in points])
            y1 = max([j for i,j in points])
        BaseNode.__init__(self,
                          x0=x0, y0=y0, x1=x1, y1=y1,
                          x=(x0+x1)/2.0, y=(y0+y1)/2.0,
                          w=(x1-x0), h=(y1-y0),
                          debug=debug)
        self.points = points
        self.startstyle=startstyle
        self.endstyle=endstyle
        self.arrowstyle=arrowstyle
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.linecolor = linecolor
        self.r = float(r)
        self.names = names
        self.bend_left = bend_left
        self.bend_right = bend_right
        self.label = label
        self.anchor = anchor
        self.controls = controls
        self.loop = loop
    def __length(self):
        startpoints = self.points[:-1]
        endpoints = self.points[1:]
        return sum([length(p,q) for p,q in zip(startpoints, endpoints)])
    
    def midpoint(self, ratio=0.5):
        """
                a         b
        <--------------><--->
        p---q----r-----s----------t----------u
                       <---------->
                             c
        <------------------------------------>
            l
            
        r = (a + b) / l    (l = total length)
        r * l = a + b
        r * l - a = b
        b/c = (r * l - a)/c
        """
        totallength = float(self.__length())
        startpoints = self.points[:-1]
        endpoints = self.points[1:]

        if ratio < 0: ratio = 0.0
        if ratio > 1: ratio = 1.0
        if ratio==0.0: return self.points[0]
        if ratio==1.0: return self.points[-1]
        prevsum = 0.0
        prevp = self.points[0]
        prevq = self.points[1]
        s = 0.0
        #print ("totallength:" % totallength)
        for p,q in zip(startpoints, endpoints):
            #print ()
            #print ("p:" % p)
            #print ("q:" % q)
            prevsum = s
            #print ("prevsum:" % prevsum)
            s += length(p,q)
            #print ("s:" % s)
            if s / totallength > ratio:
                #print ("break")
                break
            prevp = p
            prevq = q
        #print ("p: %s" % p)
        #print ("q: %s" % q)
        #print ("ratio: %s" % ratio)
        #print ("totallength: %s" % totallength)
        #print ("prevsum: %s" % prevsum)
        #print ("length(p,q): %s" % length(p, q))
        #print ("new ratio: %s" % (ratio*totallength - prevsum) / length(p,q))
        return midpoint(p, q,
                        ratio=(ratio*totallength - prevsum) / length(p,q)
                        )
        
    def __str__(self):
        x0 = self.x0
        y0 = self.y0
        x1 = self.x1
        y1 = self.y1
        points = self.points
        startstyle = self.startstyle
        endstyle = self.endstyle
        arrowstyle = self.arrowstyle
        linewidth = self.linewidth
        linestyle = self.linestyle
        linecolor = self.linecolor
        anchor = self.anchor
        label = self.label
        controls = self.controls
        loop = self.loop
        r = self.r
        names = self.names
        bend_left = self.bend_left
        bend_right = self.bend_right
        ret = ''
        ret += BaseNode.__str__(self)
        ret += line(x0=x0, y0=y0, x1=x1, y1=y1,
                    points=points,
                    startstyle=startstyle,
                    arrowstyle=arrowstyle,
                    endstyle=endstyle,
                    linestyle=linestyle,
                    linecolor=linecolor,
                    linewidth=linewidth,
                    r=r,
                    names=names,
                    bend_left=bend_left,
                    bend_right=bend_right,
                    anchor=anchor,
                    label=label,
                    controls=controls,
                    loop=loop)
        return ret

class vector(Line):
    def __init__(self, p, q,
                 linewidth=L, linecolor='black', linestyle='',
                 label=None, anchor=None):
        Line.__init__(self,
                      points=[p,q],
                      linewidth=linewidth,
                      linecolor=linecolor,
                      linestyle=linestyle,
                      endstyle='>',
                      arrowstyle='triangle')
        self.__p = p
        self.__q = q
        # not using the anchor and label in Line class
        # maybe those should be changed
        # '__' to make these attributes inaccessible to Line
        self.__anchor = anchor 
        self.__label = label   
    def __str__(self):
        s = '%s' % Line.__str__(self)
        t = ''
        label = self.__label
        if label:
            import latexcircuit as lc
            x = (self.__p[0] + self.__q[0]) / 2.0 # midpoint of vector
            y = (self.__p[1] + self.__q[1]) / 2.0
            p, q = self.__p, self.__q
            anchor = self.__anchor
            if not anchor:
                dx = q[0] - p[0]
                dy = q[1] - p[1]
                if dx == 0:
                    if random.choice([0,1]) == 0:
                        anchor = 'west'
                    else:
                        anchor = 'east'
                elif dy == 0:
                    if random.choice([0,1]) == 0:
                        anchor = 'north'
                    else:
                        anchor = 'south'
                else:
                    if float(dy)/dx > 0:
                        if random.choice([0,1]) == 0:
                            anchor = 'south east'
                        else:
                            anchor = 'north west'
                    else:
                        if random.choice([0,1]) == 0:
                            anchor = 'south west'
                        else:
                            anchor = 'north east'
            X = lc.POINT(x=x, y=y, r=0, label=label, anchor=anchor)
            t += str(X)
        return '%s\n%s' % (s, t)

#==============================================================================
# Arc
# Note that (x,y) is the starting point and not the center.
#==============================================================================
def arc(x=0, y=0, r=0, angle0=0, angle1=0,
        center=None,
        linewidth='', color='', linecolor='', linestyle='',
        endstyle='',
        startstyle='',
        ):
    if center != None:
        x0,y0 = center
        x = x0 + r * cos(angle0 * 180/math.pi)
        y = y0 + r * sin(angle0 * 180/math.pi)
    if linecolor!='': color=linecolor
    style = get_style(linewidth=linewidth, color=color, linestyle=linestyle)
    if endstyle == '':
        if startstyle == '':
            return r"\draw[%s] (%s,%s) arc (%s:%s:%s);" % \
                   (style, x, y, angle0, angle1, r)
        elif startstyle =='>':
            return r"\draw[<-,%s] (%s,%s) arc (%s:%s:%s);" % \
                   (style, x, y, angle0, angle1, r)
    elif endstyle == '>':
        if startstyle=='':
            return r"\draw[%s,->] (%s,%s) arc (%s:%s:%s);" % \
                   (style, x, y, angle0, angle1, r)
        elif startstyle=='>':
            return r"\draw[%s,<->] (%s,%s) arc (%s:%s:%s);" % \
                   (style, x, y, angle0, angle1, r)
    
def text(x=0, y=0, s='', color='', font=r'\ttfamily'):
    return r"""\draw[%s, font=%s] (%s, %s) node {%s};
""" % (color, font, x, y, s)

def boxed_text(x0, y0, x1, y1, label):
    # DEPRECATED: Use rect and Rect instead
    s = rect(x0, y0, x1, y1)
    x2, y2 = (x0+x1)/2.0, (y0+y1)/2.0
    s += text(x2, y2, label)
    return s


#==============================================================================
# Pointer
#==============================================================================
def pointer(points, color='', radius=0.1):
    # points is a list of (x,y).
    # This draws a line with endpoints from points.
    # A filled circle of radius of radius 0.1cm.
    s = circle(points[0][0], points[0][1], radius=radius)
    
    if color != '': color = ',' + color
    s += r"\draw[-> %s] (%s, %s)" %  (color, points[0][0], points[0][1])
    for point in points[1:]:
        s += " -- (%s, %s)" % (point[0], point[1])
        s += ";\n"
    return s

class Pointer(Line):
    def __init__(self,
                 x0=0, y0=0, x1=0, y1=0,
                 points=None,
                 linestyle = '', # solid, dashed, etc
                 linecolor='black',
                 linewidth=POINTER_LINEWIDTH,
                 arrowstyle='',
                 r=None,
                 label=None,
                 anchor=None,
                 debug=False):
        if r==None: r = 1.5 * linewidth
        Line.__init__(self,
                      x0=x0, y0=y0, x1=x1, y1=y1,
                      points=points,
                      startstyle='dot', 
                      endstyle='->',
                      arrowstyle=arrowstyle,
                      linestyle=linestyle,
                      linecolor=linecolor,
                      linewidth=linewidth,
                      label=label,
                      anchor=anchor,
                      r=r,
                      debug=False)


    
def get_points(x0=0, y0=0, x1=0, y1=0, style='hbroom', delta=0.0):
    """
    style:
        'vbroom':
                     |
                     +-----+
                           |
        'hbroom'
    """
    if style == 'hbroom':
        x3,y3 = x1,y1
        x1,y1 = (x0+x3)/2.0,y0; x1 += delta
        x2,y2 = x1,y3
        return [[x0,y0],[x1,y1],[x2,y2],[x3,y3]]
    elif style == 'vbroom':
        x3,y3 = x1,y1
        x1,y1 = x0,(y0+y3)/2.0; y1 += delta
        x2,y2 = x3,y1
        return [[x0,y0],[x1,y1],[x2,y2],[x3,y3]]
    return points

#==============================================================================
# attach points
# the following computes starting/ending points of edges
# the points are on the boundary of the shapes
# any point on the boundary can be returned.
# however there are special points: top, bottom, left, right, topright, etc.
#==============================================================================
def get_edge(x0=0, y0=0, x1=0, y1=0, 
             width=0, height=0, radius=0,
             node_shape='rect'):
    # returns a,b,c,d where (a,b), (c,d) are points of the edge
    # joining the two nodes with given data
    if node_shape == 'rect':
        if y0 - height/2.0 > y1 + height / 2.0:
            # pointing down
            return x0, y0 - height/2.0, x1, y1 + height/2.0
        elif y0 + height/2.0 < y1 - height / 2.0:
            # pointing up
            return x0, y0 + height / 2.0, x1, y1 - height / 2.0
        else:
            # sideways
            return x0 + width / 2.0, y0, x1 - width / 2.0, y1
    elif node_shape == 'circle':
        source = x0, y0
        target = x1, y1
        # compute intersection of line st and circle about s
        st = [target[0] - source[0], target[1] - source[1]]
        length = math.sqrt(st[0]**2 + st[1]**2)
        u = [st[0]/length, st[1]/length]
        s1 = [source[0] + radius * u[0], source[1] + radius * u[1]]
        # compute intersection of line ts and circle about t
        ts = [-st[0], -st[1]]
        u = [-u[0], -u[1]]
        t1 = [target[0] + radius * u[0], target[1] + radius * u[1]]
        return s1[0], s1[1], t1[0], t1[1]

def tree2(edges=[],
          label={},
          node_constructor=None):
    """
    Want to take tree of edges and let the function position the
    nodes.

    edges = {'A':['B','C','D'],
             'B':['E','F','G'],
            }

    label = {'A':'$a$'}

    Note: the graph might be a forest.
    
    1. Find all leaves
    
    """

    # vertices
    vertices = []
    for k, v in edges.items():
        if k not in vertices: vertices.append(k)
        for x in v:
            if x not in vertices: vertices.append(x)
        
    #print ("vertices: %s" % vertices)

    for v in vertices:
        if v not in edges.keys():
            edges[v] = []
    
    label_keys = label.keys()
    for k in v:
        if k not in label_keys: label[k] = k
    
    s = ''
    return s

def tree(pos, # return value from function positions
         width = 0.5,
         height = 0.5, # assume rect
         edges = [], # list of [name1, name2] where name1, name2 are keys in
                # positions or [name1:[name2,name3,name4]
         hor_sep = 0.25, # min horizontal separation between rect boundaries
         node_shape = 'circle',
         node_label = None,
         radius = 0.25,
         autoadjust=False,
         ):
    keys = pos.keys()
    if node_label == None:
        node_label = {}
    for key in keys:
        if key not in node_label.keys():
            node_label[key] = key

    for key in pos.keys():
        if key not in edges.keys():
            edges[key] = []
            
    if autoadjust:
        height_nodes = {}
        for key in keys:
            y = pos[key][1]
            if y not in height_nodes.keys(): height_nodes[y] = []
            height_nodes[y].append(key)
        heights = height_nodes.keys()
        heights.sort()
        for i,h in enumerate(heights):
            if i == 0:
                nodes = height_nodes[h]
                x_nodes = [(pos[node][0], node) for node in nodes]
                x_nodes.sort()
                for j,x_node in enumerate(x_nodes):
                    if j == 0:
                        pos[node][0] = 0
                    else:
                        x,node = x_node
                        pos[node][0] = j * (width + hor_sep)
            else:
                # not leaves case
                nodes = height_nodes[h]
                # order nodes by x-coord
                nodes = [(pos[node][0], node) for node in nodes]
                nodes.sort()
                nodes = [node for _,node in nodes]
                for j,node in enumerate(nodes):
                    # find children and set x of node to be the middle
                    # if a node does not have children, then
                    # set it to the middle between siblings [FIXIT]
                    children = edges[node]
                    if children != []:
                        minx = min([pos[child][0] for child in children])
                        maxx = max([pos[child][0] for child in children])
                        pos[node][0] = (minx + maxx)/2.0
                    else:
                        # no children
                        if j == 0: # leftmost sibling
                            pos[node][0] = 0
                        else: # fix
                            leftsibling = nodes[j - 1]
                            pos[node][0] = pos[leftsibling][0]+width+hor_sep
                        
    s= ""
    for key in keys:
        center_x, center_y = pos[key]
        x0 = center_x - width / 2.0
        y0 = center_y - height / 2.0
        x1 = center_x + width / 2.0
        y1 = center_y + height / 2.0
        if node_shape == 'rect':
            s += rect(x0=x0, y0=y0, x1=x1, y1=y1,
                      align='c',
                      s=node_label[key])
        elif node_shape == 'circle':
            s += circle(x=center_x, y=center_y, r=radius,
                        s=node_label[key])
                
    if node_shape == 'rect':
        for key in keys:
            source_x, source_y = pos[key]
            for target in edges.get(key, []):
                target_x, target_y = pos[target]

                if source_y - height/2.0 > target_y + height / 2.0:
                    # pointing down
                    s += line(source_x, source_y - height/2.0,
                              target_x, target_y + height/2.0)
                elif source_y + height/2.0 < target_y - height / 2.0:
                    s += line(source_x, source_y + height / 2.0,
                              target_x, target_y - height / 2.0)
                else:
                    # sideways
                    s += line(source_x + width / 2.0, source_y,
                              target_x - width / 2.0, target_y)
    elif node_shape == 'circle':
        for key in keys:
            source_x, source_y = pos[key]
            for target in edges.get(key, []):
                target_x, target_y = pos[target]
                source = source_x, source_y
                target = target_x, target_y
                # compute intersection of line st and circle about s
                st = [target[0] - source[0], target[1] - source[1]]
                length = math.sqrt(st[0]**2 + st[1]**2)
                u = [st[0]/length, st[1]/length]
                s1 = [source[0] + radius * u[0], source[1] + radius * u[1]]
                # compute intersection of line ts and circle about t
                ts = [-st[0], -st[1]]
                u = [-u[0], -u[1]]
                t1 = [target[0] + radius * u[0], target[1] + radius * u[1]]
                s += line(s1[0], s1[1], t1[0], t1[1])
    return s

#==============================================================================
# For drawing arrays
# array - 1d array drawn horizontally
#==============================================================================
def array(x0, y0, width, height,
          xs,
          linewidth=L,
          arraylinewidth=L, celllinewidth='',
          color=''):
    if arraylinewidth==0 and linewidth!=0: arraylinewidth=linewidth
    if celllinewidth==0 and linewidth!=0: celllinewidth=linewidth

    s = ''    
    s += rect(x0=x0, y0=y0,
              x1=x0+len(xs)*width, y1=y0+height,
              linewidth=arraylinewidth)
    textx = x0 + width / 2.0
    texty = y0 + height / 2.0
    linex = x0 + width
    liney = y0
    for i, x in enumerate(xs):
        s += text(textx, texty, x, color=color)
        textx += width
        if i != len(xs) - 1:
            s += line(linex, liney, linex, liney+height,
                      color=color, linewidth=celllinewidth)
            linex += width
    return s

#==============================================================================
# 2d array
#==============================================================================
def array2(x0=0, y0=0, width=1.0, height=1.0,
           vs=[],
           linewidth=0,
           arraylinewidth=L, celllinewidth=L,
           color='',
           ):
    ret = ''
    x = x0
    for v in vs:
        r = Rect(x0=x, y0=y0, x1=x+width, y1=y0+height, label=v,
                 linewidth=celllinewidth)
        ret += str(r)
        x += width - celllinewidth
    return ret

class Array2d(RectContainer):
    def __init__(self, x=0, y=0, xs=[],
                 linewidth=L, width=1, height=1, linecolor='black'):
        RectContainer.__init__(self, x=x, y=y, align='left', direction='top-to-bottom')
        for row in xs:
            c = RectContainer(x=0, y=0, align='bottom', direction='left-to-right')
            for x in row:
                c += Rect2(x0=0, y0=0, x1=width, y1=height,
                           linewidth=linewidth, linecolor=linecolor,
                           label=r'{\texttt{%s}}' % x)
            self += c
        for c in self:
            c.x = c.x0; c.y = c.y0; c.layout()


"""
class Array2d: # (RectContainer): # Maybe subclass RectContainer??
    def __init__(self, x=0, y=0, xs=[],
                 width=1, height=1,
                 linewidth=0.04,
                 linecolor='black'):
        
        self.arr = RectContainer(x=0, y=0, align='left', direction='top-to-bottom')
        for rows in xs:
            c = RectContainer(x=0, y=0,
                              align='bottom', direction='left-to-right')
            for x in rows:
                c += Rect2(x0=0, y0=0, x1=width, y1=height,
                           linecolor=linecolor, linewidth=linewidth,
                           label=r'{\texttt{%s}}' % x)
            self.arr += c
        for c in self.arr:
            c.x = c.x0
            c.y = c.y0
            c.layout()
        
    def __str__(self):
        return str(self.arr)
"""

#==============================================================================
# draw swaps
#
# swaps is a list of (index1, index2, dy)
#     p4     p5
#     --------
#    /        \  <---- 90 degree arc
# p1 |        | p2     with radius = cellwidth/2
# p0 v        v p3
#
# general function bend: specify
#     --------       ^
#    /        \      | dy=1   radius of arc (default=min(|dy|, |p0[0], p1[0]|))
#    |        |      |
# p0 v        v p3   v
#
# default radius computation
# CASE:
#     --       
#    /  \      
#    |  |      
# p0 v  v p3 
# radius = (x distance of p0-p3)/2
#
# CASE:
#     --------------       
#    /              \      
#    |              |      
# p0 v              v p3 
# radius = dy
# for now assume p0,p3 parallel to x axis
def bend(p0, p3, dy=1, radius=None,
         linewidth=L, linecolor='black', linestyle='',
         startstyle='>', endstyle='>'):
    if radius == None: radius=min(abs(dy), abs(p0[0] - p3[0])/2.0)
    dx = p3[0] - p0[0]
    if dy > 0:
        p1 = [p0[0], max(p0[1], p3[1]) + dy - radius]
        if p0[1] >= p1[1]: # something's funny here
            p1[1] = p0[1] + 0.0001
    else:
        p1 = (p0[0], min(p0[1], p3[1]) + dy + radius)
    p2 = (p0[0] + dx, p1[1])
    p4 = (p0[0] + radius, p0[1] + dy)
    p5 = (p3[0] - radius, p0[1] + dy)
    s = ''
    # left vertical arrow
    if startstyle in ['>', '->']:
        s += line(p1[0], p1[1], p0[0], p0[1],
                  linewidth=linewidth, linecolor=linecolor, linestyle=linestyle,
                  endstyle=startstyle, arrowstyle='triangle')
    else:
        s += line(p1[0], p1[1], p0[0], p0[1],
                  linewidth=linewidth, linecolor=linecolor, linestyle=linestyle,
                  endstyle='')
    # right vertical arrow
    if endstyle in ['>', '->']:
        s += line(p2[0], p2[1], p3[0], p3[1],
              endstyle=endstyle, arrowstyle='triangle',
              linewidth=linewidth, linecolor=linecolor, linestyle=linestyle)
    else:
        s += line(p2[0], p2[1], p3[0], p3[1],
              linewidth=linewidth, linecolor=linecolor, linestyle=linestyle)
        
    # hroizontal line
    s += line(p4[0], p4[1], p5[0], p5[1],
              linewidth=linewidth, linecolor=linecolor, linestyle=linestyle)
    # draw arcs
    if dy > 0:
        s += arc(x=p2[0], y=p2[1], r=radius, angle0=0, angle1=90,
                 linewidth=linewidth, linecolor=linecolor, linestyle=linestyle)
        s += arc(x=p1[0], y=p1[1], r=radius, angle0=180, angle1=90,
                 linewidth=linewidth, linecolor=linecolor, linestyle=linestyle)
    else:
        s += arc(x=p2[0], y=p2[1], r=radius, angle0=0, angle1=-90,
                 linewidth=linewidth, linecolor=linecolor, linestyle=linestyle)
        s += arc(x=p1[0], y=p1[1], r=radius, angle0=180, angle1=270,
                 linewidth=linewidth, linecolor=linecolor, linestyle=linestyle)
    return s




#==============================================================================
# The function shell executes a linux shell command and returns the stdout
# and stderr.
#==============================================================================
def myexec(cmd, timeout=None):
    """
    execute a shell command with timeout.
    TODO: timeout not done yet
    """
    from subprocess import Popen, PIPE

    p = Popen(cmd, shell=True, bufsize=0,
              stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    p.wait() # can be a problem ...
    (stdin,
     stdout,
     stderr) = (p.stdin, p.stdout, p.stderr)
    stdout = stdout.read().strip()
    stderr = stderr.read().strip()
    returncode = p.returncode
    return stdout, stderr, returncode

def exec_python(s):
    pass

def pdflatex(filename):
    if not filename.endswith('.tex'): filename += '.tex'
    d = {'filename':filename}
    cmd = 'pdflatex -halt-on-error --shell-escape %(filename)s' % d
    stdout, stderr, returncode = myexec(cmd)
    if os.path.exists('%s.pdf' % filename):
        # second pass ... how to check if this is necessary?
        stdout, stderr, returncode = myexec(cmd)
    return stdout, stderr, returncode

def pdfcrop(filename):
    """
    dnf install -y texlive-pdfcrop
    """
    if not filename.endswith('.pdf'): filename += '.pdf'
    d = {'filename':filename}
    cmd = 'pdfcrop %(filename)s %(filename)s' % d
    stdout, stderr, returncode = myexec(cmd)
    return stdout, stderr, returncode
    
#==============================================================================
# The function shell executes a linux shell command and returns the stdout
# and stderr.
#==============================================================================

def getprompt(hostname='localhost'):
    import getpass
    user = getpass.getuser()
    cwd = os.getcwd()
    a,b = os.path.split(cwd)
    if b == user: b = '~'
    return "[%s@%s %s]" % (user, hostname, b)

def postprocess(s): return s

def shell2(cmd,
          CWD='home/student',
          TESTDIR='',
          dir='', # a better name for TESTDIR
          postprocess=None,
          latex=True,
          execute=True,
          ):
    # Same as shell() except that this version has cache
    ahash = hash(str(cmd))
    filename = 'tmp/%s.tex' % ahash 
    if os.path.exists(filename):
        s = readfile(filename)
    else:
        s = shell(cmd=cmd,
                  CWD=CWD,
                  TESTDIR=TESTDIR,
                  dir=dir,
                  postprocess=postprocess,
                  latex=latex,
                  execute=execute,
                  )
        writefile(filename, s)
    # add hash filename to s
    if latex:
        s += r'''
\begin{center}
{\scriptsize \verb!%s!}
\end{center}
''' % filename
    return s
    
def shell(cmd,
          CWD='home/student',
          TESTDIR='',
          dir='', # a better name for TESTDIR
          postprocess=None,
          latex=True,
          fontsize=r'\small', # ADDED 2021/4/1
          execute=True,
          prompt=None,
          width=80,
          include_stderr=True,
          ):
    if isinstance(cmd, str): cmd = [cmd]
    cwd = os.getcwd()
    if dir != '': TESTDIR = dir
    
    if TESTDIR:
        os.chdir(TESTDIR)
    if not prompt:
        prompt = getprompt()
    s = ''
    for c in cmd:
        if execute:
            p = Popen(c, shell=True, bufsize=2048,
                      stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
            p.wait() # can be a problem ...
            (stdin,
             stdout,
             stderr) = (p.stdin, p.stdout, p.stderr)
            stdout = stdout.read()
            stderr = stderr.read()
        else:
            stdout = stderr = ''

        # Python3 upgrade: Popen returns bytes.
        # Need to convert to string
        stdout = to_string(stdout)
        stderr = to_string(stderr)
        
        if not include_stderr: stderr = ''
        t = "%s %s\n%s%s" % (prompt, c, stdout, stderr)
        t = t.replace(cwd, CWD)
        if postprocess:
            t = postprocess(t)
        s += t
        
    s = s.rstrip()
    if latex:
        # wraparound
        lines = s.split('\n')
        t = []
        for line in lines:
            while (len(line) > width):
                x, line = line[:width], line[width:]
                t.append(x)
            if line != "":
                t.append(line)
        s = '\n'.join(t)
        s = r'''\begin{Verbatim}[frame=single,fontsize=%s]
%s
\end{Verbatim}
''' % (fontsize, s)
        #s = verbatim(s)
    os.chdir(cwd)

    return to_string(s)


#==============================================================================
# The function positions a dictionary of k,v where k is the string and v
# is the position of k.
#==============================================================================
def positions(layout="", xscale=1, yscale=1):
    """ If layout is 
  A
B C
    Then this returns {'A':(2,0), 'B':(0,-1), 'C':(2,-1)}
"""
    layout = [_ for _ in layout.split('\n')]
    # removing pre-pended blank lines
    while 1:
        if layout[0].strip() == '':
            layout = layout[1:]
        else:
            break

    d = {}
    for row,line in enumerate(layout):
        s = line
        symbols = [_ for _ in s.split(' ') if _ != '']
        for symbol in symbols:
            col = line.index(symbol)
            # Python3 change
            if symbol in d: # d.has_key(symbol)
                raise ValueError("repeat symbols %s" % symbols)
            d[symbol] = [col*xscale, -row*yscale]
    return d

        
def pipes(center=[0,0],
          numpipes=1, pipeheight=1, pipewidth=0.3, dx=0.2,
          color=''):
    # draws a bunch of | 
    pass
    s = ''
    s += line(pipex, pipey, 
              pipex, pipey + pipeheight,
              linewidth=pipewidth, color=color)


def chunkedarray(x=0, y=0, cellwidth=1, cellheight=1,
                 arr=[],
                 linewidth=L,
                 color='',
                 pipewidth=0.1,
                 spacing=0.1,
                 pipeheight=None,
                 chunklabels=[],
                 celllabels=[],
                 swaps=[],
                 labels=[], # new
                 dividers=[]): # new
 
    # labels is a list of
    # s, index, description
    #
    # Example: s='pivot', index=0, description='<->', dy = 1
    # Example: s='pivot', index=0, description='--', dy = 1
    # Example: s='kill', index=[0,5,6], description='->', dy = -1
    # Example: s='kill', index=[0,5,6], description='->', dy = -1
    # Example: s='left', index=[0,5], description='{', dy=-1

    def celltop(index):
        # compute the (x,y) of the cell at index
        pass
    
    def cellbottom(index):
        pass
    
    xss = arr
    if pipeheight==None:
        pipeheight = cellheight * 1.4

    s = ''

    # draw cells
    ys = []
    for xs in xss:
        ys += xs
    s += array(x, y, width=cellwidth, height=cellheight, xs=ys,
               linewidth=linewidth, arraylinewidth=linewidth, celllinewidth=linewidth)

    # Draw the bend for swaps
    for swap in swaps:
        if len(swap) == 2:
            index1, index2 = swap
            dy = -cellwidth
        else:
            index1, index2, dy = swap
        if index1 > index2: index1, index2 = index2, index1
        x0 = x + (index1 + 0.5) * cellwidth
        x1 = x + (index2 + 0.5) * cellwidth
        if dy > 0:
            y0 = y1 = y + cellheight
        else:
            y0 = y1 = y
        s += bend([x0,y0], [x1,y1], dy, cellwidth/2.0) # , cellwidth / 2.0)
         
    # draw cell labels
    # distinguish between label above or below
    for nodetext, index, dy in celllabels:
        celllabelx = x + (index + 0.5) * cellwidth
        # NOTE: dy is the displacement from the bottom or the
        # top of the cell
        if dy < 0:
            celllabely = y + dy
        else:
            celllabely = y + (dy + cellheight)
        s += text(celllabelx, celllabely, nodetext)
        arrowheadx = celllabelx
        arrowtailx = celllabelx
        if dy < 0:
            arrowtaily = y + dy + 0.3
            length = -dy - 0.3
        else: # dy >= 0
            arrowtaily = y + cellheight + dy - 0.3
            length = -dy + 0.3
        s += "%s" % Path(x=arrowtailx, y=arrowtaily, start='',
                         points=[(0,0), (0, length)], linewidth='1')

    # draw chunk labels
    for i,chunklabel in enumerate(chunklabels):
        if isinstance(chunklabel, (list, tuple)):
            label, dy = chunklabel
        else:
            label = chunklabel
            dy = 0.7
        # compute center of label
        x0 = x + cellwidth * sum([len(xs) for xs in xss[:i]])
        x1 = x0 + cellwidth * len(xss[i])
        labelx = (x0 + x1)/2.0
        if dy > 0:
            labely = y + cellheight + dy
        else:
            labely = y + dy
        s += text(labelx, labely, label)
        # draw 'brace'
        if label != '':
            if dy > 0:
                if abs(x0 - x1) >= 0.5:
                    s += '\draw (%s,%s) -- (%s,%s) -- (%s,%s);\n' % \
                     (x0+0.1, y+cellheight+0.1,
                      labelx, labely - 0.6 * dy,
                      x1-0.1, y+cellheight+0.1)
                    s += '\draw (%s,%s) -- (%s,%s);\n' % \
                     (labelx, labely - 0.6 * dy,
                      labelx, labely - 0.3)
                else:
                    s += '\draw (%s,%s) -- (%s,%s);\n' % \
                     (labelx, y+cellheight+0.1, labelx, labely - 0.3)
            else:
                if abs(x0 - labelx) >= 0.3:
                    s += '\draw (%s,%s) -- (%s,%s) -- (%s,%s);\n' % \
                         (x0+0.1, y-0.1, labelx, y-cellwidth/2, x1-0.1, -0.1)
                    s += '\draw (%s,%s) -- (%s,%s);\n' % \
                         (labelx, y-cellwidth/2, labelx, labely + 0.3)
                else:
                    s += '\draw (%s,%s) -- (%s,%s);\n' % \
                         (labelx, y-0.1, labelx, labely + 0.3)
    # draw pipes
    # correct case of multiple consecutive empty lists (can be a problem is there are too many ...)

    # new pipe drawing
    i = 0
    runlen = 0
    pipey = y - (pipeheight - cellheight) / 2.0
    while i < len(xss):
        runlen += len(xss[i])
        
        # count number of empty lists after xss[i]
        j = i + 1 # have to keep i so as to compute drawing position
        numempty = 0
        while j < len(xss) and xss[j] == []:
            numempty += 1
            j += 1
            
        # draw pipes at index i
        count = numempty + 1 # number of pipes to draw

        if j == len(xss): count -= 1
        
        x0 = x + runlen * cellwidth # pipes about this x-coord
        #
        #             # # # # # #
        #             # # # # # # 
        #             # # # # # #
        # -----------------+--------------------
        #                  x0
        # Total width of pipes = numpipes * (pipewidth) + (numpipes - 1) * spacing
        totalwidth = count * pipewidth + (count - 1) * spacing 
        pipex = x0 - totalwidth/2.0 + pipewidth/2.0
        if i == 0 and xss[0] == []:
            pipex = x + spacing
        elif j == len(xss):
            pipex = pipex - totalwidth / 2.0 - spacing/2.0
        for k in range(count):
            s += line(pipex, pipey, 
                      pipex, pipey + pipeheight,
                      linewidth='%scm' % pipewidth, color=color)
            pipex += pipewidth + spacing
        i = j

    return s



#==============================================================================
# Draws a frame/record.
#==============================================================================
def frame(env, top='', W=1.2, H=0.6):
    # TODO: string
    # TODO: pointer
    # TODO: heap
    # TODO: frame stack
    
    # W - width of int value box
    # H - height of value box

    s = ''
    y = 0
    h = H
    space = 0.2 # between boxes
    s = rect(x0=-1, y0= -(h + space) * (len(env) - 1) - h, x1=3, y1=1, linewidth=0.1)

    if top != '':
        s += rect(x0=-1, y0=1, x1=3, y1=1.5, s=r'{\verb!%s!}' % top, linewidth=0)
    for k,v in env:
        if isinstance(v, int): w = W
        elif isinstance(v, float): w = W * 2
        elif isinstance(v, str) and len(v) == 1: w = W / 2
        else: w = W

        s += text(x=-0.5, y=y+h/2.0, s=k)
        s += rect(x0=0, y0=y, x1=w, y1=y+h)
        
        if isinstance(v, str) and len(v) == 1:
            s += text(x=w/2.0, y=y+h/2.0, s=r"{\verb!'%s'!}" % v)
        else:
            s += text(x=w/2.0, y=y+h/2.0, s="%s" % v)
        y -= h + space
        
    return s


#==============================================================================
# Save pdf image and do pdfcrop
# makepdf(latex) will create a cropped pdf with the latex fragment.
# This is saved in tmp/[filename] where filename is the md5 hash digest of
# the latex string.
#
# Handle 2 cases:
# - latex is a latex fragment
# - latex is a python program that generates a latex fragment
#==============================================================================
def makepdf(latex,
            ahash=None,
            filename=None, # example: 'main'
            ):
    if ahash==None: ahash = hash(latex)
    latex = latex.strip()
    TMP = 'tmp'
    s = r"""
\documentclass[a4paper,12pt]{scrbook}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{fancyvrb}
\usepackage{parskip}
\usepackage{lastpage}
\usepackage{verbatim,boxedminipage,enumitem}
\usepackage{ifthen}
\usepackage{color,graphicx}
\usepackage{pgf}
\usepackage{longtable}
\usepackage{upquote}
%\usepackage[all]{xy}
\usepackage{tobiShell}
\usepackage{tikz}
\usetikzlibrary{automata}
\usetikzlibrary{arrows}
\usepackage{pgf,pgfarrows,pgfnodes}
\usepackage{pgfplots}
\usepackage{circuitikz}
\usetikzlibrary{circuits}
\usetikzlibrary{circuits.logic.US}
\usepackage{mymath}
\usepackage{python}
%------------------------------------------------------------------
% Verbatim for console window - single line frame, no line numbers
%------------------------------------------------------------------
\DefineVerbatimEnvironment%
 {console}{Verbatim}
 {frame=single}

%--------------------------------------------------------
% Remove the vertical spacing before and after Verbatim.
%--------------------------------------------------------
\usepackage{atbeginend}
\BeforeBegin{console}{\mbox{}\\ \begin{minipage}{\textwidth}\vspace{3pt}}
\AfterEnd{console}{\vspace{4pt} \end{minipage} \\ }

\begin{document}
\thispagestyle{empty}

""" + latex + r"""

\end{document}
"""
    
    import os
    cwd = os.getcwd()
    if not os.path.exists(TMP):
        os.makedirs(TMP)
    os.chdir(TMP)

    if not filename:
        filename = ahash
    writefile("%s.tex" % filename, s)

    stdout, stderr, returncode = pdflatex(filename)
    
    if os.path.exists("%s.pdf" % filename):
        stdout, stderr, returncode = pdfcrop(filename)
    else:
        pass
    os.chdir(cwd)
    return stdout, stderr, returncode

def hash(s):
    import hashlib
    return hashlib.md5(s).hexdigest()

    
def includegraphics(filename, include_filename=False):
    if include_filename:
        return r"""\begin{center}
\includegraphics{%s}
\\
{\scriptsize \verb!%s!}
\end{center}
""" % (filename, filename)
    else:
        return r"""\begin{center}
\includegraphics{%s}
\end{center}
""" % filename
    



def makeandincludegraphics(latex='',
                           python='',
                           filename=None,
                           include_filename=True,
                           ):
    if filename!=None:
        ahash = filename
    else:
        ahash = IFELSE(python!='', hash(python), hash(latex))

    #--------------------------------------------------------------------------
    # Execute python source to get latex string. If there's an error,
    # execute_error is True.
    # If python source is '', just use the parameter latex.
    #--------------------------------------------------------------------------
    execute_error = False
    if python!='':
        latex = execute(python, print_result=False)
        # WARNING: latex can be stdout or console of source,stdout,stderr.
        # The following hack disambiguates
        if latex.count(r'\begin{console}') == 3: execute_error = True
    else:
        # in this case the parameter latex is used directly
        pass

    if execute_error:
        # The above python source has an error. 
        return latex
    else:
        # Use latex directly or python was executed without error.
        hash_latex_pdf = "tmp/%s.pdf" % ahash
    
        if not os.path.exists(hash_latex_pdf):
            stdout, stderr, returncode = makepdf(latex, ahash)

        if not os.path.exists(hash_latex_pdf):
            return r"""
***** ERROR IN makeandincludegraphics: no pdf file.

See tmp/%s.tex.

See stdout and stderr below:
%s
%s
""" % (ahash, console(stdout[-600:]), console(stderr[-600:]))
        else:
            return includegraphics(hash_latex_pdf, include_filename=include_filename)







class Node(BaseNode):
    def __init__(self,
                 x=None, y=None, # center
                 w=None, h=None, # width, height
                 x0=None, y0=None, x1=None, y1=None, # bounding box
                 # Note that either w,h or x0,y0,x1,y1 is specified
                 s='',
                 align='t',
                 innersep=0.07,
                 radius=0.1,
                 background='blue!5!white',
                 linewidth=0,
                 linestyle='',
                 debug=True):
        BaseNode.__init__(self,
                          x=x, y=y, w=w, h=h,
                          x0=x0, y0=y0, x1=x1, y1=y1,
                          debug=debug)
        self.s = s
        self.align = align
        self.innersep = innersep
        self.radius = radius
        self.background = background
        self.linewidth = linewidth
        self.linestyle = linestyle
        
    def __str__(self):
        x0 = self.x0
        x1 = self.x1
        y0 = self.y0
        y1 = self.y1
        s = r'{\textsf{\scriptsize %s}}' % self.s
        background = self.background
        innersep = self.innersep
        radius = self.innersep
        align = self.align
        linewidth = self.linewidth
        linestyle = self.linestyle
        ret = rect(x0=x0, y0=y0, x1=x1, y1=y1,
                 innersep=innersep, radius=radius,
                 align=align, s=s, background=background, linewidth=linewidth,
                 linestyle=linestyle)
        ret += BaseNode.__str__(self)
        return ret




#==============================================================================
# This is used by cs-prog.py
#==============================================================================
class Container(Node):
    # Extra boundary spacing for component nodes 
    BORDERX = 0.1
    BORDERY = 0.15

    def __init__(self, nodes=[], s=''):
        if nodes == []:
            raise "Container.__init__: nodes is empty"
        # compute rect data and place in d
        minx = min([n.x0 for n in nodes])
        maxx = max([n.x1 for n in nodes])
        miny = min([n.y0 for n in nodes])
        maxy = max([n.y1 for n in nodes])
        if s=='':
            align = 'c'
        else:
            align = 't'

        # WARNING: hardcode
        if s in ['INTERMEDIATE', 'ADVANCED']:
            s = ''
        else:
            maxy += 0.4 # Hardcoded
            s = r'''\begin{center}
            %s
            \end{center}
            ''' % s
        Node.__init__(self,
                      x0=minx - Container.BORDERX,
                      y0=miny - Container.BORDERY,
                      x1=maxx + Container.BORDERX,
                      y1=maxy + Container.BORDERY,
                      s=s,
                      linewidth=0.01, # ADDED
                      align=align)




class Path:

    """
    suppose points = [p0, p1]

    points is a sequence of (x,y) or [x,y] and strings
    the strings are
    "left 0.5", "right 2", "up 5", "down 2"
    "flush left", "flush right", "flush up", "flush down"

    flush is toward the bounding box of p0, p1
    flush left: point is from current point in path to the left of bounding box
    flush right: ... to the left of bounding box
    """
        
    def __init__(self,
                 x=0, y=0, # offset of the points
                 points=[],
                 description=None,
                 start='dot', end='->',
                 color='', linewidth='', moves=''):
        self.x = x
        self.y = y
        self.color = color
        self.linewidth = linewidth
        self.start = start
        self.end = end

        # CHECK THIS FIX FOR OTHER CASES
        if self.start == '<-' and self.end == '->':
            self.end = '<->'
        
        self.points = []
        if description in [None, '']:
            self.points = points
        elif description.startswith('down'):
            # Example: description = "down 0.5"
            down = description.split(' ')[1].strip()
            down = float(down)
            # draws a "U" shape path of one of the following shapes:
            #              P
            # S            |     or     |
            # ^            |            |             ^
            # |            |            |             |
            # +------------+            +-------------+
            # R             Q
            # points is the starting point and ending point
            P = [x + points[0][0], y + points[0][1]]
            Q = [P[0], P[1] - down]
            R = [points[1][0], Q[1]]
            S = [x + points[1][0], y + points[1][1]]
            self.points = [P, Q, R, S]
        elif description.startswith('up'):
            # Example: description = "up 0.5"
            up = description.split(' ')[1].strip()
            up = float(up)
            # R            Q
            # +----------- +
            # |            |     
            # |            |     
            # V            |     
            # S            |     
            #              P
            P = [x + points[0][0], y + points[0][1]]
            Q = [P[0], P[1] + up]
            R = [points[1][0], Q[1]]
            S = [x + points[1][0], y + points[1][1]]
            self.points = [P, Q, R, S]
        elif description == '???':
            # CASE: 90 degree turn (i.e. something like L shape or
            # rotation or reflection)
            pass

        # ALTERNATIVE TO description
        if moves!="" and len(self.points) > 0:
            pass
            
    def __str__(self):
        if self.points in [[], None] : return ''

        if self.linewidth not in ['', None]:
            linewidth = "line width=%s" % self.linewidth
        else:
            linewidth = ''
        s = r"\draw[%s] " % ','.join([self.end, self.color, linewidth])
        
        points = self.points
        
        #x, y = self.center() ?????
        x, y = self.x, self.y
        
        s += "(%s, %s)" %  (x + points[0][0], y + points[0][1])
        for point in points[1:]:
            s += " -- (%s, %s)" % (x + point[0], y + point[1])
        s += ";\n"
            
        # draw start if it's a dot
        if self.start == 'dot':
            s += circle(x+points[0][0], y+points[0][1],
                        filled=True, color=self.color)
        return s
        
#==============================================================================
# Doubly Linked List Node
#==============================================================================
class DoublyLinkedListNode(RectContainer):
    def __init__(self, x=0, y=0, prev='', label='', next='', width=1, linewidth=DOUBLE_LINKED_LIST_LINEWIDTH):
        RectContainer.__init__(self, x=x, y=y)
        if prev == None:
            self += CrossedRect2(0, 0, 0.5, 0.5, linewidth=linewidth)
        else:
            self += Rect2(0, 0, 0.5, 0.5, linewidth=linewidth)
        self += Rect2(x0=0, y0=0, x1=width, y1=0.5, linewidth=linewidth, label=r'\texttt{%s}' % label)
        if next == None:
            self += CrossedRect2(0, 0, 0.5, 0.5, linewidth=linewidth)
        else:
            self += Rect2(0, 0, 0.5, 0.5, linewidth=linewidth)

#==============================================================================
# Singly Linked List Node
#==============================================================================
class SinglyLinkedListNode(RectContainer):
    def __init__(self, x=0, y=0, label='', next='', width=1, 
                 linewidth=SINGLE_LINKED_LIST_LINEWIDTH):
        RectContainer.__init__(self, x=x, y=y)
        #if prev == None:
        #    self += CrossedRect2(0, 0, 0.5, 0.5, linewidth=linewidth)
        #else:
        #    self += Rect2(0, 0, 0.5, 0.5, linewidth=linewidth)
        self += Rect2(x0=0, y0=0, x1=width, y1=0.5, linewidth=linewidth, 
                      label=r'\texttt{%s}' % label)
        if next == None:
            self += CrossedRect2(0, 0, 0.5, 0.5, linewidth=linewidth)
        else:
            self += Rect2(0, 0, 0.5, 0.5, linewidth=linewidth)

#==============================================================================
# consolegrid
#==============================================================================
def consolegrid(numrows=1, numcols=21, s=''):
    if isinstance(s, str):
        lines = s.split('\n')
        if len(lines) > numrows: numrows = len(lines)
        lines = [list(line) for line in lines]
        tnumcols = max([len(line) for line in lines] + [-1])
        numcols = max(numcols, tnumcols)
        lines = [line + ['' for i in range(numcols - len(line))] \
                 for line in lines]
        lines = lines + [ ['' for k in range(numcols)] \
                          for i in range(numrows - len(lines))]
    elif isinstance(s, list):
        lines = [['' for i in range(numcols)] for j in range(numrows)]
        for i, row in enumerate(s):
            for j, col in enumerate(row):
                lines[i][j] = col
    s = '|'.join(['p{0.35cm}' for _ in range(numcols)])
    s = '|%s|' % s + '}\n'
    s += r'\hline' + '\n'
    for line in lines:
        s += ' & '.join(line)
        s += r' \\ \hline'  + '\n'
    s = s[:-1]
    return r"""
{\Large\texttt{
\begin{longtable}{
%s
\end{longtable}
}}""" % s


#==============================================================================
# This is from the ciss362-automata/r/dfa/graph/graph.py and is the latest
# version
#==============================================================================
def automata(
    xscale=1,
    yscale=2,
    layout="",
    separator="|",
    edges="",
    initial_bend=28,
    delta_bend=8,
    minimum_size=None,
    **args
    ):
    pos = positions(layout,xscale,yscale)
    node = {}
    #print ("pos: %s" % pos)
    for k,v in pos.items():
        node[k] = {'pos':v}
        node[k]['initial'] = ""
        node[k]['accept'] = ""
        node[k]['label'] = k

    e = {}
    for v in [_ for _ in edges.split(separator) if _ != '']:
        #print ("v:" % v)
        q1,v = v.split(',',1)
        v,q2 = v.rsplit(',',1)
        e[(q1,q2)] = v

    for k in node.keys():
        for v in [_ for _ in args.get(k,'').split(separator) if _ != '']:
            if v == 'initial':
                node[k]['initial'] = ",initial"
            elif v == 'accept':
                node[k]['accept'] = ",accepting"
            elif v.startswith('label='):
                node[k]['label'] = v.replace('label=', '').strip()
            else:
                raise ValueError("unknown option for node [%s]" % v)

    # form node string
    node_str = ""
    node_items = list(node.items()) # PYTHON3
    node_items.sort()
    for k,v in node.items():
        d = {}
        d['name'] = k
        d['label'] = v['label']
        d['initial'] = v['initial']
        d['accept']= v['accept']
        try:
            d['pos'] = "(%3s,%3s)" % (v['pos'][0], v['pos'][1])
        except:
            print ("v[pos]: %s" % v['pos'])
            raise
        if minimum_size == None:
            node_str += r"\node[state%(initial)s%(accept)s] (%(name)s) at %(pos)s {%(label)s};" % d
        else:
            d.update({'minimum_size':minimum_size})
            node_str += r"\node[state%(initial)s%(accept)s, minimum size=%(minimum_size)s] (%(name)s) at %(pos)s {%(label)s};" % d
        node_str += '\n'

    def edge_shape(q0,q1,node,e):

        # edges going right: label above
        # edges going left: label below
        #
        
        def between(p0,p,p1):
            u = p[0]-p0[0], p[1]-p0[1]
            v = p1[0]-p[0], p1[1]-p[1]
            dot = u[0]*v[0] + u[1]*v[1] # dot product
            len_u = math.sqrt(u[0]*u[0] + u[1]*u[1])
            len_v = math.sqrt(v[0]*v[0] + v[1]*v[1])
            return abs(dot - len_u * len_v) < 0.01
        
        if q0==q1:
            return "[loop above]" # have to decide on which loop
        
        p0, p1 = node[q0]['pos'],node[q1]['pos']
        # count num of nodes between
        count = 0
        for p in node.keys():
            if p not in [q0,q1]:
                if between(p0,node[p]['pos'],p1):
                    count += 1
	#print ("p0,p1,count: %s %s %s" % (p0,p1,count))
        if count == 0:
            if (q1,q0) in e.keys(): angle = 10
            else: angle = 0
        else:
            if count == 1:
                angle = initial_bend + delta_bend*count - 5
            else:
                angle = initial_bend + delta_bend*count
        
        if p0[0] < p1[0]:
            return "[bend left=%s,pos=0.5,above]" % angle
        else:
            # the two nodes are on above each other
            # THIS IS WRONG WHEN TARGET NODE IS BELOW SOURCE 
            return "[bend left=%s,pos=0.5]" % angle
    edge_str = ""
    #print ("e: %s" % e)
    e2 = list(e.items()) # PYTHON3
    e2.sort()
    for k, v in e2:
        q1,q2 = k
        if q1 not in node.keys():
            raise ValueError("state [%s] in edges param not found in layout" % q1)
        if q2 not in node.keys():
            raise ValueError("state [%s] in edges param not found in layout" % q2)

        d = {'q1':q1, 'q2':q2, 'label':v, 'edge':edge_shape(q1,q2,node,e)}
        if q1==q2:
            edge_str += r"(%(q1)s) edge %(edge)s node {%(label)s} ()" % d
        else:
            edge_str += r"(%(q1)s) edge %(edge)s node {%(label)s} (%(q2)s)" % d
        edge_str += '\n'
    return r'''
\begin{center}
\begin{tikzpicture}[>=triangle 60,shorten >=0.5pt,node distance=2cm,auto,initial text=]
%s
\path[->]
%s
;
\end{tikzpicture}
\end{center}
    ''' % (node_str, edge_str)




if __name__ == '__main__':

    '''
    from latextool_basic import *

    bline = Line(points=[(0,-1), (5,-1), (5,-6)], 
                 linecolor='blue', linewidth=0.1, 
                 startstyle='dot', arrowstyle='triangle', endstyle='->')
    
    print (bline.midpoint(ratio=0.2))
    '''

    '''
    print (table([('',  2, 5,  8),
             ('', '', 3,  6),
            ],
            col_headings = ['0', '2', '5', '8'],
            row_headings = ['0', '2', '5', '8'],
            topleft_heading = r'$\Delta X$',
           ))
    '''

    print (consolegrid(2))

#==============================================================================
# Matrix
# Use in ciss380
# See ciss380/n/matrix.py
#
# This is from CISS380 graphics class
#
# SHOULD DEPRECATE AND USE numpy.
#==============================================================================
class vec:
    def __init__(self, x, y=None):
        if y == None:
            self.x = x
        else:
            self.x = []
            for a,b in zip(x, y):
                self.x.append(b - a) 

    def latex(self):
        s = ", ".join([str(_) for _ in self.x])
        return r"\langle %s \rangle" % s

    
    
def plot(vectors=[], vector=[]):

    if vector != []:
        vectors.append(vector)
        
    vs = []
    for v in vectors:
        start,end = v
        a,b = start
        c,d = end
        vs.append(r"\addplot[->] coordinates {(%s,%s) (%s,%s)};" % (a,b,c,d))
    vs = '\n'.join(vs)
    vectors = vs

    return r"""
\begin{center}
\begin{tikzpicture}[>=triangle 60,scale=.6]
\begin{axis}[
width=5in, height=4in,
xmin=-5, xmax=5,
ymin=-3, ymax=5,
axis x line=middle,
axis y line=middle,
grid=major
]
%(vectors)s
\end{axis}
\end{tikzpicture}
\end{center}
""" % {'vectors':vectors}



def vec2dplot(plot, vectors, x0=None, y0=None, x1=None, y1=None,
              draw_axes=True):
    import math
    if x0 == None or x1 == None:
        xs = [p[0] for p,q in vectors] + [q[0] for p,q in vectors]
        if x0 == None:
            x0 = 0
            if xs != []:
                x0 = min(xs); x0 -= 0.1; x0 = math.floor(x0)
            if draw_axes:
                if x0 > -1: x0 = -1
        if x1 == None:
            x1 = 0
            if xs != []:
                x1 = max(xs); x1 += 0.1; x1 = math.ceil(x1)
            if draw_axes:
                if x1 < 1: x1 = 1
    if y0 == None or y1 == None:
        ys = [p[1] for p,q in vectors] + [q[1] for p,q in vectors]
        if y0 == None:
            y0 = 0
            if ys != []:
                y0 = min(ys); y0 -= 0.1; y0 = math.floor(y0)
            if draw_axes:
                if y0 > -1: y0 = -1
        if y1 == None:
            y1 = 0
            if ys != []:
                y1 = max(ys); y1 += 0.1; y1 = math.ceil(y1)
            if draw_axes:
                if y1 < 1: y1 = 1
    plot += Grid(x0=x0, y0=y0, x1=x1, y1=y1, linecolor='black!10', label_axes=True, fontsize='footnotesize')
    if draw_axes:
        axes(plot, x0=x0, y0=y0, x1=x1, y1=y1)
    for (p,q) in vectors:
        plot += vector(p, q)
    return


def answer(width=3, height=1.2, answer=''):

    x0 = 1.25
    x1 = width + x0
    y0 = -height/2
    y1 = height + y0
    
    return r"""
\begin{tikzpicture}
\draw ( %(x0)s, %(y0)s ) rectangle ( %(x1)s, %(y1)s );
\draw (2.6, 0) node { %(answer)s };
\draw (0, 0) node {ANSWER:};
\end{tikzpicture}
""" % {'x0':x0, 'x1':x1, 'y0':y0, 'y1':y1, 'answer':answer}


import sys, copy
from fractions import Fraction

def xxx(v):
    if v < 0: return "(%s)" % v 
    else: return "%s" % v
    

def augmatrix(aug):
    colsize = (aug.colsize)//2
    option = ("c"*colsize) + "|" + ("c"*colsize)
    str_matrix = (r"\begin{bmatrix}[%s]" + '\n') % option
    for row in aug.xs:
        row0 = ["%5s" % _ for _ in row]
        row0 = " & ".join(row0)
        row0 += r" \\" + "\n"
        str_matrix += row0
    str_matrix += r"""\end{bmatrix}
"""
    return str_matrix


def latex_inverse(m):

    n, computations = m.inv()

    s = ""
    for i,computation in enumerate(computations):
        if i != 0: s += r" \displaybreak[0]\\ "
        s += latex(computation)

    x = augmatrix(m.augment())
    return r"""\begin{align*}
%s %s\end{align*}
""" % (x, s)


def latex_bmatrix(xs):

    if isinstance(xs, Matrix): return latex_bmatrix(xs.xs)
    
    s = (r"\begin{bmatrix}" + '\n')
    for row in xs:
        row0 = ["%5s" % _ for _ in row]
        row0 = " & ".join(row0)
        row0 += r" \\" + "\n"
        s += row0
    s += r"""\end{bmatrix}"""
    return s

def latex_mult(m, n):
    s = ""
    s += r"\begin{align*}"
    
    s += "& " + latex_bmatrix(m.xs)
    s += latex_bmatrix(n.xs)
    s += r" \\ " + '\n'

    xs = []
    for r in range(m.rowsize):
        row = []
        for c in range(n.colsize):
            entry = ["(%s)(%s)" % (m[r,k],n[k,c]) for k in range(m.colsize)]
            entry = " + ".join(entry)
            row.append(entry)
        xs.append(row)

    s += "& = "
    s += latex_bmatrix(xs)
    s += r" \\" + "\n"
    
    xs = []
    for r in range(m.rowsize):
        row = []
        for c in range(n.colsize):
            entry = []
            for k in range(m.colsize):
                x = m[r,k] * n[k,c]
                if x < 0: x = "(%s)" % x
                else: x = "%s" % x
                entry.append(x)
            entry = " + ".join(entry)
            row.append(entry)
        xs.append(row)

    s += "& = "
    s += latex_bmatrix(xs)
    s += r" \\ " + "\n"

    s += "& = "
    s += latex_bmatrix(m * n)

    s += r"\end{align*}"
    
    return s

def latex_boolean_product_matrix(A, B):
    s = latex_mult(A, B)
    s = s.replace(r'\end{bmatrix}', r'\end{bmatrix} \odot', 1)
    s = s.replace('+', r'\lor')
    s = s.replace(')(', r'\land')
    for i in range(2, 1):
        s = s.replace(str(i), '1')
    return s

def latex(computation):
    name, params, aug = computation

    if name == 'swap':
        r0, r1 = params
        r0 += 1
        r1 += 1
        arrow = r"""\underrightarrow{\,\,\, R_%s \leftrightarrow R_%s \,\,\,} &
""" % (r0, r1)

    elif name == 'mult':
        r, k = params
        r += 1
        k = str(k)
        arrow = r"""\underrightarrow{\,\,\, R_%s \rightarrow \left( %s \right) R_%s \,\,\,}&
""" % (r, k, r)

    elif name == 'addmult':
        k, r0, r1 = params
        k = str(k)
        r0 += 1
        r1 += 1
        arrow = r"""\underrightarrow{\,\,\, R_%s \rightarrow R_%s + \left( %s \right) R_%s \,\,\,}&
""" % (r1, r1, k, r0)
        
    else:
        raise ValueError("unknown name:" + name)

    if arrow.startswith('\n'): sys.exit()
    str_matrix = augmatrix(aug)
    return arrow + str_matrix



    
class Matrix:

    latex = ""
    lookup = {}
    omit_zero = False # include 0 expansion for determinant
    
    def __init__(self, xs):
        self.xs = copy.deepcopy(xs)
        self.rowsize = len(self.xs)
        self.colsize = len(self.xs[0])
        if any([len(self.xs[r])!=self.colsize for r in range(self.rowsize)]):
            raise ValueError("column size not the same")

    def __str__(self):
        xs = self.xs
        width = []
        for c in range(self.colsize):
            col = [str(xs[r][c]) for r in range(self.rowsize)]
            lens = [len(_) for _ in col]
            width.append(max(lens))
        m = ''
        for r,row in enumerate(xs):
            m += '['
            for c,col in enumerate(row):
                m += str(col).rjust(width[c])
                if c < self.colsize - 1:
                    m += ", "
            m += ']\n'
        return m

    def samesize(self, m):
        return self.rowsize == m.rowsize and self.colsize == m.colsize

    def __isub__(self, m):
        if not self.samesize(m):
            raise ValueError("cannot add: incompatible sizes")
        for r in range(self.rowsize):
            for c in range(self.colsize):
                self[r, c] -= m[r, c]
        return self

    def __sub__(self, m):
        n = copy.deepcopy(self)
        n -= m
        return n
 
    def __mul__(self, m):
        if not isinstance(m ,Matrix):
            ret = copy.deepcopy(self)
            for r in range(self.rowsize):
                for c in range(self.colsize):
                    ret[r, c] *= m
            return ret
        else:
            if self.colsize != m.rowsize:
                raise ValueError("cannot mult: incompatible sizes")
            xs = []
            for r in range(self.rowsize):
                row = []
                for c in range(m.colsize):
                    s = 0
                    for k in range(self.colsize):
                        s += self[r, k] * m[k, c]
                    row.append(s)
                xs.append(row)
            return Matrix(xs)
            
    def __iadd__(self, m):
        if not self.samesize(m):
            raise ValueError("cannot add: incompatible sizes")
        for r in range(self.rowsize):
            for c in range(self.colsize):
                self[r, c] += m[r, c]
        return self
    
    def __add__(self, m):
        n = copy.deepcopy(self)
        n += m
        return n
    
    def rowswap(self, r0, r1):
        xs = self.xs
        for c in range(self.colsize):
            xs[r0][c], xs[r1][c] = xs[r1][c], xs[r0][c]

    def rowmult(self, r, k):
        # multiply row r with k
        for c in range(self.colsize):
            self.xs[r][c] *= k
            
    def rowaddmultiple(self, k, r0, r1):
        # add c*r0 to r1
        xs = self.xs
        for c in range(self.colsize):
            xs[r1][c] = xs[r1][c] + k * xs[r0][c]

    def __getitem__(self, k):
        r,c = k
        return self.xs[r][c]
    
    def __setitem__(self, k, v):
        r,c = k
        self.xs[r][c] = v
    
    def inv(self):
        # returns inverse and a list of computations of the
        # augmented matrix

        # Build augmented matrix
        augmat = self.augment()

        computations = []
        
        xs = self.xs
        for r in range(self.rowsize):

            # find and row to swap with
            r0 = r
            while r0 < augmat.rowsize and augmat[r0, r] == 0:
                r0 += 1
            if r0 == augmat.rowsize:
                raise ValueError("matrix has no inverse")

            # swap is necessary
            if r0 != r:
                augmat.rowswap(r0, r)
                computations.append(('swap', (r, r0), copy.deepcopy(augmat)))
            
            # force leading term of row to be 1
            k = augmat[r,r]**-1
            if k != 1:
                augmat.rowmult(r, k)
                computations.append(('mult', (r, k), copy.deepcopy(augmat)))

            # knock out all column values other than leading term
            for r1 in range(self.rowsize):
                if r1 == r: continue
                k = -augmat[r1, r]
                if k == 0: continue
                augmat.rowaddmultiple(k, r, r1)
                computations.append(('addmult', (k, r, r1), copy.deepcopy(augmat)))

            #print (augmat)

        # extract the inverse
        xs = []
        for r in range(self.rowsize):
            row = []
            for c in range(self.colsize):
                row.append(augmat[r, self.colsize + c])
            xs.append(row)
            
        return Matrix(xs), computations

    def augment(self):
        """ Add an identity matrix to the left of the given matrix
        """
        aug = []
        for i, row in enumerate(self.xs):
            extra = [0 for _ in range(self.colsize)]
            extra[i] = 1
            aug.append(row + extra)
        augmat = Matrix(aug)
        return augmat

    def delete_row(self, r):
        del self.xs[r]
        self.rowsize -= 1
        
    def delete_col(self, c):
        for row in self.xs:
            del row[c]
        self.colsize -= 1

    def minor(self, r, c):
        m = copy.deepcopy(self)
        m.delete_row(r)
        m.delete_col(c)
        return m
    
    def det(self):
        if self.rowsize != self.colsize:
            raise ValueError("det error: matrix not square")
            
        if self.rowsize == 1:
            # base
            return self[0,0]

        else:
            # recursion
            row = self.xs[0]
            computation0 = []
            computation1 = []
            computation2 = []
            computation3 = []
            computation4 = []
            computation5 = []
            for c, a in enumerate(row):
                if Matrix.omit_zero and a == 0:
                    computation0.append('0')
                else:
                    aminor = self.minor(0,c)
                    computation0.append(
                        "(-1)^{1+%s} (%s) \det %s" \
                        % (c+1, a, latex_bmatrix(aminor))
                        )
                    computation1.append(
                        "(%s) (%s) \det %s" \
                        % ((-1)**(1+c+1), a, latex_bmatrix(aminor))
                        )
                    computation2.append(
                        "(%s) \det %s" \
                        % ((-1)**(1+c+1) * a, latex_bmatrix(aminor))
                        )
                    if aminor.rowsize == 1:
                        computation3.append("(%s)(%s)" % \
                                            ((-1)**(1+c+1)*a,aminor[0,0]))
                        val = (-1)**(1+c+1)*a*aminor[0,0]
                        computation4.append(val)

            computation0 = " + ".join(computation0)
            computation1 = " + ".join(computation1)
            computation2 = " + ".join(computation2)
            computation3 = " + ".join(computation3)
            
            string = r"\det " + latex_bmatrix(self)
            string += "&= " + computation0 + "\\\\ \n" +\
                      "&= " + computation1 + "\displaybreak[0] \\\\ \n" +\
                      "&= " + computation2 + "\displaybreak[0] \\\\ \n"

            if computation3 != "":
                string += "&= " + computation3 + "\displaybreak[0] \\\\ \n"
            
            if len(computation4) > 0:
                s = sum(computation4)
                computation4 = " + ".join([xxx(_) for _ in (computation4)])
                computation5 = str(s)
                string += "&= " + computation4 + "\displaybreak[0] \\\\ \n"
                if computation4 != computation5:
                    string += "&= " + computation5 + "\displaybreak[0] \\\\ \n"
                
            Matrix.latex += string

            s = 0
            for c, a in enumerate(row):
                if Matrix.omit_zero and a == 0: continue
                aminor = self.minor(0,c)
                s += (-1)**(0 + c) * a * aminor.det()
            Matrix.lookup[str(self)] = s

            if self.rowsize > 2:
                Matrix.latex += r"\THEREFORE \det " + latex_bmatrix(self)

                yyy = []
                for c, a in enumerate(row):
                    if Matrix.omit_zero and a == 0: continue
                    aminor = self.minor(0,c)
                    v1 = (-1)**(0 + c) * a
                    v2 = Matrix.lookup[str(aminor)]
                    yyy.append("(%s)%s" % (v1, xxx(v2)))
                yyy = " + ".join(yyy)
                Matrix.latex += "&= " + yyy + "\displaybreak[0] \\\\ \n"
                Matrix.latex += "&= %s \\\\\n" % Matrix.lookup[str(self)]
                
            return s

def latex_add_matrix(m, n):
    a = latex_bmatrix(m)
    b = latex_bmatrix(n)
    c = latex_bmatrix(m + n)

    xs = []
    for i in range(m.rowsize):
        row = []
        for j in range(m.colsize):
            u = m[i,j]
            if u < 0: u = '(%s)' % u
            v = n[i,j]
            if v < 0: v = '(%s)' % v
            row.append('%s + %s' % (u, v))
        xs.append(row)
    d = Matrix(xs)
    d = latex_bmatrix(d)
    return r'''
\begin{align*}
%s + %s
&= %s \\
&= %s 
\end{align*}
    ''' % (a, b, d, c)


def latex_and_matrix(m, n):
    a = latex_bmatrix(m)
    b = latex_bmatrix(n)
    
    #c = latex_bmatrix(m + n)

    xs = []
    ys = []
    for i in range(m.rowsize):
        xs_row = []
        ys_row = []
        for j in range(m.colsize):
            u = m[i,j]
            if u < 0: u = '(%s)' % u
            v = n[i,j]
            if v < 0: v = '(%s)' % v
            xs_row.append(r'%s \land %s' % (u, v))
            ys_row.append((u % 2) * (v % 2))
        xs.append(xs_row)
        ys.append(ys_row)
    c = Matrix(ys)
    c = latex_bmatrix(c)
    d = Matrix(xs)
    d = latex_bmatrix(d)
    return r'''
\begin{align*}
%s \land %s
&= %s \\
&= %s 
\end{align*}
    ''' % (a, b, d, c)
    
#==============================================================================
# Originally FunctionPlot = Plot from plot.py
#==============================================================================
from math import *
import traceback

# Use to be Plot from plot.py
class FunctionPlot:
    def __init__(self,
                 width="5in",
                 height="3in",
                 domain="0:10",
                 color="black",
                 line_width='1',
                 num_points = 100,
                 legend_pos = "outer north east",
                 vars=['x','y'], # independent and dependent vars
                 tick_label_style=None,
                 ):
        self.width = width
        self.height = height
        self.domain = domain
        self.color = color
        self.line_width = line_width
        self.num_points = num_points
        self.vars = vars
        if len(self.vars) == 1: self.vars.append('y')
        self.legend_pos = legend_pos
        if tick_label_style:
            tick_label_style = r"tick label style={%s}" % tick_label_style
        else:
            tick_label_style = ""
            "legend pos=outer north east,"
        self.pre = r"""
\begin{center}
\begin{tikzpicture}[line width=%(line_width)s]
\begin{axis}[width=%(width)s, height=%(height)s,
             scatter/classes={a={mark=*,draw=black}},
             xlabel={\mbox{}},
             xlabel style={name=xlabel}, 
             ylabel={\mbox{}}, %(tick_label_style)s
             legend style={
                at={(xlabel.south)},
                yshift=-1ex,
                anchor=north,
                legend cell align=left,
                },
        ]
]""" % {'height':self.height,
        'width':self.width,
        'line_width':line_width,
        'tick_label_style':tick_label_style}
        self.body = ""
        self.post = r"""\end{axis}\end{tikzpicture}\end{center}"""
        self.exception = ''
        
    def add(self,
            *arglist,
            **argdict):
        """
        LINE GRAPH BY POINTS
        obj.add(((1,1),(2,2),(3,3)),line_width='1',color='black')

        LINE GRAPH BY LATEX FUNCTION
        obj.add("x**2 + 1",line_width='1',color='black')

        LINE GRAPH BY GENERATING POINTS BY PYTHON EXPRESSION
        obj.add("x**2 + 1", line_width='1', color='black', python=1)
        
        """
        try:
            d = {}
            d['color'] = argdict.get('color', self.color)
            d['line_width'] = argdict.get('line_width', self.line_width)
            d['domain'] = argdict.get('domain', self.domain)
            d['python'] = argdict.get('python', False)
            if d['python'] != False: d['python'] = True
            d['pin'] = argdict.get('pin', '')
            if d['pin'] in [1, '1', True]:
                d['pin'] = 'below right'
            d['style'] = argdict.get('style', '')
            d['num_points'] = argdict.get('num_points', self.num_points)
            if d['num_points'] <= 2: d['num_points'] = 3 # FIXIT
            d['vars'] = argdict.get('vars', self.vars)
            d['legend'] = argdict.get('legend', None)
            d['mark size'] = argdict.get('mark_size', '1')

            if isinstance(arglist[0], str):
                if not d['python']:
                    d['function'] = arglist[0]
                    d['expr'] = arglist[0]
                    partbody = r"""\addplot[draw=%(color)s, domain=%(domain)s, line width=%(line_width)s]{%(function)s};""" % d
                else: # python expr
                    d['expr'] = expr = arglist[0]
                    minx, maxx = d['domain'].split(':')
                    minx = float(minx.strip())
                    maxx = float(maxx.strip())
                    d['maxx'] = maxx
                    dx = (maxx - minx) / (d['num_points'] - 1)
                    x = minx; exec('%s = x' % d['vars'][0])
                    points = []
                    while x <= maxx:
                        try:
                            # in case for log function the x is not in domain
                            # can be a problem if the expression is written
                            # wrongly
                            #print ("---> expr: %s" % d['expr'])
                            y = eval(d['expr'])
                            points.append("(%s,%s)" % (x,y))
                        except Exception as e1: # don't use e ... conflicts with math.e
                            pass
                            #print (e)
                        x += dx; exec('%s = x' % d['vars'][0])
                    
                    try:
                        # add last point just in case of fp errors
                        x = maxx; exec('%s = x' % d['vars'][0])
                        y = eval(d['expr'])
                        points.append("(%s,%s)" % (x,y))
                    except Exception as e1:
                        pass
                    
                    d['points'] = '\n'.join(points)
                            
            elif isinstance(arglist[0], (list, tuple)):
                if d['style'] != 'scatter':
                    d['points'] = "\n".join([str(_) for _ in arglist[0]]) 
                else:
                    d['points'] = "\n".join(["%s %s a" % (x,y) for (x,y) in arglist[0]])
            if d['style'] == '':
                partbody = r"""\addplot[draw=%(color)s, line width=%(line_width)s] coordinates {%(points)s};""" % d
            elif d['style'] == 'step':
                partbody = r"""\addplot[const plot, draw=%(color)s, line width=%(line_width)s] coordinates {%(points)s};""" % d
            elif d['style'] == 'scatter':
                partbody = r"""\addplot[scatter,only marks,mark size=%(mark size)s,scatter src=explicit symbolic]
table[meta=label] {
x y label
%(points)s
};"""
                partbody = partbody % d
            
            self.body += partbody
            
            # pin
            pin = ''
            if d['pin']:
                d['pin_message'] = "$y=%s$" % argdict.get('pin_message', d['expr'])
                d['pin_message'] = d['pin_message'].replace("**", "^") 
                d['pin_message'] = d['pin_message'].replace("*", " ")
                d['pin_message'] = d['pin_message'].replace("log(", "\log(")
                d['pin_message'] = d['pin_message'].replace("sin(", "\sin(")
                if d['pin_message'] == '$y=$': d['pin_message'] = ''
                d['pin_x'] = argdict.get('pin_x', d['maxx'] * 0.8) # depends on maxx
                x = d['pin_x']
                exec('%s = x' % d['vars'][0])
                if d['expr']:
                    d['pin_y'] = eval(expr) # depends on expr
                else:
                    d['pin_y'] = 0 # TODO

                if d['pin_message'] != '':
                    pin = r"""\node[pin=%(pin)s:{%(pin_message)s}] at (axis cs:%(pin_x)s,%(pin_y)s) {};""" % d
                
            self.body += pin

            # legend
            legend = ''
            if d['legend']:
                legend = r"\addlegendentry{%s}" % d['legend']

            self.body += legend
    
        except Exception as e:
            str_e = str(e)
            f = open('traceback.txt', 'w')
            traceback.print_exc(file=f)
            f.close()
            str_tb = open('traceback.txt', 'r').read()
            self.exception = '%s\n\n%s' % (str_tb, str_e)
            raise
    def __str__(self):
        if self.exception:
            return self.exception
        else:
            return "%s\n%s\n%s" % (self.pre, self.body, self.post)



#==============================================================================
# graph and graph_coloring_label from latextool.py
#==============================================================================
def graph_coloring_label(
    *args
    ):
    """ args is a list of (var,value,list) """

    args = args[0]
    return args
    
    domains = [(len(z),z) for x,y,z in args]
    domains.sort()
    longest_domain = domains[-1][1]

    # put mbox into arg which has [] list
    def f(z):
        if z == []: xs = longest_domain
        else: xs = z
        return r'\mbox{$\{%s\}$}' % (','.join(xs))
    
    args = [(x,y,f(z)) for x,y,z in args]
    
    lines = [r"$%s$ & \hskip-9pt $= %s$ & \mbox{$%s$}" % (x,y,z) \
             for x,y,z in args]

    return r'''\begin{tabular}{lll}
\end{tabular}'''


"""
Example:
  graph(shape='circle',
        minimumsize='14mm',
        layout='''
          A
         B C
        D E F G
        ''',
        edges='A-B,A>C',
        A='shape=rectangle, label=$A$, pos=(3,5)',
        B='label=B',
        )
The last keyword args A,B are kept in the dict args.
"""
def graph(shape='circle',
          minimum_size='14mm',
          layout=None,
          xscale=1,
          yscale=2,
          edges='',
          separator=',',
          fill=None,
          fill_dict=None, # NEW
          xoffset=0,
          yoffset=0,
          **args
          ):
    """ For output of graphs for latex using the pgf library """

    # get all the nodes from layout
    nodes = [x for x in layout.replace('\n', ' ').split(' ') if x != '']

    # now get nodes from args
    for key in args.keys():
        if key not in nodes: nodes.append(key)

    if fill_dict==None:
        fill_dict = {}
        
    # put all nodes into dict and fill with default values
    node_dict = {}
    for node in nodes:
        node_dict[node] = {'shape':shape,
                           'minimum_size':minimum_size,
                           'pos':None,
                           'label':'$%s$' % node,
                           'fill': fill_dict.get(node, fill),
                           }

    # now overwrite with args
    for key,value in args.items():
        if key != 'edge_label':
            parts = [_.strip() for _ in value.split(separator) \
                     if _.strip() != '']
            for part in parts:
                try:
                    k,v = part.split('=', 1)
                    k,v = k.strip(), v.strip()
                    node_dict[key][k] = v
                except:
                    pass

    # remove pre and post blank lines
    layout_lines = [line for line in layout.split('\n')]
    
    # make sure every line has the same number of chars by appending ' '
    max_len = max([len(line) for line in layout_lines])
    layout_lines = [line + (max_len - len(line)) * ' ' for line in layout_lines]
    # remove leftmost char from every line if it's ' '
    while 1:
        # check if every line begins with ' '
        if all([line[0] == ' ' for line in layout_lines]):
            layout_lines = [line[1:] for line in layout_lines]
        else:
            break

    # now place the nodes
    s = ''
    for line_index, line in enumerate(layout_lines):
        for node in nodes:
            p = re.compile('(^| )%s(\Z| )' % node)
            search = p.search(line)
            if search:
                ind = search.start()
                if search.group()[0] == ' ': ind += 1
                shape = node_dict[node]['shape']

                # Python3 change
                if 'graph coloring' in node_dict[node]: # OLD: node_dict[node].has_key('graph coloring')
                    label = node_dict[node]['label']
                    label = graph_coloring_label(eval(label))
                else:
                    label = node_dict[node]['label']

                size = 'minimum size=%s' % node_dict[node]['minimum_size']
                if node_dict[node]['fill']:
                    size += ',fill=%s' % node_dict[node]['fill']
                if shape=='rectangle':
                    # Python3
                    if 'minimum width' in node_dict[node]: # OLD: node_dict[node].has_key('minimum width')
                        size += ',minimum width=%s' % node_dict[node]['minimum width']
                    # Python3 change
                    if 'minimum height' in node_dict[node]:
                        size += ',minimum height=%s' % node_dict[node]['minimum height']
                if shape=='tree':
                    # Python3 change
                    if 'minimum height' in node_dict[node]:
                        size += ',minimum height=%s' % node_dict[node]['minimum height']
                if 'text width' in node_dict[node]:
                    size += ',text width=%s' % node_dict[node]['text width']

                if shape=='tree':
                    # empty node
                    # the triangle
                    s += r'''\node at (%s,%s)
    [%s,
     draw,%s,
     anchor=north] (%s) {%s};''' % \
                         (ind*xscale, -line_index*yscale,
                          'isosceles triangle, shape border rotate=+90',
                          size,
                          node + 'triangle',
                          label)
                    s += '\n';
                    s += r'\coordinate (%s) at (%s,%s);' % \
                         (node, xoffset + ind*xscale, yoffset -line_index*yscale)                    
                elif shape=='None':
                    s += r'\node at (%s,%s) [%s] (%s) {%s};' % \
                         (xoffset + ind*xscale, yoffset -line_index*yscale, size, node, label)
                else:
                    s += r'\node at (%s,%s) [%s,draw,%s] (%s) {%s};' % \
                         (xoffset + ind*xscale, yoffset -line_index*yscale, shape, size, node, label)
                    
                s += '\n'

    #print ("s:",)
    
    # now add edges
    for edge in [_.strip() for _ in edges.strip().split(',') if _.strip() != '']:
        start = None
        for node in nodes:
            if edge.startswith(node):
                start = node
                break
        if start == None:
            print ("\nERROR: UNKNOWN START NODE IN %s" % edge)
            continue
        
        end = None
        for node in nodes:
            if edge.endswith(node):
                end = node
                break
        if end == None:
            print ("\nERROR: UNKNOWN START NODE IN %s" % edge)
            continue

        linetype = edge[len(start):][:-len(end)]
        
        if linetype == '>': linetype = '->'
        elif linetype == '<': linetype = '<-'
        elif linetype == '-': pass
        elif linetype == '->': pass
        elif linetype == 'dashed': linetype='dashed' #????
        else:
            print ()
            print ("ERROR: UNKNOWN LINE TYPE %s" % linetype)
            print ()
            continue

        # Python3 change
        if 'edge_label' in args \
               and (start,end) in args['edge_label']:
            s += r'\draw [%s,thick] (%s) -- (%s) node[%s]{%s}  ;' % \
                 (linetype, start, end,
                  args['edge_label'][(start,end)].get('style','auto,pos=0.5'), 
                  args['edge_label'][(start,end)]['label'])
            s += '\n'            
        else:
            s += r'\draw [%s,thick] (%s) -- (%s);' % (linetype, start, end)
            s += '\n'

    return r'''
\begin{tikzpicture}
%s
;
\end{tikzpicture}
    ''' % s


def graph2(shape='circle',
           minimum_size='14mm',
           layout=None,
           xscale=1,
           yscale=2,
           edges='',
           separator=',',
           fill=None,
           fill_dict=None,
           xoffset=0,
           yoffset=0,
           **args):
    """
    same as graph but as a string without the tikzpicture env
    """
    
    #s = apply(graph,
    #          (shape,
    #           minimum_size,
    #           layout,
    #           xscale,
    #           yscale,
    #           edges,
    #           separator,
    #           fill,
    #           fill_dict,
    #           xoffset,
    #           yoffset,
    #           ),
    #          args)
    s =  graph(shape,
               minimum_size,
               layout,
               xscale,
               yscale,
               edges,
               separator,
               fill,
               fill_dict,
               xoffset,
               yoffset,
               **args)
    s = s.replace(r"\begin{tikzpicture}", "")
    s = s.replace(r"\end{tikzpicture}", "")
    return s

def path(xs=[], linecolor='', style='', bend=''):
    pass
#==============================================================================
def table2(plot,
           m,
           x0=None, y0=None,
           x=0, y=0, # ADDED 6/28/2016 -- x0, y0 deprecated
           rowlabel='x', collabel='y',
           rownames=None, colnames=None,# for labeling rows and columns
           width=0.7, height=0.7,       # of cell
           do_not_plot=False,           # basically just to get the
                                        # container
           rect=None,                   # Plays the role of Rect constructor
                                        # for each x in m, I call rect(m)
           linewidth=None,
           border_linewidth=None,
          ):
    """
    2D array / table with labels for row and column.
    Can be used for instance in 2D table lookup in dynamic programming.
    
    TODO:
    - the rows and columns are labeled with index values. Allow arbitrary
      strings.
    """
    
    if x0==None: x0 = x
    if y0==None: y0 = y
    if linewidth==None: linewidth=0.06
    WIDTH, HEIGHT = width, height
    C = RectContainer(x=x0, y=y0, align='left', direction='top-to-bottom')
    numrows = len(m)
    numcols = max(len(m[i]) for i in range(numrows))
    # If a row has fewer columns, create blanks
    #for row in m:
    #    row = row + ['?' for _ in range(numcols - len(row))] 

    if border_linewidth==None: border_linewidth=0.06
    for xs in m:
        row0 = RectContainer(x=0, y=0, align='bottom', direction='left-to-right')
        for x in xs:
            if rect:
                row0 += rect(x)
            else:
                row0 += Rect2(x0=0, y0=0, x1=WIDTH, y1=HEIGHT,
                              linewidth=0.02, label=r'{\texttt{%s}}' % x)
        C += row0; row0.x = row0.x0; row0.y = row0.y0; row0.layout()

    if not do_not_plot:
        plot += C;

        # index for column
        if colnames==None:
            colnames = [r'\texttt{%s}' % _ for _ in range(numcols)]
        elif len(colnames) != numcols:
            colnames = colnames[:numcols] + \
                       ['' for _ in range(numcols - len(colnames))]
        for x,y in zip(colnames, [C[0][c] for c in range(numcols)]):
            # use rect's of the top row and anchor colname
            x0,y0 = y.top()
            plot += r'\node[anchor=south] at (%s,%s) {%s};' % (x0, y0, x)

        # index for row. rownames to the left of left column.
        if rownames==None:
            rownames = [r'\texttt{%s}' % _ for _ in range(numrows)]
        elif len(rownames) != numrows:
            rownames = rownames[:numrows] + \
                       ['' for _ in range(numrows - len(rownames))]
        for x,y in zip(rownames, [C[r][0] for r in range(numrows)]):
            # use rect's of the left column and anchor row name
            x0,y0 = y.left()
            plot += r'\node[anchor=east] at (%s,%s) {%s};' % (x0, y0, x)
        
        # boundary
        x0,y0=C[-1][0].bottomleft()
        x1,y1=C[0][-1].topright()
        #  WARNING: Changeing Rect2 to Rect
        plot += Rect2(x0=x0,y0=y0,x1=x1,y1=y1,linewidth=border_linewidth)
        
        # diagonal line separating row name and col name
        if rowlabel and collabel:
            x0,y0 = C[0][0].topleft()
            plot += Line(points=[(x0,y0),(x0-1,y0+1)], linewidth=0.08) # WARNING: hardcoding
            # row label
            plot += r'\node[anchor=north east] at (%s,%s) {%s};' % \
                    (x0-1/2.0, y0+1/2.0, rowlabel)
            # col labeltttfx
            plot += r'\node[anchor=south west] at (%s,%s) {%s};' % \
                    (x0-1/2.0, y0+1/2.0, collabel)

    return C # return array

#==============================================================================
# 2d array of 2d arrays
def table3(p,
           M,
           x0=0, y0=0,
           width=0.7, height=0.7,       # of cell
           do_not_plot=False,           # basically just to get the
                                        # container
           rect=None,                   # Plays the role of Rect constructor
                                        # for each x in m, I call rect(m)
           background=None,
           vphantom=None,               # vphantom: string
                                        #           Use this vphantom
                                        # vphantom: None
                                        #           Autocompute vphantom
           title=None,
           title_distance=0.1,
           linewidth=None,
           border_linewidth=None,
          ):

    if background:
        import copy
        N = table3(p=p, M=copy.deepcopy(M),
                   x0=x0, y0=y0,
                   width=width, height=height,
                   rect=rect,
                   do_not_plot=True,
                   linewidth=linewidth,
                   border_linewidth=border_linewidth)
        for (a,b,c,d), background_color in background.items():
            r = N[a][b][c][d]
            x0_,y0_ = r.bottomleft()
            x1_,y1_ = r.topright()
            p += str(Rect(x0=x0_, y0=y0_, x1=x1_, y1=y1_,
                          linewidth=0,
                          background=background_color))
        return table3(p=p, M=M,
                      x0=x0, y0=y0,
                      rect=rect,
                      width=width, height=height, linewidth=linewidth,
                      border_linewidth=border_linewidth) 

    N = [[0 for c in r] for r in M]

    #--------------------------------------------------------------------------
    # Form vphamtom: This can cause problems when the values contain some
    # latex commands. Set phantom parameter to '' (example) in that case.
    #--------------------------------------------------------------------------
    if vphantom == None:
        allvalues = []
        for r in M:
            for c in r:
                for r0 in c:
                    for c0 in r0:
                        if c0 not in allvalues:
                            allvalues.append(c0)

        allvalues = ''.join([str(_) for _ in allvalues])
        vphantom = r'\vphantom{%s}' % allvalues
    else:
        vphantom = r'\vphantom{%s}' % vphantom

    #--------------------------------------------------------------------------
    # Add vphantom to M
    #--------------------------------------------------------------------------
    for a in M:
        for b in a:
            for c in b:
                for i in range(len(c)):
                    c[i] = '{%s%s}' % (vphantom, c[i])
    
    for r,row in enumerate(M):
        if r == 0:
            pass
        else:
            x0,y0 = N[r-1][0].bottomleft()
        for c,col in enumerate(row):
            m = M[r][c]
            C = table2(p, m,
                       x0=x0,y0=y0,
                       width=width, height=height,
                       do_not_plot=do_not_plot,
                       rownames=[], colnames=[], collabel=None, rowlabel=None,
                       rect=rect,linewidth=linewidth, border_linewidth=border_linewidth)
            x0,y0 = C.topright()
            N[r][c] = C

    if title:
        # Create a named node for N.
        # 
        x, y = N[0][0].topleft()
        randname = randstr()
        from latexcircuit import POINT
        y += title_distance # HARDCODED CONSTANT
        p += str(POINT(x=x, y=y, r=0, anchor='flushtopleft', label=title)) 
    return N

#==============================================================================
# table4
#==============================================================================
def table4(p,
           M,
           x0=0, y0=0,
           widths=None, height=0.7,
           do_not_plot=False,           # basically just to get the
                                        # container
           background=None,
           vphantom=None,               # vphantom: string
                                        #           Use this vphantom
                                        # vphantom: None
                                        #           Autocompute vphantom
           title=None,
           title_distance=0.1,
          ):
    m00 = [M[0]]
    m10 = M[1:]
    M = [[m00],[m10]]
    def rect(x):
        rect.i = rect.i + 1
        rect.i = rect.i % len(widths)
        return Rect(x0=0, y0=0, x1=widths[rect.i], y1=height, label=x)
        return rect__
    rect.i = -1
    return table3(p, M, x0=x0, y0=y0, rect=rect, do_not_plot=do_not_plot,
                  background=background, vphantom=vphantom,
                  title=title, title_distance=title_distance)
    
#==============================================================================
# table5: same as 4 but no header
#==============================================================================
def table5(p,
           M,
           x0=0, y0=0,
           widths=None, height=0.7,
           do_not_plot=False,           # basically just to get the
                                        # container
           background=None,
           vphantom=None,               # vphantom: string
                                        #           Use this vphantom
                                        # vphantom: None
                                        #           Autocompute vphantom
           title=None,
           title_distance=0.1,
          ):
    M = [[M]]

    def rect(x):
        rect.i = rect.i + 1
        rect.i = rect.i % len(widths)
        return Rect(x0=0, y0=0, x1=widths[rect.i], y1=height, s=x, align='t',
                    innersep=0.1, radius=0.0)
        return rect__
    rect.i = -1
    return table3(p, M, x0=x0, y0=y0, rect=rect, do_not_plot=do_not_plot,
                  background=background, vphantom=vphantom,
                  title=title, title_distance=title_distance)
    
           
def shorten(p0, p1, factor=0.5,
            start_by=None, end_by=None, by=None):
    x0, y0 = p0
    x1, y1 = p1
    """
    shorten a vector about the midpoint
    (x0, y0) --------*-------> (x1, y1)
        (x0, y0) ----*---> (x1, y1)
    Note that the midpoint of the shortened vector is the same
    as the original vector.

    This is useful in drawing arrows between cells in a memorization
    table where you need to shorten the vector from the center of one
    cell to another so that the contents of the cells are not
    overwritten.

    ADDED:
        start_by - shorten the starting point by this amount
        end_by - shorten the starting point by this amount
    """
    dx, dy = x1 - x0, y1 - y0
    length = sqrt(dx * dx + dy * dy)
    ux, uy = dx/length, dy/length # normalized

    if start_by==None and end_by==None and by==None:
        midx, midy = x0 + dx/2.0, y0 + dy/2.0
        p0 = midx - factor/2.0 * dx, midy - factor/2.0 * dy 
        p1 = midx + factor/2.0 * dx, midy + factor/2.0 * dy 
    else:
        if by!=None:
            start_by = by
            end_by = by
        else:
            if start_by==None: start_by = 0
            if end_by==None: end_by = 0
        p0 = x0 + start_by * ux, y0 + start_by * uy
        p1 = x1 - end_by * ux, y1 - end_by * uy
    return p0,p1


#============================================================================
# Code
#============================================================================
def code(p, M, width=0.2, height=0.4, d={'':' ', '.':' '},
         border_linewidth=0,
         innersep=0.1,
         x=0, y=0,
         ):
    if isinstance(M, str):
        #M = M.strip()
        M = M.split('\n')
        M = [list(line) for line in M]
    elif isinstance(M, list):
        if all(isinstance(line, list) for line in M):
            pass
    else:
        # invalid M?
        M = [list('invalid M')]
        
    numcols = max([len(line) for line in M])
    M = [line + ['' for _ in range(numcols - len(line))] \
        for line in M]
    def f(c):
        if c in d.keys():
            c = d[c]
        return r'\texttt{%s}' % c
    M = [[f(_) for _ in line] for line in M]
    def rect(x, width=width, height=height):
        return Rect(x0=0, y0=0, x1=width, y1=height, label=x,
                    linewidth=0)
    N = table3(p=p, M=[[M]], rect=rect, linewidth=0,
               x0=x, y0=y,
               border_linewidth=0)
    # Make the border slightly larger?
    x0,y0 = N[-1][0].bottomleft(); x0 -= innersep; y0 -= innersep
    x1,y1 = N[0][-1].topright(); x1 += innersep; y1 += innersep
    p += Rect(x0=x0, y0=y0, x1=x1, y1=y1, linewidth=border_linewidth)
    return N
def coderect(N, r0, c0, r1, c1, linecolor='red', linewidth=0.04):
    x0,y0 = N[0][0][r0][c0].bottomleft(); x0-=0.05; y0-=0.05
    x1,y1 = N[0][0][r1][c1].topright(); x1+=0.05; y1+=0.05
    r0 = Rect(x0=x0, y0=y0, x1=x1, y1=y1,
              linecolor=linecolor, linewidth=linewidth)
    return r0
def linebelow(p, N, r, c0, c1):
    linewidth = 0.02
    rect = coderect(N, r, c0, r, c1)
    x0, y0 = rect.bottomleft(); p0 = (x0, y0 + 0.05)
    x1, y1 = rect.bottomright(); p1 = (x1, y1 + 0.05)
    p += Line(points=[p0, p1], linewidth=linewidth)    
def divlinebelow(p, N, r, c0, c1):
    linewidth = 0.02
    rect0 = coderect(N, r, c0, r, c1)
    x0, y0 = rect0.bottomleft(); p0 = (x0, y0 + 0.05)
    rect1 = coderect(N, r, c0 - 1, r, c1)
    x1, y1 = rect1.bottomleft(); p1 = (x1, y1 + 0.05)
    x0 = (x0 + x1) / 2.0
    p0 = (x0, y0 + 0.05)

    x1, y1 = rect0.bottomright(); p1 = (x1, y1 + 0.05)
    p2 = (x0, y0 - 0.32) # 0.32 = height, hardcoded
    
    p += Line(points=[p0, p1], linewidth=linewidth)

    p3 = (p0[0] + 0.1, (p0[1] + p2[1])/2.0)
    p += Line(points=[p0, p2], controls=[p3], linewidth=linewidth)
def decpoint(N, r, c):
    """ Place decimal point at bottomright of N[r][c] """
    r = coderect(N, r, c, r, c)
    x,y = r.bottomright()
    return Circle(x=x-0.045, y=y+0.122, r=0.015, background='black')









# Adjacency list
def adjlist(p=None,
            X=0, Y=0,
            xs=[[1,2],[3,4],[],[5,6],[7,8,9],[0]],
            pointerwidth = 0.5, pointerheight = 0.5,
            nodevspace=0.2, nodehspace=0.5,
            nodewidth=0.5, nodeheight=0.5,
            gap = 2):
    """
    Returns
    - rectcontainer (of pointers)
    - list of lines to draw crosses in the pointer container
    - list of list of rects (the nodes)
    - list of lines from pointers to first node of each list of node
    - list of list of lines from node to node
    """
    
    def node(x, y, width, height, s):
        """ Warning: each node is a container ... right now there's
        only one rect in the container """
        c = RectContainer(x=x, y=y)
        c += Rect2(x0=0, y0=0, x1=width, y1=height, label=r'{\texttt{%s}}' % s)
        return c
    
    def cross(r):
        return Line(points=[r.topleft(), r.bottomright()]), Line(points=[r.topright(), r.bottomleft()]) 

    n = len(xs)
    crosses = {}
    nodes = {}
    lines = {} # lines from pointer to node or node to node
    
    # array of pointers
    r = RectContainer(x=X, y=Y, align='left', direction='top-to-bottom')
    for i in range(n):
        r += Rect2(x0=0, y0=0, x1=pointerwidth, y1=pointerheight, label='')

    for i,s in enumerate(xs):

        if n % 2 == 0:
            """
                       +-+
                       | |
                       +-+
                       
                       +-+
            +-+        | |
            | |        +-+
            +-+        
            | |        +-+
            +-+        | |
            | |        +-+
            +-+---------------------------------------------------
            | |
            +-+
            """

            y = -(n / 2.0) * pointerheight + (n/2.0 - 1 - i) * (nodevspace + nodeheight)  + 0.5 * nodevspace
        else:
            """
                       +-+
                       | |
                       +-+
                     
            +-+        +-+
            | |        | |
            +-+        +-+
            | |
            +-+        +-+
            | |--------| |----------------------------------------
            +-+        +-+
            | |
            +-+
            """
            y = -(n/2.0) * pointerheight \
                + (n/2 - i) * (nodevspace + nodeheight) - 0.5 * nodeheight 
        x = pointerwidth + gap
        prev = None
        if s == []:
            l1,l2 = cross(r[i])
            crosses[i] = [l1, l2]
        else:
            anodes = []
            alines = []
            for j,t in enumerate(s):
                anode = node(x, y, nodewidth, nodeheight, t)
                x += nodewidth + nodehspace
                anodes.append(anode)
                if j == 0:
                    alines.append(Line(points=[r[i].center(), anode.left()], endstyle='>'))
                else:
                    alines.append(Line(points=[prev.right(), anode.left()], endstyle='>'))
                prev = anode
            nodes[i] = anodes
            lines[i] = alines
                
    return r, crosses, nodes, lines

#==============================================================================
# K-maps
#==============================================================================
def kmap_rect(rectBL, rectTR=None, linecolor='red', linewidth=0.1, d=0.15):
    if rectTR == None: rectTR = rectBL
    x0, y0 = rectBL.bottomleft(); x0 += d; y0 += d
    x1, y1 = rectTR.topright();     x1 -= d; y1 -= d
    radius = min(rectBL.x1 - rectBL.x0, rectBL.y1 - rectBL.y0)/2.0 - d
    return Rect2(x0=x0, y0=y0, x1=x1, y1=y1,
                 linewidth=linewidth, radius=radius, linecolor=linecolor)

def kmap_NN(p, rectBL, rectTR=None, linewidth='0.1', linecolor='blue', d=0.15):
    # bend in rect from east edge to east edge
    # rectBL - bottomleft rect
    # rectTR - topright rect. If this is None, then it's set to rectBL
    if rectTR == None: rectTR = rectBL
    radius = min(rectBL.x1 - rectBL.x0, rectBL.y1 - rectBL.y0)/2.0 - d
    # p0    p3
    #
    # p1    p2
    p1 = rectBL.bottomleft(); p1 = (p1[0] + d, p1[1] + d)
    p3 = rectTR.topright();   p3 = (p3[0] - d, p3[1]    )    
    p0 = (p1[0], p3[1])
    p2 = (p3[0], p1[1])
    
    p += r'''
\draw[color=%s, line width=%scm, rounded corners=%scm] %s -- %s -- %s -- %s;
    ''' % (linecolor, linewidth, radius,
           str(p0), str(p1), str(p2), str(p3))

def kmap_SS(p, rectBL, rectTR=None, linewidth='0.1', linecolor='blue', d=0.15):
    # bend in rect from east edge to east edge
    if rectTR == None: rectTR = rectBL
    radius = min(rectBL.x1 - rectBL.x0, rectBL.y1 - rectBL.y0)/2.0 - d
    # p0    p3
    #
    # p1    p2
    p1 = rectBL.bottomleft(); p1 = (p1[0] + d, p1[1]    )
    p3 = rectTR.topright();   p3 = (p3[0] - d, p3[1] - d)    
    p0 = (p1[0], p3[1])
    p2 = (p3[0], p1[1])

    p += r'''
\draw[color=%s, line width=%scm, rounded corners=%scm] %s -- %s -- %s -- %s;
    ''' % (linecolor, linewidth, radius,
           str(p1), str(p0), str(p3), str(p2))

def kmap_WW(p, rectBL, rectTR=None, linewidth='0.1', linecolor='blue', d=0.15):
    # bend in rect from east edge to east edge
    if rectTR == None: rectTR = rectBL
    radius = min(rectBL.x1 - rectBL.x0, rectBL.y1 - rectBL.y0)/2.0 - d
    # p0    p3
    #
    # p1    p2
    p1 = rectBL.bottomleft(); p1 = (p1[0]    , p1[1] + d)
    p3 = rectTR.topright();   p3 = (p3[0] - d, p3[1] - d)    
    p0 = (p1[0], p3[1])
    p2 = (p3[0], p1[1])

    p += r'''
\draw[color=%s, line width=%scm, rounded corners=%scm] %s -- %s -- %s -- %s;
    ''' % (linecolor, linewidth, radius,
           str(p0), str(p3), str(p2), str(p1))

def kmap_EE(p, rectBL, rectTR=None, linewidth='0.1', linecolor='blue', d=0.15):
    # bend in rect from east edge to east edge
    if rectTR == None: rectTR = rectBL
    radius = min(rectBL.x1 - rectBL.x0, rectBL.y1 - rectBL.y0)/2.0 - d
    # p0    p3
    #
    # p1    p2
    p1 = rectBL.bottomleft(); p1 = (p1[0] + d, p1[1] + d)
    p3 = rectTR.topright();   p3 = (p3[0]    , p3[1] - d)
    p0 = (p1[0], p3[1])
    p2 = (p3[0], p1[1])

    p += r'''
\draw[color=%s, line width=%scm, rounded corners=%scm] %s -- %s -- %s -- %s;
    ''' % (linecolor, linewidth, radius,
           str(p3), str(p0), str(p1), str(p2))

def kmap_NW(p, rectBL, rectTR=None, linewidth='0.1', linecolor='blue', d=0.15):
    # bend in rect from east edge to east edge
    if rectTR == None: rectTR = rectBL
    radius = min(rectBL.x1 - rectBL.x0, rectBL.y1 - rectBL.y0)/2.0 - d
    # p0    p3
    #
    # p1    p2
    p1 = rectBL.bottomleft(); p1 = (p1[0]    , p1[1] + d)
    p3 = rectTR.topright();   p3 = (p3[0] - d, p3[1]    )
    p0 = (p1[0], p3[1]) # not used
    p2 = (p3[0], p1[1])
    p += r'''
\draw[color=%s, line width=%scm, rounded corners=%scm] %s -- %s -- %s;
    ''' % (linecolor, linewidth, radius,
           str(p3), str(p2), str(p1))

def kmap_SE(p, rectBL, rectTR=None, linewidth='0.1', linecolor='blue', d=0.15):
    # bend in rect from east edge to east edge
    if rectTR == None: rectTR = rectBL
    radius = min(rectBL.x1 - rectBL.x0, rectBL.y1 - rectBL.y0)/2.0 - d
    # p0    p3
    #
    # p1    p2
    p1 = rectBL.bottomleft(); p1 = (p1[0] + d, p1[1]    )
    p3 = rectTR.topright();   p3 = (p3[0]    , p3[1] - d)
    p0 = (p1[0], p3[1])
    p2 = (p3[0], p1[1])
    p += r'''
\draw[color=%s, line width=%scm, rounded corners=%scm] %s -- %s -- %s;
    ''' % (linecolor, linewidth, radius,
           str(p1), str(p0), str(p3))

def kmap_NE(p, rectBL, rectTR=None, linewidth='0.1', linecolor='blue', d=0.15):
    # bend in rect from east edge to east edge
    if rectTR == None: rectTR = rectBL
    radius = min(rectBL.x1 - rectBL.x0, rectBL.y1 - rectBL.y0)/2.0 - d
    # p0    p3
    #
    # p1    p2
    p1 = rectBL.bottomleft(); p1 = (p1[0] + d, p1[1] + d)
    p3 = rectTR.topright();   p3 = (p3[0]    , p3[1])
    p0 = (p1[0], p3[1])
    p2 = (p3[0], p1[1])
    p += r'''
\draw[color=%s, line width=%scm, rounded corners=%scm] %s -- %s -- %s;
    ''' % (linecolor, linewidth, radius,
           str(p0), str(p1), str(p2))

def kmap_SW(p, rectBL, rectTR=None, linewidth='0.1', linecolor='blue', d=0.15):
    # bend in rect from east edge to east edge
    if rectTR == None: rectTR = rectBL
    radius = min(rectBL.x1 - rectBL.x0, rectBL.y1 - rectBL.y0)/2.0 - d
    # p0    p3
    #
    # p1    p2
    p1 = rectBL.bottomleft(); p1 = (p1[0]    , p1[1]    )
    p3 = rectTR.topright();   p3 = (p3[0] - d, p3[1] - d)
    p0 = (p1[0], p3[1])
    p2 = (p3[0], p1[1])
    p += r'''
\draw[color=%s, line width=%scm, rounded corners=%scm] %s -- %s -- %s;
    ''' % (linecolor, linewidth, radius,
           str(p2), str(p3), str(p0))


def get_kmap_data(m, circle_terms=[1, '1','d'], donotremove=None, debug=False):
    """
    returns a dictionary d
    d['nonprime']
    d['essential-prime']
    d['nonessential-prime']
    where each is a dictionary of lists of implicants organized by size, i.e.,
    
    d['nonprime'][1] = [..., nonprime implicants of size 1, ...]
    d['nonprime'][2] = [..., nonprime implicants of size 2, ...]
    d['nonprime'][4] = [..., nonprime implicants of size 4, ...]
    etc.
    
    An implicant x is of the form (r0,r1,c0,c1) where
    - r0,r0+1,...,r1 (up to mod row size of m)
    - c0,c0+1,...,c1 (up to mod column size of m)
    
    An implicant appears only once.
    """
    if donotremove == None: donotremove = []

    #if circle:
    # Compute implicants
    # X = {(rect,False)} where rect is 1-by-1 rects containing '1'
    # The flag tells us if the rect is including in a larger one.
    # Let r0,r1 be rects in X with flags f0,f1.
    # If r0,r1 share a common edge and the combine size is a power of 2,
    # we combine them to get R:
    #   put (R, False) in X
    #   set flags f0,f1 of r0,r1 to True (they are covered by another rect.
    #
    # We have to make sure that two rects r0,r1 are not combined again and
    # again.
    rowsize = len(m)
    colsize = len(m[0])
    circle = True
    if donotremove==None: donotremove = []
    if circle:
        groups = {}
        
        # groups is a dictionary of of the form
        # groups = [..., ((r0,r1),(c0,c1),covered), ...]
        # where covered is a bool and is true if this rect was covered with another
        groups[1] = []
        for r, row in enumerate(m):
            for c, col in enumerate(row):
                if col in circle_terms:
                    groups[1].append([(r,r),(c,c),False])

        size = 1
        while 1:
         
            groups[2*size] = []

            length = len(groups[size])
            for i in range(length):
                rect = groups[size][i]
                (r0,r1),(c0,c1),_ = rect
                for j in range(i + 1, length):
                    RECT = groups[size][j]
                    if rect == RECT: continue
                    # combine is total size if power of 2 and
                    # the two rect groups share a common edge
                    (r0,r1),(c0,c1),_ = rect
                    (R0,R1),(C0,C1),_ = RECT
                    if (c1 + 1) % colsize == C0 and r0==R0 and r1==R1:
                        # right of rect meets left of RECT
                        if C1 + 1 == c0:
                            c0 = 0; C1 = colsize - 1
                        if [(r0,r1),(c0,C1),False] not in groups[2*size]:
                            if debug: print ("1 ---> %s" % [(r0,r1),(c0,C1),False])
                            groups[2*size].append([(r0,r1),(c0,C1),False])
                        rect[2] = True
                        RECT[2] = True
                    elif (C1 + 1) % colsize == c0 and r0==R0 and r1==R1:
                        # right of RECT meets left of rect
                        if c1 + 1 == C0:
                            C0 = 0; c1 = colsize - 1
                        if [(r0,r1),(C0,c1),False] not in groups[2*size]:
                            if debug: print ("2 ---> %s" % [(r0,r1),(C0,c1),False])
                            groups[2*size].append([(r0,r1),(C0,c1),False])
                        rect[2] = True
                        RECT[2] = True
                    elif (r1 + 1) % rowsize == R0 and c0==C0 and c1==C1:
                        # bottom of rect meets top of RECT
                        if R1 + 1 == r0:
                            r0 = 0; R1 = rowsize - 1
                        if [(r0,R1),(c0,c1),False] not in groups[2*size]:
                            if debug: print ("3 ---> %s" % [(r0,R1),(c0,c1),False]) 
                            groups[2*size].append([(r0,R1),(c0,c1),False])
                        rect[2] = True
                        RECT[2] = True
                    elif (R1 + 1) % rowsize == r0 and c0==C0 and c1==C1:
                        # bottom of RECT meets top of rect
                        if r1 + 1 == R0:
                            R0 = 0; r1 = rowsize - 1
                        if [(R0,r1),(c0,c1),False] not in groups[2*size]:
                            if debug: print ("4 ---> %s" % [(R0,r1),(c0,c1),False])
                            groups[2*size].append([(R0,r1),(c0,c1),False])
                        rect[2] = True
                        RECT[2] = True
            if debug:
                print ("groups[%s]:" % size)
                for x in groups[size]: print ("   %s" % x)
                print ("groups[%s]:" % (2*size))
                for x in groups[2*size]: print ("   %s" % x)
            if groups[2*size] == []: break
            size = 2*size
            
        # Removing of certain redundant groups
        # The following will produce three groups:
        #      1 1
        #    1 1
        # Two horizontal and 1 vertical.
        # The vertical should be removed
        # This will produce 4 groups:
        #      1 1
        #    1 1
        #    1
        # Two horizontal and 2 vertical.
        # The vertical should be removed
        # Method: for each group, G, if coordinates in G is covered by
        #         all other groups, remove G. Start with G of smallest size
        # Does this greedy method works?
        #'''
        def add_rows_cols(rows_cols, r0,r1,c0,c1):
            if debug: print ("rows_cols: %s" % rows_cols)
            if debug: print ("r0,r1,c0,c1: %s" % str(r0,r1,c0,c1))
            r = r0
            while 1:
                #if debug: print ("r0: %s" % r0)
                c = c0
                while 1:
                    #if debug: print ("c0: %s" % c0)
                    if (r,c) not in rows_cols:
                        rows_cols.append((r,c))
                    if c == c1: break
                    c = (c + 1) % colsize
                if r == r1: break;
                r = (r + 1) % rowsize
            return rows_cols

        if debug:
            print ("before removal of nonessentials")
            for k,v in groups.items():
                print (k,v)

        # In the above, the 'covered' flag was set to true if an implicant was combined.
        # Now we need to take care of implicants which are covered by two other
        # implicants, i.e., an implicant can be nonessential if it appears in a larger
        # implicant, but it can also be nonessential because it was covered by two
        # other implicants. We also need to make sure that in the situation where a
        # collection of implicants cover each other, the *SMALLEST* one is marked as
        # non-essential. So we mark implicants as nonessential starting with the
        # smallest size.
        # If ((r0,r1),(c0,c1),f) is in groups[size], then
        # f == True:  Was combined, i.e., not prime
        # f == False: Not combined, i.e., prime
        # After the following, the nonessential primes are removed and placed in list
        # nonessential_prime
        size = 1
        nonessential_prime = {}
        while groups[size] != []:
            if debug: print ("\nsize: %s" % size)
            change = False
            nonessential_prime[size] = []
            for x in groups[size]:
                (r0,r1),(c0,c1),f = x
                if f: continue
                # DOES NOT WORK ... CHECK
                if ((r0,r1),(c0,c1)) in donotremove: continue
                x_rows_cols = add_rows_cols([], r0,r1,c0,c1)
                if debug: print ("x_rows_cols: %s" % x_rows_cols)
                
                # compute (row,col)s covered by all groups[size] except for x    
                rows_cols = []
                _ = 1
                while groups[_] != []:
                    for y in groups[_]:
                        if debug: print ("x: %s" % x)
                        if debug: print ("y: %s" % y)
                        if y == x:
                            if debug: print ("same ... skip")
                            continue
                        (_r0,_r1),(_c0,_c1),_f = y
                        if _f:
                            if debug: print ("already combined ... skip")
                            continue
                        rows_cols = add_rows_cols(rows_cols, _r0,_r1,_c0,_c1)
                    _ = 2 * _

                if debug: print ("rows_cols: %s" % rows_cols)
                def issubset(xs,ys):
                    for x in xs:
                        if x not in ys: return False
                    return True

                if issubset(x_rows_cols, rows_cols):
                    nonessential_prime[size].append(x)
                    groups[size].remove(x)
                    change = True
                    break
            if not change:
                size *= 2 
        #'''
        if debug:
            print ("after removal of nonessentials")
            for k,v in groups.items():
                print (k,v)

    size = 1
    nonprime = {}
    essential_prime = {}
    while 1:
        if groups[size] == []: break
        nonprime[size] = []
        essential_prime[size] = []
        for x in groups[size]:
            ((r0,r1),(c0,c1),f) = x
            t = ((r0,r1),(c0,c1))
            if f:
                nonprime[size].append(t)
            else:
                essential_prime[size].append(t)
        size *= 2
                
    return {'nonprime':nonprime,
            'nonessential-prime':nonessential_prime,
            'essential-prime':essential_prime}

def get_SOP(rowlabel, collabel, rownames, colnames, essential_prime):
    s = ''
    for size,v in essential_prime.items():
        for x in v:
            pass
    pass

def kmap(p, m=None,
         width=0.7, height=0.7,
         rowlabel='', # TODO: make this a list of strings for SOP/POS computation 
         collabel='', # TODO: make this a list of strings for SOP/POS computation 
         circle=True,
         circle_terms=[1, '1', 'd'],
         donotremove=None,
         d=0.15,
         style_selector=None,
         decimal=False,
         decimal_offset=0.2,
         decimal_format=r'{\tiny\texttt{%s}}',
         linecolor='red',
         linecolors=None, # Dictionary for selecting coloring of essential prime implicants
                          # linecolors[((1,1),(2,2))] = 'red' means that if an implicant
                          # ***contains*** (1,1),(2,2), then it will be colored red.
         sop=False,
         linewidth=None,
         debug=False):
    
    import random; random.seed()
    def default_linewidth_selector(_):
        return 0.1
    def default_linecolor_selector(_):
        colors = ['red',
                  'yellow',
                  'magenta',
                  'blue',
                  'green',
                  'cyan',
                  ]
        return random.choice(colors)
    def default_d_selector(_):
        return d
    default_style_selector = {'linecolor': default_linecolor_selector,
                              'linewidth': default_linewidth_selector,
                              'd': default_d_selector}
    if style_selector == None: style_selector = default_style_selector
    
    LABELS = {2:[r'\texttt{%s}' % _ for _ in ('0','1')],
              4:[r'\texttt{%s}' % _ for _ in ('00','01', '11', '10')],
              8:[r'\texttt{%s}' % _ for _ in ('000','001','011','010','100','101','111','110')],
              }
    
    rowsize = len(m)
    colsize = len(m[0])
    rownames = LABELS.get(rowsize, [])
    colnames = LABELS.get(colsize, [])
    
    C = table2(p, m, width=width, height=height,
               rownames=rownames, 
               colnames=colnames,
               rowlabel=rowlabel, collabel=collabel,
               linewidth=linewidth)

    if circle:        
        kmap_data = get_kmap_data(m, circle_terms=circle_terms, donotremove=donotremove)
        if debug: print (kmap_data)

        size = 1
        while 1:
            # Python 3
            if not size in kmap_data['essential-prime']: break

            for (r0,r1),(c0,c1) in kmap_data['essential-prime'][size]:
                if debug: print ((r0,r1),(c0,c1))

                # Choose linecolor
                try:
                    linecolor = style_selector['linecolor'](((r0,r1),(c0,c1)))
                except:
                    linecolor = default_style_selector['linecolor'](((r0,r1),(c0,c1)))

                # Choose linewidth
                try:
                    linewidth = style_selector['linewidth'](((r0,r1),(c0,c1)))
                except:
                    linewidth = default_style_selector['linewidth'](((r0,r1),(c0,c1)))

                # Choose d - the distance of implicant to cell boundary
                try:
                    d__ = style_selector['d'](((r0,r1),(c0,c1)))
                except:
                    d__ = default_style_selector['d'](((r0,r1),(c0,c1)))
                
                if r0 <= r1 and c0 <= c1:
                    p += kmap_rect(C[r1][c0], C[r0][c1],
                                   d=d__, linecolor=linecolor, linewidth=linewidth)
                elif r0 <= r1 and c0 > c1:
                    kmap_WW(p, C[r1][0], C[r0][c1],
                            d=d__, linecolor=linecolor)
                    kmap_EE(p, C[r1][c0], C[r0][colsize-1],
                            d=d__, linecolor=linecolor, linewidth=linewidth)
                elif r0 > r1 and c0 <= c1:
                    kmap_NN(p, C[0][c0], C[r1][c1],
                            d=d__, linecolor=linecolor, linewidth=linewidth)
                    kmap_SS(p, C[r0][c0], C[rowsize-1][c1],
                            d=d__, linecolor=linecolor, linewidth=linewidth)
                elif r0 > r1 and c0 > c1:
                    kmap_NW(p, C[r1][0], C[0][c1],
                            d=d__, linecolor=linecolor, linewidth=linewidth)
                    kmap_NE(p, C[r1][c0], C[0][colsize-1],
                            d=d__, linecolor=color)
                    kmap_SW(p, C[rowsize-1][0], C[r0][c1],
                            d=d__, linecolor=linecolor, linewidth=linewidth)
                    kmap_SE(p, C[rowsize-1][c0], C[r0][colsize-1],
                            d=d__, linecolor=linecolor, linewidth=linewidth)
            size *= 2

    if decimal:
        count = 0
        for r in range(rowsize):
            for c in range(colsize):
                x0,y0 = C[r][c].bottomleft();
                x0,y0 = x0 + decimal_offset, y0 + decimal_offset
                try:
                    a = ''.join([_ for _ in rownames[r] if _ in '0123456789'])
                    b = ''.join([_ for _ in colnames[c] if _ in '0123456789'])
                    s = '%s%s' % (a, b)
                    dec = int(s, 2)
                except:
                    dec = '?'
                p += Rect(x0=x0,y0=y0,x1=x0,y1=y0,
                          label = decimal_format % dec,
                          linewidth=0)
        count += 1

    if sop:
        def get_implicant(rownames=rownames,colnames=colnames,
                          rowlabel=rowlabel,collabel=collabel,
                          t=None):
            implicant = ''
            
            rowsize = len(rownames)
            colsize = len(colnames)
            ((r0,r1),(c0,c1)) = t
            rows = []

            # rows = [... row index values in t...]
            r = r0
            while 1:
                rows.append(r)
                r = (r + 1) % rowsize
                if r == r1: break
            # rowvalues = [...]
            rowvalues = [rownames[i] for i in rows]
            if len(rownames) == 2:
                if len(rowvalues) == 1:
                    if rowvalues[0] in ['0', 0]:
                        implicant += rownames[0] + "'"
                    elif rowvalues[0] in ['1', 1]:
                        implicant += rownames[0]
                    else:
                        implicant += '?'
            elif len(rownames) == 4:
                # the rowvalues contains two coordinates
                rowvalues = [(t[0], t[1]) for t in rowvalues]
                row0values = []
                for i in rows:
                    if rowvalues[i][0] not in row0values:
                        row0values.append(rowvalues[i][0])
                if len(row0values) == 1:
                    if row0values[0] in [0, '0']:
                        implicant += rownames[0] + "'"
                    elif row0values[0] in [1, '1']:
                        implicant += rownames[0] 
                    else:
                        implicant += '?'
                row1values = []
                for i in rows:
                    if rowvalues[i][0] not in row0values:
                        row1values.append(rowvalues[i][1])
                if len(row1values) == 1:
                    if row1values[0] in [0, '0']:
                        implicant += rownames[1] + "'"
                    elif row1values[0] in [1, '1']:
                        implicant += rownames[1] 
                    else:
                        implicant += '?'
                
            cols = []
            c = c0
            while 1:
                cols.append(c)
                c = (c + 1) % colsize
                if c == c1: break
            colvalues = [colnames[i] for i in cols]
                                      
            (r0,r1),(c0,c1) = t
            
        for t in kmap_data['essential-prime']:
            get_implicant(rownames=rownames,colnames=colnames,
                          rowlabel=rowlabel,collabel=collabel,
                          t=t)
            
    return C

#==============================================================================
# UML
#==============================================================================
def uml_class(p,
                 X0, Y0,
                 width=6,
                 height=0.4,
                 linewidth=0.03,
                 vspace=0.2,
                 innersep=0.1,
                 classname='Student',
                 attributes=[],
                 methods=[],
                 showempty=True,
                 name=None):
                 
    def entry(t):
        return Rect2(x0=0, y0=0, x1=width, linewidth=0,
                     innersep=innersep,
                     y1=height, align='c',
                     s=r'{\texttt{%s}}' % t)
               
    def blank(vspace=vspace):
        return Rect2(x0=0, y0=0, x1=width, y1=vspace, linewidth=0, innersep=innersep,
                     label='') 

    c = RectContainer(x=X0, y=Y0, align='left',
                      direction='top-to-bottom',
                      name=name)

    # class name
    classnames = [blank(),
                  Rect2(x0=0, y0=0, x1=width, linewidth=0, innersep=innersep,
                        y1=height,
                        label=r'{\texttt{\textbf{%s}}}' % classname),
                  blank()]
                 
    # attributes
    if attributes:
        attributes = [blank()] +\
                     [entry(x) for x in attributes] +\
                     [blank()]
    else:
        if showempty:
            attributes = [blank(0.1), blank(0.1)]
        else:
            attributes = []
        
    # methods
    if methods:
        methods = [blank()] + [entry(x) for x in methods] + [blank()]
    else:
        if showempty:
            methods = [blank(0.1), blank(0.1)]
        else:
            methods = []
            
    for x in classnames + attributes + methods:
        c += x
    c.layout()
    p += c

    # line below class section
    p += Line(points=[classnames[-1].bottomleft(), classnames[-1].bottomright()],linewidth=linewidth)

    # line below attributes
    if attributes:
        p += Line(points=[attributes[-1].bottomleft(), attributes[-1].bottomright()], linewidth=linewidth)

    # boundary of container
    p += Rect2(x0=c.x0, y0=c.y0, x1=c.x1, y1=c.y1, linewidth=linewidth)

    return c


def ver_association(p, p0, p1, s='', c0='', c1='', dx=0, dy=0,
                    starttip='',
                    endtip=''):
    """
    p0 is top
    """
    if p0[1] > p1[1]: p0,p1 = p1,p0
    p += r'\draw[%s-%s] (%s,%s)--(%s,%s);' % (starttip, endtip, p0[0],p0[1],p1[0],p1[1])
    x,y = (p0[0]+p1[0])/2.0, (p0[1]+p1[1])/2.0
    p += r'\node [anchor=east] at (%s,%s) {\texttt{%s}};' % (x, y, s)
    p += r'\node [anchor=south west] at (%s,%s) {\texttt{%s}};' % (p0[0], p0[1], c0)
    p += r'\node [anchor=north west] at (%s,%s) {\texttt{%s}};' % (p1[0], p1[1], c1)

def hor_association(p, p0, p1, s='', c0='', c1='', dx=0, dy=0, starttip='', endtip=''):
    """
    p0 is left
    """
    if p0[1] > p1[1]: p0,p1 = p1,p0
    p += r'\draw[%s-%s] (%s,%s)--(%s,%s);' % (starttip, endtip, p0[0],p0[1],p1[0],p1[1])
    x,y = (p0[0]+p1[0])/2.0, (p0[1]+p1[1])/2.0
    p += r'\node [anchor=south] at (%s,%s) {\texttt{%s}};' % (x, y, s)
    p += r'\node [anchor=north west] at (%s,%s) {\texttt{%s}};' % (p0[0], p0[1], c0)
    p += r'\node [anchor=north east] at (%s,%s) {\texttt{%s}};' % (p1[0], p1[1], c1)

def horver_association(p, p0, p1, s='', c0='', c1='', dx=0, dy=0, starttip='', endtip=''):
    """
    p0 is left
    """
    if p0[1] > p1[1]: p0,p1 = p1,p0
    x0,y0 = p0
    x1,y1 = p1
    p += r'\draw[%s-%s] (%s,%s)--(%s,%s)--(%s,%s);' % (starttip, endtip,
                                              p0[0],p0[1],x1,y0,p1[0],p1[1])
    x,y = (p0[0]+p1[0])/2.0, (p0[1]+p1[1])/2.0
    p += r'\node [anchor=north] at (%s,%s) {\texttt{%s}};' % ((x0+x1)/2.0, y0, s)
    p += r'\node [anchor=south west] at (%s,%s) {\texttt{%s}};' % (p0[0], p0[1], c0)
    p += r'\node [anchor=north west] at (%s,%s) {\texttt{%s}};' % (p1[0], p1[1], c1)

def verhor_association(p, p0, p1, s='', c0='', c1='', dx=0, dy=0, starttip='', endtip=''):
    """
    p0 is lower
    """
    if p0[1] > p1[1]: p0,p1 = p1,p0
    x0,y0 = p0
    x1,y1 = p1
    p += r'\draw[%s-%s] (%s,%s)--(%s,%s)--(%s,%s);' % (starttip, endtip,
                                              p0[0],p0[1],x0,y1,p1[0],p1[1])
    x,y = (p0[0]+p1[0])/2.0, (p0[1]+p1[1])/2.0
    p += r'\node [anchor=east] at (%s,%s) {\texttt{%s}};' % (x0, (y0+y1)/2.0, s)
    p += r'\node [anchor=south west] at (%s,%s) {\texttt{%s}};' % (p0[0], p0[1], c0)
    p += r'\node [anchor=north east] at (%s,%s) {\texttt{%s}};' % (p1[0], p1[1], c1)

def enws_association(p, p0, p1, s='', c0='', c1='', dx=0, dy=0, starttip='', endtip='', de=0, dn=0):
    """
    p0 is left
    """
    x0, y0 = p0
    x4, y4 = p1[0], p1[1]
    
    x1, y1 = x0 - de, y0
    x2, y2 = x0 - de, y0 + dn
    x3, y3 = x4, y0 + dn
    p += r'\draw[%s-%s] (%s,%s)--(%s,%s)--(%s,%s)--(%s,%s)--(%s,%s);' % \
         (starttip, endtip,
          x0, y0,
          x1, y1,
          x2, y2,
          x3, y3,
          x4, y4)
    x,y = (x2+x3)/2.0, (y2+y3)/2.0
    p += r'\node [anchor=south] at (%s,%s) {\texttt{%s}};' % (x, y, s)
    p += r'\node [anchor=north east] at (%s,%s) {\texttt{%s}};' % (p0[0], p0[1], c0)
    p += r'\node [anchor=south west] at (%s,%s) {\texttt{%s}};' % (p1[0], p1[1], c1)

def association(p, p0, p1, s='', c0='', c1='', dx=0, dy=0, starttip='', endtip='', layout='',
                de=1, dn=1, dw=1, ds=1, moves=None):

    if layout in ['e','E']:
        hor_association(p=p, p0=p0, p1=p1, s=s, c0=c0, c1=c1, dx=dx, dy=dy, starttip=starttip, endtip=endtip)
    elif layout in ['w','W']:
        hor_association(p=p, p0=p1, p1=p0, s=s, c0=c1, c1=c0, dx=dx, dy=dy, starttip=endtip, endtip=starttip)
    elif layout in ['n','N']:
        ver_association(p=p, p0=p0, p1=p1, s=s, c0=c0, c1=c1, dx=dx, dy=dy, starttip=starttip, endtip=endtip)
    elif layout in ['s','S']:
        ver_association(p=p, p0=p1, p1=p0, s=s, c0=c1, c1=c0, dx=dx, dy=dy, starttip=endtip, endtip=starttip)
    elif layout in ['en','EN']:
        #
        # association goes LEFT then UP
        # 
        horver_association(p=p, p0=p0, p1=p1, s=s, c0=c0, c1=c1, dx=dx, dy=dy, starttip=starttip, endtip=endtip)
    elif layout in ['ne','NE']:
        #
        # association goes UP then RIGHT
        # 
        verhor_association(p=p, p0=p0, p1=p1, s=s, c0=c0, c1=c1, dx=dx, dy=dy, starttip=starttip, endtip=endtip)
    elif layout in ['sw','SW']:
        #
        # association goes DOWN then LEFT
        # 
        horver_association(p=p, p0=p1, p1=p0, s=s, c0=c1, c1=c0, dx=dx, dy=dy, starttip=starttip, endtip=endtip)
    elif layout in ['se','SE']:
        #
        # association goes DOWN then RIGHT
        # 
        horver_association(p=p, p0=p1, p1=p0, s=s, c0=c1, c1=c0, dx=dx, dy=dy, starttip=starttip, endtip=endtip)
    elif layout in ['wnes','WNES']:
        #
        # association goes EAST, NORTH, WEST, SOUTH
        # For reflexive in clockwise direction
        # 
        enws_association(p=p, p0=p0, p1=p1, s=s, c0=c0, c1=c1, dx=dx, dy=dy, starttip=starttip, endtip=endtip, de=de, dn=dn)
    else:
        if moves == None:
            ps = [p0, p1]
        else:
            ps = [p0]
            last = p0
            for move in moves:
                if isinstance(move, str):
                    move = (move, 1)
                if move[0] == 'n':
                    _p = last[0], last[1] + move[1]
                elif move[0] == 's':
                    _p = last[0], last[1] - move[1]
                elif move[0] == 'e':
                    _p = last[0] + move[1], last[1]
                elif move[0] == 'w':
                    _p = last[0] - move[1], last[1]
                elif move[0] == 'x':
                    _p = (move[1][0], last[1])
                elif move[0] == 'y':
                    _p = (last[0], move[1][1])
                    
                ps.append(_p)
                last = _p
        
        t = '--'.join(['(%s,%s)' % (x,y) for (x,y) in ps])
        p += r'\draw[%s-%s] %s;' % (starttip, endtip, t)

        def ddd(p0, p1):
            x0,y0 = p0
            x1,y1 = p1
            if x0 == x1:
                if y0 < y1: return 'N'
                else: return 'S'
            elif y0 == y1:
                if x0 < x1: return 'E'
                else: return 'W'
                
        # draw constraint at starting point
        if ddd(ps[0], ps[1]) == 'N': 
            anchor = 'south west'
        elif ddd(ps[0], ps[1]) == 'S': 
            anchor = 'north west'
        elif ddd(ps[0], ps[1]) == 'E': 
            anchor = 'north west'
        elif ddd(ps[0], ps[1]) == 'W':
            anchor = 'north east'
        else: #???
            anchor = "east"
        p += r'\node [anchor=%s] at (%s,%s) {\texttt{%s}};' % (anchor, p0[0], p0[1], c0)
            
        # draw constraint at ending point
        if ddd(ps[-2], ps[-1]) == 'N': # up
            anchor = 'north west'
        elif ddd(ps[-2], ps[-1])=='S': # down
            if len(ps) > 2 and ddd(ps[-3],ps[-2])=='W':
                anchor = 'south east'
            else:
                anchor = 'south west'
        elif ddd(ps[-2], ps[-1])=='E': # right
            anchor = 'north east'
        elif ddd(ps[-2],ps[-1])=='W': # left
            anchor = 'north west'
        else: #???
            anchor = "east"
        p += r'\node [anchor=%s] at (%s,%s) {\texttt{%s}};' % (anchor, ps[-1][0], ps[-1][1], c1)

        # draw association label
        if len(ps) == 2:
            if ps[0][0] == ps[1][0]: # vertical
                anchor = 'east'
            else:
                anchor = 'south'
            x,y = (ps[0][0]+ps[1][0])/2.0, (ps[0][1]+ps[1][1])/2.0
        else:
            # for now put on 1st or 2nd segment depending on which one is longer
            d0 = abs(ps[0][0] - ps[1][0]) + abs(ps[0][1] - ps[1][1])
            d1 = abs(ps[1][0] - ps[2][0]) + abs(ps[1][1] - ps[2][1])
            if d0 > d1:
                # draw on 1st segment
                # either above or below
                q, r = ps[0], ps[1]
                u = ps[2]
                if ddd(q, r) in ['N','S']:
                    if ddd(r, u) == 'E':
                        anchor = 'east'
                    else:
                        anchor = 'west'
                else:
                    if ddd(r,u)=='N':
                        anchor = 'north'
                    else:
                        anchor = 'south'
            else:
                q, r = ps[1], ps[2]
                if ddd(ps[0],q)=='E' and ddd(q,r)=='N':
                    anchor = 'west'
                else:
                    anchor = 'east'
                
                    x, y = (q[0] + r[0]) / 2.0, (q[1] + r[1]) / 2.0
            
        p += r'\node [anchor=%s] at (%s,%s) {\texttt{%s}};' % (anchor, x, y, s)
            
def uml_functioncall(k,
                     activationbarwidth=0.4,
                     klsname0='', klsname1='',
                     y=0,
                     linestyle='',
                     s=''):
    r0 = k[klsname0]; p0 = r0.bottom()
    r1 = k[klsname1]; p1 = r1.bottom()
    # Need to find the midpoint between two worldline closest to starting worldline
    bottoms = [v.bottom() for v in k.values()]
    xs = [x for x,_ in bottoms]
    xs.sort()
    index = xs.index(p0[0]) # where the bottom of r0 is
    # x2 is where the function label will be
    if p0[0] < p1[0]:
        x0 = p0[0] + activationbarwidth / 2.0
        x1 = p1[0] - activationbarwidth / 2.0
        x2 = xs[index + 1]
    else:
        x0 = p0[0] - activationbarwidth / 2.0
        x1 = p1[0] + activationbarwidth / 2.0
        x2 = xs[index - 1]
    x2 = (x0 + x2) / 2.0
    y2 = y + 0.25
    line = Line(points=[(x0,y), (x1,y)], linestyle=linestyle, endstyle='>')
    rect = Rect(x0=x2, y0=y2, x1=x2, y1=y2, label=r'\texttt{%s}' % s, linewidth=0)
    return line, rect


def uml_usecase_man(p, x0=0, y0=0, x1=None, y1=None, w = 1,
                    aspect_ratio=1/1.5):
    """
    aspect_ratio = width/height
    """
    
    """
    +-----+
    |     |
    |     | face
    +-----+
    |     | body + arm
    |     |
    +-----+
    |     | legs
    |     |
    +-----+
    """
    
    # width
    if x1 == None:
        x1 = x0 + w
    w = (x1 - x0)
    if y1 == None:
        h = w/aspect_ratio
        y1 = y0 + h
        
    rect = Rect(x0=x0, y0=y0, x1=x1, y1=y1, linewidth=0.1, linecolor='red')
    p += rect
    # one third of height
    dy = (y1 - y0) / 3.0
    # midx
    midx = (x0 + x1) / 2.0

    # face -- draw last    
    head = midx, y0 + dy * 2.5
    r = min(w, dy) / 2.0 * 0.8
    
    # abdomen
    abdomen = midx, y0+dy

    # body
    p += Line(points=[head, abdomen])

    # arms
    p += Line(points=[(x0, y0 + 1.75*dy), (x1, y0 + 1.75*dy)])

    # legs
    p += Line(points=[(x0, y0), abdomen, (x1,y0)])

    # draw face
    p += Circle(x=head[0], y=head[1], r=r, linewidth=0.01, background='white')

    return rect



#==============================================================================
# Chess
#==============================================================================
def chess(p, x=0, y=0,
          xs=None,
          WIDTH = 0.7,       # Width and height of each cell
          WHITE = 'white',
          BLACK = 'black!20',
          IMAGE_PATH = None, # Function to return path to image for a piece
                             # IMAGE_PATH('P') returns the image path to
                             # white pawn, etc.
          ):

    def __image_path(ch):
        FILE_EXTENSION = 'png'
        import latextool_basic
        import inspect, os
        latextool_basic_dir = os.path.split(inspect.getfile(latextool_basic))[0]
        filename = r'data/chess/%s/%s%s.%s' % (FILE_EXTENSION,
                                               IFELSE(ch.isupper(), 'w', 'b'),
                                               ch.lower(),
                                               FILE_EXTENSION)
        return os.path.join(latextool_basic_dir, filename)

    image_path = IFELSE(IMAGE_PATH == None, __image_path, IMAGE_PATH)

    # if xs is a dict, convert to 2d array
    if isinstance(xs, dict):
        xs = [[xs.get((r,c), ' ') for c in range(8)] for r in range(8)]
    
    C = RectContainer(x=x, y=y, align='left', direction='top-to-bottom')
    for r in range(8):
        row = RectContainer(x=-0.01, y=0, align='bottom', direction='left-to-right')
        for c in range(8):
            color = IFELSE((r + c) % 2 == 0, WHITE, BLACK)
            label = IFELSE(xs[r][c] in ['', ' '],
                           '',
                           r'\includegraphics[width=%sin,height=%sin]{%s}' % \
                           (WIDTH*0.42,
                            WIDTH*0.42,
                            image_path(xs[r][c])))
            row += Rect2(x0=0, y0=0, x1=WIDTH, y1=WIDTH, linecolor='black',
                         linewidth=0.01,
                         background=color,
                         label=label)
        C += row
        row.x = row.x0
        row.y = row.y0
        row.layout()

    p += C

    # Border line width
    if WIDTH >= 0.8:
        borderlinewidth = 0.1
    elif WIDTH >= 0.7:
        borderlinewidth = 0.09
    elif WIDTH >= 0.6:
        borderlinewidth = 0.08
    elif WIDTH >= 0.5:
        borderlinewidth = 0.07
    elif WIDTH >= 0.4:
        borderlinewidth = 0.06
    elif WIDTH >= 0.3:
        borderlinewidth = 0.05
    elif WIDTH >= 0.2:
        borderlinewidth = 0.04
    else:
        borderlinewidth = 0.03
    
    # Border. Note that 'black' color and border line width are hardcoded.
    x0,y0 = C.bottomleft()
    x1,y1 = C.topright()
    p += Rect2(x0=x0,y0=y0,x1=x1,y1=y1,
               linewidth=borderlinewidth,
               linecolor='black')

    # Choose fontsize for row and column labels
    if WIDTH >= 0.8:
        fontsize =  r'\normalsize'
    elif WIDTH >= 0.7:
        fontsize =  r'\small'
    elif WIDTH >= 0.6:
        fontsize =  r'\footnotesize'
    elif WIDTH >= 0.5:
        fontsize =  r'\scriptsize'
    else:
        fontsize =  r'\tiny'

    # Row labels
    for r in range(7, -1, -1):
        x0,y0 = C[r][0].bottomleft(); x0 -= WIDTH
        x1,y1 = C[r][0].topright(); x1 -= WIDTH
        p += Rect(x0=x0, y0=y0, x1=x1, y1=y1, label=r'%s{\textsf{%s}}' % (fontsize, 8 - r), linewidth=0)
    
    # Column labels
    for c in range(0, 8):
        x0,y0 = C[7][c].bottomleft(); y0 -= WIDTH
        x1,y1 = C[7][c].topright(); y1 -= WIDTH
        p += Rect(x0=x0, y0=y0, x1=x1, y1=y1, label=r'%s{\vphantom{abcdefgh}\textsf{%s}}' % (fontsize, "abcdefgh"[c]),
                  linewidth=0)
                
    return C




class XAxis:
    '''
      A. In PGF
     x0
      o-------------------------------------------------------------o
          |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
          |        |        |        |        |        |        |
          0        1        2        3        4        5        6
          < label >
             gap


      B. Rewrite labels to this:
    
   start
      o-------------------------------------------------------------o
          |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
          |        |        |        |        |        |        |
        0x10^2   5x10^2  10x10^2  15x10^2  20x10^2  25x10^2  30x10^2
          < label >
             gap

     User specifies in terms of B but without the "x10^2".
    
    USEFUL:
       xaxis = XAxis(...)
       p = xaxis(2.57) return the pgf coordinate of x = 2.57 on axis

       What about large graphs where axis label is 0, 10^2, 10^4, 10^6, etc.
       Maybe call parameter units
    '''
    def __init__(self,
                 x0=0, y0=0,                      # where to start drawing x-axis
                 start=0.0, end=10.0,             # axes is [0.0, 10.0]
                 xscale=1.0,                      # if 0.5, then 0 to 0.5 is marked 1
                 start_tick=0.2, end_tick=12.25,  # 1st and last tick marks
                 tick_gap=0.25,                   # distance between ticks
                 tick_len=0.1,
                 start_label=None, end_label=None,# start label, end label
                                                  # if none, then label 0.0 and
                                                  # grow both ways
                 label_gap=1,                     # label between gaps
                 label_anchor_gap=0,              # anchor point from axes
                                                  # where anchor is used for label
                 label_fontsize=r'\small',
                 linewidth=0.1,
                 linecolor='black',
                 arrowhead=None):
        self.x0 = x0
        self.y0 = y0
        self.start = start
        self.end = end
        self.xscale = xscale
        self.start_tick = start_tick
        self.end_tick = end_tick
        self.tick_gap = tick_gap
        self.tick_len = tick_len
        self.start_label = start_label
        self.end_label = end_label
        self.label_gap = label_gap
        self.label_anchor_gap = label_anchor_gap
        self.linecolor = linecolor
        self.label_fontsize = label_fontsize
        self.arrowhead = arrowhead
    def x(self):
        return 0.0
    def graph_to_pgf(x, y):
        """ convert graph x,y to pgf x,y """
        x0, y0 = self.x0, self.y0
        pgf_x = x - x0 - self.start
        pgf_y = y - y0
        return (pgf_x, pgf_y)
    def __str__(self):
        x0 = self.x0
        y0 = self.y0
        linecolor = self.linecolor
        length = self.end - self.start
        s = ""
        s += str(Line(x0=x0, y0=y0, x1=x0+length, y1=y0, linecolor=linecolor))

        # ticks
        tick = self.start_tick
        while tick <= self.end_tick:
            x0_pgf_tick = x0 + tick - self.start
            y0_pgf_tick = y0
            x1_pgf_tick = x0_pgf_tick
            y1_pgf_tick = y0 - self.tick_len
            s += str(Line(x0=x0_pgf_tick, y0=y0_pgf_tick, x1=x1_pgf_tick, y1=y1_pgf_tick, linecolor=linecolor))  
            tick += self.tick_gap
        return s

def axes(p,
         x0=0, y0=0, x1=1, y1=1,
         linewidth=None, linecolor='black!50',
         origin=(0,0),
         x_axis_label='',  
         y_axis_label='',
):
    from latexcircuit import POINT
    """
    Draws axes into plot p
    TODO: Separate x- and y-axis. For each axes, API is
    See x_axis function
    """
    if linewidth==None:
        p += Line(points=[(x0, origin[1]), (x1, origin[1])], endstyle='>', linecolor=linecolor) # x axis
        p += Line(points=[(origin[0], y0), (origin[0], y1)], endstyle='>', linecolor=linecolor) # y axis
    else:
        p += Line(points=[(x0, origin[1]), (x1, origin[1])],
                  linewidth=linewidth, endstyle='>', linecolor=linecolor) # x axis
        p += Line(points=[(origin[0], y0), (origin[0], y1)],
                  linewidth=linewidth, endstyle='>', linecolor=linecolor) # y axis
    # x-axis label
    if x_axis_label:
        X = POINT(x=x1, y=origin[1], r=0, label=x_axis_label, anchor='west')
        p += str(X)
    # y-axis label
    if y_axis_label:
        X = POINT(x=origin[0], y=y1, r=0, label=y_axis_label, anchor='south')
        p += str(X)

#==============================================================================
# The following is a temporary dumping ground for 3dplot
#==============================================================================
def opengl_canonical_cube():
    return r'''
\tdplotsetmaincoords{70}{110}
  \begin{tikzpicture}[scale=1, tdplot_main_coords]

    % front A-B-C-D
    \coordinate (A) at ( 1,-1,-1); % lower left
    \coordinate (B) at ( 1,-1, 1); % top left
    \coordinate (C) at ( 1, 1, 1); % top right
    \coordinate (D) at ( 1, 1,-1); % bottom right

    % right side C-D-E-F
    \coordinate (E) at (-1, 1,-1);
    \coordinate (F) at (-1, 1, 1);

    % top side C-F-G-B
    \coordinate (G) at (-1, -1, 1);
    
    % part of axes inside the canonical box
    \draw[thick,-] (0,0,0) -- (1,0,0) node[anchor=north east]{}; % x
    \draw[thick,-] (0,0,0) -- (0,1,0) node[anchor=north west]{}; % y
    \draw[thick,-] (0,0,0) -- (0,0,1) node[anchor=south]{};      % z

    % front
    \draw[fill=gray!70,fill opacity=0.85] (A) -- (B) -- (C) -- (D) -- cycle;
    \draw[thick,->] (1,0,0) -- (5,0,0) node[anchor=north east]{$z$}; % x
    
    % right
    \draw[fill=gray!90,fill opacity=0.85] (C) -- (D) -- (E) -- (F) -- cycle;
    \draw[thick,->] (0,1,0) -- (0,3,0) node[anchor=north west]{$x$}; % y

    % top
    \draw[fill=gray!40,fill opacity=0.85] (C) -- (F) -- (G) -- (B) -- cycle;
    \draw[thick,->] (0,0,1) -- (0,0,2.5) node[anchor=south]{$y$}; % y
   
\end{tikzpicture}
'''

#==============================================================================
# Logic
#==============================================================================
def prooftree(xs, indent=0):
    """
    Two cases: xs is a string or (string, string, list)

    Two base cases:
        xs is string
        xs = ('foo', 'bar', [])
    """

    indentation = ' ' * indent
    
    if type(xs) == type(""):
        # simple case
        return  '%(indentation)s{\n%(indentation)s%(root)s%(indentation)s}' % \
               {'indentation':indentation, 'root':xs}     

    # root
    root = \
r'''%(indentation)s{
%(indentation)s%(root)s
%(indentation)s}''' % {'indentation':indentation, 'root':xs['root']}

    # children
    children = []
    for a in xs['children']:
        children.append(prooftree(a, indent + 4))
    if len(children) == 0:
        children = '{\n}'
    else:
        children = ('\n' + (' '*(indent+4)) + '\\\\\n').join(children)
        children = r'''%(indentation)s{
%(indentation)s%(children)s
%(indentation)s}''' % {'children':children, 'indentation':indentation}
        
    rule = r'{%s}' % xs['rule']

    
    indentation = indent * ' '
    return \
r"""%(indentation)s{
%(indentation)s\inferrule*[right={\textit{\textup{%(rule)s}}}]
%(children)s
%(root)s
%(indentation)s}""" % \
     {'indentation':indentation, 'rule':rule, 'children':children, 'root':root}

#==============================================================================
# Table tennis
# ttv - draw table
# ttv_pos - returns dictionry of positions
#==============================================================================
def ttv(p, x=0,y=0, factor=0.5):
    W = 5.0 * factor; H = 9.0 * factor
    r0 = Rect(x0=x, y0=y, x1=x+W, y1=y+H, linewidth=0.05)
    p += r0
    p += Line(points=[(x+W/2,y),(x+W/2,y+H)], linewidth=0.001)
    p += Line(points=[(x,y+H/2),(x+W,y+H/2)], linewidth=0.001)
    return r0

def ttv_pos(x=0, y=0, factor=0.5):
    """
            +---+---+
          d |   |   | h
          c |   |   | g
            +---+---+
          b |   |   | f
          a |   |   | e
            +---+---+

          a = left0
          b = left1
          c = left2
          d = left3
          e = right0
          f = right1
          g = right2
          h = right3
    """
    W = 5.0 * factor; H = 9.0 * factor
    x0 = x; y0 = y;
    x1 = x0 + W; y1 = y0 + H 
    h = (y1 - y0) / 8.0
    d = {}
    d['left0'] = (x0 - factor, y0 + h)
    d['left1'] = (x0 - factor, y0 + 3*h)
    d['left2'] = (x0 - factor, y0 + 5*h)
    d['left3'] = (x0 - factor, y0 + 7*h)
    d['right0'] = (x1 + factor, y0 + h)
    d['right1'] = (x1 + factor, y0 + 3*h)
    d['right2'] = (x1 + factor, y0 + 5*h)
    d['right3'] = (x1 + factor, y0 + 7*h)
    return d

#==============================================================================
# matching
#==============================================================================
def matching(p,
             x=0, y=0,
             C=None, S=None,
             pos=None,
             ranking=None,
             match=None,
             rankcolor='blue!70',
             ranklinewidth=0.04,
             matchcolor='red!40',
             matchlinewidth=0.2,
             rankwidth=0.4,
             rankheight=0.4,
             noderadius=0.25,
             hsep=4.0,
             vsep=0.9,
             ):
    if not pos:
        maxnum = max(len(C), len(S))
        pos = {}
        for i, c in enumerate(C):
            pos[c] = (x, y + (maxnum - (i + 1)) * vsep)
        for i, s in enumerate(S):
            pos[s] = (x + hsep, y + (maxnum - (i + 1)) * vsep)

    if ranking==None: ranking = {}
    if match==None: match = []
    # draw nodes
    for c in C + S:
        label = "$%s_%s$" % (c[0], c[1])
        p += Circle(center=pos[c], r=noderadius, label=label,
                    background='blue!10',
                    name=c)

    # draw match
    for c,s in match:
        p += Line(names=[c, s], linecolor=matchcolor, linewidth=matchlinewidth)

    # draw rankings for c1
    for c, ss in ranking.items():
        for rank, s in enumerate(ss):
            p0 = pos[c]
            p1 = pos[s]
            p2 = ((p0[0] + p1[0])/2.0, (p0[1] + p1[1])/2.0) 
            p += Rect(x0=p2[0]-rankwidth/2, y0=p2[1]-rankheight/2,
                      x1=p2[0]+rankwidth/2, y1=p2[1]+rankheight/2, 
                      label=r'{\footnotesize\text{%s}}' % rank,
                      background='white', linewidth=ranklinewidth,
                      linecolor=rankcolor,
                      name='%s%s' % (c,s))
            p += Line(names=[c,'%s%s' % (c,s), s], endstyle='>',
                      linecolor=rankcolor,
                      linewidth=ranklinewidth, arrowstyle='triangle')

#==============================================================================
# graphs
#==============================================================================
from math import sin, cos, pi
def cyclegraph(p=None,
               x=0, y=0, radius=1,# radius is radius of cycle
               r=None,
               background=None,
               num=5,
               startdegree=None,
               drawline=True,
               linewidth=0.03,
               linecolor='black',
               labels=None,
               names=None, # mapping from range(num) to string for node name
               ):
    # Cycle graph
    # Default tikz node name is [radius][degree]
    # center is 0,0
    if r==None:
        r = Graph.r
    if background==None:
        background = Graph.background
    if startdegree==None:
        if num % 2 == 0:
            startdegree = 0
        else:
            startdegree = 90
    diffdeg = 360.0/num
    deg = startdegree

    tnames = dict([(i,i) for i in range(num)])
    if names != None:
        for k,v in names.items():
            try:
                k = int(k) # in case user uses '0' instead of 0
            except: pass
            tnames[k] = v
    names = tnames
    #print ("names:", names)

    tlabels=dict([(i,'') for i in range(num)])
    if labels!=None:
        for k in labels.keys():
            tlabels[k] = labels[k]
    labels = tlabels
    
    for i in range(num):
        #print ("i:", i)
        radians = deg * pi / 180.0
        x0, y0 = x + radius * cos(radians), y + radius * sin(radians)
        x0, y0 = round(x0, 2), round(y0, 2)
        name = str(names[i])
        #print ("name:", name)
        p += Circle(x=x0, y=y0, r=r,
                    label = labels[i],
                    linewidth = linewidth,
                    linecolor=linecolor,
                    background = background,
                    name = name
        )
        deg += diffdeg
        #print (p)
        
    if drawline:
        ns = []
        for i in range(num + 1):
            name = names[i % num]
            ns.append(name)
        p += Line(names=ns, linewidth=linewidth)

def petersen(p,
             x=0,y=0,
             radius0=1, radius1=2,
             linewidth=0.03):
    # names = 0, 1, 2, 3, 4
    cyclegraph(p=p,
               x=x, y=y,
               num=5,
               radius=radius0, startdegree=18, drawline=False)
    # names = 5, 6, 7, 8, 9
    cyclegraph(p=p,
               x=x, y=y,
               num=5,
               names=dict([(i, str(5 + i)) for i in range(5)]),
               radius=radius1, startdegree=18)
    # star
    p += Line(names=['%s' % ((2*i) % 5) \
                     for i in range(6)], linewidth=linewidth)
    # join inner to outer
    for i in range(5):
        p += Line(names=['%s' % i, '%s' % (i + 5)],
                  linewidth=linewidth)

def completegraph(p=None, num=5, radius=1,
                  startdegree=None,
                  drawline=True,
                  labels=None,
                  linewidth=0.03):
    cyclegraph(p=p, num=num, radius=radius, startdegree=startdegree,
               drawline=False, labels=labels)
    if drawline:
        for i in range(0, num):
            for j in range(i, num):
                name0 = '%s' % i
                name1 = '%s' % j
                p += Line(names=[name0, name1], linewidth=linewidth)
    

def stargraph(p=None,
              x=0, y=0,
              num=5, radius=1,
              r=0.2,
              startdegree=None,
              names=None):
    tnames = dict([(i,i) for i in range(num)])
    tnames['center'] = 'center'
    if names != None:
        for k,v in names.items():
            try: k = int(k)
            except: pass
            tnames[k] = v
    names = tnames
    cyclegraph(p=p, x=x, y=y, num=num, radius=radius,
               drawline=False, startdegree=startdegree, names=names)

    # TODO: Fix to make sure center is drawn last
    p += Graph.node(x=x, y=y, r=r, name=names['center'])

    for i in range(hnum):
        p += Graph.edge(names=[names['center'], names[i]])

    p += Graph.node(x=x, y=y, r=r, name=names['center'])

def graphnode(p=None,
              x=0, y=0,
              r=0.2,
              linewidth=0.03, linecolor='', linestyle='',
              label='',
              background='blue!20',
              anchor=None,
              name=None):
    #print ("----- r:", r)
    if name == None:
        c = Circle(x=x, y=y, r=r,
                   label=label,
                   anchor=anchor,
                   linecolor=linecolor, linestyle=linestyle,
                   background=background, linewidth=linewidth)
    else:
        c = Circle(x=x, y=y, r=r,
                   label=label,
                   anchor=anchor,
                   linecolor=linecolor, linestyle=linestyle,
                   background=background, linewidth=linewidth,
                   name=name)
    if p != None: p += c
    return c

def graphedge(p=None,
              linewidth=0.03,
              linecolor='black',
              linestyle='',
              names=None):
    x = Line(names=names, linestyle=linestyle,
             linewidth=0.03, linecolor=linecolor)
    if p != None: p += x
    return x

def grapharc(p=None,
             linewidth=0.03,
             linecolor='black',
             names=None):
    x = Line(names=names, linewidth=0.03, linecolor=linecolor,
             endstyle='>', arrowstyle='triangle')
    if p != None: p += x
    return x

def completebipartite(p=None,
                      x=0, y=0,
                      num1=3, num2=3,
                      horsep=1, versep=1,
                      drawline=True,
                      names=None):
    len1 = (num1 - 1) * horsep
    len2 = (num2 - 1) * horsep
    maxlen = max(len1, len2)
    
    x0 = x + (maxlen - len1) / 2.0
    for i in range(num1):
        p += Graph.node(x=x0, y=y + versep, name='1%s' % i)
        x0 += horsep

    x0 = x + (maxlen - len2) / 2.0
    for i in range(num2):
        p += Graph.node(x=x0, y=y, name='0%s' % i)
        x0 += horsep

    if drawline:
        for i in range(num1):
            for j in range(num2):
                p += Graph.edge(names=['1%s' % i, '0%s' % j])
    
    

    
class Graph:
    
    background = 'blue!10'
    linewidth = 0.03
    linecolor = 'black'
    linestyle = ''
    arrowstyle = 'triangle'
    
    r = 0.2
    x = 0
    y = 0
    
    @staticmethod
    def node(p=None,
             x=None, y=None,
             r=None,
             linewidth=None,
             linestyle=None,
             linecolor=None,
             background=None,
             label='',
             anchor=None,
             name=None):
        if x==None: x = Graph.x
        if y==None: y = Graph.y
        if r==None: r = Graph.r
        if linestyle==None: linestyle = Graph.linestyle
        if linewidth==None: linewidth = Graph.linewidth
        if linecolor==None: linecolor = Graph.linecolor
        if background==None: background = Graph.background
        return graphnode(p=None,
                         x=x, y=y,
                         r=r,
                         linewidth=linewidth,
                         linecolor=linecolor,
                         linestyle=linestyle,
                         label=label,
                         background=background,
                         anchor=anchor,
                         name=name)
    
    @staticmethod
    def edge(p=None,
             linewidth=None,
             linecolor=None,
             linestyle=None,
             startstyle='',
             endstyle='',
             bend_left=None, bend_right=None,
             label=None, anchor=None,
             names=None,
             loop=None):
        if linestyle==None: linestyle = Graph.linestyle
        if linewidth==None: linewidth = Graph.linewidth
        if linecolor==None: linecolor = Graph.linecolor
        x = Line(names=names, linestyle=linestyle,
                 bend_left=bend_left, bend_right=bend_right,
                 label=label, anchor=anchor,
                 startstyle=startstyle, endstyle=endstyle,
                 linewidth=linewidth, linecolor=linecolor, loop=loop)
        if p != None: p += x
        return x
    
    @staticmethod
    def arc(p=None,
            linewidth=None,
            linecolor=None,
            linestyle=None,
            arrowstyle=None,
            bend_left=None,
            bend_right=None,
            label=None, anchor=None,
            names=None,
            loop=None,
            ):
        if linestyle==None: linestyle = Graph.linestyle
        if linewidth==None: linewidth = Graph.linewidth
        if linecolor==None: linecolor = Graph.linecolor        
        if arrowstyle==None: arrowstyle = Graph.arrowstyle     
        x = Line(names=names, arrowstyle=arrowstyle, endstyle='>',
                 bend_left=bend_left, bend_right=bend_right,
                 label=label, anchor=anchor,
                 linewidth=linewidth, linecolor=linecolor, linestyle=linestyle,
                 loop=loop)
        if p != None: p += x
        return x

#==============================================================================
# Intervals
#==============================================================================
def intervals(p,
              dy=1,
              axislength=10,
              xss=None):
    def L(x0, x1, y, label='', linecolor='black'):
        return Line(points=[(x0,y),(x1,y)], linecolor=linecolor,
                    linewidth=0.1, label=label)

    y = 0
    p += Line(points=[(0,y),(axislength,y)],
              endstyle='>', arrowstyle='triangle')

    y += dy / 2.0
    for xs in xss:
        for interval in xs:
            if len(interval)==3:
                x0,x1,label = interval
                linecolor='black'
            elif len(interval)==4:
                x0,x1,label,linecolor = interval
            p += L(x0, x1, y, label=label, linecolor=linecolor)
            y += dy

#==============================================================================
# PDA
#==============================================================================
class PDA:
    pda_w=3,
    body_h=2,
    vsep=1,  # vertical sep between bottom of tape and top of pda
    hsep=1,  # horizontal sep between right edge of pda and stack
    armv=None,
    w=0.6,
    input_tape_str=False,
    stack_str=False,
    with_stack=True, # without stack can be used for DFA, NFA, TM,...
    def __init__(self):
        pass

def drawstack(p,
              x=0, y=0,
              w=0.6, h=0.6,
              xs=[],
              sep=0.1, # separation between cells and container walls
              direction='top-to-bottom',
              min_size=1, # minimum number of values in stack
                          # If min_size is 1 and the stack values is [],
                          # then a blank cell is drawn.
                          # In general, if min_size is m and len(xs) is
                          # n, then (m - n) blank cells are drawn
              extra_h=0, 
          ):
    #
    #  |   |  |
    #  |   |  | extra h
    #  | x |
    #  | y |
    #  +---+
    # stack: the list below is from top to bottom of stack values

    def cell(label='', linewidth=0.02):
        return Rect2(0, 0, w, h, label=label, linewidth=linewidth)

    stackvalues = xs
    stack = RectContainer(x=x, y=y, align='left', direction='top-to-bottom')
    for i in range(min_size - len(stackvalues)):
        stack += cell('',linewidth=0)
    for i in stackvalues:
        stack += cell(i)
    p += stack 

    # stack outline
    x0,y0 = stack.topleft();     x0 -= sep; y0 += extra_h
    x1,y1 = stack.bottomleft();  x1 -= sep; y1 -= sep
    x2,y2 = stack.bottomright(); x2 += sep; y2 -= sep
    x3,y3 = stack.topright();    x3 += sep; y3 += extra_h
    p += Line(points=[(x0,y0), (x1,y1), (x2,y2), (x3,y3)], linewidth=0.02) 
    return stack


def pda(p,
        x0=0, y0=0, # coordinates of bottom-left of tape
        stackvalues=[], tape=[''], state=r'$q_0$', head_index=0,
        body_w=3,
        body_h=2,
        vsep=1,  # vertical sep between bottom of tape and top of pda
        hsep=1,  # horizontal sep between right edge of pda and stack
        armv=None,
        w=0.6, h=None,
        input_tape_str=False,
        stack_str=False,
        with_stack=True, # without stack can be used for DFA, NFA, TM,...
        include_arm_and_stack=True, # set to false for DFA/NFA/TM
        no_draw=False,
        ):
    
    if no_draw:
        p = copy.deepcopy(p)    
    if armv==None: armv = body_h / 2.0
    if h==None: h = w
    
    # format all values in stack and tape
    vphantom = ''.join(stackvalues + tape)
    vphantom = r'\vphantom{%s}' % vphantom
    stackvalues = [r'{%s\texttt{%s}}' % (vphantom, _) for _ in stackvalues]
    tape = [r'{%s\texttt{%s}}' % (vphantom, _) for _ in tape]

    def cell(label='',
             linewidth=0.02):
        return Rect2(0, 0, w, h,
                     label=label,
                     linewidth=linewidth)
        
    # input tape
    tapecontainer = RectContainer(x=x0, y=y0, align='bottom', direction='left-to-right')
    for i in tape:
        tapecontainer += cell(i)

    tape = tapecontainer
    p += tape
    p += Line(x0=tape[-1].x1, y0=tape[-1].y1, x1=tape[-1].x1+w/2.0, y1=tape[-1].y1,
              linewidth=0.02)
    p += Line(x0=tape[-1].x1, y0=tape[-1].y0, x1=tape[-1].x1+w/2.0, y1=tape[-1].y0,
              linewidth=0.02)

    # "input tape"
    if input_tape_str:
        x0,y0 = tape.topleft(); y0 += 0.5
        p += Rect(x0=x0, y0=y0, x1=x0+6, y1=y0, linewidth=0, s='input tape')

    # pda
    x0,y0 = tape.bottomleft(); y0 -= body_h + vsep
    x1,y1 = x0 + body_w, y0 + body_h
    pda = Rect(x0=x0, y0=y0, x1=x1, y1=y1, label=state, linewidth=0.02)
    p += pda

    # read/write head
    p0 = (x0, y0) = pda.top()
    p3 = (x3, y3) = tape[head_index].bottom()
    p1 = (x0, (2.0*y0+1.0*y3)/3.0)
    p2 = (x3, (2.0*y0+1.0*y3)/3.0)
    p += Line(points=[p0, p1, p2, p3], linewidth=0.02, endstyle='>')

    # stack
    if include_arm_and_stack:
        x0,y0 = pda.right(); x0 += hsep; y0 -= 2*armv
        stack = drawstack(p, x=x0, y=y0, w=w,h=w, xs=stackvalues, sep=0.1, # WARNINGL hardcoing 0.1
                          extra_h = armv)

        # "stack"
        if stack_str:
            x0,y0 = stack.bottomright(); x0 += 0.3; y0 += 0.05
            p += Rect(x0=x0,x1=x1+4,y0=y0,y1=y0,linewidth=0,s='stack')

        # arm
        p0 = (x0,y0) = pda.right()
        (x1,y1) = stack.top(); y1 += armv 
        p += Line(points=[p0, (x1,y0), (x1,y1)], linewidth=0.02)
        p += Line(points=[(x1-0.2, y1-0.2), (x1-0.2, y1), (x1+0.2, y1), (x1+0.2, y1-0.2)], linewidth=0.02)

        x0,y1 = tape.topleft()
        x1 = max(tape.right()[0] + w/2, stack.right()[0] + 0.1) # WARNINGL hardcoing 0.1
        y0 = min(pda.bottom()[1], stack.bottom()[1] - 0.1)
    else:
        x0,y1 = tape.topleft()
        x1 = max(tape.right()[0] + w/2.0, pda.right()[0])
        y0 = pda.bottom()[1]
    return Rect(x0=x0,y0=y0,x1=x1,y1=y1,linewidth=0)


def pda_step(p,
             stackvalues0, tape0, state0, head_index0,
             stackvalues1, tape1, state1, head_index1,
             ):
    r1 = pda(p, x0=0, y0=0,
             stackvalues = stackvalues0,
             tape = tape0,
             state = state0,
             head_index = head_index0,
             vsep=0.5,
             armv=0.5,
             body_w=2, body_h=1,
             w=0.5,
             )

    x0,y0 = r1.bottomleft()
    x1,y1 = r1.topright()

    p += Line(points=[(x1+1,-1.5),(x1+2,-1.5)], linewidth=0.1, linecolor='red', endstyle='>')

    x0,y0 = r1.bottomleft()
    x1,y1 = r1.topright()

    pda(p, x0=x1+3, y0=0,
        stackvalues = stackvalues1,
        tape = tape1,
        state = state1,
        head_index = head_index1,
        vsep=0.5,
        armv=0.5,
        body_w=2, body_h=1,
        w=0.5,
        )


def pda_computation(p,
                    x=0, y=0,
                    max_x=10, # max x value before 'line' break
                    data=None,
                    arrowhlen=0.5,
                    arrowvlen=0.6,
                    arrowhsep=0.25,
                    arrowvsep=0.3,
                    arrowvsep2=None,
                    voffset=-0.8,
                    hoffset=0.8,
                    w=0.4,
                    ):
    # data is a list of (state, tapevalues, head_index, stackvalues)
    #
    #          
    #             arrowhlen
    #             .
    #             .  arrowhsep
    # voffset   <->.  <->
    # ^ +------+   .     +-------+         +--------+
    # | |      |         |       |         |        |
    # v |      |   -->   |       |         |        |
    #   |      |         |       |         +--------+
    #   +------+         |       |                      arrowvsep  
    #                    +-------+ ............|..........
    #   hoffset                                |            ^
    #  <->                                     |         
    #     +------------------------------------+     ^   
    #     |                                          |
    #     v                                          v arrowvlen
    #                                                  arrowvsep2 -- distance between arrow head and top of body
    #  +------+
    #  |      |
    #  +------+
    def pda0(p, x0, y0, stackvalues, tape, state, head_index, no_draw=False):
        return pda(p,
                   x0=x0,y0=y0,
                   stackvalues = stackvalues,
                   tape = tape,
                   state = state,
                   head_index = head_index,
                   vsep=0.5, hsep=0.25,
                   body_w=1, body_h=0.7, w=0.4,
                   no_draw=no_draw,
                   )

    if arrowvsep2==None: arrowvsep2 = arrowvsep
    x0, y0 = x, y
    old_x, old_y = x, y # keep just in case
    min_y = 0 # min y used drawing pdas
    
    index = 0
    while 1:
        if index >= len(data): break
        state, tape, head_index, stackvalues = data[index]
        r = pda0(p,
                 x0=x0, y0=y0,
                 stackvalues=stackvalues,
                 tape=tape,
                 state=state,
                 head_index=head_index)

        #======================================================================
        # Now check for next pda
        #======================================================================
        x1,y1 = r.bottomright()
        min_y = min(min_y, y1)
        
        if index + 1 <= len(data) - 1:
            state, tape, head_index, stackvalues = data[index + 1]
            nextr = pda0(p,
                         x0=x0, y0=y0,
                         stackvalues=stackvalues,
                         tape=tape,
                         state=state,
                         head_index=head_index,
                         no_draw=True)
            x6,_ = nextr.bottomright()

            if x6 > max_x:
                # arrow from approx (x1,y1) to approx nextr.top()
                x0 = old_x

                x1,y1 = r.bottom(); y1 -= arrowvsep
                x2,y2 = x1, min_y - arrowvsep
                if y2 >= y1 - arrowvsep: y2 = y1 - arrowvsep
                x3,y3 = x0 + hoffset, y2 
                x4,y4 = x3, y3 - arrowvlen
                p += Line(points=[(x1,y1),
                                  (x2,y2),
                                  (x3,y3),
                                  (x4,y4)],
                          linewidth=0.1, endstyle='>')
                y0 = y4 - arrowvsep2 - w
                min_y = 0
            else:
                # CASE: no line break
                # Draw arrow to next pda (only if there's a next one)
                p += Line(points=[(x1 + arrowhsep, y0 + voffset),
                                  (x1 + arrowhsep + arrowhlen, y0 + voffset)],
                          linewidth=0.1, endstyle='>', linecolor='green')
                x0 = x1 + arrowhsep + arrowhlen + arrowhsep

        index += 1




# generalization of pda_computation
def sequence(p,
             x=0, y=0,
             max_x=10, # max x value before 'line' break
             rect=None,
             arrowhlen=0.5,
             arrowvlen=0.6,
             arrowhsep=0.25,
             arrowvsep=0.3,
             arrowvsep2=0.7,
             voffset=-0.8,
             hoffset=0.8,
             ):
    # data is a list of (state, tapevalues, head_index, stackvalues)
    #
    #          
    #             arrowhlen
    #             .
    #             .  arrowhsep
    # voffset   <->.  <->
    # ^ +------+   .     +-------+         +--------+
    # | |      |         |       |         |        |
    # v |      |   -->   |       |         |        |
    #   |      |         |       |         +--------+
    #   +------+         |       |                      arrowvsep  
    #                    +-------+ ............|..........
    #   hoffset                                |            ^
    #  <->                                     |         
    #     +------------------------------------+     ^   
    #     |                                          |
    #     v                                          v arrowvlen
    #                                                  arrowvsep2 -- distance between arrow head and top of body
    #  +------+
    #  |      |
    #  +------+
    if arrowvsep2==None: arrowvsep2 = arrowvsep
    x0, y0 = x, y
    old_x, old_y = x, y # keep just in case
    min_y = 0 # min y used drawing pdas
    
    index = 0
    while 1:
        if rect(index=index, p=p, x0=x0, y0=y0)==None: break
        r = rect(index=index, p=p, x0=x0, y0=y0)

        #======================================================================
        # Now check for next pda
        #======================================================================
        x1,y1 = r.bottomright()
        min_y = min(min_y, y1)
        
        if rect(index + 1,p=p,x0=x0,y0=y0,no_draw=True) != None:
            nextr = rect(index + 1, p=p, x0=x0, y0=y0, no_draw=True)
            x6,_ = nextr.bottomright()

            if x6 > max_x:
                # arrow from approx (x1,y1) to approx nextr.top()
                x0 = old_x

                x1,y1 = r.bottom(); y1 -= arrowvsep
                x2,y2 = x1, min_y - arrowvsep
                if y2 >= y1 - arrowvsep: y2 = y1 - arrowvsep
                x3,y3 = x0 + hoffset, y2 
                x4,y4 = x3, y3 - arrowvlen
                p += Line(points=[(x1,y1),
                                  (x2,y2),
                                  (x3,y3),
                                  (x4,y4)],
                          linewidth=0.2, endstyle='>')
                y0 = y4 - arrowvsep2
                min_y = 0
            else:
                # CASE: no line break
                # Draw arrow to next pda (only if there's a next one)
                p += Line(points=[(x1 + arrowhsep, y0 + voffset),
                                  (x1 + arrowhsep + arrowhlen, y0 + voffset)],
                          linewidth=0.2, endstyle='>')
                x0 = x1 + arrowhsep + arrowhlen + arrowhsep

        index += 1





def dfa(p,
        x0=0, y0=0, # coordinates of bottom-left of tape
        body_w=3,
        body_h=2,
        tape=[''], state='', head_index=0,
        vsep=1,  # vertical sep between bottom of tape and top of pda
        hsep=1,  # horizontal sep between right edge of pda and stack
        w=0.6, h=None,
        input_tape_str=False,
        no_draw=False,
        ):
    return pda(p,
               x0=x0, y0=y0, # coordinates of bottom-left of tape
               tape=tape, state=state, head_index=head_index,
               body_w=body_w,
               body_h=body_h,
               vsep=vsep,  # vertical sep between bottom of tape and top of pda
               w=w, h=h,
               input_tape_str=input_tape_str,
               stack_str=False,
               with_stack=False,
               include_arm_and_stack=False, 
               no_draw=no_draw,
               )
#==============================================================================
# Othello
#==============================================================================
def othello(p,
            m=[],
            x=0, y=0,
            rownames=None, colnames=None,
            whites = ['W', 'w', 'o', 'O'],
            blacks = ['B', 'b', '@', 'x', 'X'],
            width=0.7, height=None,
            do_not_plot=False,
            linewidth='',
            border_linewidth=0.06,
            ):
    if height==None: height = width
    if rownames==None:
        rownames=[r'\texttt{%s}' % chr(ord('a') + i) for i in range(len(m))]
    if colnames==None:
        colnames=[r'\texttt{%s}' % i for i in range(len(m[0]))]
    board = table2(p, m, x=x, y=y, width=width, height=height,
                   rownames=rownames,
                   colnames=colnames,
                   rowlabel=None, collabel=None,
                   do_not_plot=do_not_plot,linewidth=linewidth,
                   border_linewidth=border_linewidth)
    if not do_not_plot:
        for r,row in enumerate(m):
            for c,v in enumerate(row):
                x,y = board[r][c].center()
                if v in [' ', '']:
                    pass
                elif v in blacks:
                    p += Circle(x=x, y=y, r=0.2, background='black')
                elif v in whites:
                    p += Circle(x=x, y=y, r=0.2, background='white', linewidth=0.04)
                else:
                    p += Circle(x=x, y=y, r=0.2, linewidth=0, label=v)
    return board
#==============================================================================
# tic-tac-toe
#==============================================================================
def ttt(p,
        m=[],
        x=0, y=0,
        rownames=None, colnames=None,
        width=0.7, height=None,
        ratio=0.5, # space margin within the cell
        linewidth=0.04,
        border_linewidth=0.06,
        ):
    '''
    m is a matrix of ' ' or '' (space), 'X' or 'x', 'O' or 'o' 
    '''
    if height==None: height = width
    if rownames==None:
        rownames=[r'\texttt{%s}' % chr(ord('a') + i) for i in range(len(m))]
    if colnames==None:
        colnames=[r'\texttt{%s}' % i for i in range(len(m[0]))]
        
    m0 = copy.deepcopy(m)
    for r,row in enumerate(m):
        for c,_ in enumerate(row):
            m0[r][c] = ''
    board = table2(p, m0, x=x, y=y, width=width, height=height,
                   rownames=rownames,
                   colnames=colnames,
                   rowlabel=None, collabel=None,
                   border_linewidth=border_linewidth)

    ratio1 = (1 - ratio)/2.0 # distance of X tips to cell corner

    for r,row in enumerate(m):
        for c,v in enumerate(row):
            x,y = board[r][c].center()
            if v in [' ', '']:
                pass
            elif v in ['x', 'X']:
                rect = board[r][c]
                x0,y0 = rect.topleft(); x1,y1 = rect.bottomright()
                x0 += ratio1 * width; y0 -= ratio1 * width; p0=(x0,y0)
                x1 -= ratio1 * width; y1 += ratio1 * width; p1=(x1,y1)
                p += Line(points=[p0,p1], linewidth=linewidth)
                x0,y0 = rect.topright(); x1,y1 = rect.bottomleft()
                x0 -= ratio1 * width; y0 -= ratio1 * width; p0=(x0,y0)
                x1 += ratio1 * width; y1 += ratio1 * width; p1=(x1,y1)
                p += Line(points=[p0,p1], linewidth=linewidth)
            elif v in ['o', 'O']:
                p += Circle(x=x, y=y, r=ratio/1.8 * width, linewidth=linewidth)
    return board

#==============================================================================
# ER diagram
#==============================================================================
class ER:
    linewidth = 0.03
    boldlinewidth = 0.1
    attrib_width = 2; attrib_height = 0.8
    entity_width = 2; entity_height = 0.8
    relation_width = 3; relation_height = 2
    attrib_sep = 0.5  # separation between attributes (both vertical and horizontal)
    attrib_dist = 1.0 # distance of attrib to entity/relation
    aspect = True
    
    @staticmethod
    def attrib(center=(0,0), name='', label='',
               double=False,
               linestyle='',
               ):
        width = ER.attrib_width; height = ER.attrib_height; linewidth = ER.linewidth
        x,y = center
        x0 = x - width / 2.0;  x1 = x + width / 2.0
        y0 = y - height / 2.0; y1 = y + height / 2.0
        return ellipse(x0=x0, y0=y0, x1=x1, y1=y1,linestyle=linestyle,
               name=name, label=label, linewidth=linewidth, double=double)
    
    @staticmethod
    def labelfunc(s):
        s = s.replace('_', r'\_')
        return r'\texttt{%s}' % s

    @staticmethod
    def line(names, linestyle='', endstyle='', linewidth=None, arrowstyle=''):
        if linewidth==None: linewidth=ER.linewidth
        return str(Line(names=names, linewidth=linewidth,
                        linestyle=linestyle,
                        endstyle=endstyle, arrowstyle=arrowstyle))
    
    @staticmethod
    def edge(names):
        return str(Line(names=names, linewidth=ER.linewidth))
    @staticmethod
    def boldedge(names):
        return str(Line(names=names, linewidth=ER.boldlinewidth))
    @staticmethod
    def arc(names):
        return str(Line(names=names,
                        endstyle='>',
                        arrowstyle='triangle',
                        linewidth=ER.linewidth))
    @staticmethod
    def boldarc(names):
        return str(Line(names=names,
                        endstyle='>',
                        arrowstyle='triangle',
                        linewidth=ER.boldlinewidth))
    
    @staticmethod
    def entity(center, name='', label=None,
               attribs=None,
               derived=None,
               keys=None,
               dasheds=None,
               labelfunc=None, anchor=None,
               double=None,
               ):
        if label==None: label=name
        if double==None: double = []
        if double==True: double = [name]
        if derived==None: derived = []
        if labelfunc==None: labelfunc = ER.labelfunc
        ret = str(ER.entity_only(center=center, name=name, label=label, labelfunc=labelfunc, double=name in double))
        ret += str(ER.attribs(center=center, name=name, attribs=attribs,
                              keys=keys, dasheds=dasheds,
                              labelfunc=labelfunc, anchor=anchor,
                              double=double, derived=derived,
                              width=ER.entity_width, height=ER.entity_height))
        return ret

    @staticmethod
    def relation(center, name='', label=None,
                 attribs=None, keys=None,
                 labelfunc=None, anchor=None, double=None,
               ):
        if label==None: label=name
        if double==None: double = {}
        if double==True: double = [name]
        if labelfunc==None: labelfunc = ER.labelfunc
        ret = str(ER.relation_only(center=center, name=name, label=label, labelfunc=labelfunc, double=name in double))
        ret += str(ER.attribs(center=center, name=name,
                              attribs=attribs, keys=keys, labelfunc=labelfunc,
                              width=ER.relation_width, height=ER.relation_height,
                              anchor=anchor, double=double))
        return ret
    
    @staticmethod
    def entity_only(center,
                    name='',
                    label='', double=False,
                    labelfunc=None,
               ):
        width = ER.entity_width; height = ER.entity_height; linewidth = ER.linewidth
        x,y = center
        x0 = x - width / 2.0;  x1 = x + width / 2.0
        y0 = y - height / 2.0; y1 = y + height / 2.0
        label = labelfunc(label)
        ret = ''
        if double:
            d = 0.1
            ret += str(Rect(x0=x0 + d, y0=y0 + d , x1=x1-d, y1=y1-d,
                            linewidth=linewidth))
        ret += str(Rect(x0=x0, y0=y0, x1=x1, y1=y1,
                    name=name, label=label, linewidth=linewidth))
        return ret
    
    @staticmethod
    def relation_only(center,
                      name='',
                      label='', double=False,
                      labelfunc=None,
               ):
        width = ER.relation_width; height = ER.relation_height; linewidth = ER.linewidth
        label = labelfunc(label)
        return diamond(center=center,width=width,height=height,
                       label=label,name=name,double=double,
                       linewidth=linewidth)

    @staticmethod
    def associative_entity_only(center,
                                name='',
                                label='', double=False,
                                labelfunc=None,
               ):
        ret = str(ER.relation(center, name=name, label=label))
        ret += r'\node [draw=black, fit=(%s), line width=%scm, inner sep=0] {};' % (name, ER.linewidth)
        return ret

    @staticmethod
    def relation_attribs(p, center, relation_name, attribs=None,
                         keys=None,
                         labelfunc=None,
                         double=None,
                         anchor=None):
        if labelfunc == None:
            labelfunc = ER.labelfunc                
        if attribs==None: attribs = []
        if anchor==None: anchor={}
        if double==None: double=[]
        if keys==None: keys = []
        p += ER.relation(center, name=relation_name, double=double,
                         label=labelfunc(relation_name))

    @staticmethod
    def attribs(center=(0,0), # center of either entity or relation
                name=None,    # name of either entity or relation
                width=None,   # width of either entity or relation
                height=None,  # height of either entity or relation
                attribs=None,
                keys=None,
                labelfunc=None,
                double=None,
                anchor=None,
                derived=None,
                dasheds=None, # ADDED FOR PARTIAL KEY
    ):
        if labelfunc == None:
            labelfunc = ER.labelfunc
        if double==None: double=[]
        if attribs==None: attribs = []
        if keys==None: keys = []
        if dasheds==None: dasheds=[]
        if anchor==None: anchor={}
        if derived==None: derived=[]
        if width==None: width = max(ER.entity_width, ER.relation_width)
        if height==None: height = max(ER.entity_height, ER.relation_height)
        
        # all attribs
        temp_attribs = attribs[:]

        ret = ""

        # north attribs
        attribs = [_ for _ in temp_attribs if anchor.get(_,None) in ['north',None]]
        y = center[1] + height/2.0 + ER.attrib_dist + ER.attrib_height/2.0        
        num_attribs = len(attribs)
        total_len = num_attribs * ER.attrib_width + (num_attribs - 1) * ER.attrib_sep
        x = center[0] - total_len / 2.0 + ER.attrib_width / 2.0 
        for a in attribs:
            if a in keys:
                label = r'\underline{%s}' % labelfunc(a)
            elif a in dasheds:
                label = r'\dashuline{%s}' % labelfunc(a)
            else:
                label = labelfunc(a)
            if a not in derived:
                linestyle = ''
            else:
                linestyle = 'dashed'
            ret += str(ER.attrib(center=(x,y), name=a, label=label, double=a in double, linestyle=linestyle))
            x += (ER.attrib_width + ER.attrib_sep) 
            ret += str(ER.line(names=[a, name], linestyle=linestyle))
            
        # south attribs
        attribs = [_ for _ in temp_attribs if anchor.get(_,None) in ['south']]
        y = center[1] - height/2.0 - ER.attrib_dist - ER.attrib_height/2.0
        num_attribs = len(attribs)
        total_len = num_attribs * ER.attrib_width + (num_attribs - 1) * ER.attrib_sep
        x = center[0] - total_len / 2.0 + ER.attrib_width / 2.0 
        for a in attribs:
            if a in keys:
                label = r'\underline{%s}' % labelfunc(a)
            else:
                label = labelfunc(a)
            if a not in derived:
                linestyle = ''
            else:
                linestyle = 'dashed'
            ret += ER.attrib(center=(x,y), name=a, label=label,
                             double=a in double, linestyle=linestyle)
            x += (ER.attrib_width + ER.attrib_sep) 
            ret += str(ER.line(names=[a, name], linestyle=linestyle))

        # east attribs
        attribs = [_ for _ in temp_attribs if anchor.get(_,None) in ['east']]
        x = center[0] + width/2.0 + ER.attrib_dist + width/2.0
        num_attribs = len(attribs)
        total_len = num_attribs * ER.attrib_height + (num_attribs - 1) * ER.attrib_sep
        y = center[1] - total_len / 2.0 + ER.attrib_height / 2.0 
        for a in attribs:
            if a in keys:
                label = r'\underline{%s}' % labelfunc(a)
            else:
                label = labelfunc(a)
            if a not in derived:
                linestyle = ''
            else:
                linestyle = 'dashed'
            ret += ER.attrib(center=(x,y), name=a, label=label, double=a in double, linestyle=linestyle)
            y += (ER.attrib_height + ER.attrib_sep) 
            ret += str(ER.line(names=[a, name], linestyle=linestyle))

        # west attribs
        attribs = [_ for _ in temp_attribs if anchor.get(_,None) in ['west']]
        x = center[0] - width/2.0 - ER.attrib_dist - width/2.0
        num_attribs = len(attribs)
        total_len = num_attribs * ER.attrib_height + (num_attribs - 1) * ER.attrib_sep
        y = center[1] - total_len / 2.0 + ER.attrib_height / 2.0 
        for a in attribs:
            if a in keys:
                label = r'\underline{%s}' % labelfunc(a)
            else:
                label = labelfunc(a)
            if a not in derived:
                linestyle = ''
            else:
                linestyle = 'dashed'
            ret += ER.attrib(center=(x,y), name=a, label=label, double=a in double, linestyle=linestyle)
            y += (ER.attrib_height + ER.attrib_sep)
            ret += str(ER.line(names=[a, name], linestyle=linestyle))

        return ret

def crowfoot(p,
             x, y,
             kind, # '1' or '0..1' or '1..*' or '*'
             direction="west",
             dx=0.1,
             dx1=-1, # if -1, then dx1 = dx/2.0
             dy=-1, # if -1, then dy = dx
             linewidth=0.03,
             ):
    # For crow foot notation on top of line.
    # Line not included.

    # dy -- Radius of circle
    #       Also used for 1/2 of length of the vertical pipe
    #
    #  dx  dx1
    #  <-> <->
    #     |     ----       ^
    #     |    /    \      |  dy 
    #     |   |      |     v
    #  ---+---+------+-----------------------------------
    #     |   |      |
    #     |    \    /
    #     |     ----
    #
    #  dx  dx1
    #  <-> <->
    #     |   |   
    #     |   |    
    #     |   |   
    #  ---+---+------------------------------------------
    #     |   |
    #     |   |
    #     |   |
    #
    # TODO:
    # 1. Put into Line class. API: Add as startstyle and
    #    endstyle. Syntax is endstyle='crowfeet:0..1'
    # 2. Include line color.

    if dx1 < 0: dx1 = dx/2.0
    if dy < 0: dy = dx
    # 0 or 1
    if kind=='0..1' and direction=='west':
        p += Circle(x=x+dx+dx1+dy, y=y, r=dy,
                    background='white',
                    linewidth=linewidth)
        p += Line(points=[(x+dx, y-dy), (x+dx, y+dy)],
                  linewidth=linewidth)
    elif kind=='0..1' and direction=='east':
        p += Circle(x=x-dx-dx1-dy, y=y, r=dy, linewidth=linewidth,
                    background='white')
        p += Line(points=[(x-dx, y-dy), (x-dx, y+dy)],
                  linewidth=linewidth)

    # 1 -- exactly one
    elif kind=='1' and direction=='west':
        p += Line(points=[(x + dx, y - dy), (x + dx, y + dy)],
                  linewidth=linewidth)
        p += Line(points=[(x + dx + dx1, y-dy), (x + dx + dx1, y + dy)],
                  linewidth=linewidth)
    elif kind=='1' and direction=='east':
        p += Line(points=[(x - dx, y - dy), (x - dx, y + dy)],
                  linewidth=linewidth)
        p += Line(points=[(x - dx - dx1, y - dy), (x - dx - dx1, y + dy)],
                  linewidth=linewidth)
        
    # * -- no constraint    
    elif kind=='*' and direction=='west':
        p += Circle(x=x+dx+dy, y=y, r=dy, linewidth=linewidth,
                    background='white')
        p += Line(points=[(x+dx, y), (x, y+dy)],
                  linewidth=0.03)
        p += Line(points=[(x+dx, y), (x, y-dy)],
                  linewidth=0.03)
    elif kind=='*' and direction=='east':
        p += Circle(x=x-dx-dy, y=y, r=dy, linewidth=linewidth,
                    background='white')
        p += Line(points=[(x-dx, y), (x, y+dy)],
                  linewidth=linewidth)
        p += Line(points=[(x-dx, y), (x, y-dy)],
                  linewidth=linewidth)
        
    # 1..* -- at least one
    elif kind=='1..*' and direction=='west':
        p += Line(points=[(x+dx, y-dy), (x+dx, y+dy)],
                  linewidth=0.03)
        p += Line(points=[(x+dx, y), (x, y+dy)],
                  linewidth=linewidth)
        p += Line(points=[(x+dx, y), (x, y-dy)],
                  linewidth=linewidth)
    elif kind=='1..*' and direction=='east':
        p += Line(points=[(x-dx, y-dy), (x-dx, y+dy)],
                  linewidth=linewidth)
        p += Line(points=[(x-dx, y), (x, y+dy)],
                  linewidth=linewidth)
        p += Line(points=[(x-dx, y), (x, y-dy)],
                  linewidth=linewidth)
        
#==============================================================================
# To create a node as a bounding box
#==============================================================================
def fit(name,
        names=None,     # names of tikz nodes
        innersep=0,
        linewidth='',
        linestyle='',
        linecolor='',
        shape='rectangle',
        label='',
        ):
    names = ' '.join(['(%s)' % _ for _ in names])
    return r'''\node
    [draw=%(linecolor)s,
    %(shape)s,
    fit=%(names)s,
    inner sep=%(innersep)scm,
    %(linestyle)s]
    (%(name)s) {%(label)s};''' % {'name':name, 'names':names, 'linecolor':linecolor,
    'linestyle':linestyle, 'shape':shape,
    'innersep':innersep, 'label':label,
    }

#=============================================================================
# Heapfile
#=============================================================================
def heapfilepage(p,
                 nrows, ncols,
                 slots,
                 free_offset=None,
                 colors=['blue!20', 'green!20', 'red!20', 'yellow!20', 'cyan!20', 'brown!20', 'violet!20'],
                 ):

    if free_offset==None:
        free_offset = max([0] + [x + y for (x,y) in slots])
        
    from latexcircuit import POINT
    width = height = 0.7
    colorsindex = 0

    m = [['' for i in range(ncols)] for j in range(nrows)
        ]

    C = table2(p, m, width=width, height=height, do_not_plot=True)

    def colorcells(p, color='blue!20', rcs=None):
        for r,c in rcs:
            x0,y0 = C[r][c].bottomleft() 
            x1,y1 = C[r][c].topright()
            p += Rect(x0=x0, y0=y0, x1=x1, y1=y1,
                      background=color, label='', linewidth=0)

    for offset, length in slots:
        #if offset == -1: continue
        for i in range(length):
            offset_ = offset + i
            r = offset_ / ncols
            c = offset_ % ncols
            colorcells(p, rcs=[(r,c)], color=colors[colorsindex])
        colorsindex = (colorsindex + 1) % len(colors)

    table2(p, m, width=0.7, height=0.7,
        rownames=[],
        colnames=[],
        rowlabel=None, collabel=None)

    def merge(p, r, c, label='', color='black!10'):
        x0,y0 = C[r][c].bottomleft() ; y0+=0.01 
        x1,y1 = C[r][c+1].topright() ; x1-=0.005
        r = Rect(x0=x0, y0=y0, x1=x1, y1=y1,
              background=color, label=label, linewidth=0.01)
        p += r
        return r

    # free offset 
    c0 = merge(p, nrows - 1, ncols - 2, label='{\small %s}' % free_offset)

    # size of slots
    c1 = merge(p, nrows - 1, ncols - 4, label='{\small %s}' % len(slots))

    # offset,length
    k = nrows * ncols - 6
    for offset, length in slots:
        #if offset == -1: continue
        r, c = k / ncols, k % ncols
        c2 = merge(p, r, c, label='{\small %s}' % length); k -= 2
        r, c = k / ncols, k % ncols  
        c3 = merge(p, r, c, label='{\small %s}' % offset); k -= 2
        #x0,y0 = c3.topleft(); x0 += 0.2; y0 -= 0.2
        #r,c = offset / ncols, offset % ncols
        #p += Line(points=[(x0,y0), C[r][c].center()], endstyle='>')

    # draw record space -- free space boundary
    if len(slots) > 0:
        offset, length = slots[-1]
        offset += length - 1
        r, c = offset / ncols, offset % ncols
        p += Line(points=[C[r][0].bottomleft(),
                          C[r][c].bottomright(),
                          C[r][c].topright(),
                          C[r][-1].topright(),
                          ],
                  linewidth=0.08, linecolor='black!60', linestyle='dashed')

    # draw free space -- footer boundary
    offset = nrows * ncols - 4 * (1 + len(slots)) - 1
    r, c = offset / ncols, offset % ncols
    p += Line(points=[C[r][0].bottomleft(),
                      C[r][c].bottomright(),
                      C[r][c].topright(),
                      C[r - 1][-1].bottomright(),
                      ],
              linewidth=0.08, linecolor='black!60', linestyle='dashed')

    # free offset arrow
    x0,y0 = c0.topleft(); x0 += 0.2; y0 -= 0.2
    r, c = free_offset / ncols, free_offset % ncols
    p += Line(points=[(x0,y0), C[r][c].center()], endstyle='>')

    # draw slot's offset arrow
    k = -4
    for offset, length in slots:
        k -= 4
        i = ncols * nrows + k
        r, c = i / ncols, i % ncols
        x0,y0 = C[r][c].topleft(); x0 += 0.2; y0 -= 0.2
        r,c = offset / ncols, offset % ncols
        if offset == -1: continue
        p += Line(points=[(x0,y0), C[r][c].center()], endstyle='>')

    def labelsections(p, row, label):
        x0,y0 = C[row][-1].center(); x0 += 0.5
        x1,y1 = x0 - 0.4, y0
        p += Line(points=[(x0,y0), (x1,y1)], linewidth=0.1, endstyle='>')
        p += str(POINT(x=x0, y=y0, r=0, label=r'{\small %s}' % label,
             anchor='west'))

    # need to find 1st row of free space
    # TODO: Need to handle case when there is no free space of free space not touching
    # rightmost column.
    r,c = free_offset / ncols, free_offset % ncols
    labelsections(p, r, 'free space')
    labelsections(p, -1, 'footer')

    # TODO: record space can be empty
    if not (free_offset / ncols == 0 and free_offset % ncols == 0):
        x0,y0 = C[0][0].center(); y0 += 0.6
        x1,y1 = x0, y0 - 0.5
        p += Line(points=[(x0,y0), (x1,y1)], linewidth=0.1, endstyle='>')
        p += str(POINT(x=x0, y=y0, r=0, label=r'{\small %s}' % 'record space', anchor='south'))

    # draw border one more time
    x0,y0 = C[-1][0].bottomleft()
    x1,y1 = C[0][-1].topright()
    p += Rect(x0=x0, y0=y0, x1=x1, y1=y1, linewidth=0.04)

    return C

#==============================================================================
# B+ tree
# bptnode -- B+ tree internal node 
#==============================================================================
def bpt_node(x, y, M, widths=[0.2,0.7], height=0.5,
             linewidth=0.03,
             linecolor='black',
             background=''):
    def node(x=0, y=0, M=None, widths=[0.2, 0.7], height=0.5):
        c = RectContainer(x=x, y=y)
        for i,x in enumerate(M):
            if widths[i] > 0:
                c += Rect2(x0=0, y0=0, x1=widths[i], y1=height, label=x,
                           linecolor=linecolor, background=background,
                           linewidth=linewidth)
            else:
                c += Line(x0=0, y0=0, x1=widths[i], y1=height, label=x,
                          linecolor=linecolor,
                          linewidth=0.02)
        return c

    M0 = []
    widths0 = []
    for _ in M:
        M0 += ['', _]
        widths0 += widths
    M0.append('')
    widths0.append(widths[0])
    return node(x=x, y=y, M=M0, widths=widths0, height=height)

def bpt_leafnode(x, y, M, widths=[0.7,0.2], height=0.5,
                 linewidth=0.03,
                 linecolor='black',
             background=''):
    def node(x=0, y=0, M=None, widths=[0.7, 0.2], height=0.5):
        c = RectContainer(x=x, y=y)
        for i,x in enumerate(M):
            if widths[i] > 0:
                c += Rect2(x0=0, y0=0, x1=widths[i], y1=height, label=x,
                           linecolor=linecolor, background=background,
                           linewidth=linewidth)
            else:
                c += Line(x0=0, y0=0, x1=widths[i], y1=height, label=x,
                          linecolor=linecolor,
                          linewidth=0.02)
        return c

    M0 = []
    widths0 = []
    for _ in M:
        M0 += [_, '']
        widths0 += widths
    M0.append('')
    widths0.append(widths[1])
    return node(x=x, y=y, M=M0, widths=widths0, height=height)

def bpt_arc(node0, node1, index, delta=0.0, r=None,
            linecolor='black'):
    # node0 -> node1 through pointer of given index
    x0,y0 = node1.top()
    x1,y1 = node0[2 * index].center()
    halfheight = node0[2*index].height()/2.0
    points = get_points(x1, y1, x0, y0, 'vbroom', delta=delta - halfheight)
    return Pointer(points = points, arrowstyle='triangle',
                   linecolor=linecolor,
                   r=r, linewidth=0.02)
def bptree_get_siblings(x, y, siblings_data, widths, height, node_sep):
    ''' returns list of bpt_nodes '''
    max_num_keys = len(siblings_data[0])
    node_width = max_num_keys * widths[1] + (max_num_keys + 1) * widths[0]
    siblings = [] 
    for i,M in enumerate(siblings_data):
        siblings.append(bpt_node(x=x + i * (node_width + node_sep),
                                 y=y, M=M, widths=widths, height=height))
    return siblings

def bptree_get_root(y=0, keys=[], children=[], widths=[], height=[]):
    # Place root: Note that we need to center the root above the children.
    # Also, the root's center is center for NON-BLANK keys.
    root_keys = len([_ for _ in keys if _ != ''])
    root_width = root_keys * widths[1] + (root_keys + 1)  * widths[0]
    if len(children) % 2 == 1:
        x2 = children[(len(children))//2].top()[0]
    else:
        x0 = children[len(children)//2 - 1].top()[0]
        x1 = children[len(children)//2].top()[0]
        x2 = (x0 + x1) / 2.0
    root = bpt_node(x=x2 - 0.5 * (root_keys * widths[1] + (root_keys + 1) * widths[0]),
                    y=y, M=keys, widths=widths, height=height)
    return root

# number of bends or levels in the arcs
def bptree_get_arcs(root, children, vsep, height):
    #print ("root:", root)
    #print ("children:", children)
    if len(children) % 2 == 1:
        num_arc_levels = len(children) / 2 + 1
        deltas = [(num_arc_levels - _ - 1) * float(vsep)/(num_arc_levels) - height for _ in range(num_arc_levels)]
        deltas = deltas + deltas[:-1][::-1]
    else:
        num_arc_levels = len(children) / 2
        if num_arc_levels == 1:
            deltas = [0.0, 0.0]
        else:
            deltas = [(num_arc_levels - _ - 1) * float(vsep)/(num_arc_levels) - 0.25 for _ in range(num_arc_levels)]
            deltas = deltas + deltas[::-1]
    arcs = [bpt_arc(root, child, i, delta=delta) \
            for i, (child, delta) in enumerate(zip(children, deltas))]
    return arcs

def bptree_get_labels(keyss, arcs, placements=None):
    # placement is a list of (ratio, anchor), one for each arc

    labels = []
    if placements==None:
        placements = [(1, 'south west') for _ in arcs]
        
    for i, (arc, (ratio, anchor)) in enumerate(zip(arcs, placements)):
        x,y = arc.midpoint()

        if i == 0:
            label = r'$(-\infty, %s)$' % keyss[0][0]
        elif i == len(arcs) - 1:
            label = r'$[%s, \infty)$' % keyss[0][len(arcs) - 2]
        else:
            label = r'$[%s,%s)$' % (keyss[0][i - 1], keyss[0][i])

        '''
        anchor = 'south'; ratio = 0.5
        if len(arcs) % 2 == 1 and i == len(arcs) / 2:
            anchor = 'west'; ratio = 0.8
        elif len(arcs) % 2 == 0 and i in [len(arcs)/2 - 1, len(arcs)/2]:
            anchor = 'south'; ratio = 0.9
        '''

        #anchor = 'west'; ratio = 0.8

        from latexcircuit import POINT
        x,y = arc.midpoint(ratio=ratio)
        X = POINT(x=x, y=y, r=0, label=r'{\tiny %s}' % label, anchor=anchor)
        labels.append(str(X))
    return labels


def bptree(p,
           edges,
           nodes=None,
           widths=[0.1, 0.5],
           height=0.4,
           node_sep=0.1,
           vsep=1.25, # vertical separation -- from bottom of root to top of child
           # special handling
           arc_linewidth=None,
           draw=True,
           ):
    # edges = {'A':['B','C','D','E'],
    #         'B':['G','H','I','J'],...
    #        }
    # nodes = {'A':[0,1,2,3],...
    #
    flattened_values = reduce(lambda x,y:x+y, edges.values())
    #print ("flattened:", flattened_values)
    roots = [key for key in edges.keys() if key not in flattened_values]
    if len(roots) > 1:
        #print ("more than one root: roots =", roots)
        return
    # Print bottom up.
    # Print leaves first. A parent is placed based on centering it above children.
    # The problem is placing leaves of different parents when the depth is different.
    #
    #            X
    #        
    #   X     X X X X     X
    #                     
    # X X X            X X X X
    #
    # BFS to give each node a depth.
    #
    #                      X X X X
    #        
    #          X X X X                  X X X X    
    #                     
    # X X X X  X X X X  X X X X    X X X X   X X X X
    #
    # For each non-leaf node n, get the positions of the children.
    # Place n in the middle above the children.
    #
    # Might be a good idea to create a rect for siblings?
    # That way the top() of this rect can be used easily to place the parent.
    #
    # Suppose d is max depth.
    # Place all the nodes at max depth d. These are leaf nodes.
    #   Siblings are placed next to each other.
    #   For two different groups of siblings, spacing depends on leaves in higher depth.
    # Place all nodes at depth d - 1:
    #   First place nodes which are not leaf:
    #     Place them in the middle and above the children
    #   Second place the leaf nodes
    #
    # Do DF traversal to collect leaves in left-to-right order.
    # Placed them accordingly.
    # Then do post order DF traversal and place nodes based on children's positions.
    
    root = roots[0]
    stack = [root]
    depth = {}; depth[root] = 0
    while stack != []:
        x, stack = stack[0], stack[1:]
        x_depth = depth.get(x, None)
        if x_depth == None: assert "%s does not have depth" % x
        children = edges.get(x, None)
        if children == None:
            # this is a leaf
            pass
        else:
            child_depth = x_depth + 1
            for child in children:
                depth[child] = child_depth
            stack += children
    #print depth
    # For each depth, starting with max depth, place the nodes
    # according to the order given by the edges, going left-to-right

    # Collect leaves:
    leaves = []
    stack = [root]
    while stack != []:
        x, stack = stack[0], stack[1:]
        #print ("x:", x)
        children = edges.get(x, None)
        #print ("children:", children)
        if children == None:
            leaves.append(x)
        else:
            stack = children + stack
        #print ("stack:", stack)
        
    #print ("leaves:", leaves)

    # Place leaves:
    # max depth at y = 0
    #
    #
    #                   xxxxx xxxxx xxxxx
    #                  
    # xxxxx xxxxx xxxxx                   xxxxx xxxxx xxxxx <--- max depth
    maxdepth = max(depth.values())
    #print ("maxdepth:", maxdepth)
    rect = {} # dictionary of bpt_nodes
    for i,leaf in enumerate(leaves):
        max_num_keys = len(nodes[leaf])
        node_width = max_num_keys * widths[1] + (max_num_keys + 1) * widths[0]
        #print (node_width)
        #print (node_sep)
        x = i * (node_width + node_sep)
        y = -10 + (maxdepth - depth[leaf]) * (height + vsep)
        r = bpt_node(x=x, y=y, M=nodes[leaf], widths=widths, height=height)
        rect[leaf] = r
        #p += r
    # Place non-leaf. Can do post order tranversal. Or iterate from maxdepth to 0
    done = leaves[:]
    for d in range(maxdepth, -1, -1):
        #print ("d:", d)
        todo = [_ for _ in nodes.keys() if depth[_] == d and _ not in done]
        #print ("todo:", todo)
        for n in todo:
            max_num_keys = len(nodes[n])
            node_width = max_num_keys * widths[1] + (max_num_keys + 1) * widths[0]
            #print ("n:", n) 
            children = edges[n]
            xs = [rect[_].top()[0] for _ in children]
            xs.sort()
            x0 = xs[0]
            x1 = xs[-1]
            x = (x0 + x1)/2.0 - node_width/2.0
            y = -10 + (maxdepth - d) * (height + vsep)
            r = bpt_node(x=x, y=y, M=nodes[n], widths=widths, height=height)
            rect[n] = r
            #p += r
            done.append(n)
    # Arcs
    arcs = {}
    for k,v in edges.items():
        #print ("k,v:", k,v)
        parent = rect[k]
        children = [rect[_] for _ in v]
        arcs[k] = bptree_get_arcs(parent, children, vsep, height)
        #for arc in arcs[k]:
        #    p += arc

    labels = {}
    for k in edges.keys():
        _ = [nodes[k]] + [nodes[i] for i in edges[k]]
        labels_ = bptree_get_labels(_,
                            arcs[k], placements=None)
        #for label in labels:
        #    p += label
        labels[k] = labels
    # placement is a list of (ratio, anchor), one for each arc

    if draw:
        for _ in rect.values(): p += _
        for _ in arcs.values():
            for __ in _: p += __
        for _ in labels.values():
            for __ in labels: p += __
    return rect, arcs, labels
#==========================================================================    
# Parse tree
#==========================================================================    
def parse_tree(p, d, labels, edges): 
    rects = {}
    for k,(x,y) in d.items():
        rects[k] = Rect(x0=x, y0=y-0.3, x1=x, y1=y+0.3, label=labels[k],
                        name=k, linecolor='white')
        p += rects[k]
    for k,v in edges.items():
        for _ in v:
            p += Line(points=[rects[k].bottom(), rects[_].top()])
    return rects

#=========================================================================
# CYK table
#=========================================================================
def cyk(p, m, w=None,
        width=2.3, height=0.7,
        background=None,
        rect=None,
        fontsize=None,
        do_not_plot=False):
    
    size = len(m)
    if background==None: background={}
    if w==None: w = ' '
    def getrect():
        i = {0:0}
        def rect(x):
            if fontsize:
                x = r'{\%s %s}' % (fontsize, x)
            row, col = int(i[0] / size), i[0] % size
            if (row, col) in background.keys():
                i[0] += 1
                return Rect2(x0=0, y0=0, x1=width, y1=height,
                            innersep=0.2,
                            linewidth=0.05,
                            background=background[(row, col)],
                            s='%s' % x, align='t')
            else:
                i[0] += 1
                return Rect(x0=0, y0=0, x1=width, y1=height,
                            innersep=0.2,
                            s='%s' % x, align='t')
        return rect
    if rect==None:
        rect = getrect()
    c = table2(p, m, width=width, height=height,
               rowlabel='$j$', collabel='$i$',
               rect=rect,
               rownames=range(1, size+1), colnames=range(1, size+1), do_not_plot=do_not_plot)
    if not do_not_plot:
        widths = [c[0][i].topright()[0] - c[0][i].topleft()[0] for i in range(size)]
        x,y = c[0][0].topleft(); y += 0.5
        c0 = RectContainer(x=x, y=y)
        for x,_ in zip(w,widths):
            c0 += Rect2(x0=0, y0=0, x1=_, y1=0.7,
                        linewidth=0.1, linecolor='white',
                        label=r'{\texttt{%s}}' % x)
        p += c0
    return c                  

#========================================================================
# SP FP
# Draw fields of IEEE 754 Single Precision
#========================================================================
def spfp(p, x=0, y=0, s='0', ebias='11111111', f='11111111111111111111111'):
    from latexcircuit import POINT
    c = RectContainer(x=1, y=1)
    c += Rect2(x0=0, y0=0, x1=1, y1=0.6, label=s)
    c += Rect2(x0=0, y0=0, x1=2, y1=0.6, label=ebias)
    c += Rect2(x0=0, y0=0, x1=5, y1=0.6, label=f)
    p += c
    x,y = c[0].bottom(); X = POINT(x=x, y=y, r=0, label='{\scriptsize 1 bit}', anchor='north'); p += str(X)        
    x,y = c[1].bottom(); X = POINT(x=x, y=y, r=0, label='{\scriptsize 8 bits}', anchor='north'); p += str(X)        
    x,y = c[2].bottom(); X = POINT(x=x, y=y, r=0, label='{\scriptsize 23 bits}', anchor='north'); p += str(X)        
    return c

#==============================================================================
# Binary tree
# Note: uses Graph
#==============================================================================
def bintreepositions(edges, node_width=0.8, node_vsep=1.0, node_hsep=0.2):
    keys = list(edges.keys())
    rhs = []
    for k in edges.keys():
        for x in edges[k]:
            if x not in [None, '']:
                if x not in rhs: rhs.append(x)
    nodes = list(keys)
    roots = [x for x in keys if x not in rhs]
    root = roots[0]
    for x in edges.values():
        for y in x:
            if y not in nodes: nodes.append(y)
    def height(p, edges):
        if p == None:
            return -1
        else:
            xs = [height(x, edges) for x in edges.get(p, [None])]
            return 1 + max(xs)
    ht = height(root, edges)
    d = {}
    queue = [(root, 0, 0, 1, (0,0))] # node, depth, child#, nsiblings, parent position
    while queue != []:
        x,depth,child,nsiblings,ppos = queue[0]; del queue[0]
        #if x in [None,'']: continue
        if depth==0:
            pos = (0,0)
        else:
            hsep = 2**(ht - depth)*(node_width + node_hsep) # betw centers
            pos = -((2**depth - 1) * hsep)/2.0 + child * hsep, -(node_vsep*depth)
            pos = round(pos[0],3), round(pos[1],3)
        if x not in [None,'']:
            d[x] = pos
        for i,a in enumerate(edges.get(x,[])):
            queue.append((a, depth+1, 2*child + i, len(edges.get(x,[])), pos))
    return d

 
def bintree(p=None,
            edges=[],
            node_width=0.3,
            node_vsep=1.0,
            node_hsep=0.3,
            node=None,
            edge=None,
            label=None):
    if label!=None:
        __label = label
    else:
        __label = (lambda x:(r'\texttt{%s}' % x))
    pos = bintreepositions(edges=edges,
                           node_width=node_width,
                           node_hsep=node_hsep,
                           node_vsep=node_vsep)
    # for name, remove non-alphanumerics
    def xxxxx(s):
        s = str(s)
        import string
        # WARNING: check valid charactre for node name
        valid = string.ascii_letters + string.digits + '$?_-' # cannot have ",.():" and some other special characters
        return ''.join([c for c in s if c in valid])
    __name = xxxxx
    if node==None:
        def node(x, y, name, l):
            return Graph.node(x=x, y=y, r=node_width,
                              name=__name(name),
                              label=__label(l))
    if edge==None:
        def edge(names):
            return Graph.edge(names=names)

    for k,(x,y) in pos.items():
        p += node(x=x, y=y, name=k, l=k)
    for k,v in edges.items():
        for x in v:
            if x in [None,'']: continue
            p += edge(names=[k,x])
    return pos

class BinTree:
    
    node = None
    edge = None
    label = None
    node_width = 0.4
    node_vsep = 1.0
    node_hsep = 0.4
    
    @staticmethod
    def run(p, edges, label=None):
        if label==None: label=None
        return bintree(p=p,
                       edges=edges,
                       node_width=BinTree.node_width,
                       node_vsep=BinTree.node_vsep,
                       node_hsep=BinTree.node_hsep,
                       node=BinTree.node,
                       edge=BinTree.edge,
                       label=label)


def drawheap(p, edges, node=None, node_hsep=None, include_array=True):
    BinTree.node_hsep = 0.6
    BinTree.node = node
    if node_hsep: BinTree.node_hsep = node_hsep
    BinTree.node_width = 0.35    
    pos = BinTree.run(p, edges)

    if include_array:
        keys = pos.keys()
        values = []
        for v in edges.values(): values += v
        root = [k for k in keys if k not in values][0]

        # bfs
        s = [root]
        results = []
        while len(s) > 0:
            x = s.pop(0); results.append(x)
            s += edges.get(x, [])
        
        # smallest y in pos
        y = min([y for (_,y) in pos.values()])
        y -= 1
        n = len(results)
        x,_ = pos[root]
        width = 0.6; height = 0.6
        x -= n / 2.0 * width
        p += Array2d(x, y, width=width, height=height, 
                     xs=[results])

    return pos
     

def array_to_edges(xs):
    '''
    Returns edges from array xs where xs is a heap
    '''
    edges = {}
    def left(i): return 2 * i + 1
    def right(i): return 2 * i + 2
    todo = [0] # list of indices
    n = len(xs)
    while len(todo) > 0:
        i,todo = todo[0],todo[1:]
        #print ("i:", i, left(i), right(i), xs[left(i)], xs[right(i)])
        if right(i) <= n - 1:
            edges[xs[i]] = [xs[left(i)], xs[right(i)]]
            todo.append(left(i))
            todo.append(right(i))
        elif left(i) <= n - 1:
            edges[xs[i]] = [xs[left(i)]]
            todo.append(left(i))
    return edges

#==============================================================================
# For student tests
#==============================================================================
def test_score_table():
    p = Plot()
    M = 1; N = 21
    m00 = [['Question']]
    m10 = [[i] for i in range(M, N)]
    m01 = [['Points'],
    ]
    m11 =[[''] for i in range(M, N)]

    M = [[m00, m01], [m10, m11]]
    N = table3(p, M, 0, 0, width=3, height=0.8)

    M = 21; N = 41
    m00 = [['Question']]
    m10 = [[i] for i in range(M, N)]
    m01 = [['Points'],
    ]
    m11 =[[''] for i in range(M, N)]

    M = [[m00, m01], [m10, m11]]
    N = table3(p, M, 8, 0, width=3, height=0.8)

    M = 1; N = 2
    m00 = [['TOTAL']]
    m10 = [[''] for i in range(M, N)]
    m01 = [[''],]
    m11 =[[''] for i in range(M, N)]
    
    M = [[m00, m01], [m10, m11]]
    N = table3(p, M, 8, -17.5, width=3, height=0.8)
    print(p)

def practice_disclaimer():
    print(r'''
\begin{center}
\fbox{\begin{minipage}{0.75\textwidth}
    \textsc{Warning}.
Note that this is a practice test.
    It does not mean that you are fully prepared for the test
just by going through a practice test.
The only sure way to be fully prepared is to
study all the
class material, including class notes,
    assignments, etc.
\end{minipage}}
\end{center}
''')

def ciss240_written_test_instructions():
    print(r'''
    \textsc{Instructions}
\begin{enumerate}

\li This is a closed-book, no-discussion, no-calculator, no-computer
    test.

\li Cheating is a serious academic offense. If caught you will 
    receive an immediate score of -100\%.

\li If a question asks for an output and the code contains
    an error, write \verb!ERROR! as output.
        If the program or code segment does not terminate
    (i.e. it runs forever without stopping), write \verb!INFINITE LOOP!
    as output.
    When writing output, use one cell for each output character
    in the grid provided.

\li If a question asks the computation of a value
    or the value of a variable and the program or
    code fragment contains
    an error, write \verb!ERROR! as value.
    If the value is undefined, write \verb!UNDEFINED!.
    If the program or code segment does not terminate
    (i.e. it runs forever without stopping), write \verb!INFINITE LOOP!
    for the answer.

\li When you're asked to write a C++ statement, don't forget that it must
    end with a semicolon.
    
\li Unless otherwise stated, bubblesort refers to the bubblesort algorithm in
    our notes where values are sorted in ascending order.

\end{enumerate}
    ''')
