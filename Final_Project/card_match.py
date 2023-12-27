import pygame
import random
import sys
import time
from os import path
import json
# 초기화
pygame.init()
FPS = 60
clock = pygame.time.Clock()

# 화면 설정 - 풀스크린 모드
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()  # 화면의 너비와 높이를 가져옴

pygame.display.set_caption("Card Match Game!")
background_images = {}

# 음악
pygame.mixer.init()
pygame.mixer.music.load('snd/joyful-snowman.mp3')  # 음악 파일 경로
pygame.mixer.music.set_volume(0.15)  # 볼륨 설정, 0.0에서 1.0 사이
pygame.mixer.music.play(-1)  # 무한 반복 재생

# 사운드 파일 로드
error_sound = pygame.mixer.Sound('snd/error.ogg')
error_sound.set_volume(1)  # 클릭 사운드의 볼륨을 50%로 설정

click_sound = pygame.mixer.Sound('snd/click.wav')
flip_sound = pygame.mixer.Sound('snd/flip.wav')
windbell_sound = pygame.mixer.Sound('snd/wind-bell.mp3')
star_sound = pygame.mixer.Sound('snd/star.mp3')
fail_sound = pygame.mixer.Sound('snd/fail.mp3')
match_sound = pygame.mixer.Sound('snd/match.mp3')
game_start_sound = pygame.mixer.Sound('snd/game-start.mp3')


# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 폰트
font = pygame.font.Font('font/Silver.ttf', 36)

# 이미지 크기 조절
CARD_WIDTH, CARD_HEIGHT = 130, 172
CARD_GAP = 20  # 카드 간격

y = HEIGHT - 150  # 버튼을 하단에 위치


# 나가기 버튼 이미지 로드
exit_button_image = pygame.image.load("img/close.png")
exit_button_rect = exit_button_image.get_rect(
    topleft=(WIDTH - exit_button_image.get_width(), 0))


matched_pairs = set()  # 맞춘 카드의 쌍을 저장하는 집합
flipped_cards = []  # 현재 뒤집힌 카드를 저장하는 리스트
flip_count = 0  # 현재 턴에서 뒤집은 카드의 개수를 저장하는 변수
selected_level = None
total_flips = 0
current_level = "Level 1"
# 종료 버튼 그리기 함수

# 이미지 파일명을 리스트로 저장
image_files = [f'img/tutorial/{str(i).zfill(3)}.png' for i in range(1, 7)]
images = [pygame.transform.scale(pygame.image.load(
    image_file), (WIDTH, HEIGHT)) for image_file in image_files]


def draw_exit_button(screen):
    screen.blit(exit_button_image, exit_button_rect)
 # 텍스트 그리기


def load_card_images(level):
    global current_level
    image_paths = []
    if level == "Level 1":
        for i in range(1, 6):
            image_paths.append(
                (f"img/level1/card{i}", f"img/level1/card{i}.png"))
            current_level = 1
    elif level == "Level 2":
        for i in range(1, 9):
            image_paths.append(
                (f"img/level2/card{i}", f"img/level2/card{i}.png"))
            current_level = 2
    elif level == "Level 3":
        for i in range(1, 13):
            image_paths.append(
                (f"img/level3/card{i}", f"img/level3/card{i}.png"))
            current_level = 3
    card_images = {name: pygame.transform.scale(pygame.image.load(
        path), (CARD_WIDTH, CARD_HEIGHT)) for name, path in image_paths}
    return card_images


def initialize_board():
    global board, cards, card_images, card_back, start_x, start_y
    draw_exit_button(screen)

    # 선택된 레벨에 따라 카드 세트 조정 및 열과 행 결정
    if selected_level == "Level 1":
        cards = [f"img/level1/card{i}" for i in range(1, 6)] * 2
        cols, rows = 5, 2
        card_back = "img/level1/card_back.png"
    elif selected_level == "Level 2":
        cards = [f"img/level2/card{i}" for i in range(1, 9)] * 2
        cols, rows = 4, 4
        card_back = "img/level2/card_back.png"
    elif selected_level == "Level 3":
        cards = [f"img/level3/card{i}" for i in range(1, 13)] * 2
        cols, rows = 6, 4
        card_back = "img/level3/card_back.png"

    card_back = pygame.transform.scale(
        pygame.image.load(card_back), (CARD_WIDTH, CARD_HEIGHT))
    random.shuffle(cards)

    total_card_width = cols * CARD_WIDTH + (cols - 1) * CARD_GAP
    total_card_height = rows * CARD_HEIGHT + (rows - 1) * CARD_GAP

    start_x = (WIDTH - total_card_width) // 2
    start_y = (HEIGHT - total_card_height) // 2

    card_images = load_card_images(selected_level)

    board = [(card, True) for card in cards]

    draw_all_cards(screen)
    pygame.display.flip()
    pygame.time.delay(3000)
    game_start_sound.play()
    show_message("Start!", screen, duration=450)

    board = [(card, False) for card in cards]


