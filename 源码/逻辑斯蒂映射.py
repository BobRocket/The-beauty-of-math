from manim import 
from tqdm import tqdm

class LogisticMap(Scene)
    def construct(self)
        # 放个坐标系
        ax = Axes(
            x_range=[2, 4, 0.5],
            y_range=[0, 1, 0.5],
            tips=False,
            axis_config={include_numbers True},
        ).add_coordinates()

        self.add(ax)
        self.wait(2, frozen_frame=True)

        # 准备处理每一个点的动画效果，用valueTracker当作播放时间来控制动画效果
        curr_time = self.renderer.time
        tracker = ValueTracker(0)

        # 动画整体播放20秒，单个点的的淡入动画耗时3秒，20秒后所有点全部淡入完成
        self.total_animation_time = 20.0
        self.single_dot_animation_time = 3.0
        def updater_alpha(mobj)
            # 获取每个点在坐标系里的位置
            array = [mobj.get_coord(0),mobj.get_coord(1),mobj.get_coord(2)]
            cod = ax.point_to_coords(array)
            # 计算每个点所处横向空间的百分比
            k = cod[0]
            k = (k-2.0)2.0

            # 处理点的淡入动画
            # 根据当前播放时间，计算该点透明度，单个点透明度最大值控制在0.25
            last_time = tracker.get_value()
            last_time_dot = last_time - (k  (self.total_animation_time-self.single_dot_animation_time))
            last_time_clipped = np.clip(last_time_dot, 0.0,self.single_dot_animation_time)
            alpha = last_time_clippedself.single_dot_animation_time0.25

            # 处理点的闪烁动画
            # 用该点纵坐标+横坐标作为种子，随便乘一下。。。（^_^)，取小数点后第四第五位（随意选的），算作一个0~100之内的随机数
            # 根据该伪随机数，随机找一些点，分成32批，轮流闪烁一次，20秒内一共闪烁32次
            blink_times = np.linspace(0,20,32)
            blink_times = last_time - blink_times
            random_factor = (mobj.get_coord(1)+10.0)kcurr_time
            random_factor = round(random_factor % 0.01  0.0001)
            blink_time = 1000

            # 轮流查询这32批随机点，看是否轮到它们该闪烁的时间
            for i,blink_group in enumerate(blink_times)
                if random_factor = (i+1) and random_factor i
                    blink_time = blink_group

            # 如果这一批到达闪烁动画的时间段，修改其透明度，覆盖之前计算得到的淡入透明度值，此处透明度最大值为1.0
            if blink_time != 1000
                if abs(blink_time) = 0.3
                    alpha = 0.25 + (0.3-blink_time) 1.75
                    alpha = np.clip(alpha,0.25,1.0)
                else
                    pass

            mobj.set_opacity(alpha)

        # 画逻辑斯蒂映射的正文如下
        # 分支参数mu取值2.0~4.0，其中每隔0.005采样一次，用于描绘
        mu = np.arange(2, 4, 0.005)
        x = 0.2 # 函数迭代初值
        iters = 1000 # 不进行描画的迭代次数
        last = 80 # 最后画出结果的迭代次数

        # 一共1080次循环开始
        for i in tqdm(range(iters+last))
            # 关键的非线性方程在此
            # 2.0~4.0的所有分支参数同步进行迭代计算
            x = mu  x  (1 - x)
            # 每个分支参数，都先“不可见”地运行个1000次，
            # 1000次后，该收敛的已经差不多收敛完成了，然后80次用于描画结果
            if i = iters
                # 根据分支参数mu值，放入各个点
                for j, k in enumerate(mu)
                    # 3.4之前的，吸引子是一个点或者两个点，大多重叠，所以画个20点就够了，用于微量提升运行速度
                    # 越到右边，需要描画的点越多一点，体现其混沌程度
                    if (k=3.4 and i1020) or (k3.4 and i=(680+k100))
                        dot_axes = Dot(ax.coords_to_point(k, x[j]), radius=0.02, color=BLUE,fill_opacity=0.25)
                        # 给每个点加上之前设计好的动画效果updater
                        dot_axes.add_updater(updater_alpha)
                        self.add(dot_axes)

        # 整个动画线性播放20s
        self.play(tracker.animate(rate_func=linear).set_value(self.total_animation_time),run_time=self.total_animation_time)
        self.wait(2) 