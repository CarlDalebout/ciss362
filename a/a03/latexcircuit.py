from latextool_basic import *


def rotate_about(p0, p1, t):
    if t:
        x, y = p0
        x0, y0 = p1
        x, y = x - x0, y - y0
        c = cos(t); s = sin(t)
        x, y = x * c - y * s, x * s + y * c
        x, y = x + x0, y + y0
        return round(x,5), round(y,5)
    else:
        return p0


def source(name='x', x=0, y=0, withnot=True):
    """
    x(X0)  (X1)---(X)
                   |
                   |
                  (X4)----NOT GATE(__XNOT, XNOT)
"""

    xpath = r"""
\path (%(x)s, %(y)s) coordinate (%(nameupper)s0);
\draw (%(x)s, %(y)s) node {$%(name)s$};
\path (%(x)s, %(y)s) ++(0.5, 0) coordinate (%(nameupper)s1);
\path (%(nameupper)s1) ++(0.5, 0) coordinate (%(nameupper)s);
\draw (%(nameupper)s1) -- (%(nameupper)s);
"""

    xnotpath = ''
    if withnot:
        xnotpath = r"""
\fill[black] (%(nameupper)s) circle (2pt);
\path (%(nameupper)s)  ++(0.5, -0.5) coordinate (__%(nameupper)sNOT);
\draw (__%(nameupper)sNOT) node[not gate, scale=0.5] (%(nameupper)sNOT) {};
\draw (%(nameupper)s) |- (%(nameupper)sNOT);
\fill[black] (%(nameupper)s |- %(nameupper)sNOT) circle (2pt);
"""
    return ("% ----- SOURCE " + name) + \
            (xpath + xnotpath) % \
            {'nameupper':name.upper(), 'name':name, 'x':x, 'y':y}


def source2(name='x', x=0, y=0):
    # Same as source, except that this version expects name is for instance
    # either "x" or "x'" and not both and draws one line to save space
    """
    x(X0)  (X1)--------------(X2: X or XNOT)
"""

    is_not = (name[-1] == "'")
    if is_not: name = name[:-1]

    xpath = r"""
\draw (%(x)s, %(y)s) node {$%(name)s$};
"""
    if is_not:
        xpath += r"""
\path (%(x)s, %(y)s) ++(0.5, 0) coordinate (%(nameupper)s0);
\path (%(x)s, %(y)s) ++(1.5, 0) coordinate (__%(nameupper)sNOT);
\draw (__%(nameupper)sNOT) node[not gate, scale=0.5] (%(nameupper)sNOT) {};
\draw (%(nameupper)s0) -- (%(nameupper)sNOT.input);
"""
    else:
        xpath += r"""
\path (%(x)s, %(y)s) ++(0.5, 0) coordinate (%(nameupper)s);
"""

    return ("% ----- SOURCE " + name) + \
            xpath % \
            {'nameupper':name.upper(), 'name':name, 'x':x, 'y':y}

#==============================================================================
# Gates
#==============================================================================
def GATE(gate='and', name='AND',
         x=0, y=0,
         inputs=1, direction='down', output_length=0):
    # If inputs == 1, then no gate is drawn but a variable
    # is set at the given coordinates.
    # NOTE: not gate is scales to 0.5
    if gate not in ['and', 'or', 'not', 'xor', 'nor', 'nand', 'xnor']:
        raise ValueError("invalid gate %s" % gate)
    if direction not in ['down', 'up', 'left', 'right']:
        raise ValueError("invalid gate %s" % gate)

    dx, dy = 0, 0
    rotate=''
    scale=1

    if inputs == 1 and gate != 'not':
        s = r"""\path (%(x)s, %(y)s) coordinate (%(name)s);"""
        inputs=''
    else:
        if gate == 'not': scale = 0.5
        directions = {'down':270, 'up':90, 'left':180, 'right':0}
        rotate = directions[direction]
        inputs = ','.join(['normal' for _ in range(inputs)])
        inputs = '{%s}' % inputs
        s = r"""
\draw (%(x)s, %(y)s) node [%(gate)s gate, scale=%(scale)s, inputs=%(inputs)s, rotate=%(rotate)s] (%(name)s) {};
\draw (%(name)s.output) -- ++(%(dx)s, %(dy)s);
"""
        if direction == 'up': dy = output_length
        elif direction == 'down': dy = -output_length
        elif direction == 'left': dx = -output_length
        else: dx = output_length

    return s % {'gate':gate, 'name':name, 'scale':scale,
                'x':x, 'y':y, 'inputs':inputs, 'rotate':rotate,
                'dx':dx, 'dy':dy}


def AND(name, x=0, y=0, inputs=1, direction='down', output_length=0):
    return GATE('and', name=name,
                x=x, y=y,
                inputs=inputs, direction=direction,
                output_length=output_length)

def OR(name, x=0, y=0, inputs=1, direction='right', output_length=0.5):
    return GATE('or', name=name,
                x=x, y=y,
                inputs=inputs, direction=direction,
                output_length=output_length)

def NOT(name, x=0, y=0, direction='right', output_length=0.5):
    return GATE('not', name=name,
                x=x, y=y,
                inputs=inputs, direction=direction,
                output_length=output_length)