# 버튼 텍스트
def load_background_images():
    global background_images
    for level in range(1, 4):  # Level 1부터 Level 3까지
        background_image = pygame.image.load(
            f"img/back_ground/level{level}.png")
        background_image = pygame.transform.scale(
            background_image, (WIDTH, HEIGHT))
        background_images[f"Level {level}"] = background_image


def set_background(level):
    level_key = f"Level {level}"
    screen.blit(background_images[level_key], (0, 0))


def draw_text_in_button(text, button_rect, font, screen):
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.center = button_rect.center
    screen.blit(text_surface, text_rect)
# 카드 위치 계산 함수


def calculate_card_position(card_index, level):
    if level == "Level 1":
        cols = 5
        rows = 2
    elif level == "Level 2":
        cols = 4
        rows = 4
    elif level == "Level 3":
        cols = 6
        rows = 4

    col = card_index % cols
    row = card_index // cols
    x = start_x + col * (CARD_WIDTH + CARD_GAP)
    y = start_y + row * (CARD_HEIGHT + CARD_GAP)
    return (x, y)


# 카드 플립효과


def flip_animation(card_index, screen, board):

    # 카드의 위치 계산
    card_pos = calculate_card_position(card_index, selected_level)

    # 카드를 좌우로 뒤집는 애니메이션
    for scale in list(range(CARD_WIDTH, 0, -9)) + list(range(0, CARD_WIDTH, 9)):
        # 여기에 애니메이션 관련 코드를 작성

        # 해당 카드를 제외하고 모든 카드를 그림
        draw_all_cards_except(screen, board, [card_index])
        card = board[card_index][0]
        scaled_card = pygame.transform.scale(
            card_images[card], (scale, CARD_HEIGHT))
        draw_exit_button(screen)
        display_flip_count(screen)
        screen.blit(scaled_card, card_pos)
        pygame.display.flip()

    # 카드 상태 업데이트
    board[card_index] = (card, not board[card_index][1])


def match_animation(card_indices, screen, board):
    # 각 카드의 원본 이미지와 위치 가져오기

    original_images = [card_images[board[index][0]] for index in card_indices]
    original_sizes = [image.get_size() for image in original_images]
    card_positions = [calculate_card_position(
        index, selected_level) for index in card_indices]

    # 크기를 점차 줄여가며 애니메이션 표시
    for scale_factor in range(100, 0, -8):  # 100%에서 0%까지 5%씩 감소
        draw_all_cards_except(screen, board, card_indices)  # 리스트로 전달

        for i, index in enumerate(card_indices):
            scaled_size = (int(original_sizes[i][0] * scale_factor / 100),
                           int(original_sizes[i][1] * scale_factor / 100))
            if scaled_size[0] > 0 and scaled_size[1] > 0:
                scaled_card = pygame.transform.scale(
                    original_images[i], scaled_size)
                pos_x = card_positions[i][0] + \
                    (original_sizes[i][0] - scaled_size[0]) // 2
                pos_y = card_positions[i][1] + \
                    (original_sizes[i][1] - scaled_size[1]) // 2
                draw_exit_button(screen)
                display_flip_count(screen)
                screen.blit(scaled_card, (pos_x, pos_y))

        pygame.display.flip()
        # pygame.time.delay(2)

    # 애니메이션 완료 후 카드 상태 업데이트
    for index in card_indices:
        card = board[index][0]
        board[index] = (card, not board[index][1])


def draw_all_cards_except(screen, board, except_indices):
    set_background(current_level)
    if not isinstance(except_indices, list):
        except_indices = [except_indices]

    for i, (card, flipped) in enumerate(board):
        if card in matched_pairs or i in except_indices:
            continue  # 매치된 카드 또는 현재 애니메이션 대상 카드는 건너뛰기

        x, y = calculate_card_position(i, selected_level)
        card_image = card_images[card] if flipped else card_back

        screen.blit(card_image, (x, y))


