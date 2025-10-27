# pip install pygame
import pygame
from collections import deque
import time
import sys
import random

pygame.init()

font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 40)
small_font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 25)
width, height = 700, 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("미로 찾기")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 0)

dx = [-1, 1, 0, 0]
dy = [0, 0, -1, 1]

# --- 1. input_size 함수 수정 (모드 선택 추가) ---
def input_size():
    num_str = ""
    active = False
    input_box = pygame.Rect(width//2 - 60, height//2 - 10, 120, 50)
    
    num = None
    
    # 1. 크기 입력 루프
    while num is None:
        screen.fill(WHITE)
        text = font.render("미로 크기를 입력하세요", True, BLACK)
        hint = small_font.render("숫자를 입력하고 Enter를 누르세요 (1~30)", True, GRAY)
        pygame.draw.rect(screen, BLUE if active else GRAY, input_box, 3)

        num_display = font.render(num_str, True, RED)
        text_width = num_display.get_width()
        text_height = num_display.get_height()
        text_x = input_box.centerx - (text_width // 2)
        text_y = input_box.centery - (text_height // 2)
        
        screen.blit(text, (width//2 - 200, height//2 - 80))
        screen.blit(num_display, (text_x, text_y))
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
                        num = int(num_str) # <--- num이 확정되면 루프 탈출
                elif event.key == pygame.K_BACKSPACE:
                    num_str = num_str[:-1]
                elif event.unicode.isdigit() and len(num_str) < 2:
                    num_str += event.unicode

    # 2. 모드 선택 루프
    manual_button = pygame.Rect(width//2 - 220, height//2, 200, 80)
    auto_button = pygame.Rect(width//2 + 20, height//2, 200, 80)
    
    manual_text = font.render("수동", True, BLACK)
    auto_text = font.render("자동", True, BLACK)
    
    while True:
        screen.fill(WHITE)
        title = font.render("모드를 선택하세요", True, BLACK)
        screen.blit(title, (width//2 - title.get_width()//2, height//2 - 100))
        
        # 버튼 그리기
        pygame.draw.rect(screen, GRAY, manual_button, 0, 10)
        pygame.draw.rect(screen, GRAY, auto_button, 0, 10)
        
        # 버튼 텍스트 그리기 (중앙 정렬)
        manual_text_rect = manual_text.get_rect(center=manual_button.center)
        auto_text_rect = auto_text.get_rect(center=auto_button.center)
        screen.blit(manual_text, manual_text_rect)
        screen.blit(auto_text, auto_text_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if manual_button.collidepoint(event.pos):
                    return num, 'manual' # <--- num과 모드를 함께 반환
                if auto_button.collidepoint(event.pos):
                    return num, 'auto' # <--- num과 모드를 함께 반환

# --- (draw_maze, bfs 함수는 기존과 동일) ---

def draw_maze(maze, num, cell_size):
    for y in range(num):
        for x in range(num):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            
            if (y, x) == (0, 0) or (y, x) == (num - 1, num - 1):
                color = YELLOW  # 시작점과 도착점은 노란색
            elif maze[y][x] == 1:
                color = RED
            else:
                color = WHITE
                
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)
            
def bfs(maze, num):
    visited = [[False] * num for _ in range(num)]
    parent = [[None] * num for _ in range(num)]
    dist = [[0] * num for _ in range(num)]
    q = deque([(0, 0)])
    visited[0][0] = True

    if maze[0][0] == 1:
        return None, None

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

# --- 2. 자동 미로 생성 함수 (신규) ---
def generate_maze(num):
    # 1. 모든 칸을 벽(1)으로 채운 미로를 만듭니다.
    maze = [[1] * num for _ in range(num)]
    stack = deque()
    
    # 2. (0, 0)에서 시작
    start_y, start_x = 0, 0
    maze[start_y][start_x] = 0
    stack.append((start_y, start_x))

    while stack:
        y, x = stack[-1] # 현재 위치 (pop하지 않고 엿보기)
        
        # 3. 방문 가능한 이웃(2칸 떨어진) 찾기
        neighbors = []
        for i in range(4):
            # 2칸 떨어진 이웃
            ny, nx = y + dy[i] * 2, x + dx[i] * 2
            
            # 미로 범위 안이고, 아직 방문 안 한(벽인) 이웃
            if 0 <= ny < num and 0 <= nx < num and maze[ny][nx] == 1:
                neighbors.append((ny, nx, i)) # 방향(i)도 함께 저장
        
        if neighbors:
            # 4. 이웃이 있으면, 랜덤하게 하나 골라 이동
            ny, nx, i = random.choice(neighbors)
            
            # 5. 현재 위치와 이웃 사이의 벽(1칸 떨어진)을 뚫습니다.
            wy, wx = y + dy[i], x + dx[i]
            maze[wy][wx] = 0
            maze[ny][nx] = 0 # 이웃도 길로 만듦
            
            stack.append((ny, nx)) # 이웃을 스택에 추가
        else:
            # 6. 막다른 길이면, 스택에서 pop (뒤로가기)
            stack.pop()

    # 7. 도착 지점 (num-1, num-1)을 강제로 엽니다.
    maze[num-1][num-1] = 0
    
    # 8. (만약 도착 지점이 고립되었다면) 위쪽이나 왼쪽 벽을 뚫어 연결
    if num > 1:
        if maze[num-2][num-1] == 1 and maze[num-1][num-2] == 1:
            # (num-2, num-1)을 뚫어 (num-3, num-1) 또는 (num-1, num-1)과 연결
            maze[num-2][num-1] = 0 
            
    return maze

# --- 3. main 함수 수정 (모드 분기) ---
def main():
    while True:
        # 1. num과 mode를 함께 받음
        num, mode = input_size()
        
        cell_size = min(width, height) // num
        maze = [[0] * num for _ in range(num)]

        if mode == 'manual':
            # --- (A) 수동 모드 (기존과 동일) ---
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
                            if (y, x) != (0, 0) and (y, x) != (num - 1, num - 1):
                                maze[y][x] = 1
                    elif pygame.mouse.get_pressed()[2]:
                        mx, my = pygame.mouse.get_pos()
                        x, y = mx // cell_size, my // cell_size
                        if 0 <= x < num and 0 <= y < num:
                            if (y, x) != (0, 0) and (y, x) != (num - 1, num - 1):
                                maze[y][x] = 0
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        drawing = False
        
        elif mode == 'auto':
            # --- (B) 자동 모드 (신규) ---
            maze = generate_maze(num) # <--- 자동 생성
            
            # 생성된 미로를 보여주고 BFS 시작 대기
            waiting = True
            while waiting:
                screen.fill(WHITE)
                draw_maze(maze, num, cell_size)
                guide = small_font.render("자동 생성 완료! Enter를 눌러 탐색 시작", True, BLACK)
                screen.blit(guide, (20, height - 40))
                pygame.display.flip()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        waiting = False

        
        # --- (BFS, 경로 복원, 애니메이션은 수동/자동 공통) ---
        
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
        if 1 <= num <= 15:
            speed = 0.1  # 기본 속도
        else: # 16 <= num <= 30 (input_size에서 보장됨)
            speed = 0.06
        running = True
        while running:
            screen.fill(WHITE)
            draw_maze(maze, num, cell_size)

            # 이동 경로 그리기
            if parent is not None:
                for i in range(path_index):
                    py, px = path[i]
                    pygame.draw.rect(screen, GREEN, (px * cell_size, py * cell_size, cell_size, cell_size))

                if path_index < len(path):
                    py, px = path[path_index]
                    pygame.draw.rect(screen, GREEN, (px * cell_size, py * cell_size, cell_size, cell_size))
                    path_index += 1
                    time.sleep(speed)

            # 결과 메시지 (애니메이션이 끝났거나 경로가 없을 때)
            if (parent is not None and path_index == len(path)) or (parent is None):
                
                if parent is None:
                    main_message_text = "도달할 수 없습니다"
                else:
                    main_message_text = f"{distance}번 만에 도착!"
                
                text_surface = font.render(main_message_text, True, BLACK)
                guide_surface = small_font.render("다시하기(R)", True, BLACK)
                
                total_text_width = max(text_surface.get_width(), guide_surface.get_width())
                total_text_height = text_surface.get_height() + guide_surface.get_height()
                padding = 40
                box_width = total_text_width + padding * 2
                box_height = total_text_height + padding * 2
                box_x = (width // 2) - (box_width // 2)
                box_y = (height // 2) - (box_height // 2) - 30
                
                background_rect = pygame.Rect(box_x, box_y, box_width, box_height)
                
                pygame.draw.rect(screen, GRAY, background_rect, 0, 10)
                pygame.draw.rect(screen, BLACK, background_rect, 3, 10)
                
                text_rect = text_surface.get_rect(center=(background_rect.centerx, background_rect.centery - guide_surface.get_height() // 2 - 10))
                screen.blit(text_surface, text_rect)
                
                guide_rect = guide_surface.get_rect(center=(background_rect.centerx, background_rect.centery + text_surface.get_height() // 2 + 10))
                screen.blit(guide_surface, guide_rect)

            pygame.display.flip()

            # 이벤트
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    running = False
                        
main()