def dottedbend(coord1, coord2, direction="|-"):
    if direction not in ['|-', '-|']:
        raise ValueError('invalid direction %s' % direction)
    return r"""
\draw (%(coord1)s) %(direction)s (%(coord2)s);
\fill[black] (%(coord1)s %(direction)s %(coord2)s) circle (2pt);
""" % {'coord1':coord1, 'coord2':coord2, 'direction':direction}


def join_to_and(inputs, gate_name, gate_direction='down'):
    num_inputs = len(inputs)
    nums = range(num_inputs, 0, -1)
    if gate_direction == 'down':
        t = ''
        if num_inputs > 1:
            for i,name in zip(nums, inputs):
                name = name.upper()
                if name[-1] == "'": name = name[:-1] + 'NOT'
                target = "%(gate_name)s.input %(i)s" % \
                         {'i':i, 'gate_name':gate_name}
                s = dottedbend(name,target,direction="-|")
                t += s
            return t
        else: # num_inputs == 1
            name = inputs[0].upper()
            if name[-1] == "'": name = name[:-1] + 'NOT'
            target = "%(gate_name)s" % {'gate_name':gate_name}
            s = dottedbend(name,target,direction="-|")
            t += s
            return t
    else:
        raise Value("gate_direction %s invalid" % gate_direction)


def SOP_or_POS(gate1='and', gate2='or',
               vars=['x','y','z'], terms=[['x','y'],['y','z']],
               space_saving_with_not_gate=False):

    s = ""
    allliterals = flatten(terms)
    x, y = 0, 0

    if space_saving_with_not_gate:
        for var in vars:
            var_present = var in allliterals
            varnot_present = ("%s'" % var) in allliterals
            if var_present and varnot_present:
                s += source(name=var, x=x, y=y, withnot=True)
                y -= 1
            else:
                name = IFELSE(var_present, var, "%s'" % var)
                s += source2(name=name, x=x, y=y)
                y -= 0.5
    else:
        for var in vars:
            varnot_present = ("%s'" % var) in allliterals
            s += source(name=var, x=x, y=y, withnot=varnot_present)
            y -= 1

    x = 3
    y -= 0.5
    max_inputs = max([len(term) for term in terms])
    if max_inputs > 4:
        y -= (max_inputs - 4) * 0.1
    s += "% ----- FIRST GATES\n"
    for i,term in enumerate(terms):
        gate_name = 'AND%s' % (i+1)
        if len(term) > 4: x += (len(term) - 4) * 0.075
        f = IFELSE(gate1=='and', AND, OR)
        s += f(gate_name, x=x, y=y, direction='down', inputs=len(term), output_length=0)
        if len(term) > 4: x += (len(term) - 4) * 0.075
        x += 1
        s += join_to_and(term, gate_name=gate_name)
    x += 0.75

    # Move OR gate down more if AND and/or OR gate is large
    y -= abs(len(terms)) * 0.15 + \
         max([len(term) for term in terms]) * 0.15
    s += "% ----- OR GATE\n"
    f = IFELSE(gate2=='or', OR, AND)
    s += f(name='OR', x=x, y=y, direction='right', inputs=len(terms), output_length=0.5)
    if len(terms) > 1:
        for i in range(len(terms)):
            if len(terms[i]) == 1:
                s += dottedbend('AND%s' % (i+1), 'OR.input %s' % (i+1))
            else:
                s += dottedbend('AND%s.output' % (i+1), 'OR.input %s' % (i+1))
    else:
        s += dottedbend('AND1', 'OR')

    return r"""
\begin{center}
\begin{tikzpicture}[circuit logic US]
%s
\end{tikzpicture}
\end{center}
""" % s


def SOP(vars, terms, space_saving_with_not_gate=False):
    # example: terms = [['x','y'], ['x', "z'"]] for xy + xz'
    #
    # space_saving_with_not_gate: If True, then the lines for literals
    #                           are equally spaces.
    #                           If False, then space is allocated for
    #                           each literal even when they are not
    #                           present. This means that the non-prime
    #                           literals are equally spaced vertically.
    return SOP_or_POS(gate1='and', gate2='or',
                      vars=vars, terms=terms,
                      space_saving_with_not_gate=space_saving_with_not_gate)


def POS(vars, terms, space_saving_with_not_gate=False):
    return SOP_or_POS(gate1='or', gate2='and',
                      vars=vars, terms=terms,
                      space_saving_with_not_gate=space_saving_with_not_gate)


def strexpr_to_vars_and_terms(expr, format='sop'):
    # If sop = "xyz + x'z", then [["x","y","z"],["x'","z"]] is returned.

    def terms_to_vars(terms):
        vars = [_.replace("'","") for _ in flatten(terms)]
        vars = removedup(vars)
        vars.sort()
        return vars

    def term_to_list(term):
        # xyz' -> ['x','y',"z'"]
        u = []
        for ch in term:
            if ch == "'":
                u[-1] = u[-1] + "'"
            else:
                u.append(ch)
        return u

    if format=='sop':
        terms = expr.split('+')
        terms = [term.strip() for term in terms]
        terms = [term_to_list(term) for term in terms]
        vars = terms_to_vars(terms)
    else:
        # (x + y)(x' + y')
        expr = expr[1:-1].replace(" ","").replace("+","")
        terms = expr[1:-1].split(")(")
        # (x + y)(x' + y') -> ["xy", "x'y'"]
        terms = [term_to_list(term) for term in terms]
        vars = terms_to_vars(terms)
    return vars, terms


