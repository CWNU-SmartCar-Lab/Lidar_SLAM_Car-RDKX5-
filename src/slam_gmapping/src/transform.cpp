#include "slam_gmapping/transform.h"

// 修改 1: Jazzy 中必须使用 .hpp
#include "tf2_ros/create_timer_ros.hpp" 

using std::placeholders::_1;

Transform::Transform() : Node("transform_node"),
                         transform_thread_(nullptr) {
    // 修改 2: 为所有 declare_parameter 增加显式类型和默认值
    this->declare_parameter<std::string>("parents_frame", "odom");
    this->declare_parameter<std::string>("child_frame", "laser");
    this->declare_parameter<double>("x", 0.0);
    this->declare_parameter<double>("y", 0.0);
    this->declare_parameter<double>("z", 0.0);
    this->declare_parameter<double>("roll", 0.0);
    this->declare_parameter<double>("pitch", 0.0);
    this->declare_parameter<double>("yaw", 0.0);

    this->get_parameter_or<std::string>("parents_frame", parents_frame, "odom");
    this->get_parameter_or<std::string>("child_frame", child_frame, "laser");
    this->get_parameter_or<double>("x", x, 0.0);
    this->get_parameter_or<double>("y", y, 0.0);
    this->get_parameter_or<double>("z", z, 0.0);
    this->get_parameter_or<double>("roll", roll, 0.0);
    this->get_parameter_or<double>("pitch", pitch, 0.0);
    this->get_parameter_or<double>("yaw", yaw, 0.0);

    //Degree to radius:
    yaw = yaw * M_PI / 180;
    pitch = pitch * M_PI / 180;
    roll = roll * M_PI / 180;
    // Abbreviations for the various angular functions
    double cy = cos(yaw * 0.5);
    double sy = sin(yaw * 0.5);
    double cp = cos(pitch * 0.5);
    double sp = sin(pitch * 0.5);
    double cr = cos(roll * 0.5);
    double sr = sin(roll * 0.5);
    rotation_w = cy * cp * cr + sy * sp * sr;
    rotation_x = cy * cp * sr - sy * sp * cr;
    rotation_y = sy * cp * sr + cy * sp * cr;
    rotation_z = sy * cp * cr - cy * sp * sr;

    buffer_ = std::make_shared<tf2_ros::Buffer>(get_clock());
    auto timer_interface = std::make_shared<tf2_ros::CreateTimerROS>(
            get_node_base_interface(),
            get_node_timers_interface());
    buffer_->setCreateTimerInterface(timer_interface);
    node_ = std::shared_ptr<rclcpp::Node>(this, [](rclcpp::Node *) {});
    tfB_ = std::make_shared<tf2_ros::TransformBroadcaster>(node_);
    transform_thread_ = std::make_shared<std::thread>
            (std::bind(&Transform::publishLoop, this));
}

void Transform::publishLoop() {
    rclcpp::Rate r(1.0 / 0.05);
    while (rclcpp::ok()) {
        publishTransform();
        r.sleep();
    }
}


void Transform::publishTransform() {
    // 修改 3: 使用现代的 from_seconds 替换已被废弃的老旧 Duration 初始化方式
    rclcpp::Time tf_expiration = get_clock()->now() + rclcpp::Duration::from_seconds(tf_delay_);
    
    geometry_msgs::msg::TransformStamped transform;
    transform.header.frame_id = parents_frame;
    transform.header.stamp = tf_expiration;
    transform.child_frame_id = child_frame;
    transform.transform.translation.x = x;
    transform.transform.translation.y = y;
    transform.transform.translation.z = z;
    transform.transform.rotation.w = rotation_w;
    transform.transform.rotation.x = rotation_x;
    transform.transform.rotation.y = rotation_y;
    transform.transform.rotation.z = rotation_z;
    try {
        tfB_->sendTransform(transform);
    }
    catch (tf2::LookupException &te) {
        RCLCPP_INFO(this->get_logger(), te.what());
    }
}

int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);
    auto transform = std::make_shared<Transform>();
    rclcpp::spin(transform);
    return (0);
}