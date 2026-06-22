# Foxglove Demo
## Demo video 
https://youtu.be/yxn0pycE9H8

## Wiring
<img width="4080" height="2296" alt="mystm32foxglovedemo" src="https://github.com/user-attachments/assets/307d54cb-0a87-4340-a257-deee09ca2c99" />

## Instruction
1. Build and deploy the firmware code to your STM32F411RE
2. Run
```sh
pip install -e .
```
3. Run for Windows
```sh
python -m backend.foxglove_server COM11
```
Run for Linux
```sh
python -m backend.foxglove_server /dev/ttyUSB0 --baud 115200 --print-rows
```
4. Open Foxglove Studio and run "Open Connection"
5. Import panel layout in foxglove directory for convenience. 