def SOP2(sop, space_saving_with_not_gate=False):
    """ example: sop = "abc + a'bc'" """
    vars, terms = strexpr_to_vars_and_terms(sop)
    return SOP(vars, terms,
               space_saving_with_not_gate=space_saving_with_not_gate)

def POS2(sop, space_saving_with_not_gate=False):
    """ example: sop = "abc + a'bc'" """
    vars, terms = strexpr_to_vars_and_terms(sop, format="pos")
    return POS(vars, terms,
               space_saving_with_not_gate=space_saving_with_not_gate)


def rand_SOP(nchars=random.randrange(4,6),
             nterms=random.randrange(3,5),
             minlen=random.randrange(1,4),
             maxlen=random.randrange(5,9),
             sortterm=True):

    chars = list("abcdefghijklmnopqrstuvwxyz")[:nchars]

    exprlist = []
    for _ in range(nterms):
        random.shuffle(chars)
        length = random.randrange(minlen, maxlen+1)
        term = chars[:length] # a chunk of characters

        t = []
        for _ in term:
            prime_or_not = random.choice(["", "'"])
            t.append("%s%s" % (_, prime_or_not))
        term = t
        term.sort()
        term = ''.join(term)
        exprlist.append(term)
    expr = " + ".join(exprlist)
    return expr

#=============================================================================
# NEW STUFF HERE
#
# coordinates is "left" of the bounding box and not the bottomleft
# aspect ratio is preserved.
# So just need (x,y) and height
#=============================================================================
class LOGIC_GATE:
    def __init__(self,
                 x, y, h,
                 x0, y0, x1, y1,
                 aspect=1.2,
                 linecolor='black',
                 linewidth=0.04,
                 label='',
                 angle=None,
                 boundary=None,
                 inputs=None,
                 output=None,
                 ):
        if angle:
            t = angle
            p = (x, y)
            x0,y0 = rotate_about((x0, y0), p, t)
            x1,y1 = rotate_about((x1, y1), p, t)
            inputs = [rotate_about(p0, p, t) for p0 in inputs]
            output = rotate_about(output, p, t)
            boundary = [rotate_about(p0,p,t) for p0 in boundary]
        self.x = x
        self.y = y
        self.h = h
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.label = label
        self.linecolor = linecolor
        self.linewidth = linewidth
        self.angle = angle
        self.inputs_ = inputs
        self.output_ = output
        self.boundary_ = boundary
    def inputs(self):
        return self.inputs_
    def set_inputs(self, inputs):
        self.inputs_ = inputs
    def output(self):
        return self.output_
    def set_output(self, output):
        self.output_ = output
    def boundary(self):
        return self.boundary_
    def set_boundary(self, boundary):
        self.boundary_ = boundary

class LOGIC_BLOCK:

    def __init__(self,
                 x=0, y=0, h=3, w=2,
                 points={'in0':('',(0, 0.1)),
                         'out0':('',(0.1)),
                         },
                 s='',
                 linecolor='black',
                 linewidth='0.05cm',
                 ):
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.s = s
        self.linecolor=linecolor
        self.linewidth=linewidth
        self.points_ = {}

        for k,v in points.items():
            _, (x0,y0) = v
            self.points_[k] = (_, (x+x0,y+y0))

    def point(self, x):
        return self.points_[x][1]

    def __str__(self):
        s = ''
        x, y, w, h = self.x, self.y, self.w, self.h
        x0 = x; y0 = y;
        x1 = x+w; y1 = y+h;
        s_ = self.s
        linecolor = self.linecolor
        linewidth = self.linewidth

        s1 = ''
        for k,v in self.points_.items():
            label, (x_,y_) = v
            # check if point on left
            if x_ == x:
                anchor = 'west'
            elif x_ == x+w:
                anchor = 'east'
            elif y_ == y:
                anchor = 'south'
            else:
                anchor = 'north'

            if anchor=='east':
                s1 = r'\node[anchor=%s] at (%s,%s) {%s};' % \
                     (anchor, x_, y_, label)
            elif anchor=='west':
                s1 = r'\node[anchor=%s] at (%s,%s) {%s};' % \
                     (anchor, x_, y_, label)
            elif anchor=='north':
                s1 = r'\node[anchor=%s] at (%s,%s) {%s};' % \
                     (anchor, x_, y_, label)
            elif anchor=='south':
                s1 = r'\node[anchor=%s] at (%s,%s) {%s};' % \
                     (anchor, x_, y_, label)
            s += '\n%s\n' + s1

        s += '%s' % Rect(x0=x0, y0=y0, x1=x1, y1=y1,
                        linecolor=linecolor,
                        linewidth=linewidth.replace('cm',''),
                        innersep=0.4 * h/3.0, # WARNING: HARD CODED
                        s=r'\begin{center} %s \end{center}' % s_,
                         align='c',
                        )

        return s

