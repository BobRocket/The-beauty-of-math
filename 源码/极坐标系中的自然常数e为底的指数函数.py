from manim import *

class exp_visualize(Scene):
    def construct(self):
        #添加极坐标系
        polarplane_pi = PolarPlane(
            azimuth_units="PI radians",
            size=10,
            azimuth_label_font_size=33.6,
            radius_config={"font_size": 1},
            radius_max=1,
            radius_step=1,
            background_line_style = {"stroke_opacity": 0}
        ).add_coordinates()

        #再准备一个笛卡尔坐标系
        number_place = NumberPlane()

        #在极坐标中准备自然常数e为底的指数函数曲线
        exp_graph = polarplane_pi.plot_polar_graph(lambda x: np.exp(x),theta_range=[-4.0*PI,8.0*PI])
        exp_graph.set_stroke([GREEN, BLUE, BLUE_E])
        graph_template = exp_graph.copy()
        graph_template.set_stroke(width=0)
        polarplane_pi.add(graph_template)
        self.add(polarplane_pi)


        #在笛卡尔坐标系中描绘极坐标系的经线，这十条直线是静止不动的
        line0 = number_place.plot(lambda x: 0, color=WHITE, stroke_width=2)
        line1 = number_place.plot(lambda x: np.tan(np.pi*0.1)*x, color=BLUE, stroke_width=2)
        line2 = number_place.plot(lambda x: np.tan(np.pi*0.2)*x, color=BLUE, stroke_width=2)
        line3 = number_place.plot(lambda x: np.tan(np.pi*0.3)*x, color=BLUE, stroke_width=2)
        line4 = number_place.plot(lambda x: np.tan(np.pi*0.4)*x, color=BLUE, stroke_width=2)
        line5 = Line(DOWN*5,UP*5, color=WHITE, stroke_width=2)
        line6 = number_place.plot(lambda x: np.tan(np.pi*0.6)*x, color=BLUE, stroke_width=2)
        line7 = number_place.plot(lambda x: np.tan(np.pi*0.7)*x, color=BLUE, stroke_width=2)
        line8 = number_place.plot(lambda x: np.tan(np.pi*0.8)*x, color=BLUE, stroke_width=2)
        line9 = number_place.plot(lambda x: np.tan(np.pi*0.9)*x, color=BLUE, stroke_width=2)
        self.add(line0,line1,line2,line3,line4,line5,line6,line7,line8,line9)

        #极坐标放大100倍
        self.play(polarplane_pi.animate.apply_function(lambda p: p*100.0),run_time=3,rate_functions=smooth)

        #为指数函数曲线准备动画刷新效果：根据渲染时间逐渐画出整个曲线
        curr_time = self.renderer.time
        exp_graph.add_updater(lambda m: m.pointwise_become_partial(
            graph_template, 0.0, (self.renderer.time-curr_time)/36 ,
        ))

        #指数函数曲线动画过程中，为曲线顶端描画一个圆点
        dot = Dot(color=BLUE_B, radius=0.04)
        dot.add_updater(lambda d: d.move_to(exp_graph.get_end()))

        #把指数函数曲线和圆点添加到场景中
        self.add(exp_graph, dot)

        #准备八组圆环，用于表现极坐标系的纬线
        #（由于极坐标缩放后，圆环位置不是exp对应的数值位置，所以以下这些位置是动作制作过程中试出来的）
        r_circles1 = np.arange(-1, 3, 0.5 )
        r_circles2 = np.arange(3, 3, 0.5 )
        r_circles3 = np.arange(3, 4, 0.5 )
        r_circles4 = np.arange(3, 6, 0.5 )
        r_circles5 = np.arange(3, 7, 0.5 )
        r_circles6 = np.arange(4, 8, 0.5 )
        r_circles7 = np.arange(5, 9, 0.5 )
        r_circles8 = np.arange(3, 9, 0.5 )
        plane_circles1 = VGroup(*[Circle(np.exp(x)) for x in r_circles1]).set_stroke(width=2,color=BLUE)
        plane_circles2 = VGroup(*[Circle(np.exp(x)) for x in r_circles2]).set_stroke(width=2,color=BLUE)
        plane_circles3 = VGroup(*[Circle(np.exp(x)) for x in r_circles3]).set_stroke(width=2,color=BLUE)
        plane_circles4 = VGroup(*[Circle(np.exp(x)) for x in r_circles4]).set_stroke(width=2,color=BLUE)
        plane_circles5 = VGroup(*[Circle(np.exp(x)) for x in r_circles5]).set_stroke(width=2,color=BLUE)
        plane_circles6 = VGroup(*[Circle(np.exp(x)) for x in r_circles6]).set_stroke(width=2,color=BLUE)
        plane_circles7 = VGroup(*[Circle(np.exp(x)) for x in r_circles7]).set_stroke(width=2,color=BLUE)
        plane_circles8 = VGroup(*[Circle(np.exp(x)) for x in r_circles8]).set_stroke(width=2,color=BLUE)


        #添加纬线，并对极坐标整体一边做一组组缩小动画
        polarplane_pi.add(plane_circles1)
        polarplane_pi.prepare_for_nonlinear_transform()
        self.play(polarplane_pi.animate.apply_function(lambda p: p*1.0),run_time=3,rate_functions=rush_from)
        polarplane_pi.add(plane_circles2)
        self.play(polarplane_pi.animate.apply_function(lambda p: p*0.95),run_time=3,rate_functions=rush_from)
        polarplane_pi.add(plane_circles3)
        self.play(polarplane_pi.animate.apply_function(lambda p: p*0.25),run_time=3,rate_functions=rush_from)
        polarplane_pi.add(plane_circles4)
        self.play(polarplane_pi.animate.apply_function(lambda p: p*0.04),run_time=3,rate_functions=rush_from)
        polarplane_pi.add(plane_circles5)
        self.play(polarplane_pi.animate.apply_function(lambda p: p*0.03),run_time=3,rate_functions=rush_from)
        polarplane_pi.add(plane_circles6)
        self.play(polarplane_pi.animate.apply_function(lambda p: p*0.04),run_time=3,rate_functions=rush_from)
        polarplane_pi.add(plane_circles7)
        self.play(polarplane_pi.animate.apply_function(lambda p: p*0.04),run_time=3,rate_functions=rush_from)
        self.play(polarplane_pi.animate.apply_function(lambda p: p*0.05),run_time=3,rate_functions=rush_from)
        polarplane_pi.add(plane_circles8)
        self.play(polarplane_pi.animate.apply_function(lambda p: p*0.05),run_time=3,rate_functions=rush_from)
        self.play(polarplane_pi.animate.apply_function(lambda p: p*0.04),run_time=3,rate_functions=rush_from)

        self.wait(3) 