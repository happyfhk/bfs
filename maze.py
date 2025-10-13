#pip install Pygame

import pygame
from collections import deque
import time

pygame.init()
width=800
height=600
screen=pygame.display.set_mode((width,height))
pygame.display.set_caption("미로 찾기")

while True:
    num=int(input("미로의 크기를 입력하세요"))
    
    if(num<1):
        break