#           +----------+
#           |          |
# (in0) - x |        s | - (out0)
#           |          |
#           |          |
# (in1) - y |        c | - (out1)
#           |          |
#           +----------+
class HALF_ADDER(LOGIC_BLOCK):
  def __init__(self,
               x=0, y=0, h=3,
               s='half adder',
               linecolor='black',
               linewidth='0.05cm',
               aspect=1.6
               ):

    w = h / aspect
    if w < 2:
        t = r"{\scriptsize %s}"
    else:
        t = r"{\small %s}"

    points = {}
    points['in0']  = (t % '$A$', (0, 0.75 * h))
    points['in1']  = (t % '$B$', (0, 0.25 * h))
    points['out0'] = (t % '$S$', (w, 0.75 * h))
    points['out1'] = (t % '$C$', (w, 0.25 * h))    
    LOGIC_BLOCK.__init__(self,
                         x=x, y=y, w=w, h=h,
                         s=t % s,
                         linecolor=linecolor,
                         linewidth=linewidth,
                         points=points)



  def __str__(self):
    return LOGIC_BLOCK.__str__(self)


class AND_GATE(LOGIC_GATE):
    def __init__(self,
                 name=None,          # pgf name
                 x=0, y=0, h=1,
                 inputs=2,
                 linecolor='black',
                 linewidth='0.04cm',
                 label=None,
                 angle=None,
                 ):
        """
              p6   p5 p4
              +-----
        ----->|    |\
              |    | |p3  dy/2 = radius of circle
        ----->|    |/
              +-----
              p0   p1 p2

        """
        aspect = 1.2 # Check ANSI
        x0 = x
        y0 = y - h/2.0
        x1 = x0 + 1.2
        y1 = y + h/2.0

        dy = float(y1 - y0)
        dx = float(x1 - x0)
        if float(dx)/dy != 1.2:
            # assume dy is correct -- i.e., the user chose the right
            # height to accomodate enough inputs
            x1 = x0 + aspect * dy
            dx = x1 - x0

        r = dy / 2.0
        d = dy / inputs
        inputs_ = []
        y_ = y0 + d/2.0
        for _ in range(inputs):
            inputs_.append((x0, round(y_,5))); y_ += d

        output_ = (x1 - r + r * 0.7, (y0 + y1) / 2.0)

        # Note that the boundary rect has actually
        # x1 - r + r * 0.7 for the x1-value
        p0 = (x0, y0)
        if x1 - r >= x0:
            p1 = (x1 - r, y0)
        else:
            p1 = (x1, y0)
        p2 = (x1, y0)
        p3 = (x1, y0 + r)
        p4 = (x1, y1)
        p5 = (x1 - r, y1)
        p6 = (x0, y1)
        boundary_ = [p0,p1,p2,p3,p4,p5,p6]

        LOGIC_GATE.__init__(self,
                            x=x, y=y, h=h,
                            x0=x0, y0=y0, x1=x1, y1=y1,
                            linecolor=linecolor,
                            linewidth=linewidth,
                            label=label,
                            angle=angle,
                            boundary=boundary_,
                            inputs=inputs_,
                            output=output_,
                            )

    def __str__(self):
        [p0,p1,p2,p3,p4,p5,p6] = self.boundary()
        s = str(p0) + ' -- ' + str(p1) + \
            ' ..controls ' + str(p2) + ' and ' + str(p4) + \
            ' .. ' + str(p5) + \
            ' -- ' + str(p6) + ' -- cycle'

        options = {}
        options['color'] = self.linecolor
        options['line width'] = self.linewidth
        options = ','.join(['%s=%s' % (k,v) for k,v in options.items()])
        s = r"\draw [%s] %s;" % (options, s)

        if self.label:
            x0, y0 = self.x0, self.y0
            x1, y1 = self.x1, self.y1
            x = (x0 + x1) / 3.0
            y = (y0 + y1) / 2.0
            s += '%s' % Rect(x0=x, y0=y, x1=x, y1=y, label=self.label,
                             linewidth=0)
        return s



class OR_GATE(LOGIC_GATE):
    def __init__(self,
                 name=None,          # pgf name
                 x=0, y=0, h=1,
                 inputs=2,
                 linecolor='black',
                 linewidth='0.04cm',
                 angle=None,
                 label=''
                 ):
        """
              p6   p5 p4
              +-----
        ----->|    |\
              |    | |p3  dy/2 = radius of circle
        ----->|    |/
              +-----
              p0   p1 p2

        """
        aspect = 1.2 # Check ANSI

        x0 = x
        y0 = y - h/2.0
        x1 = x0 + 1.2
        y1 = y + h/2.0

        dy = float(y1 - y0)
        dx = float(x1 - x0)
        if float(dx)/dy != 1.2:
            # assume dy is correct -- i.e., the user chose the right
            # height to accomodate enough inputs
            x1 = x0 + aspect * dy
            dx = x1 - x0

        r = dy / 2.0
        d = dy / inputs
        inputs_ = []
        y_ = y0 + d/2.0
        for _ in range(inputs):
            c = round(-(y_ - y0)*(y_ - y1) * 0.2, 6)
            if h <= 1: c += 0.05 * h
            inputs_.append((x0 + c, round(y_, 5)))
            y_ += d

        p0 = (x0, y0)
        if x1 - r >= x0:
            p1 = (x1 - r, y0)
        else:
            p1 = (x1, y0)
        p2 = (x1 - r, y0)
        p3 = (x1, y0 + r)
        p4 = (x1 - r, y1)
        p5 = (x1 - r, y1)
        p6 = (x0, y1)
        dy = p6[1] - p0[1]
        p8 = p0[0] + 1.0/6 * dy, p0[1] + 1.0 / 6 * dy
        p7 = p0[0] + 1.0/6 * dy, p0[1] + 5.0 / 6 * dy
        boundary_ = [p0,p1,p2,p3,p4,p5,p6,p7,p8]
        output_ = p3
        LOGIC_GATE.__init__(self,
                            x=x, y=y, h=h,
                            x0=x0, y0=y0, x1=x1, y1=y1,
                            linecolor=linecolor,
                            linewidth=linewidth,
                            label=label,
                            angle=angle,
                            boundary=boundary_,
                            inputs=inputs_,
                            output=output_,
                            )

    def __str__(self):
        [p0,p1,p2,p3,p4,p5,p6,p7,p8] = self.boundary()

        # two more points for the curved back
        """
              p6   p5 p4
              +-----
        ----->|p7  |\
              |    | |p3  dy/2 = radius of circle
        ----->|p8  |/
              +-----
              p0   p1 p2

        """
        s = str(p0) + ' .. controls ' + str(p2) +  ' .. ' + str(p3) + \
            ' ..controls ' + str(p4) + ' .. ' + str(p6) + \
            \
            ' ..controls ' + str(p7) + ' and ' + str(p8) + \
            ' .. ' + str(p0) + \
            ' -- cycle'

        options = {}
        options['color'] = self.linecolor
        options['line width'] = self.linewidth
        options = ','.join(['%s=%s' % (k,v) for k,v in options.items()])
        s = r"\draw [%s] %s;" % (options, s)

        if self.label:
            x0, y0 = self.x0, self.y0
            x1, y1 = self.x1, self.y1
            x = (x0 + x1) / 3.0
            y = (y0 + y1) / 2.0
            s += '%s' % Rect(x0=x, y0=y, x1=x, y1=y, label=self.label,
                             linewidth=0)

        return s

