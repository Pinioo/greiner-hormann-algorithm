ENTRY = 0
EXIT = 1

IN = 0
OUT = 1
ON = 2

def det(a, b, c):
    return a.x * b.y + a.y * c.x + b.x * c.y - b.y * c.x - a.y * b.x - a.x * c.y

class Vertex:
    def __init__(self, x, y, intersect=False, alpha=0):
        self.x = x
        self.y = y
        self.next = None
        self.prev = None
        self.intersect = intersect
        self.entry_exit = None
        self.neighbour = None
        self.alpha = alpha

    def next_vertex(self):
        to_return = self.next
        while to_return.intersect:
            to_return = to_return.next
        return to_return


class Polygon:
    def __init__(self):
        self.first = None

    def add_vertex(self, x, y):
        if self.first is None:
            self.first = Vertex(x, y)
            self.first.prev = self.first
            self.first.next = self.first
        else:
            new_vertex = Vertex(x, y)
            new_vertex.next = self.first
            new_vertex.prev = self.first.prev
            self.first.prev.next = new_vertex
            self.first.prev = new_vertex

    def insert_vertex(self, u, v, to_insert):
        curr = u
        while curr.next != v and to_insert.alpha < curr.alpha:
            curr = curr.next
        to_insert.next = curr.next
        to_insert.prev = curr
        curr.next.prev = to_insert
        curr.next = to_insert

    def rotate_list(self):
        curr = self.first
        while True:
            (curr.prev, curr.next) = (curr.next, curr.prev)
            curr = curr.prev
            if curr == self.first:
                break

    def test_location(self, vertex):
        curr = self.first
        next = curr.next_vertex()
        count = 0

        while True:
            if upper.y == lower.y:
                continue
            upper = max(curr, next, key=lambda v: v.y)
            lower = min(curr, next, key=lambda v: v.y)
            tmp_det = det(lower, upper, vertex)
            if tmp_det > 0 and (lower.y < vertex.y <= upper.y):
                count += 1
            elif tmp_det == 0:
                return ON
            curr = next
            next = next.next_vertex()
            if curr == self.first:
                break

        if count % 2 == 1:
            return IN
        else:
            return OUT


def det_intersections(poly1, poly2):
    p1_curr = poly1.first
    p1_next = p1_curr.next_vertex()
    while True:
        p2_curr = poly2.first
        p2_next = p2_curr.next_vertex()
        while True:
            inter = intersect(p1_curr, p1_next, p2_curr, p2_next)
            if inter is not None:
                ((x, y), alpha_p1, alpha_p2) = inter
                new_vertex_p1 = Vertex(x, y, intersect=True, alpha=alpha_p1)
                new_vertex_p2 = Vertex(x, y, intersect=True, alpha=alpha_p2)

                new_vertex_p1.neighbour = new_vertex_p2
                new_vertex_p2.neighbour = new_vertex_p1

                poly1.insert_vertex(p1_curr, p1_next, new_vertex_p1)
                poly2.insert_vertex(p2_curr, p2_next, new_vertex_p2)

            p2_curr = p2_next
            p2_next = p2_next.next_vertex()
            if p2_curr == poly2.first:
                break
        p1_curr = p1_next
        p1_next = p1_next.next_vertex()
        if p1_curr == poly1.first:
            break

def intersect(u1, u2, v1, v2):
    px = u1.x
    py = u1.y
    qx = v1.x
    qy = v1.y

    ry = u2.y - u1.y
    rx = u2.x - u1.x
    sy = v2.y - v1.y
    sx = v2.x - v1.x

    rxs = sy * rx - sx * ry
    if rxs == 0:
        return None

    alpha_u = ((qx - px) * sy - (qy - py) * sx) / rxs
    alpha_v = ((qx - px) * ry - (qy - py) * rx) / rxs

    if (0 < alpha_u < 1) and (0 < alpha_v < 1):
        x = px + alpha_u * rx
        y = py + alpha_u * ry
        return ((x, y), alpha_u, alpha_v)

    return None

def set_vertices(poly1, poly2):
    curr = poly1.first
    loc = poly2.test_location(curr)
    next_mode = ENTRY if loc == OUT else EXIT
    while True:
        if curr.intersection:
            curr.entry_exit = next_mode
            curr.neighbour.entry_exit = next_mode
            next_mode = (next_mode + 1) % 2
        curr = curr.next
        if curr == poly1.first:
            break

# Clipping algorithm based on article https://www.inf.usi.ch/hormann/papers/Greiner.1998.ECO.pdf
# By Grunter Greiner and Kai Hormann

def greiner_hormann(poly1, poly2, mode):
    poly2.rotate_list()
    det_intersections(poly1, poly2)
    set_vertices(poly1, poly2)
    # Core algorithm
    polygons_list = []
    curr = poly1.first
    while True:
        if curr.intersect:
            first_point = curr
            first_point.intersect = False
            first_point.neighbour.intersect = False
            new_poly = Polygon()
            new_poly.add_vertex(Vertex(curr.x, curr.y))
            act_mode = curr.entry_exit
            while True:
                if act_mode == ENTRY:
                    curr = curr.next
                else:
                    curr = curr.prev
                if curr == first_point or curr.neighbour == first_point:
                    break
                new_poly.add_vertex(Vertex(curr.x, curr.y))
                if curr.intersect:
                    curr.intersect = False
                    curr.neighbour.intersect = False
                    act_mode = (act_mode + 1) % 2
                    curr = curr.neighbour
            polygons_list.append(new_poly)
        curr = curr.next
        if curr == poly1.first:
            break
    return polygons_list
