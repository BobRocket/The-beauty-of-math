from manim import *
import math
import drawSvg as draw
from drawSvg import Drawing
from hyperbolic import euclid, util
from hyperbolic.poincare.shapes import *
from hyperbolic.poincare import Transform
from hyperbolic.poincare.util import radialEuclidToPoincare, radialPoincareToEuclid, \
                                     poincareToEuclidFactor, triangleSideForAngles
import hyperbolic.tiles as htiles

P1_define = 4
P2_define = 3
q_define = 3
depth_define = 6
class TileDecoratorFish(htiles.TileDecoratorPolygons):
    def __init__(self, p1=P1_define, p2=P2_define, q=q_define):
        theta1, theta2 = math.pi*2/p1, math.pi*2/p2
        phiSum = math.pi*2/q
        r1 = triangleSideForAngles(theta1/2, phiSum/2, theta2/2)
        r2 = triangleSideForAngles(theta2/2, phiSum/2, theta1/2)
        tGen1 = htiles.TileGen.makeRegular(p1, hr=r1)
        tGen2 = htiles.TileGen.makeRegular(p2, hr=r2)

        t1 = tGen1.centeredTile()
        t2 = tGen2.placedAgainstTile(t1, side=-1)
        t3 = tGen1.placedAgainstTile(t2, side=-1)
        pointBase = t3.vertices[-1]
        points = [Transform.rotation(deg=i*360/p1).applyToPoint(pointBase)
                  for i in range(p1)]
        vertices = t1.vertices

        edges = []
        for i, point in enumerate(points):
            v1 = vertices[i]
            v2 = vertices[(i+1)%p1]
            edge = Hypercycle.fromPoints(*v1, *v2, *point, segment=True, excludeMid=True)
            edges.append(edge)
        edgePoly = Polygon(edges=edges, vertices=vertices)

        origin = Point(0,0)
        corner = Point.fromHPolar(r1, theta=0)
        corner2 = Transform.rotation(rad=theta1).applyToPoint(corner)
        center = Point.fromHPolar(r2, theta=math.pi-phiSum/2)
        center = Transform.translation(corner).applyToPoint(center)
        poly = Polygon.fromVertices((origin, corner, center, corner2))
        desc = poly.makeRestorePoints()
        descs = [Transform.rotation(deg=i*360/p1).applyToList(desc)
                 for i in range(p1)]

        super().__init__(edgePoly, polyDescs=descs)
        self.p1 = p1
        self.p2 = p2
        self.colors = [TEAL_B, BLUE_C, BLUE_D, BLUE_E, YELLOW, TEAL]
    def toDrawables(self, elements, tile=None, layer=0, **kwargs):
        if tile is None:
            trans = Transform.identity()
            codes = range(self.p1)
        else:
            trans = tile.trans
            codes = [side.code[1] for side in tile.sides]
        polys = [Polygon.fromRestorePoints(trans.applyToList(desc))
                 for desc in self.polyDescs]
        ds = []
        if layer == 0:
            for i, poly in enumerate(polys[1:]):
                color = self.colors[codes[i]]
                d = poly.toDrawables(elements, fill=color, opacity=0.5, **kwargs)
                ds.extend(d)
        # if layer == 1:
        #     dLast = polys[0].toDrawables(elements, hwidth=0.1, fill='black', **kwargs)
        #     ds.extend(dLast)
        # if layer == 2:
        #     for i, poly in enumerate(polys[0:]):
        #         d = poly.toDrawables(elements, hwidth=0.01, fill='black', **kwargs)
        #         ds.extend(d)
        return ds