class NOT_GATE(LOGIC_GATE):
    def __init__(self,
                 name=None,          # pgf name
                 x=0, y=0, h=0.5,
                 inputs=1,
                 linecolor='black',
                 linewidth='0.04cm',
                 angle=None,
                 label=None
                 ):
        aspect = 1
        inputs_ = [(x, y)]
        r = 0.2 * h # radius of circle
        center = (x + h + r, y)
        output_ = (x + h + 2 * r, y)
        boundary_ = [(x, y - h/2.0), (x + h, y), (x, y + h/2.0),
                     (x, y - h/2.0),
                     ]
        x0 = x; y0 = y - h/2.0
        x1 = x + h + 2 * r; y1 = y + h/2.0

        LOGIC_GATE.__init__(self,
                            x=x, y=y, h=h,
                            x0=x0, y0=y0, x1=x1, y1=y1,
                            linecolor=linecolor,
                            linewidth=linewidth,
                            label=label,
                            angle=angle,
                            boundary=boundary_,
                            inputs=inputs_,
                            output=output_,
                            )
        self.center = center
        if angle:
            self.center = rotate_about(center, (x,y), angle)
        self.r = r

    def input(self):
        return self.inputs()[0]
    def __str__(self):
        linewidth = self.linewidth
        linecolor = self.linecolor
        a = Line(points=self.boundary(), linewidth=linewidth,
                 linecolor=linecolor)
        x, y = self.center
        r = self.r
        b = Circle(x=x, y=y, r=r,
                   linewidth=linewidth, linecolor=linecolor)
        return '%s\n%s' % (a, b)


class NAND_GATE(LOGIC_GATE):
    def __init__(self,
                 name=None,          # pgf name
                 x=0, y=0, h=1,
                 inputs=2,
                 linecolor='black',
                 linewidth='0.04cm',
                 label=None,
                 angle=None,
                 ):
        and_gate = AND_GATE(x=x, y=y, h=h,
                            inputs=inputs,
                            linecolor=linecolor,
                            linewidth=linewidth,
                            label=label,
                            angle=None)
        self.r = r = 0.2 * 0.5
        x0, y0 = and_gate.output()
        output_ = x0 + 2 * r + h * 0.05, y0
        if angle:
            output_ = rotate_about(output_, (x, y), angle)
        center = (x0 + r + h * 0.05, y0)
        if angle:
            center_ = rotate_about(center_, (x, y), angle)
        self.center = center
        and_gate = AND_GATE(x=x, y=y, h=h,
                            inputs=inputs,
                            linecolor=linecolor,
                            linewidth=linewidth,
                            label=label,
                            angle=angle)
        self.and_gate = and_gate
        self.output_ = output_
    def output(self):
        return self.output_
    def inputs(self):
        return self.and_gate.inputs()
    def __str__(self):
        linewidth = self.and_gate.linewidth
        linecolor = self.and_gate.linecolor
        s0 = str(self.and_gate)
        x,y = self.center
        r = self.r
        s1 = str(Circle(x=x, y=y, r=r,
                        linewidth=linewidth, linecolor=linecolor))
        return '%s\n%s\n' % (s0,s1)



