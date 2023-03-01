from manim import *
import itertools  as it
from functools import reduce
import operator as op

class FourierCirclesScene(Scene):
    CONFIG = {
        "n_vectors": 10,
        "big_radius": 2,
        "colors": [
            BLUE_D,
            BLUE_C,
            BLUE_E,
            GREY_BROWN,
        ],
        "circle_style": {
            "stroke_width": 2,
        },
        "vector_config": {
            "buff": 0,
            "max_tip_length_to_length_ratio": 0.35,
            "fill_opacity": 0.75,
        },
        "circle_config": {
            "stroke_width": 1,
            "stroke_opacity": 0.75,
        },
        "base_frequency": 1,
        "slow_factor": 0.25,
        "center_point": ORIGIN,
        "parametric_function_step_size": 0.01,
        "drawn_path_color": YELLOW,
        "drawn_path_stroke_width": 4,
        "interpolate_config": [0, 1],
    }

    def __init__(self,**kwargs):
        for k in FourierCirclesScene.CONFIG:
            print('set',k,FourierCirclesScene.CONFIG[k])
            setattr(self,k,FourierCirclesScene.CONFIG[k])
        print('init:',self.__class__)
        super(FourierCirclesScene, self).__init__(**kwargs)

    def setup(self):
        self.slow_factor_tracker = ValueTracker(
            self.slow_factor
        )
        self.vector_clock = ValueTracker(0)
        self.vector_clock.add_updater(
            lambda m, dt: m.increment_value(
                self.get_slow_factor() * dt
            )
        )
        self.add(self.vector_clock)

    def get_slow_factor(self):
        return self.slow_factor_tracker.get_value()

    def get_vector_time(self):
        return self.vector_clock.get_value()

    def get_freqs(self):
        n = self.n_vectors
        all_freqs = list(range(n // 2, -n // 2, -1))
        all_freqs.sort(key=abs)
        return all_freqs

    def get_coefficients(self):
        return [complex(0) for x in range(self.n_vectors)]

    def get_color_iterator(self):
        return it.cycle(self.colors)

    def get_rotating_vectors(self, freqs=None, coefficients=None):
        vectors = VGroup()
        self.center_tracker = VectorizedPoint(self.center_point)

        if freqs is None:
            freqs = self.get_freqs()
        if coefficients is None:
            coefficients = self.get_coefficients()

        last_vector = None
        for freq, coefficient in zip(freqs, coefficients):
            if last_vector is not None:
                center_func = last_vector.get_end
            else:
                center_func = self.center_tracker.get_location
            vector = self.get_rotating_vector(
                coefficient=coefficient,
                freq=freq,
                center_func=center_func
            )
            vectors.add(vector)
            last_vector = vector
        return vectors

    # 计算每一个箭头状态
    def get_rotating_vector(self, coefficient, freq, center_func):
        vector = Vector(RIGHT, **self.vector_config)

        # 根据每个频率（箭头）的参数，计算其模长，也就是比重，反映到箭头大小的描画
        vector_scale = abs(coefficient)
        if (vector_scale>1):
            vector_scale = 1
        VMobject.scale(vector, vector_scale)

        # 根据每个频率（箭头）的参数，计算其相位，也就是和正实数轴夹角，反映到箭头方向的初始化
        if abs(coefficient) == 0:
            phase = 0
        else:
            phase = np.log(coefficient).imag
        vector.rotate(phase, about_point=ORIGIN)

        vector.freq = freq
        vector.coefficient = coefficient
        vector.center_func = center_func
        vector.add_updater(self.update_vector)
        return vector

    # 随时间变化，更新每个箭头起始点，和方向
    def update_vector(self, vector, dt):
        time = self.get_vector_time()
        coef = vector.coefficient
        freq = vector.freq
        phase = np.log(coef).imag

        vector.set_length(abs(coef))
        vector.set_angle(phase + time * freq * TAU)
        vector.shift(vector.center_func() - vector.get_start())
        return vector

    def get_circles(self, vectors):
        return VGroup(*[
            self.get_circle(
                vector,
                color=color
            )
            for vector, color in zip(
                vectors,
                self.get_color_iterator()
            )
        ])

    def get_circle(self, vector, color=BLUE):
        circle = Circle(color=color, **self.circle_config)
        circle.center_func = vector.get_start
        circle.radius_func = vector.get_length
        circle.add_updater(self.update_circle)
        return circle

    # 随时间变化，更新每个箭头相应圆心
    def update_circle(self, circle):
        circle.set_width(2 * circle.radius_func())
        circle.move_to(circle.center_func())
        return circle

    # 计算通过级数描绘得到的整个图形路径
    def get_vector_sum_path(self, vectors, color=YELLOW):
        coefs = [v.coefficient for v in vectors]
        freqs = [v.freq for v in vectors]
        center = vectors[0].get_start()

        # 函数随时间变化，根据时间抽样点的函数值，等于该时间所有箭头求和叠加效果，时间抽样间隔为0.001
        path = ParametricFunction(
            lambda t: center + reduce(op.add, [
                complex_to_R3(coef * np.exp(TAU * 1j * freq * t))
                for coef, freq in zip(coefs, freqs)
            ]),
            t_range=[0, 1, 0.001],
            color=color,
            dt =0.001,
        )
        return path

    # TODO, this should be a general animated mobect
    def get_drawn_path_alpha(self):
        return self.get_vector_time()

    # 将【通过级数描绘得到的整个图形路径】细分，根据当前播放时间，调整每一小段的宽度，表现渐变效果
    def get_drawn_path(self, vectors, stroke_width=None, fade_rate=0.2, **kwargs):
        if stroke_width is None:
            stroke_width = self.drawn_path_stroke_width
        path = self.get_vector_sum_path(vectors, **kwargs)
        broken_path = CurvesAsSubmobjects(path)
        broken_path.curr_time = 0
        start, end = self.interpolate_config

        def update_path(path, dt):
            alpha = self.get_drawn_path_alpha()
            n_curves = len(path)
            for a, sp in zip(np.linspace(0, 1, n_curves), path):
                b = (alpha - a)
                if b < 0:
                    width = 0
                else:
                    factor = interpolate(start, end, (1- (b % 1)))
                    width = stroke_width * factor
                sp.set_stroke(width=width)
            path.curr_time += dt
            return path

        broken_path.set_color(self.drawn_path_color)
        broken_path.add_updater(update_path)
        return broken_path

    # Computing Fourier series
    # i.e. where all the math happens
    # 关键函数，在此函数中计算各个频率（箭头）的参数
    def get_coefficients_of_path(self, path, n_samples=10000, freqs=None):
        if freqs is None:
            freqs = self.get_freqs()
        dt = 1 / n_samples
        ts = np.arange(0, 1, dt)
        # 输入矢量图形路径采样
        samples = np.array([
            path.point_from_proportion(t)
            for t in ts
        ])
        samples -= self.center_point
        # 各采样值转换为复数形式
        complex_samples = samples[:, 0] + 1j * samples[:, 1]

        # 针对每一个频率（箭头），
        # 计算f(t)*e^(-2*pi*i*n*t)对于t序列求和，
        # 数量图形采样值（复数形式）就是公式里的f(t)
        result = []
        for freq in freqs:
            riemann_sum = np.array([
                np.exp(-TAU * 1j * freq * t) * cs
                for t, cs in zip(ts, complex_samples)
            ]).sum() * dt
            result.append(riemann_sum)

        return result

# 画文字
class FourierOfPiSymbol(FourierCirclesScene):
    CONFIG = {
        "n_vectors": 201,
        "center_point": ORIGIN,
        "slow_factor": 0.05,
        "n_cycles": 1,
        "tex": "\\aleph_0",
        "start_drawn": True,
        "max_circle_stroke_width": 1,
    }

    def __init__(self,**kwargs):
        super(FourierOfPiSymbol, self).__init__(**kwargs)
        # super().__init__(**kwargs)
        for k in FourierOfPiSymbol.CONFIG:
            print('set',k,FourierOfPiSymbol.CONFIG[k])
            setattr(self,k,FourierOfPiSymbol.CONFIG[k])
        print('init:',self.__class__)

    # 正文开始
    def construct(self):
        # 各元素各就各位
        self.add_vectors_circles_path()
        # 视频描绘一个周期轮回
        for n in range(self.n_cycles):
            self.run_one_cycle()

    # 初始化个元素的函数，依次获取输入图形，计算参数，整理待描绘元素，放到场景中
    def add_vectors_circles_path(self):
        # 获取输入图形路径
        path = self.get_path()
        # 通过路径，计算各个频率（箭头）参数
        coefs = self.get_coefficients_of_path(path)

        for freq, coef in zip(self.get_freqs(), coefs):
            print(freq, "\t", coef)

        # 通过各个频率（箭头）参数，收集所有箭头元素，待描绘
        vectors = self.get_rotating_vectors(coefficients=coefs)
        # 通过各个箭头，收集相应圆圈，待描绘
        circles = self.get_circles(vectors)
        self.set_decreasing_stroke_widths(circles)

        # 通过各个箭头，准备实际能画出的路径，待描绘
        drawn_path = self.get_drawn_path(vectors)
        # 将时间提前设置为1，可以模拟前一轮描绘的路径残影
        if self.start_drawn:
            self.vector_clock.increment_value(1)

        #全员各就各位，请上舞台场景
        self.add(vectors)
        self.add(circles)
        self.add(drawn_path)

        self.vectors = vectors
        self.circles = circles
        self.path = path
        self.drawn_path = drawn_path

    def run_one_cycle(self):
        time = 1 / self.slow_factor
        self.wait(time)

    def set_decreasing_stroke_widths(self, circles):
        mcsw = self.max_circle_stroke_width
        for k, circle in zip(it.count(1), circles):
            circle.set_stroke(width=max(
                # mcsw / np.sqrt(k),
                mcsw / k,
                mcsw,
            ))
        return circles

    # 通过Tex获得PI图形的矢量路径
    def get_path(self):
        tex_mob =  MathTex(r"\pi")
        tex_mob.set_height(6)
        path = tex_mob.family_members_with_points()[0]
        path.set_fill(opacity=0)
        path.set_stroke(WHITE, 1)
        return path

# 画svg图
class FourierOfTrebleClef(FourierOfPiSymbol):
    CONFIG = {
        "n_vectors": 101,
        "slow_factor": 0.1,
        "run_time": 25,
        "start_drawn": True,
        "file_name": "./assets/svg_images/yinfu.svg",
        "height": 7.5,
    }

    def __init__(self,**kwargs):
        super(FourierOfTrebleClef, self).__init__(**kwargs)
        # super().__init__(**kwargs)
        for k in FourierOfTrebleClef.CONFIG:
            print('set',k,FourierOfTrebleClef.CONFIG[k])
            setattr(self,k,FourierOfTrebleClef.CONFIG[k])
        print('init:',self.__class__)

    # 获取SVG对象
    def get_shape(self):
        shape = SVGMobject(self.file_name)
        return shape

    # 获取SVG对象中的矢量路径
    def get_path(self):
        shape = self.get_shape()
        path = shape.family_members_with_points()[0]
        path.set_height(self.height)
        path.set_fill(opacity=0)
        path.set_stroke(WHITE, 0)
        return path

# 画音符
class ComplexFourierSeriesExample(FourierOfTrebleClef):
    CONFIG = {
        "slow_factor": 0.01, # 慢放倍数
        "file_name": "./assets/svg_images/yinfu2.svg", # 音符svg文件存放位置
        "run_time": 10,
        "n_vectors": 300, # 300个箭头
        "n_cycles": 2,
        "max_circle_stroke_width": 0.75,
        "drawing_height": 6,  # 调整音符在画面中的大小
        "center_point": RIGHT*0.5, # 调整音符在画面中的位置
        "top_row_center": ORIGIN,
        "top_row_label_y": 2,
        "top_row_x_spacing": 0.0,
        "top_row_copy_scale_factor": 0.9,
        "start_drawn": True,
        "plane_config": {
            "axis_config": {"unit_size": 2},
            "x_range": [-2.5,2.5],
            "y_range": [-1.25,1.25],
            "background_line_style": {
                "stroke_width": 1,
                "stroke_color": GREY_B,
            },
        },
        "top_rect_height": 2.5,
    }

    def __init__(self,**kwargs):
        super(ComplexFourierSeriesExample, self).__init__(**kwargs)
        # super().__init__(**kwargs)
        for k in ComplexFourierSeriesExample.CONFIG:
            print('set',k,ComplexFourierSeriesExample.CONFIG[k])
            setattr(self,k,ComplexFourierSeriesExample.CONFIG[k])
        print('init:',self.__class__)

    def construct(self):
        self.add_vectors_circles_path()
        self.circles.set_stroke(opacity=0.5)
        self.run_one_cycle()

    def get_path(self):
        path = super().get_path()
        path.set_height(self.drawing_height)
        path.shift(UP*0.025)
        return path

    # 由于采样，还有计算精度等问题，描绘出来的图形路径，和所有箭头叠加的终点会有一点距离
    # 通过此函数补足这最后一个尾巴
    def get_path_end(self, vectors, stroke_width=None, **kwargs):
        if stroke_width is None:
            stroke_width = self.drawn_path_st
        # 描绘出来的图形路径整体
        full_path = self.get_vector_sum_path(vectors, **kwargs)

        # 待描绘的最后一个尾巴
        path = VMobject()
        path.set_stroke(
            self.drawn_path_color,
            stroke_width
        )

        def update_path(p):
            alpha = self.get_vector_time() % 1
            # 把图形路径整体的最后一小段的效果复制出来
            p.pointwise_become_partial(
                full_path,
                np.clip(alpha - 0.01, 0, 1),
                np.clip(alpha, 0, 1),
            )
            # 把这一小段的最终点，移动到箭头叠加得到的终点，使线条和箭头相触
            p.get_points()[-1] = vectors[-1].get_end()

        path.add_updater(update_path)
        return path

    def get_drawn_path_alpha(self):
        return super().get_drawn_path_alpha() - 0.002

    # 最终画的时候，图形路径和尾巴一起画
    def get_drawn_path(self, vectors, stroke_width=2, **kwargs):
        odp = super().get_drawn_path(vectors, stroke_width, **kwargs)
        return VGroup(
            odp,
            self.get_path_end(vectors, stroke_width, **kwargs),
        )