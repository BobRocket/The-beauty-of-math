from manim import *
import pymunk as pm
import random

class PhyCircle(Circle):
    def __init__(self,
                 radius: float = None,
                 Color=RED,
                 velocity=(0, 0),
                 elasticity=0.8,
                 density=1,
                 pos=(0, 0),
                 **kwargs, ):
        super().__init__(radius=radius, color=Color, **kwargs)

        # 创建刚体小球（形状，弹性，密度），设置初始速度，位置
        mass = 5
        inertia = pm.moment_for_circle(mass, 0, radius, (0,0))
        self.body = pm.Body(mass, inertia)
        self.body.velocity = velocity
        self.body.position = pos[0], pos[1]

        self.shape = pm.Circle(
            self.body,
            radius,
            (0,0))
        self.shape.elasticity = elasticity
        self.shape.density = density

        # 更新位置描绘
        def simulate(b):
            x, y = b.body.position
            b.move_to(x*RIGHT + y*UP)
        self.add_updater(simulate)

class BrownianMovement(Scene):
    def construct(self):
        # 创建物理计算的空间，重力为0
        self.space = pm.Space()
        self.space.gravity = (0, 0)

        self.unvisible_balls = []
        self.visible_balls = []

        # 创建物理空间的固定边框（方形空间）
        self.setup_lines()

        # 创建6000个半透明小球，随机位置，随机速度，弹性为1，全反弹
        for num in range(6000):
            posX,posY = (5.5 * (random.random()-0.5), 5.5 * (random.random()-0.5))
            VelocityX,VelocityY = ((random.random()-0.5), (random.random()-0.5))
            phy_circle = PhyCircle(radius=0.02,
                                   elasticity=1,
                                   pos=(posX,posY),
                                   velocity=(VelocityX,VelocityY)).set_fill(TEAL_E, opacity=0.4).set_stroke(TEAL_E,width=0.1,opacity=0.4)
            self.space.add(phy_circle.body, phy_circle.shape)
            self.add(phy_circle)

        # 创建600个蓝色小球，聚集在空间内中上部，初始速度向下，弹性为1，全反弹
        for num in range(600):
            posX,posY = (0.3 * (random.random()-0.5), 0.3 * random.random()+2.2)
            phy_circle = PhyCircle(radius=0.02,
                                   elasticity=1,
                                   pos=(posX,posY),
                                   velocity=(0,-2.5)).set_fill(BLUE_C, opacity=0.8).set_stroke(BLUE_C, width=0.1, opacity=0.8)
            self.space.add(phy_circle.body, phy_circle.shape)
            self.add(phy_circle)

        # 画一个方形，用于展示物理空间边框
        square = Square(5.6).set_stroke(WHITE,width = 2,opacity = 1)
        self.add(square)

        self.wait(2)

        # 每帧更新计算五次物理迭代
        def step(dt):
            step_count = 5
            for n in range(step_count):
                self.space.step(dt/step_count/3)

        self.add_updater(step)

        # 一共生成50s动画
        time_tracker = ValueTracker(0)
        self.play(time_tracker.animate(run_time = 50).set_value(10))


    # 方形空间，固体边框
    # 边框弹性为1，全反弹
    # 边框摩擦力为0.1，非常小
    def setup_lines(self):
        x,y = (6, 6)
        x,y = (x/2,y/2)
        static_body = pm.Body(body_type=pm.Body.STATIC)
        static_lines = [pm.Segment(static_body, (-x,y), (-x,-y), 0.2),
                        pm.Segment(static_body, (-x,-y), (x,-y), 0.2),
                        pm.Segment(static_body, (x,-y), (x,y), 0.2),
                        pm.Segment(static_body, (x,y), (-x,y), 0.2)]
        for line in static_lines:
            line.elasticity = 1
            line.friction = 0.1

        self.space.add(static_body,*static_lines)
        self.static_lines = static_lines 