class NOR_GATE(LOGIC_GATE):
    def __init__(self,
                 name=None,          # pgf name
                 x=0, y=0, h=1,
                 inputs=2,
                 linecolor='black',
                 linewidth='0.04cm',
                 label=None,
                 angle=None,
                 ):
        or_gate = OR_GATE(x=x, y=y, h=h,
                          inputs=inputs,
                          linecolor=linecolor,
                          linewidth=linewidth,
                          label=label,
                          angle=None)
        self.r = r = 0.2 * 0.5
        x0, y0 = or_gate.output()
        output_ = x0 + 2 * r, y0
        if angle:
            output_ = rotate_about(output_, (x, y), angle)
        center = (x0 + r, y0)
        if angle:
            center = rotate_about(center, (x, y), angle)
        self.center = center
        or_gate = OR_GATE(x=x, y=y, h=h,
                           inputs=inputs,
                           linecolor=linecolor,
                           linewidth=linewidth,
                           label=label,
                           angle=angle)
        self.or_gate = or_gate
        self.output_ = output_
    def output(self):
        return self.output_
    def inputs(self):
        return self.or_gate.inputs()
    def __str__(self):
        linewidth = self.or_gate.linewidth
        linecolor = self.or_gate.linecolor
        s0 = str(self.or_gate)
        x,y = self.center
        r = self.r
        s1 = str(Circle(x=x, y=y, r=r,
                        linewidth=linewidth, linecolor=linecolor))
        return '%s\n%s\n' % (s0,s1)


class XOR_GATE(OR_GATE):
    def __init__(self,
                 name=None,          # pgf name
                 x=0, y=0, h=1,
                 inputs=2,
                 linecolor='black',
                 linewidth='0.04cm',
                 angle=None,
                 label=''
                 ):
        or_gate = OR_GATE(name=name,
                          x=x, y=y, h=h,
                          inputs=inputs,
                          )
        [p0,p1,p2,p3,p4,p5,p6,p7,p8] = or_gate.boundary()
        p6 = p6[0] - h * 0.1, p6[1]
        p7 = p7[0] - h * 0.1, p7[1]
        p8 = p8[0] - h * 0.1, p8[1]
        p9 = p0[0] - h * 0.1, p0[1]
        p = [rotate_about(_, (x,y), angle) for _ in [p6,p7,p8,p9]]
        OR_GATE.__init__(self, name=name,
                         x=x, y=y, h=h,
                         inputs=inputs,
                         linecolor=linecolor,
                         linewidth=linewidth,
                         angle=angle,
                         label=label,
                         )
        self.extras = p

    def __str__(self):

        # The following works only in the default direction.
        # Need to apply rotation
        [p6,p7,p8,p9] = self.extras

        s0 = OR_GATE.__str__(self)
        # two more points for the curved back
        """
              p6   p5 p4
              +-----
        ----->|p7  |\
              |    | |p3  dy/2 = radius of circle
        ----->|p8  |/
              +-----
              p0   p1 p2

        """
        s = str(p6) + \
            \
            ' ..controls ' + str(p7) + ' and ' + str(p8) + \
            ' .. ' + str(p9)

        options = {}
        options['color'] = self.linecolor
        options['line width'] = self.linewidth
        options = ','.join(['%s=%s' % (k,v) for k,v in options.items()])
        s2 = r"\draw [%s] %s;" % (options, s)

        return '%s\n%s\n' % (s0, s2)

class POINT:
    """ There's some side effect in this class. The plot object cannot be named p.
    
plot = Plot() # not p
X = POINT(x=0, y=0, r=0, label=r'$x$', anchor='north')
plot += str(X)
    
    """
    
    def __init__(self,
                 x=0, y=0, r=0.08,
                 inputs=1,
                 linecolor='black',
                 label=None,
                 anchor='east',
                 name=None,          # pgf name
                 draw=True,
                 ):
        self.x_ = round(x,3)
        self.y_ = round(y,3)
        self.r_ = round(r,3)
        self.label = label
        self.anchor = anchor
        self.draw = draw
        self.name = name
        #if self.name == None:
        #    self.name = randstr()

    def input(self):
        return (self.x_, self.y_)
    def inputs(self):
        return [self.input()]
    def output(self):
        return (self.x_, self.y_)

    def x(self): return self.x_
    def y(self): return self.y_

    def __str__(self):
        x,y,r,name = self.x_, self.y_, self.r_, self.name
        label = self.label
        s = ''
        if self.draw and r > 0:
            s += '%s' % Circle(x=x, y=y, r=r, background='black', name=name)
        
        s1 = ''
        if label:
            if self.anchor=='east':
                s1 = r'\node[anchor=%s] at (%s,%s) {%s};' % \
                     (self.anchor, x - r, y, self.label)
            elif self.anchor=='west':
                s1 = r'\node[anchor=%s] at (%s,%s) {%s};' % \
                     (self.anchor, x + r, y, self.label)
            elif self.anchor=='north':
                s1 = r'\node[anchor=%s] at (%s,%s) {%s};' % \
                     (self.anchor, x, y - r, self.label)
            elif self.anchor=='south':
                s1 = r'\node[anchor=%s] at (%s,%s) {%s};' % \
                     (self.anchor, x, y + r, self.label)
            elif self.anchor=='flushtopleft':
                if name==None:
                    name = randstr()
                s1 = r'\coordinate (%s) at (%s,%s) {};' % (name, x, y)
                s1 += r'\node[above=0.0cm of %s.north west, anchor=south west, minimum width=0.01cm, inner sep=0cm] () {%s};' % (name, label)
                
            elif self.anchor=='flushtopright':
                if name==None:
                    name = randstr()
                s1 = r'\coordinate (%s) at (%s,%s) {};' % (name, x, y)
                s1 += r'\node[above=%scm of %s.north east, anchor=south east, minimum width=1cm, inner sep=0cm] () {%s};' % (r, name, label)
                
            elif self.anchor=='flushbottomleft':
                if name==None:
                    name = randstr()
                s1 = r'\coordinate (%s) at (%s,%s) {};' % (name, x, y)
                s1 += r'\node[below=%scm of %s.south east, anchor=north east, minimum width=1cm, inner sep=0cm] () {%s};' % (r, name, label)
                
            elif self.anchor=='flushbottomright':
                if name==None:
                    name = randstr()
                s1 = r'\coordinate (%s) at (%s,%s) {};' % (name, x, y)
                s1 += r'\node[below=%scm of %s.south west, anchor=north west, minimum width=1cm, inner sep=0cm] () {%s};' % (r, name, label)
                
            else: # need some adjustment if r is not 0
                s1 = r'\node[anchor=%s] at (%s,%s) {%s};' % \
                     (self.anchor, x, y, self.label)
                
        return '%s\n%s\n' % (s, s1)


