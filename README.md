# jumpcutter
Idea from https://github.com/carykh/jumpcutter

python3 ./jc2mp4 [input] [output] [sensitivity]

原程序太慢了，我重写了，更改了输出的方式。为了效率直接跳过无声部分，音频爆破严重。够我自己用了。

The original program is too slow for my machine.So I rewrite the conversion method.

It's use ffmpeg filter to trim and change speedrate.Then merge the video.

I don't know python too much, I don't undersand what the original is doing.So I have to rewrite the whole program.

And I need help, I'm new to github, do I need pull request from original?