# 페이드 아웃 애니메이션


def fade_out_animation(screen):
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill((0, 0, 0))
    for alpha in range(0, 255, 5):  # Increase alpha to fade out
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(20)

# 메인메뉴


def level_selection_menu():
    global selected_level, card_images
    # 레벨 선택 버튼 이미지 로드
    level_button_images = {
        "Level 1": pygame.image.load("img/button/level1.png"),
        "Level 2": pygame.image.load("img/button/level2.png"),
        "Level 3": pygame.image.load("img/button/level3.png")
    }

    button_spacing = 80
    total_buttons_width = (128 + button_spacing) * \
        len(level_button_images) - button_spacing
# 시작 위치 계산 (화면 중앙에 버튼을 배치하기 위해)
    start_x = (WIDTH - total_buttons_width) // 2
    y_position = HEIGHT // 2  # 하단에 100px 여백

    # 버튼 위치 설정
    button_positions = {}
    for i, name in enumerate(level_button_images):
        x = start_x + i * (128 + button_spacing)
        button_positions[name] = (x, y_position)

    font = pygame.font.Font('font/Silver.ttf', 60)

    while True:
        screen.fill((246, 238, 222))
        text = font.render("Choose the level of the game", True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, 300))
        screen.blit(text, text_rect)
        for name, pos in button_positions.items():
            screen.blit(level_button_images[name], pos)

        # 나가기 버튼 그리기
        draw_exit_button(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                # Check if exit button is clicked
                if exit_button_rect.collidepoint(x, y):
                    click_sound.play()
                    return  # Return to the main menu
                for name, pos in button_positions.items():
                    button_rect = pygame.Rect(
                        pos, level_button_images[name].get_size())
                    if button_rect.collidepoint(x, y):
                        click_sound.play()
                        fade_out_animation(screen)
                        selected_level = name  # Store the selected level
                        set_current_background(selected_level)  # 현재 배경 설정
                        card_images = load_card_images(
                            selected_level)  # 이미지 로드
                        return


def main_menu():
    global selected_level
    # 버튼 이미지 로드
    button_images = {
        "how": pygame.image.load("img/button/how.png"),
        "save": pygame.image.load("img/button/save.png"),
        "play": pygame.image.load("img/button/play.png"),
        "exit": pygame.image.load("img/button/exit.png")
    }
    button_spacing = 50
    total_buttons_width = (80 + button_spacing) * \
        len(button_images) - button_spacing
# 시작 위치 계산 (화면 중앙에 버튼을 배치하기 위해)
    start_x = (WIDTH - total_buttons_width) // 2
    y_position = HEIGHT - 80 - 100  # 하단에 100px 여백

    # 버튼 위치 설정
    button_positions = {}
    for i, name in enumerate(button_images):
        x = start_x + i * (80 + button_spacing)
        button_positions[name] = (x, y_position)

# title.png 이미지 로드
    title_background = pygame.image.load("img/title.png")
    title_background = pygame.transform.scale(
        title_background, (WIDTH, HEIGHT))

    while True:
        font = pygame.font.Font('font/Silver.ttf', 100)
        # 기본 메시지 렌더링
        text1 = font.render("Miss! Match!", True, WHITE)
        text2 = font.render("Card Game", True, WHITE)

        text_rect1 = text1.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 - 20))  # 메시지 위치 조정

        text_rect2 = text2.get_rect(
            center=(WIDTH // 2, HEIGHT // 2+80))  # 메시지 위치 조정

        screen.blit(title_background, (0, 0))
        screen.blit(text1, text_rect1)
        screen.blit(text2, text_rect2)

        # 각 버튼 이미지를 화면에 그리기
        for name, pos in button_positions.items():
            screen.blit(button_images[name], pos)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                for name, pos in button_positions.items():
                    button_rect = pygame.Rect(
                        pos, button_images[name].get_size())
                    if button_rect.collidepoint(x, y):
                        click_sound.play()
                        # 버튼별로 다른 동작 실행
                        if name == "play":
                            fade_out_animation(screen)
                            level_selection_menu()
                            if selected_level:
                                fade_out_animation(screen)
                                initialize_board()
                                game_loop()
                        elif name == "how":
                            fade_out_animation(screen)
                            # Tutorial 화면
                            for img in images:
                                screen.blit(img, (0, 0))  # 이미지를 화면에 그림
                                pygame.display.flip()  # 화면 업데이트
                                pygame.time.delay(1500)  # 2초 동안 대기
                                fade_out_animation(screen)  # 2초 동안 대기

                            pass
                        elif name == "save":

                            fade_out_animation(screen)
                            display_saved_data()
                            # Rank 화면
                            pass
                        elif name == "exit":
                            pygame.quit()
                            sys.exit()
        clock.tick(FPS)


# 게임 루프


def show_message(message, screen, duration=450):
    font = pygame.font.Font('font/Silver.ttf', 36)
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, 50))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(duration)


