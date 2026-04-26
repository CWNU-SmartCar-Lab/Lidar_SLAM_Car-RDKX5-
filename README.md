# YDLidar Workspace

## 目录结构

```
/home/qing/ydlidar_ws/
├── YDLidar-SDK-master/          # 核心 C++ SDK
│   ├── core/                  # 核心库（串口、网络、数学库）
│   ├── samples/                # 示例程序
│   └── python/                 # Python 绑定
├── src/
│   ├── ydlidar_ros2_driver-master/   # ROS2 驱动
│   │   ├── launch/                  # 启动文件
│   │   ├── params/                  # 配置文件
│   │   └── src/                     # 驱动源码
│   └── openslam_gmapping/           # SLAM 地图包
├── build/                     # 构建目录
├── install/                   # 安装目录
└── log/                       # 日志目录
```

## 构建命令

### 1. 构建 YDLidar-SDK

```bash
cd /home/qing/ydlidar_ws/YDLidar-SDK-master
mkdir -p build && cd build
cmake .. && make -j4
sudo make install
```

### 2. 构建 ROS2 Driver

```bash
cd /home/qing/ydlidar_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

### 3. 设置环境变量

```bash
source /home/qing/ydlidar_ws/install/setup.bash
```

## 运行命令

### 启动激光雷达

```bash
ros2 launch ydlidar_ros2_driver ydlidar_launch.py
```

### 查看扫描数据

```bash
ros2 topic echo /scan
```

### RViz 可视化

```bash
ros2 launch ydlidar_ros2_driver ydlidar_launch_view.py
```

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| port | /dev/ttyUSB0 | 串口设备名 |
| baudrate | 230400 | 波特率 |
| frame_id | laser_frame | TF 坐标系名称 |
| topic | /scan | 激光扫描话题 |

## 代码修改位置

### 串口配置
- 文件: `src/ydlidar_ros2_driver-master/params/ydlidar.yaml`
- 参数: `port: /dev/ttyUSB0`

### 启动文件
- 文件: `src/ydlidar_ros2_driver-master/launch/*.py`

### ROS2 参数
- 文件: `src/ydlidar_ros2_driver-master/src/*.cpp`