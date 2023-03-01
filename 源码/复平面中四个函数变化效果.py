from manim import *

class complex_plane_transformation(Scene):
    def construct(self):
        frame_width = config["frame_width"]
        frame_height = config["frame_height"]
        frame_width = round(frame_width)
        frame_height = round(frame_height)

        #通过画直线，创建一个复平面效果，用于z'=z^2和z'=z^3这两种变换动画，这里的直线是灰白色的
        self.add_transformable_plane()
        #用manim自带复平面，用于z'=e^z和z'=1/z这两种变换动画，这里的直线是蓝色的
        plane_complex = ComplexPlane(
            x_range=(-frame_width, frame_width, 0.6),
            y_range=(-frame_height, frame_height, 0.6),
            x_length=2*frame_width,
            y_length=2*frame_height,
        )
        self.add(plane_complex)
        plane = self.plane
        plane_ref = plane.copy()

        #创建可变化的幂的数字
        power_value = ValueTracker(1)

        self.wait(3)

        #函数z'=z^x
        def zz(p):
            p.become(plane_ref.copy().apply_complex_function(
                lambda x: (x**(power_value.get_value()))
            ))
        plane.add_updater(zz)
        #播放幂从1变成2的动画效果（z'=z^2）
        self.play(power_value.animate.set_value(2), run_time=3, rate_functions=rush_from)
        self.wait(0.5)
        #幂恢复成1的动画效果
        self.play(power_value.animate.set_value(1), run_time=3, rate_functions=rush_from)
        self.wait(0.5)

        #设置manim自带复平面的复归效果点
        plane_complex.save_state()
        plane_complex.prepare_for_nonlinear_transform()

        #播放复平面变化成z'=e^z的动画效果
        self.play(plane_complex.animate.apply_complex_function(
                lambda x: (np.exp(x))
            ), run_time=3, rate_functions=rush_from)
        self.wait(0.5)
        #把复平面恢复到复归点
        self.play(plane_complex.animate.restore(), run_time=3, rate_functions=rush_from)
        self.wait(0.5)

        #播放复平面变化成z'=1/z的动画效果
        self.play(plane_complex.animate.apply_complex_function(
                lambda x: (x**(-1))
            ), run_time=3, rate_functions=rush_from)
        self.wait(0.5)
        #把复平面恢复到复归点
        self.play(plane_complex.animate.restore(), run_time=3, rate_functions=rush_from)
        self.wait(0.5)

        #播放幂从1变成3的动画效果（z'=z^3）
        self.play(power_value.animate.set_value(3), run_time=3, rate_functions=rush_from)
        self.wait(0.5)
        #幂恢复成1的动画效果
        self.play(power_value.animate.set_value(1), run_time=3, rate_functions=rush_from)
        self.wait(0.5)
        plane.remove_updater(zz)

        self.wait(3)

    #画直线，创建一个复平面效果的函数
    def add_transformable_plane(self, **kwargs):
        frame_width = config["frame_width"]
        frame_height = config["frame_height"]
        frame_width = round(frame_width)
        frame_height = round(frame_height)

        #逐一画出第一象限的每一根横线和直线
        self.plane = self.get_dense_grid()
        #比原点要网右上偏一点点，视觉上看不出来，
        #主要是为了做动画的时候可以保证这些线上的所有点可以符合第一象限内的各点函数变化效果，排除manim计算时原点和轴线出现不想要的动画效果
        self.plane.next_to(ORIGIN, UP+RIGHT, buff = 0.01)
        #延Y轴对称复制出第二象限的直线
        self.plane.add(self.plane.copy().rotate(np.pi, axis=UP,about_point=ORIGIN))
        #延X轴对称复制出第三/四象限的直线
        self.plane.add(self.plane.copy().rotate(np.pi, axis=RIGHT,about_point=ORIGIN))
        #用白色画出X轴正轴，负轴，Y轴正轴，负轴本身，照例要偏一点点，
        #正轴负轴分开画，以及偏离0.01都是为了使manim计算函数变化动画时可以正确处理每一条直线的效果
        self.plane.add(
            Line(ORIGIN+0.01, frame_width*RIGHT, color = WHITE),
            Line(ORIGIN+0.01, frame_height*UP, color = WHITE),
            Line(ORIGIN+0.01, -frame_width*RIGHT, color = WHITE),
            Line(ORIGIN+0.01, -frame_height*UP, color = WHITE),
        )

        self.add(self.plane)

    #画出第一象限的每一根横线和直线的函数
    def get_dense_grid(self, step_size = 1.2):
        frame_width = config["frame_width"]
        frame_height = config["frame_height"]
        frame_width = round(frame_width)
        frame_height = round(frame_height)

        #用epsilon排除x轴和y轴本身，轴线不在此函数内画
        epsilon = 0.01
        #各个线按照规定的间隔准备好数据
        x_range = np.arange(
            0,
            frame_width,
            step_size
        )
        y_range = np.arange(
            0,
            frame_height,
            step_size
        )

        #画竖线
        vert_lines = VGroup(*[
            Line(
                ORIGIN,
                1*UP*frame_height,
            ).shift(x*RIGHT)
            for x in x_range
            if abs(x) > epsilon
        ])
        #复制一套，坐标网格更密集一倍
        dense_vert_lines = vert_lines.copy().shift(0.5*step_size*LEFT)

        #画横线
        horiz_lines = VGroup(*[
            Line(
                ORIGIN,
                1*RIGHT*frame_width,
            ).shift(y*UP)
            for y in y_range
            if abs(y) > epsilon
        ])
        #复制一套，坐标网格更密集一倍
        dense_horiz_lines = horiz_lines.copy().shift(0.5*step_size*DOWN)

        #全部放在一个VGroup里
        dense_grid = VGroup(horiz_lines, vert_lines,dense_vert_lines,dense_horiz_lines)

        #设置颜色和线宽
        vert_lines.set_stroke(color = GRAY, width = 3)
        horiz_lines.set_stroke(color = GRAY, width = 3)
        dense_vert_lines.set_stroke(color = GRAY, width = 3)
        dense_horiz_lines.set_stroke(color = GRAY, width = 3)

        return dense_grid 