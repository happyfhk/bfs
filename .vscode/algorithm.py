# pip install pygame
import pygame
from collections import deque
import time
import sys
import random
import heapq 

pygame.init()

# --- 1. 폰트 및 화면 설정 ---
try:
    font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 40)
    small_font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 25)
    
    try:
        small_bold_font = pygame.font.Font("C:/Windows/Fonts/malgunbd.ttf", 25)
    except FileNotFoundError:
        print("맑은 고딕 Bold 폰트(malgunbd.ttf)를 찾을 수 없습니다. set_bold(True)로 대체합니다.")
        small_bold_font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 25)
        small_bold_font.set_bold(True) # 굵게 설정

except FileNotFoundError:
    print("맑은 고딕 폰트를 찾을 수 없습니다. 기본 폰트로 대체합니다.")
    font = pygame.font.Font(None, 50)
    small_font = pygame.font.Font(None, 35)
    # (수정) 기본 폰트의 굵은 버전
    small_bold_font = pygame.font.Font(None, 35)
    small_bold_font.set_bold(True) # 굵게 설정

width, height = 700, 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("미로 찾기 알고리즘 비교")

# --- 2. 색상 및 방향 설정 ---
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 250, 0) # (가시성을 위해 약간 밝게 수정)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)
DARK_BLUE = (0, 0, 150) # 더 진한 파란색 추가
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

dx = [-1, 1, 0, 0]
dy = [0, 0, -1, 1]