class OUTPUT_POINT(POINT):
    def __init__(self,
                 x=0, y=0, r=0.08,
                 inputs=1,
                 linecolor='black',
                 label=None,
                 anchor='east',
                 gate=None,
                 output_length=2,
                 name=None,          # pgf name
                 draw=True,
                 ):
        """
        For now assume angle = 0
        """
        x,y = gate.output()
        x += output_length

        POINT.__init__(self,
                       name=None,
                       x=x, y=y,
                       inputs=inputs,
                       linecolor=linecolor,
                       label=label,
                       anchor=anchor,
                       draw=draw)
        self.gate = gate
        self.output_length = output_length
        p0 = x0,y0 = self.gate.output()
        p1 = x0 + self.output_length,y0
        self.opath = OrthogonalPath([p0,p1])

    def __str__(self):
        s0 = str(POINT.__str__(self))
        s1 = str(self.opath)
        return '%s\n%s\n' % (s0,s1)

class INPUT_POINT(POINT):
    def __init__(self,
                 x=0, y=0, r=0.08,
                 inputs=1,
                 linecolor='black',
                 label=None,
                 anchor='east',
                 gate=None,
                 input_index=0,
                 input_length=2,
                 name=None,          # pgf name
                 draw=True,
                 ):
        """
        For now assume angle = 0
        """
        x,y = gate.inputs()[input_index]
        x -= input_length

        POINT.__init__(self,
                       name=None,
                       x=x, y=y,
                       inputs=inputs,
                       linecolor=linecolor,
                       label=label,
                       anchor=anchor,
                       draw=draw)
        self.gate = gate
        self.input_length = input_length
        p0 = x0,y0 = self.gate.inputs()[input_index]
        p1 = x0 - self.input_length,y0
        self.opath = OrthogonalPath([p0,p1])

    def __str__(self):
        s0 = str(POINT.__str__(self))
        s1 = str(self.opath)
        return '%s\n%s\n' % (s0,s1)


class OrthogonalPath:
    """
    direction = 'hvh':
            +-------o
            |
            |
    o-------+

    direction = 'vh':
    +---------------o
    |
    |
    o
    
    The bend is at the middle
    """
    def __init__(self,
                 #
                 points=None,
                 #
                 gate0=None,
                 gate1=None, input_index=None,
                 #
                 direction='hvh', # vh
                 linewidth=0.04, linecolor='black',
                 endstyle='', arrowstyle='',
                 shifts=None):
        if gate1!=None and gate0!=None and input_index!=None:
            points = [gate0.output(), gate1.inputs()[input_index]]
        self.points = points[:]
        self.direction=direction.lower()
        self.linewidth = linewidth
        self.linecolor = linecolor
        self.endstyle = endstyle
        self.arrowstyle = arrowstyle
        self.shifts=shifts

    def __str__(self):
        points = self.points
        direction = self.direction
        linecolor = self.linecolor
        linewidth = self.linewidth
        endstyle = self.endstyle
        arrowstyle = self.arrowstyle
        shifts = self.shifts

        if direction == 'hvh':
            p0 = points[0]
            ps = [p0[:]]
            for i,p1 in enumerate(points[1:]):
                shift = 0
                if shifts and i < len(shifts):
                    shift = shifts[i]
                x0,y0 = p0
                x1,y1 = p1
                if y0 != y1:
                    x = (x0+x1)/2.0 + shift
                    x2,y2 = x, y0; p2=x2,y2
                    x3,y3 = x, y1; p3=x3,y3
                    ps.append(p2[:])
                    ps.append(p3[:])
                p0 = p1
            ps.append(points[-1])

        elif direction=='vh':
            # Assumes there are two values in points
            p0,p1 = points[0], points[1]
            p2 = (p0[0],p1[1])
            ps = [p0,p2,p1]

        s = ''
        s = '%s\n' % Line(points=ps,
                          linewidth=linewidth,
                          linecolor=linecolor,
                          endstyle=endstyle,
                          arrowstyle=arrowstyle,
                          )
        for p in ps[1:-1]:
            s += '%s\n' % POINT(x=p[0], y=p[1])
        return s

