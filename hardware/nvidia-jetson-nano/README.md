# nVidia Jetson Nano

The main goal is to train and to inference images/videos using DL and adhoc
hardware. As a final goal, I will record my dog using a video cam and I will
find my dog in the video, and detect the breed of the dog and other characteristics.

Not sure if train is possible with this hardware (Even transfer learning is possible for re-training networks locally onboard Jetson Nano using the ML frameworks.)

[The Jetson Nano can also be used to train machine-learning models](https://www.techrepublic.com/article/raspberry-pi-style-jetson-nano-is-a-powerful-low-cost-ai-computer-from-nvidia/)

## First steps

* [Get started](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit)
* [Jetbot](https://github.com/NVIDIA-AI-IOT/jetbot/wiki)
* [nano Forums](https://devtalk.nvidia.com/default/board/371/)
* [Links to Jetson Nano Resources & Wiki](https://devtalk.nvidia.com/default/topic/1048642/jetson-nano/links-to-jetson-nano-resources-amp-wiki/)
* [Main blog post](https://devblogs.nvidia.com/jetson-nano-ai-computing/)

## Extra modules to be bought

[Based on Jetbot bill of materials](https://github.com/NVIDIA-AI-IOT/jetbot/wiki/bill-of-materials)

* MicroSD
* Power supply (be careful with the plug adapter)
* WiFi
* Camera

## ROADMAP

* Buy all the hardware
* Integrate and configure the hardware/software to have a working system
** Install in the microUSB the https://developer.nvidia.com/embedded/jetpack
** Boot nano from the microUSB
* [Play](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit#next)
** https://www.dlology.com/blog/how-to-run-keras-model-on-jetson-nano/
** https://hackaday.com/2019/03/18/hands-on-new-nvidia-jetson-nano-is-more-power-in-a-smaller-form-factor/
** https://github.com/dusty-nv/jetson-inference
