# project_ros2

Cài đặt
1. Tạo workspace:
```
mkdir -p ~/dev_ws/src
cd ~/dev_ws/src
```
2. Clone package:
```
git clone https://github.com/chucto/project_ros2
mv ~/dev_ws/src/project_ros2/xeros10_real ~/dev_ws/src/
rm -rf project_ros2
```
3. Cấp quyền thực thi cho file
```
chmod +x ~/dev_ws/src/xeros10_real/scripts/keyboard_arm.py
```
4. Build package:
```
cd ~/dev_ws
colcon build --packages-select xeros10_real --symlink-install
```
5. Source môi trường:
```
source install/setup.bash
```
6. Chạy file launch
```
ros2 launch xeros10_real gazebo.launch.py
```