# --- 3. input_size 함수 ---
def input_size():
    num_str = ""
    active = False
    input_box = pygame.Rect(width // 2 - 60, height // 2 - 10, 120, 50)

    while True:
        screen.fill(WHITE)
        text = font.render("미로 크기를 입력하세요", True, BLACK)
        # (수정) 1~300으로 변경
        hint = small_font.render("숫자를 입력하고 Enter를 누르세요 (1~300)", True, GRAY)
        pygame.draw.rect(screen, BLUE if active else GRAY, input_box, 3)

        num_display = font.render(num_str, True, RED)
        text_rect = num_display.get_rect(center=input_box.center)
        
        screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - 80))
        screen.blit(num_display, text_rect)
        screen.blit(hint, (width // 2 - hint.get_width() // 2, height // 2 + 60))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
            elif event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    # (수정) 1~300으로 변경
                    if num_str.isdigit() and 1 <= int(num_str) <= 300:
                        return int(num_str)
                elif event.key == pygame.K_BACKSPACE:
                    num_str = num_str[:-1]
                elif event.unicode.isdigit() and len(num_str) < 3: 
                    num_str += event.unicode
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

# --- 4. 미로 그리기 (draw_maze) ---
def draw_maze(surface, maze, num, cell_size):
    """미로를 (0,0) 기준으로 surface에 그립니다 (격자 O)"""
    surface.fill(WHITE) 
    for y in range(num):
        for x in range(num):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            
            if (y, x) == (0, 0) or (y, x) == (num - 1, num - 1):
                color = YELLOW
            elif maze[y][x] == 1:
                color = RED
            else:
                color = WHITE
                
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, GRAY, rect, 1) # 격자

# --- 5. 미로 자동 생성 (generate_maze) ---
def generate_maze(num):
    maze = [[1] * num for _ in range(num)]
    stack = deque()
    
    start_y, start_x = 0, 0
    maze[start_y][start_x] = 0
    stack.append((start_y, start_x))

    while stack:
        y, x = stack[-1] 
        neighbors = []
        for i in range(4):
            ny, nx = y + dy[i] * 2, x + dx[i] * 2
            if 0 <= ny < num and 0 <= nx < num and maze[ny][nx] == 1:
                neighbors.append((ny, nx, i))
        
        if neighbors:
            ny, nx, i = random.choice(neighbors)
            wy, wx = y + dy[i], x + dx[i]
            maze[wy][wx] = 0
            maze[ny][nx] = 0 
            stack.append((ny, nx))
        else:
            stack.pop()

    maze[num - 1][num - 1] = 0
    
    if num > 1:
        if maze[num - 2][num - 1] == 1 and maze[num - 1][num - 2] == 1:
            if random.choice([True, False]):
                 maze[num - 2][num - 1] = 0
            else:
                 maze[num - 1][num - 2] = 0
                 
    return maze

# --- 6. A*용 휴리스틱 함수 (맨해튼 거리) ---
def heuristic(y, x, num):
    goal_y, goal_x = num - 1, num - 1
    return abs(y - goal_y) + abs(x - goal_x)

# --- 7. 경로 탐색 알고리즘 3가지 (BFS, DFS, A*) ---
def bfs(maze, num):
    visited = [[False] * num for _ in range(num)]
    parent = [[None] * num for _ in range(num)]
    dist = [[0] * num for _ in range(num)]
    q = deque([(0, 0)])
    visited[0][0] = True
    if maze[0][0] == 1: return None, None
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

def dfs(maze, num):
    visited = [[False] * num for _ in range(num)]
    parent = [[None] * num for _ in range(num)]
    dist = [[0] * num for _ in range(num)]
    stack = deque([(0, 0)])
    visited[0][0] = True
    if maze[0][0] == 1: return None, None
    while stack:
        y, x = stack.pop()
        if (y, x) == (num - 1, num - 1):
            return parent, dist[y][x]
        for i in range(4):
            ny, nx = y + dy[i], x + dx[i]
            if 0 <= ny < num and 0 <= nx < num:
                if not visited[ny][nx] and maze[ny][nx] == 0:
                    visited[ny][nx] = True
                    parent[ny][nx] = (y, x)
                    dist[ny][nx] = dist[y][x] + 1
                    stack.append((ny, nx))
    return None, None

def a_star(maze, num):
    parent = [[None] * num for _ in range(num)]
    g_score = [[float('inf')] * num for _ in range(num)]
    f_score = [[float('inf')] * num for _ in range(num)]
    start_y, start_x = 0, 0
    g_score[start_y][start_x] = 0
    f_score[start_y][start_x] = heuristic(start_y, start_x, num)
    open_set = [(f_score[start_y][start_x], start_y, start_x)]
    heapq.heapify(open_set)
    if maze[start_y][start_x] == 1:
        return None, None
    open_set_hash = {(start_y, start_x)}
    while open_set:
        current_f, y, x = heapq.heappop(open_set)
        open_set_hash.remove((y, x))
        if (y, x) == (num - 1, num - 1):
            return parent, g_score[y][x]
        for i in range(4):
            ny, nx = y + dy[i], x + dx[i]
            if 0 <= ny < num and 0 <= nx < num and maze[ny][nx] == 0:
                tentative_g = g_score[y][x] + 1
                if tentative_g < g_score[ny][nx]:
                    parent[ny][nx] = (y, x)
                    g_score[ny][nx] = tentative_g
                    f_score[ny][nx] = tentative_g + heuristic(ny, nx, num)
                    if (ny, nx) not in open_set_hash:
                        heapq.heappush(open_set, (f_score[ny][nx], ny, nx))
                        open_set_hash.add((ny, nx))
    return None, None

# --- 8. draw_maze_fast (격자 없는 빠른 그리기) ---
def draw_maze_fast(surface, maze, num, cell_size):
    """미로를 (0,0) 기준으로 surface에 그립니다 (격자 X)"""
    surface.fill(WHITE)
    wall_color = RED
    start_end_color = YELLOW
    
    surf_w, surf_h = surface.get_size()

    # N=250, cell_size=2 일 때 (대부분)
    if cell_size > 1: 
        for y in range(num):
            for x in range(num):
                rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                # (Surface 크기(500)를 벗어나면 그리지 않음 - 예: N=250, c=2 -> max 498)
                if rect.left >= surf_w or rect.top >= surf_h: continue

                if (y, x) == (0, 0) or (y, x) == (num - 1, num - 1):
                    color = start_end_color
                elif maze[y][x] == 1:
                    color = wall_color
                else:
                    continue 
                pygame.draw.rect(surface, color, rect)
                
    # N=700, cell_size=1 일 때 (드문 경우)
    else: 
        px_array = pygame.PixelArray(surface)
        try:
            for y in range(num):
                for x in range(num):
                    if x >= surf_w or y >= surf_h: continue 
                    
                    if (y, x) == (0, 0) or (y, x) == (num - 1, num - 1):
                        px_array[x, y] = start_end_color
                    elif maze[y][x] == 1:
                        px_array[x, y] = wall_color
        finally:
            del px_array

# --- (수정) 9. 알고리즘 실행 및 애니메이션 함수 ---
def run_algorithm(maze_surface, maze, num, cell_size, algo_name, results):
    
    if algo_name == 'dfs':
        algo_func = dfs
    elif algo_name == 'bfs':
        algo_func = bfs
    elif algo_name == 'a_star':
        algo_func = a_star
    else:
        return 

    start_time = time.perf_counter()
    parent, distance = algo_func(maze, num)
    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000
    
    results[algo_name] = (distance, duration_ms)

    path = []
    if parent is not None:
        y, x = num - 1, num - 1
        while (y, x) != (0, 0):
            path.append((y, x))
            y, x = parent[y][x]
        path.append((0, 0))
        path.reverse()

    TOTAL_ANIM_TIME = 3.0
    MIN_STEPS_PER_SEC = 200.0
    steps_per_second = MIN_STEPS_PER_SEC
    if path: 
        calculated_speed = len(path) / TOTAL_ANIM_TIME
        steps_per_second = max(MIN_STEPS_PER_SEC, calculated_speed)
        
    if num >= 150:
        steps_per_second *= 1.5 
    if num >= 200:
        steps_per_second *= 1.5

    if num * cell_size < 100:
        steps_per_second /= 2


    if num > 150: # 큰 미로는 격자 없이
        draw_func = draw_maze_fast
    else:
        draw_func = draw_maze
        
    path_index = 0
    running = True
    animation_start_time = time.time()
    
    # (신규) 스케일링된 Surface를 저장할 변수
    scaled_surface = pygame.Surface((width, height))
    
    while running:
        screen.fill(WHITE)
        
        # 1. 원본 maze_surface에 기본 미로를 그림
        draw_func(maze_surface, maze, num, cell_size) 

        # 2. 원본 maze_surface에 경로를 덧그림
        if parent is not None:
            current_time = time.time()
            elapsed_time = current_time - animation_start_time
            path_index = min(len(path), int(elapsed_time * steps_per_second))
            
            for i in range(path_index):
                py, px = path[i]
                pygame.draw.rect(maze_surface, GREEN, (px * cell_size, py * cell_size, cell_size, cell_size))

        # 3. (수정) 원본 maze_surface를 (width, height)로 스케일링
        pygame.transform.scale(maze_surface, (width, height), scaled_surface)
        
        # 4. (수정) 스케일링된 Surface를 화면 (0,0)에 blit
        screen.blit(scaled_surface, (0, 0))

        # 5. 결과 UI 렌더링
        if (parent is not None and path_index == len(path)) or (parent is None):
            if parent is None:
                main_message_text = "도달할 수 없습니다"
                sub_message_text = f"{algo_name.upper()} 수행: {duration_ms:.2f} ms"
            else:
                main_message_text = f"{algo_name.upper()}: {distance}번 만에 도착!"
                sub_message_text = f"수행 시간: {duration_ms:.2f} ms"
            
            text_surface = font.render(main_message_text, True, BLACK)
            sub_surface = small_font.render(sub_message_text, True, BLACK)
            guide_surface = small_font.render("돌아가기(B)", True, BLACK)
            
            total_h = text_surface.get_height() + sub_surface.get_height() + guide_surface.get_height() + 40
            total_w = max(text_surface.get_width(), sub_surface.get_width(), guide_surface.get_width()) + 80
            box_rect = pygame.Rect(width//2 - total_w//2, height//2 - total_h//2, total_w, total_h)
            
            pygame.draw.rect(screen, GRAY, box_rect, 0, 10)
            pygame.draw.rect(screen, BLACK, box_rect, 3, 10)
            
            screen.blit(text_surface, text_surface.get_rect(center=(box_rect.centerx, box_rect.centery - total_h/2 + 30 + text_surface.get_height()/2)))
            screen.blit(sub_surface, sub_surface.get_rect(center=(box_rect.centerx, box_rect.centery)))
            screen.blit(guide_surface, guide_surface.get_rect(center=(box_rect.centerx, box_rect.centery + total_h/2 - 30 - guide_surface.get_height()/2)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                running = False 
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()


# --- (수정) 10. main 함수 ---
def main():
    
    # (신규) 스케일링된 Surface를 미리 생성 (애니메이션과 공유)
    scaled_surface = pygame.Surface((width, height))

    while True: 
        num = input_size()
        
        cell_size = width // num 
        
        maze_pixel_size = num * cell_size
        
        maze_surface = pygame.Surface((maze_pixel_size, maze_pixel_size))
        
        maze = generate_maze(num)
        results = {} 

        # (UI 버튼 위치는 스케일링과 무관하게 고정)
        button_w, button_h = 180, 70
        gap = 20
        total_w = (button_w * 3) + (gap * 2)
        start_x = width // 2 - total_w // 2
        
        dfs_button = pygame.Rect(start_x, height // 2 - button_h // 2, button_w, button_h)
        bfs_button = pygame.Rect(start_x + button_w + gap, height // 2 - button_h // 2, button_w, button_h)
        a_star_button = pygame.Rect(start_x + (button_w + gap) * 2, height // 2 - button_h // 2, button_w, button_h)
        
        buttons = {
            'dfs': (dfs_button, "DFS"),
            'bfs': (bfs_button, "BFS"),
            'a_star': (a_star_button, "A *")
        }

        selecting = True
        while selecting:
            screen.fill(WHITE)
            
            if num > 150: 
                draw_maze_fast(maze_surface, maze, num, cell_size) 
            else:
                draw_maze(maze_surface, maze, num, cell_size)
            
            pygame.transform.scale(maze_surface, (width, height), scaled_surface)
            
            screen.blit(scaled_surface, (0, 0))
            
            # --- UI 요소들은 screen에 직접 그림 (기존과 동일) ---
            title_bg = pygame.Rect(0, 20, width, 100)
            pygame.draw.rect(screen, WHITE, title_bg, 0, 15)
            title = font.render(f"{num}x{num} 미로: 알고리즘 선택", True, BLACK)
            screen.blit(title, title.get_rect(center=title_bg.center))

            for name, (rect, text) in buttons.items():
                color = GRAY if name not in results else BLUE 
                pygame.draw.rect(screen, color, rect, 0, 10)
                text_surf = font.render(text, True, BLACK)
                screen.blit(text_surf, text_surf.get_rect(center=rect.center))

            y_offset = height // 2 + 100
            if results:
                sorted_results = sorted(results.items(), key=lambda item: item[1][1] if item[1][0] is not None else float('inf'))
                
                for name, (dist, time_ms) in sorted_results:
                    if dist is not None:
                        res_text = f"[{name.upper()}] 거리: {dist}, 시간: {time_ms:.3f} ms"
                    else:
                        res_text = f"[{name.upper()}] 경로 없음 (시간: {time_ms:.3f} ms)"
                    
                    res_surf = small_font.render(res_text, True, BLACK)
                    res_rect = res_surf.get_rect(center=(width // 2, y_offset))
                    res_bg = res_rect.inflate(20, 10)
                    pygame.draw.rect(screen, WHITE, res_bg, 0, 5)
                    screen.blit(res_surf, res_rect)
                    
                    y_offset += 35
            
            guide = small_bold_font.render("새 미로 생성 (R) | 종료 (ESC)", True, DARK_BLUE)
            screen.blit(guide, guide.get_rect(center=(width // 2, height - 30)))
            
            pygame.display.flip()

            chosen_algo = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        selecting = False 
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        for name, (rect, text) in buttons.items():
                            if rect.collidepoint(event.pos):
                                chosen_algo = name
                                break 
            
            if chosen_algo:
                run_algorithm(maze_surface, maze, num, cell_size, chosen_algo, results)


if __name__ == '__main__':
    main()