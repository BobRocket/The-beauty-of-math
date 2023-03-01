from manim import *

# 计算两个翻转的合并效果
def get_composite_rotation_angle_and_axis(angles, axes):
    angle1, axis1 = 0, OUT
    for angle2, axis2 in zip(angles, axes):
        ## Figure out what (angle3, axis3) is the same
        ## as first applying (angle1, axis1), then (angle2, axis2)
        axis2 = normalize(axis2)
        dot = np.dot(axis2, axis1)
        cross = np.cross(axis2, axis1)
        angle3 = 2*np.arccos(
            np.cos(angle2/2)*np.cos(angle1/2) - \
            np.sin(angle2/2)*np.sin(angle1/2)*dot
        )
        axis3 = (
            np.sin(angle2/2)*np.cos(angle1/2)*axis2 + \
            np.cos(angle2/2)*np.sin(angle1/2)*axis1 + \
            np.sin(angle2/2)*np.sin(angle1/2)*cross
        )
        axis3 = normalize(axis3)
        angle1, axis1 = angle3, axis3

    # 翻转角度计算结果控制在-PI到+PI之间
    if angle1 > np.pi:
        angle1 -= 2*np.pi
    return angle1, axis1

class Symmetry(ThreeDScene):
    def construct(self):
        # 立方体翻转效果数据，每两个为一组，应用于画面左侧立方体和中间立方体，一共八组
        # （第一个参数是翻转角度，第二个参数是旋转轴）
        self.angle_axis_pairs = [
            (np.pi/2, RIGHT),
            (np.pi/2, UP),
            (np.pi/2, OUT),
            (np.pi/2, DOWN),
            (np.pi*2/3, UP+RIGHT+OUT),
            (np.pi/2, RIGHT),
            (np.pi*2/3, DOWN+RIGHT+OUT),
            (np.pi, UP+LEFT),
            (np.pi, DOWN+OUT),
            (np.pi, UP+RIGHT),
            (np.pi, UP+LEFT),
            (np.pi/2, DOWN),
            (np.pi*2/3, UP+LEFT+OUT),
            (np.pi/2, RIGHT),
            (np.pi*2/3, DOWN+LEFT+OUT),
            (np.pi, UP+IN),

        ]
        self.cube_opacity = 0.4
        self.cube_colors = [BLUE]

        self.pose_matrix = self.get_pose_matrix()
        # 创建立方体
        cube = self.get_cube()

        # 再复制出两个立方体，以及加号和等号，放到场景中
        equation = cube1, plus, cube2, equals, cube3 = VGroup(
            cube, Tex("+", font_size=60),
            cube.copy(), Tex("=", font_size=60),
            cube.copy()
        )
        equation.arrange(RIGHT, buff = MED_LARGE_BUFF)
        equation.center()

        self.add(equation)

        # 一共做八次立方体翻转动画
        for n in range(8):
            # 从list中读取当前左侧和中间立方体即将应用的翻转效果数据，放到临时list中
            angle_axis_pairs_temp = list([self.angle_axis_pairs[n*2],self.angle_axis_pairs[n*2+1]])
            # 计算两个翻转的合并效果，也存放到临时list中
            angle_axis_pairs_temp.append(
                self.get_composition_angle_and_axis(angle_axis_pairs_temp)
            )
            print(angle_axis_pairs_temp[2])
            # 调整这三个翻转效果的旋转轴，需要叠加初始化翻转效果。
            axis1 = np.dot(angle_axis_pairs_temp[0][1], self.pose_matrix.T)
            axis2 = np.dot(angle_axis_pairs_temp[1][1], self.pose_matrix.T)
            axis3 = np.dot(angle_axis_pairs_temp[2][1], self.pose_matrix.T)

            # 播放翻转动画
            self.play(
                Rotate(cube1, angle_axis_pairs_temp[0][0],axis1,in_place = True),
                Rotate(cube2, angle_axis_pairs_temp[1][0],axis2,in_place = True),
                Rotate(cube3, angle_axis_pairs_temp[2][0],axis3,in_place = True),
                run_time=3,
                rate_func=smooth
            )
            self.wait(0.5)

        self.wait(2)

    # 初始化立方体，应用初始状态矩阵效果
    def get_cube(self):
        cube = Cube(fill_opacity = self.cube_opacity)
        cube.set_color_by_gradient(*self.cube_colors)
        pose_matrix = self.get_pose_matrix()
        cube.apply_function(
            lambda p : np.dot(p, pose_matrix.T),
        )
        return cube

    # 立方体初始状态的矩阵（微微旋转以适合画面展示效果）
    def get_pose_matrix(self):
        return np.dot(
            rotation_matrix(np.pi/12, UP),
            rotation_matrix(np.pi/25, RIGHT)
        )

    def get_composition_angle_and_axis(self, angle_axis_pairs_temp):
        return get_composite_rotation_angle_and_axis(
            *list(zip(*angle_axis_pairs_temp))
        ) 