def layout(p, expr, G1, G2, font=None):
    # TODO: not-complemented literal if does not appear should not draw
    # lines: 
    #
    #  B -------+---------  << ERROR THIS IS DRAW EVEN WHEN B NOT PRESENT
    #           |
    #           +-NOT---
    #expr = [['a', 'b', 'c'], ["a'", 'b']]

    ALLGATES = {} # the expressions are used -- have to assume
    # expressions are unique!!!

    LAYER1_GATES = [] # Need this just for ordered layout of layer1 gates

    literals = []     # WARNING: this is a list of not-complemented literals
    notliterals = []
    for e in expr:
        for x in e:
            y = x.replace("'", "")
            if y not in literals:
                literals.append(y)
            if x.endswith("'"):
                if y not in notliterals:
                    notliterals.append(y)
    sorted(literals)

    dy = 2          # vertical distance between gates in layer 1
    dx = 0.3        # distance between vertical wires
    x0 = 0          # for inputs
    x1 = x0 + 1     # for not of inputs
    x4 = x1 + 2     # connection mesh
    x2 = x4 + 2 + (len(literals) + len(notliterals)) * dx # 1st layer of gates
    x3 = x2 + 1.2 + 4 + (len(expr)/2 - 1)*dx     # 2nd layer of gates

    # Level 2 gate
    h = IFELSE(len(expr)<=4, 1, len(expr)*0.3) # size of layer2 gate
    g2 = G2(x=x3, y=0, h=h, inputs=len(expr))
    ALLGATES[str(expr)] = g2
    p += str(g2)
    p += str(OUTPUT_POINT(gate=g2, output_length=1, label='$f$', anchor='west'))
    del h

    n = len(expr) # number of terms/factors
    maxy = (n - 1) / 2.0 * dy
    for i,e in enumerate(expr):
        # TODO: if len(e) is 1, use POINT
        if len(e) == 1:
            # USE POINT IF TERM HAS ONE LITERAL
            #g = G1(x=x2, y=maxy - i * dy, inputs=len(e)) # testing only
            #p += str(g) #testing only
            g = POINT(x=x2, y=maxy - i * dy, r=0, inputs=len(e))
        else:
            g = G1(x=x2, y=maxy - i * dy, inputs=len(e))
        ALLGATES[str(e)] = g
        LAYER1_GATES.append(g)
        p += str(g)

    opath = OrthogonalPath

    # Layout layer 1 gates. Join them to level 2 gate.
    # TODO: make a function
    i = 0
    j = len(expr) - 1
    shift = 0
    g1 = LAYER1_GATES # shorthand
    max_output_x = max([g.output()[0] for g in g1]) # max x of all output points of gates
    min_input_x = min([x for x,y in g2.inputs()])
    bend_x = (max_output_x + min_input_x) / 2.0  # when ortho path bends
    while i <= j:
        output_x = g1[i].output()[0]
        this_bend_x = (output_x + g2.inputs()[j][0]) / 2.0
        shift = -(this_bend_x - bend_x)
        p += str(opath(gate0=g1[i], gate1=g2, input_index=j, shifts=[shift]))

        output_x = g1[j].output()[0]
        this_bend_x = (output_x + g2.inputs()[i][0]) / 2.0
        shift = -(this_bend_x - bend_x)
        p += str(opath(gate0=g1[j], gate1=g2, input_index=i, shifts=[shift]))
        i += 1
        j -= 1
        shift -= dx
    del LAYER1_GATES

    # POINTS are the connection points joining inputs or not-inputs
    # to first layer of gates
    # POINTS["a"]
    # POINTS["a'"]
    POINTS = {}

    n = len(literals)
    maxy = (n-1)/2.0 * 1 # 1 is distance between literals
    for i, e in enumerate(literals):
        if font:
            label = r'{\%s $%s$}' % (font, e)
        else:
            label = r'{$%s$}' % (e)
        g = POINT(x=x0, y=maxy - i * 1, label=label)
        POINTS[e] = g
        p += str(g)

        if e in notliterals:
            notg = NOT_GATE(x=x1, y=maxy - i * 1 - 0.5)
            ALLGATES["%s'" % e] = notg
            p += str(notg)
            p += str(opath([g.output(), notg.input()]))

    # CONNECTION_POINTS and the points for joining
    # - literals to layer1 gates
    # - not gates to layer1 gates
    # DO NOT CREATE NOT-COMPLEMENTED CONNECTION POINT IF NOT PRESENT in expr
    CONNECTION_POINTS = {}
    x = x4 # make 2 better
    for i, e in enumerate(literals):

        # OMIT DRAWING IF e NOT PRESENT IN EXPR
        if any(e in _ for _ in expr):
            point = POINTS[e] # input for literal
            _,y = point.output()

            point1 = POINT(x, y)
            p += str(point1)
            CONNECTION_POINTS[e] = point1

            p += str(opath([point.output(), point1.input()]))
        
        x += 0.3

        # now for not-literal not gate
        e_prime = e + "'"
        if e_prime in ALLGATES.keys():
            notg = ALLGATES[e_prime]
            _,y = notg.output()

            point1 = POINT(x, y)
            CONNECTION_POINTS[e_prime] = point1
            p += str(point1)

            p += str(opath([notg.output(), point1.input()]))
            x += 0.3

    # Join literals/notliterals points to layer 1 gates
    for e in expr:
        g = ALLGATES[str(e)]
        for i,x in enumerate(e):
            point = CONNECTION_POINTS[x]
            p += str(opath([point.output(), g.inputs()[i]], direction='vh'))

    #p += Grid(x0=-2, y0=-maxy-1, x1=x3+2, y1=maxy+1)

if __name__ == "__main__":
    pass
    #print source2("A")
    #print source2("A'")