class TileLayoutFish(htiles.TileLayout):
    def calcGenIndex(self, code):
        ''' Override in subclass to control which type of tile to place '''
        if code == 0 or code == 1:
                return code
        index, color, cw = code
        return index
    def calcTileTouchSide(self, code, genIndex):
        ''' Override in subclass to control tile orientation '''
        return 0
    def calcSideCodes(self, code, genIndex, touchSide, defaultCodes):
        ''' Override in subclass to control tile side codes '''
        p = len(defaultCodes)
        if code == 0 or code == 1:
            c = (code+1) % 2
            if p % 2 == 0:
                return ((c,0,1),(c,1,0))*(p//2)
            else:
                return ((c,0,1),(c,1,2),(c,2,0))*(p//3)
        index, color, otherColor = code
        c = (index+1) % 2
        # 0=yellow, 1=green, 2=red, 3=blue
        if index == 1:
            newColors = {
                (0,1): (0,2,3),
                (1,0): (1,3,2),
                (0,2): (0,3,1),
                (2,0): (2,1,3),
                (0,3): (0,1,2),
                (3,0): (3,2,1),
                (1,2): (1,0,3),
                (2,1): (2,3,0),
                (1,3): (1,2,0),
                (3,1): (3,0,2),
                (2,3): (2,0,1),
                (3,2): (3,1,0),
            }[(color, otherColor)] * 10
        elif index == 0:
            newColors = {
                (0,1): (0,3,0,3),  # 0,1,2
                (1,2): (1,3,1,3),
                (2,0): (2,3,2,3),
                (0,2): (0,1,0,1),  # 0,2,3
                (2,3): (2,1,2,1),
                (3,0): (3,1,3,1),
                (0,3): (0,2,0,2),  # 0,3,1
                (3,1): (3,2,3,2),
                (1,0): (1,2,1,2),
                (1,3): (1,0,1,0),  # 1,3,2
                (3,2): (3,0,3,0),
                (2,1): (2,0,2,0),
            }[(color, otherColor)] * 10
        else:
            assert False
        newColors = newColors[:p]
        codes = [(c,newColor,newColors[(i+1)%len(newColors)])
                for i, newColor in enumerate(newColors)]
        return codes

class PoincareDisk(Scene):
    def construct(self):
        p1 = P1_define
        p2 = P2_define
        q = q_define
        rotate = 0
        depth = depth_define

        theta1, theta2 = math.pi*2/p1, math.pi*2/p2
        phiSum = math.pi*2/q
        r1 = triangleSideForAngles(theta1/2, phiSum/2, theta2/2)
        r2 = triangleSideForAngles(theta2/2, phiSum/2, theta1/2)

        tGen1 = htiles.TileGen.makeRegular(p1, hr=r1, skip=1)
        tGen2 = htiles.TileGen.makeRegular(p2, hr=r2, skip=1)

        decorator1 = TileDecoratorFish(p1, p2, q)

        tLayout = TileLayoutFish()
        tLayout.addGenerator(tGen1, ((0,1)*10)[:p1], decorator1)
        tLayout.addGenerator(tGen2, ((0,1,2)*10)[:p2], htiles.TileDecoratorNull())
        startTile = tLayout.startTile(code=0,rotateDeg=rotate)


        p0_tracker = ValueTracker(0)
        p1_tracker = ValueTracker(1)
        deg_tracker = ValueTracker(0)
        theta_tracker = ValueTracker(-PI)

        p0 = Point.fromHPolar(p0_tracker.get_value(), theta=theta_tracker.get_value())
        p1 = Point.fromHPolar(p1_tracker.get_value(), deg=0)
        transToOrigin = Transform.translation(p0,p1)
        startTile = startTile.makeTransformed(transToOrigin)
        tiles = tLayout.tilePlane(startTile, depth=depth)

        d = Drawing(2, 2, origin='center')
        d.draw(euclid.shapes.Circle(0, 0, 1), fill=BLUE_E)
        for tile in tiles:
            d.draw(tile, layer=0)
        d.setRenderSize(w=400)
        SVGstring = d.asSvg()
        with open("test_svg.svg", 'w') as file:
            file.write(SVGstring)

        self.lastsvg = SVGMobject("test_svg.svg").scale(3)
        self.add(self.lastsvg)


        self.lastp0 = p0_tracker.get_value()
        self.lastp1 = p1_tracker.get_value()
        self.lastdeg = deg_tracker.get_value()

        self.wait(2)
        def svgupdate(dt):

            if(self.lastp0 != p0_tracker.get_value()
                or self.lastp1 != p1_tracker.get_value()
                or self.lastdeg != deg_tracker.get_value()):
                p0 = Point.fromHPolar(p0_tracker.get_value(), deg=deg_tracker.get_value())
                p1 = Point.fromHPolar(p1_tracker.get_value(), deg=0)
                transToOrigin = Transform.translation(p0,
                                                    p1)
                startTile = tLayout.startTile(code=0,rotateDeg=rotate)
                startTile = startTile.makeTransformed(transToOrigin)
                tiles = tLayout.tilePlane(startTile, depth=depth)

                d = Drawing(2, 2, origin='center')
                d.draw(euclid.shapes.Circle(0, 0, 1), fill=BLUE_E)
                for tile in tiles:
                    d.draw(tile, layer=0)
                d.setRenderSize(w=400)
                SVGstring = d.asSvg()
                with open("test_svg.svg", 'w') as file:
                    file.write(SVGstring)
                file.close()

                newsvg = SVGMobject("test_svg.svg").scale(3)
                self.add(newsvg)
                self.remove(self.lastsvg)
                self.lastsvg = newsvg

        self.add_updater(svgupdate)
        self.play(p0_tracker.animate(run_time=2).set_value(0.5), rate_func=smooth)
        self.wait(0.3)
        self.play(p0_tracker.animate(run_time=2).set_value(-0.5), rate_func=smooth)
        self.wait(0.3)
        self.play(deg_tracker.animate(run_time=4.3).set_value(450), rate_func=smooth)
        self.wait(0.3)
        self.play(p0_tracker.animate(run_time=2).set_value(0.5), rate_func=smooth)
        self.wait(0.3)
        self.play(p0_tracker.animate(run_time=2).set_value(-0.5), rate_func=smooth)
        self.wait(0.3)
        self.play(deg_tracker.animate(run_time=4.3).set_value(0), rate_func=smooth)
        self.wait(2.3) 