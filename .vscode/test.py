# pip install pygame
import pygame
from collections import deque
import time
import sys

pygame.init()

font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 40)
small_font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 25)
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("미로 찾기")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)

dx = [-1, 1, 0, 0]
dy = [0, 0, -1, 1]

def input_size():
    num_str = ""
    active = False
    input_box = pygame.Rect(width//2 - 60, height//2 - 10, 120, 50)
    while True:
        screen.fill(WHITE)
        text = font.render("미로 크기를 입력하세요:", True, BLACK)
        hint = small_font.render("숫자를 입력하고 Enter를 누르세요 (1~30)", True, GRAY)
        pygame.draw.rect(screen, BLUE if active else GRAY, input_box, 3)
        num_display = font.render(num_str, True, RED)
        screen.blit(text, (width//2 - 200, height//2 - 80))
        screen.blit(num_display, (width//2 - 20, height//2 - 5))
        screen.blit(hint, (width//2 - 200, height//2 + 60))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
            elif event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    if num_str.isdigit() and 1 <= int(num_str) <= 30:
                        return int(num_str)
                elif event.key == pygame.K_BACKSPACE:
                    num_str = num_str[:-1]
                elif event.unicode.isdigit() and len(num_str) < 2:
                    num_str += event.unicode

def draw_maze(maze, num, cell_size):
    for y in range(num):
        for x in range(num):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            color = RED if maze[y][x] == 1 else WHITE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

def bfs(maze, num):
    visited = [[False] * num for _ in range(num)]
    parent = [[None] * num for _ in range(num)]
    dist = [[0] * num for _ in range(num)]
    q = deque([(0, 0)])
    visited[0][0] = True
    while q:
        y, x = q.popleft()
        if (y, x) == (num - 1, num - 1):
            return parent, dist[y][x]
        for i in range(4):
            ny, nx = y + dy[i], x + dx[i]
            if 0 <= ny < num and 0 <= nx < num:
                if not visited[ny][nx] and maze[ny][nx] == 0:
                    visited[ny][nx] = True
                    parent[ny][nx] = (y, x)
                    dist[ny][nx] = dist[y][x] + 1
                    q.append((ny, nx))
    return None, None

def main():
    while True:
        num = input_size()
        cell_size = min(width, height) // num
        maze = [[0] * num for _ in range(num)]

        # 미로 편집
        drawing = True
        while drawing:
            screen.fill(WHITE)
            draw_maze(maze, num, cell_size)
            guide = small_font.render("왼쪽 클릭=벽 / 오른쪽 클릭=삭제 / Enter=시작", True, BLACK)
            screen.blit(guide, (20, height - 40))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif pygame.mouse.get_pressed()[0]:
                    mx, my = pygame.mouse.get_pos()
                    x, y = mx // cell_size, my // cell_size
                    if 0 <= x < num and 0 <= y < num:
                        maze[y][x] = 1
                elif pygame.mouse.get_pressed()[2]:
                    mx, my = pygame.mouse.get_pos()
                    x, y = mx // cell_size, my // cell_size
                    if 0 <= x < num and 0 <= y < num:
                        maze[y][x] = 0
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    drawing = False

        # BFS
        start_time = time.time()
        parent, distance = bfs(maze, num)
        end_time = time.time()

        # 경로 복원
        path = []
        if parent is not None:
            y, x = num - 1, num - 1
            while (y, x) != (0, 0):
                path.append((y, x))
                y, x = parent[y][x]
            path.append((0, 0))
            path.reverse()

        # 이동 애니메이션
        path_index = 0
        shown_message = False
        speed = 0.2
        running = True
        while running:
            screen.fill(WHITE)
            draw_maze(maze, num, cell_size)

            # 이동
            if parent is not None and path_index < len(path):
                py, px = path[path_index]
                pygame.draw.rect(screen, GREEN, (px * cell_size, py * cell_size, cell_size, cell_size))
                path_index += 1
                time.sleep(speed)

            # 결과 메시지
            if not shown_message:
                if parent is None:
                    text = font.render("도달할 수 없습니다", True, BLACK)
                else:
                    text = font.render(f"{distance}번 만에 도착!", True, BLACK)
                screen.blit(text, (width // 2 - 180, height // 2))
                guide = small_font.render("R 키를 눌러 다시 하기", True, BLACK)
                screen.blit(guide, (width // 2 - 120, height // 2 + 60))
                shown_message = True

            pygame.display.flip()

            # 이벤트
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    running = False

main()