def end_message(message, screen, duration=850):
    font = pygame.font.Font('font/Silver.ttf', 50)
    # 기본 메시지 렌더링
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(
        center=(WIDTH // 2, HEIGHT // 2 - 30))  # 메시지 위치 조정

    # 카드 뒤집기 횟수 메시지 렌더링
    flip_count_text = f"Total Flips: {total_flips}"
    flip_count_surface = font.render(flip_count_text, True, BLACK)
    flip_count_rect = flip_count_surface.get_rect(
        center=(WIDTH // 2, HEIGHT // 2 + 30))  # 횟수 위치 조정

    # 화면에 메시지와 카드 뒤집기 횟수 표시
    screen.blit(text, text_rect)
    screen.blit(flip_count_surface, flip_count_rect)
    pygame.display.flip()
    pygame.time.delay(duration)


def display_flip_count(screen):

    font = pygame.font.Font('font/Silver.ttf', 40)
    flip_text = f"Flip Count: {total_flips}"
    text_surface = font.render(flip_text, True, BLACK)
    screen.blit(text_surface, (10, 10))  # 화면의 적절한 위치에 표시


def draw_all_cards(screen):
    # screen.fill(WHITE)  # 화면 지우기
    set_background(current_level)
    draw_exit_button(screen)
    display_flip_count(screen)
    for i, (card, flipped) in enumerate(board):
        if card in matched_pairs:
            continue  # 매칭된 카드는 건너뛰기

        x, y = calculate_card_position(i, selected_level)

        if flipped:
            # 뒤집힌 카드 그리기
            screen.blit(card_images[card], (x, y))
        else:
            # 뒤집히지 않은 카드 그리기
            screen.blit(card_back, (x, y))

    pygame.display.flip()


def display_saved_data():
    # 레벨 3의 배경을 현재 배경으로 설정

    current_background = background_images["Level 3"]
    """저장된 오너먼트와 배경의 화면을 표시합니다."""
    try:
        with open("decorations_positions.json", "r") as f:
            decorations_positions = json.load(f)
    except FileNotFoundError:
        print("No saved data found.")
        return

    # 배경과 트리 이미지 로드
    tree_image = pygame.image.load("img/tree.png")
    tree_image_rect = tree_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    # 저장된 오너먼트 이미지 로드
    decorations = load_decorations()

    # 화면을 새로 준비하고 배경, 트리, 오너먼트를 표시
    screen.fill(WHITE)
    screen.blit(current_background, (0, 0))  # 현재 배경 설정
    draw_exit_button(screen)

    screen.blit(tree_image, tree_image_rect)  # 트리 이미지 그리기

    font = pygame.font.Font('font/Silver.ttf', 50)  # 폰트 설정
    text = font.render("* Merry Christmas *", True,
                       (255, 0, 0))  # 빨간색으로 텍스트 렌더링
    text_rect = text.get_rect(center=(WIDTH // 2, 40))  # 중앙 상단에 위치
    screen.blit(text, text_rect)

    for name, pos in decorations_positions.items():
        screen.blit(decorations[name], pos)

    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if exit_button_rect.collidepoint(x, y):
                    click_sound.play()

                    running = False
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()


def game_loop():

    global flipped_cards, flip_count, board, matched_pairs
    flip_count = 0
    running = True
    display_flip_count(screen)
    draw_exit_button(screen)
    global total_flips
    # set_background(current_level)
    while running:
        # set_background(current_level)
        draw_all_cards(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:

                x, y = pygame.mouse.get_pos()

                if exit_button_rect.collidepoint(x, y):
                    click_sound.play()

                    running = False

                if selected_level == "Level 1":
                    cols, rows = 5, 2
                elif selected_level == "Level 2":
                    cols, rows = 4, 4
                elif selected_level == "Level 3":
                    cols, rows = 6, 4

                relative_x = x - start_x
                relative_y = y - start_y
                if len(flipped_cards) == 2:
                    card1_index, card2_index = flipped_cards
                    card1 = board[card1_index][0]
                    card2 = board[card2_index][0]
                    total_flips += 1
                if 0 <= relative_x < cols * (CARD_WIDTH + CARD_GAP) and 0 <= relative_y < rows * (CARD_HEIGHT + CARD_GAP):
                    card_index = (relative_y // (CARD_HEIGHT + CARD_GAP)) * \
                        cols + (relative_x // (CARD_WIDTH + CARD_GAP))

                    # Check if the clicked card is already matched
                    if board[card_index][0] in matched_pairs:
                        continue

                    # Check if the card is already flipped or matched
                    if card_index in matched_pairs or card_index in flipped_cards:
                        continue
                    flip_sound.play()
                    display_flip_count(screen)

                    flip_animation(card_index, screen, board)
                    flipped_cards.append(card_index)

                    board[card_index] = (cards[card_index], True)

                    flip_count += 1

                    if flip_count == 2:
                        card1_index, card2_index = flipped_cards
                        card1 = board[card1_index][0]
                        card2 = board[card2_index][0]
                        total_flips += 1

                        if card1 == card2:
                            match_sound.play()
                            matched_pairs.add(card1)
                            show_message("Match!", screen)
                            pygame.time.delay(400)
                            match_animation(
                                [card1_index, card2_index], screen, board)
                            flipped_cards = []  # 매치된 카드는 다시 클릭할 수 없도록 flipped_cards 비우기
                        else:
                            error_sound.play()
                            show_message("Miss!", screen)
                            pygame.time.delay(500)
                            flip_sound.play()
                            flip_animation(card1_index, screen, board)
                            flip_sound.play()
                            flip_animation(card2_index, screen, board)

                            board[card1_index] = (card1, False)
                            board[card2_index] = (card2, False)

                        flip_count = 0
                        flipped_cards = []

                    if len(matched_pairs) == len(cards) // 2:
                        end_message("Game Over!", screen)
                        fade_out_animation(screen)
                        running = False

                        game_over()

        # draw_exit_button(screen)
        # display_flip_count(screen)
        pygame.display.flip()
        clock.tick(FPS)

    flipped_cards = []
    flip_count = 0
    matched_pairs = set()
    total_flips = 0


def calculate_stars(level, total_flips):
    if level == "Level 1":
        card_count = 5
    elif level == "Level 2":
        card_count = 8
    elif level == "Level 3":
        card_count = 12

    if total_flips <= card_count:
        return 3
    elif card_count + 1 <= total_flips <= card_count + 3:
        return 2
    elif card_count + 4 <= total_flips <= card_count + 6:
        return 1
    else:
        return 0


def display_stars(screen, num_stars):
    star_image = pygame.image.load("img/Star/star.png")
    empty_star_image = pygame.image.load("img/Star/empty_star.png")
    font = pygame.font.Font('font/Silver.ttf', 60)
    total_stars = 3  # 전체 별의 개수
    star_spacing = 120  # 별들 사이의 간격

    star_width = star_image.get_width()

    total_width = star_width * total_stars + star_spacing * (total_stars - 1)
    start_x = (WIDTH - total_width) // 2

    for i in range(total_stars):
        x = start_x + i * (star_width + star_spacing)
        if i < num_stars:
            screen.blit(star_image, (x, HEIGHT // 2 + 30))
        else:
            screen.blit(empty_star_image, (x, HEIGHT // 2 + 30))
    if num_stars == 0:
        fail_sound.play()
        text = font.render("Fail !!", True, WHITE)

    else:
        star_sound.play()
        if num_stars == 1:

            text = font.render("Good !!", True, WHITE)

        elif num_stars == 2:
            text = font.render("Excellent !!", True, WHITE)

        elif num_stars == 3:
            text = font.render("Perfect Score!!", True, WHITE)

    text_rect = text.get_rect(center=(WIDTH // 2, 360))
    screen.blit(text, text_rect)


def game_over():
    global current_background
    num_stars = calculate_stars(selected_level, total_flips)
    display_stars(screen, num_stars)
    pygame.display.flip()
    pygame.time.delay(2000)
    fade_out_animation(screen)

    # 새로운 오너먼트 생성 및 배치
    decorations = load_decorations()
    selected_decorations = select_random_decorations(decorations, num_stars)
    decorations_positions = load_decorations_positions()
    new_decorations_positions = update_new_decorations_positions(
        selected_decorations)
    decorations_positions.update(new_decorations_positions)  # 기존 위치 정보 업데이트
    save_decorations_positions(decorations_positions)

    # 오너먼트 배치 화면 표시
    display_decorations_screen(
        decorations, decorations_positions, list(new_decorations_positions.keys()))
    print("gameover")
# 오너먼트 위치 업데이트 함수


def update_new_decorations_positions(new_decorations):
    """새로운 오너먼트의 위치를 생성 및 업데이트합니다."""
    new_positions = {}
    x, y = 0, 0  # 초기 위치 설정 (왼쪽 상단)
    spacing = 25  # 오너먼트 간 간격

    for name, image in new_decorations:
        new_positions[name] = [x, y]
        x += image.get_width() + spacing  # 다음 오너먼트의 x 위치 업데이트

        # 오너먼트가 화면의 오른쪽 끝에 도달하면 다음 행으로 이동
        if x + image.get_width() > WIDTH:
            x = 0
            y += image.get_height() + spacing  # y 위치 업데이트

    return new_positions


current_background = None

# 이전에 선택한 레벨의 배경을 설정하는 함수


def set_current_background(level):
    global current_background
    current_background = background_images[f"{level}"]

# 오너먼트 배치 화면 표시 함수


def display_decorations_screen(decorations, positions, new_decorations_names):
    global current_background  # 전역 변수 사용 선언
    selected_decoration = None
    running = True
    mouse_offset_x = 0
    mouse_offset_y = 0
    tree_image = load_tree_image()  # tree.png 이미지 로드
    tree_width, tree_height = tree_image.get_size()
    tree_x = (WIDTH - tree_width) // 2
    tree_y = (HEIGHT - tree_height) // 2
    windbell_sound.play()
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 나가기 버튼 확인
                for name in new_decorations_names:  # 새 오너먼트만 선택 가능
                    pos = positions[name]
                    ornament_rect = pygame.Rect(
                        pos, decorations[name].get_size())
                    if ornament_rect.collidepoint(event.pos):
                        click_sound.play()
                        selected_decoration = name
                        mouse_offset_x = pos[0] - event.pos[0]
                        mouse_offset_y = pos[1] - event.pos[1]
                        break
                if exit_button_rect.collidepoint(event.pos):
                    click_sound.play()
                    running = False
                    # pygame.quit()
                    # sys.exit()

            elif event.type == pygame.MOUSEBUTTONUP:
                selected_decoration = None
            elif event.type == pygame.MOUSEMOTION and selected_decoration:
                positions[selected_decoration] = [event.pos[0] +
                                                  mouse_offset_x, event.pos[1] + mouse_offset_y]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:  # 'S' 키를 누르면 저장 후 종료
                    save_decorations_positions(positions)
                    running = False

                    # pygame.quit()
                    # sys.exit()

        if current_background:  # 현재 배경 이미지가 존재하는지 확인
            screen.blit(current_background, (0, 0))  # 현재 레벨의 배경 설정
        # tree.png 이미지 위치 설정
        font = pygame.font.Font('font/Silver.ttf', 30)  # 폰트 설정
        text = font.render("Press the 's' key to save and end the game....", True,
                           (0, 0, 0))  # 빨간색으로 텍스트 렌더링
        text_rect = text.get_rect(center=(WIDTH // 2, 40))  # 중앙 상단에 위치
        screen.blit(text, text_rect)

        screen.blit(tree_image, (tree_x, tree_y))

        for name, pos in positions.items():
            screen.blit(decorations[name], pos)
        draw_exit_button(screen)  # 나가기 버튼 그리기
        pygame.display.flip()
    windbell_sound.stop()
    save_decorations_positions(positions)
    print("display")


def load_tree_image():
    return pygame.image.load("img/tree.png")


def load_decorations():
    """오너먼트 이미지를 로드."""
    ornaments = {}
    for i in range(1, 9):
        image = pygame.image.load(f"img/ornament/o{i}.png")
        ornaments[f"o{i}"] = image
    return ornaments


def save_decorations_positions(positions):
    """오너먼트의 위치를 저장"""
    with open("decorations_positions.json", "w") as f:
        json.dump(positions, f)


def load_decorations_positions():
    """저장된 오너먼트 위치"""
    try:
        with open("decorations_positions.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def select_random_decorations(decorations, num_stars):
    """랜덤으로 오너먼트를 선택"""
    return random.sample(list(decorations.items()), num_stars)


if __name__ == "__main__":

    load_background_images()
    selected_menu = main_menu()
