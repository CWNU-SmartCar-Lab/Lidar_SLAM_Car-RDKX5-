import asyncio
import websockets
import json
import serial
import struct
import time  # <--- 【关键新增】：导入时间模块

# 配置与STM32连接的串口 (根据RDK X5实际引脚修改)
try:
    ser = serial.Serial('/dev/ttyUSB1', 115200, timeout=1)
    print("串口 /dev/ttyUSB1 打开成功")
except Exception as e:
    print(f"串口打开失败: {e}")
    ser = None


def send_vofa_command(cmd_type, cmd_id, cmd_obj, float_data):
    """
    按照STM32代码中的协议打包数据：
    '@' + Type + ID + Object + '=' + 4bytes float + '!' + '#'
    """
    if ser is None or not ser.is_open:
        return

    # 将浮点数转换为4字节 (小端模式 '<f')
    float_bytes = struct.pack('<f', float_data)

    # 构建协议帧
    frame = bytearray([
        ord('@'),
        ord(cmd_type),
        ord(cmd_id),
        ord(cmd_obj),
        ord('=')
    ])
    frame.extend(float_bytes)
    frame.extend([ord('!'), ord('#')])

    # 通过串口发送给STM32
    ser.write(frame)

    # === 【核心修复】：防止多个包连发导致 STM32 处理不过来 ===
    ser.flush()  # 强制清空发送缓冲区，立刻把数据推入串口线
    time.sleep(0.005)  # 强制休眠 5 毫秒，给 STM32 留出充裕的解包和清空缓存的时间


async def handle_client(websocket, path):
    print("手机端已连接")

    # 增加两个变量，分别记录上一次的舵机角度和电机速度
    last_target_angle = None
    last_target_speed = None

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("type") == "cmd":
                    speed_ratio = data.get("speed", 0.0)  # 摇杆Y轴 * 拉杆比例 [-1.0 到 1.0]
                    steer_ratio = data.get("steer", 0.0)  # 摇杆X轴 [-1.0 到 1.0]

                    # 尝试接收前端专属的“急停”标志（需要前端配合，默认 False）
                    is_estop = data.get("estop", False)

                    # === 计算目标值 ===
                    max_motor_speed = 500.0
                    target_speed = speed_ratio * max_motor_speed

                    servo_center = 90.0
                    servo_max_turn = 30.0
                    target_angle = servo_center - (steer_ratio * servo_max_turn)  # 舵机方向已修复为减号

                    # === 升级版 Debug 打印逻辑 ===
                    angle_changed = last_target_angle is None or abs(target_angle - last_target_angle) > 0.1
                    speed_changed = last_target_speed is None or abs(target_speed - last_target_speed) > 0.1

                    # 1. 专属急停按钮触发 (最高优先级)
                    if is_estop:
                        print(f"🚨 [E-STOP] 急停被按下！发送动力切断指令！电机: 0.00 | 舵机: {target_angle:.1f}°")
                        last_target_angle = target_angle
                        last_target_speed = target_speed

                    # 2. 数据发生变化时正常打印
                    elif angle_changed or speed_changed:
                        # 如果目标值都是0，说明是松开摇杆的正常刹车
                        if target_speed == 0.0 and abs(target_angle - servo_center) < 0.1:
                            print(f"🛑 [STOP] 摇杆回中停车 | 舵机: {target_angle:.1f}° | 电机: 0.00")
                        else:
                            print(f"✅ [CMD] 指令下发 | 舵机: {target_angle:.1f}° | 电机: {target_speed:.2f}")

                        # 更新记录
                        last_target_angle = target_angle
                        last_target_speed = target_speed

                    # === 发送串口指令 ===
                    send_vofa_command('E', '1', 'P', target_speed)  # 左电机
                    send_vofa_command('E', '2', 'P', target_speed)  # 右电机
                    send_vofa_command('E', '3', 'P', target_angle)  # 舵机

            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        print("手机端连接断开")


async def main():
    # 启动 WebSocket 服务器，监听 0.0.0.0:8765
    server = await websockets.serve(handle_client, "0.0.0.0", 8765)
    print("WebSocket 服务器已启动，等待手机连接...")

    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())