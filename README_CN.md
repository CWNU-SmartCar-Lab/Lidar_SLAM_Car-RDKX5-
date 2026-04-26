# YDLidar RDKX5 上位机应用

## 一、代码组成

本项目包含以下核心组件：

### 1. YDLidar-SDK（C++ 核心库）
- 位置：`YDLidar-SDK-master/`
- 功能：提供激光雷达通信协议解析、串口/网络连接、数据处理等核心功能
- 架构：
  - `core/` - 核心库（串口、网络、数学库）
  - `samples/` - 示例程序
  - `python/` - Python 绑定
  - `csharp/` - C# 绑定

### 2. ydlidar_ros2_driver（ROS2 驱动）
- 位置：`src/ydlidar_ros2_driver-master/`
- 功能：将激光雷达数据发布为 ROS2 sensor_msgs/LaserScan 话题
- 关键目录：
  - `launch/` - 启动文件
  - `params/` - 配置文件
  - `src/` - 驱动源码

### 3. 通信连接
- 激光雷达通过**串口**连接到上位机（RDKX5）
- 默认串口：`/dev/ydlidar`（需映射到实际设备如 `/dev/ttyUSB0`）
- 波特率：`512000`

---

## 二、使用方法

### 2.1 构建步骤

#### 步骤 1：构建 YDLidar-SDK

```bash
cd /home/qing/ydlidar_ws/YDLidar-SDK-master
mkdir -p build && cd build
cmake .. && make -j4
sudo make install
```

#### 步骤 2：构建 ROS2 Driver

```bash
cd /home/qing/ydlidar_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

#### 步骤 3：设置环境变量

```bash
source /home/qing/ydlidar_ws/install/setup.bash
```

### 2.2 运行步骤

#### 步骤 1：检查串口设备

确认激光雷达连接的串口设备名称：

```bash
ls -l /dev/ttyUSB*
```

#### 步骤 2：配置串口别名（可选）

```bash
sudo chmod 0777 src/ydlidar_ros2_driver/startup/*
sudo sh src/ydlidar_ros2_driver/startup/initenv.sh
```

然后重新插拔激光雷达。

#### 步骤 3：启动激光雷达

```bash
ros2 launch ydlidar_ros2_driver ydlidar_launch.py
```

#### 步骤 4：查看扫描数据

```bash
ros2 topic echo /scan
```

#### 步骤 5：RViz 可视化（可选）

```bash
ros2 launch ydlidar_ros2_driver ydlidar_launch_view.py
```

---

## 三、配置参数

### 3.1 串口配置（必须修改）

文件：`src/ydlidar_ros2_driver-master/params/ydlidar.yaml`

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `port` | /dev/ydlidar | **串口设备名**，需改为实际设备如 `/dev/ttyUSB0` |
| `baudrate` | 512000 | 波特率，根据激光雷达型号选择 |

### 3.2 其他常用参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `frame_id` | laser | TF 坐标系名称 |
| `frequency` | 10.0 | 扫描频率（Hz） |
| `angle_max` | 180.0 | 最大角度 |
| `angle_min` | -180.0 | 最小角度 |
| `range_max` | 64.0 | 最大测距（米） |
| `range_min` | 0.01 | 最小测距（米） |

---

## 四、切换 WiFi 后需要修改的地方

### 4.1 上位机 IP 地址

切换 WiFi 后，上位机（RDKX5）的 IP 地址会发生变化。如果代码中使用了固定 IP 地址，需要相应修改：

- ** ROS2 Discovery Server 配置**：如果使用了 FastDDS Discovery Server，需更新 Server IP
- **_DOMAIN ID_**：如果多设备通过 ROS2 通信，需确保 Domain ID 一致
- **环境变量**：
  ```bash
  export ROS_DOMAIN_ID=<你的Domain ID>
  ```

### 4.2 串口设备名

切换网络不会改变串口连接，但如果重新插拔激光雷达，串口设备名可能变化（如从 `/dev/ttyUSB0` 变为 `/dev/ttyUSB1`）。

**解决方法**：
- 方案 1：使用串口别名
  ```bash
  # 创建 udev 规则
  sudo nano /etc/udev/rules.d/99-ydlidar.rules
  # 添加：SUBSYSTEM=="tty", ATTRS{idVendor}=="xxxx", ATTRS{idProduct}=="xxxx", SYMLINK+="ydlidar"
  ```
- 方案 2：每次确认设备名
  ```bash
  ls -l /dev/ttyUSB*
  ```

### 4.3 ROS2 网络配置（重要）

如果上位机需要与其他 ROS2 设备通信，切换 WiFi 后可能需要配置以下内容：

#### 方案 1：设置 ROS_DOMAIN_ID

```bash
# 在 ~/.bashrc 中添加
echo 'export ROS_DOMAIN_ID=42' >> ~/.bashrc
source ~/.bashrc
```

#### 方案 2：使用环回地址

如果只需要本机通信：

```bash
export RMW_FASTDDS_USE_SHARED_MEMORY=0
export ROS_LOCALHOST_ONLY=1
```

#### 方案 3：配置 FastDDS XML 文件

创建 `fastdds.xml` 配置文件：

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<profiles>
    <transport_descriptors>
        <transport_descriptor>
            <transport_id>udp_transport</transport_id>
            <type>UDPv4</type>
            <maxInitialPeersRank>0</maxInitialPeersRank>
            <interfaceWhiteList>
                <ip>192.168.x.x</ip>  <!-- 修改为当前 WiFi IP -->
            </interfaceWhiteList>
        </transport_descriptor>
    </transport_descriptors>
    <participant>
        <rtps>
            <transportDescriptor>udp_transport</transportDescriptor>
        </rtps>
    </participant>
</profiles>
```

---

## 五、常见问题

### Q1: 激光雷达无法启动

- 检查串口设备名是否正确
- 检查波特率是否匹配
- 确认有权限访问串口：`sudo usermod -a -G dialout $USER`，然后重新登录

### Q2: 切换 WiFi 后无法接收数据

- 检查 ROS_DOMAIN_ID 是否一致
- 检查防火墙是否阻止了 UDP 端口
- 确认在同一网络下

### Q3: 数据丢失或延迟高

- 检查 WiFi 网络质量
- 降低扫描频率：`frequency: 10.0` 改为较低值
- 检查上位机性能

---

## 六、文件索引

| 用途 | 文件路径 |
|------|----------|
| 串口配置 | `src/ydlidar_ros2_driver-master/params/ydlidar.yaml` |
| 启动文件 | `src/ydlidar_ros2_driver-master/launch/ydlidar_launch.py` |
| 驱动源码 | `src/ydlidar_ros2_driver-master/src/*.cpp` |
| SDK 核心 | `YDLidar-SDK-master/core/` |