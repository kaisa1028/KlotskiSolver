import pygame
import pygame_gui
from KlotskiSolver.solver.board import Board, BlockType, Block
from KlotskiSolver.solver.solver import Solver
import numpy as np
from threading import Thread
import networkx as nx

pygame.init()

pygame.display.set_caption('Klotski Solver')
window_surface = pygame.display.set_mode((800, 600))

background = pygame.Surface((800, 600))
background.fill(pygame.Color('#111111'))

manager = pygame_gui.UIManager((800, 600))

four_square_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((60, 50), (160, 160)),
                                                  text='',
                                                  manager=manager)
two_horizontal_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((60, 230), (160, 80)), text='',
                                                     manager=manager)
two_vertical_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((240, 50), (80, 160)), text='',
                                                   manager=manager)
single_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((240, 230), (80, 80)), text='',
                                             manager=manager)
clear_blocks_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((60, 330), (260, 80)), text='Clear',
                                                   manager=manager)
calculate_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((60, 430), (260, 80)), text='Calculate',
                                                manager=manager)
prev_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((360, 450), (150, 60)), text='<<--',
                                           manager=manager)
next_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((520, 450), (150, 60)), text='-->>',
                                           manager=manager)

label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 550), (800, 50)), manager=manager, text='')
clock = pygame.time.Clock()
is_running = True

WIDTH = 4
HEIGHT = 5

x = 360
y = 50
margin = 5
length = 80

selected_block_type = None
placed_blocks = Board.standard_layout().blocks


def solver_end_condition(board: Board):
    arr = board.state[1:3, 3:5]
    return np.all(arr == 1)


solver = Solver(Board([], HEIGHT, WIDTH), solver_end_condition)
end_board_state = None
solution_path = []
solution_current_state = 0


def draw_grids():
    for i in range(WIDTH):
        for j in range(HEIGHT):
            pygame.draw.rect(window_surface, (0xc8, 0xc8, 0xc8),
                             pygame.Rect((x + i * length, y + j * length), (length - margin, length - margin)))


def draw_placed_blocks():
    for block in placed_blocks:
        left, top = block.occupying[0][0], block.occupying[0][1]
        if block.block_type == BlockType.FourSquare:
            pygame.draw.rect(window_surface, (0xc8, 0, 0),
                             pygame.Rect((x + left * length, y + top * length),
                                         (2 * length - margin, 2 * length - margin)))
        elif block.block_type == BlockType.TwoVertical:
            pygame.draw.rect(window_surface, (0xc8, 0xc8, 0),
                             pygame.Rect((x + left * length, y + top * length), (length - margin, 2 * length - margin)))
        elif block.block_type == BlockType.TwoHorizontal:
            pygame.draw.rect(window_surface, (0xc8, 0xc8, 0),
                             pygame.Rect((x + left * length, y + top * length), (2 * length - margin, length - margin)))
        elif block.block_type == BlockType.Single:
            pygame.draw.rect(window_surface, (0xc8, 0xc8, 0),
                             pygame.Rect((x + left * length, y + top * length), (length - margin, length - margin)))


def get_grid_coor():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    coor_x = (mouse_x - x) // length
    coor_y = (mouse_y - y) // length

    return coor_x, coor_y


def draw_temp_block():
    left, top = get_grid_coor()
    if selected_block_type == BlockType.FourSquare:
        left = 0 if left < 0 else WIDTH - 2 if left >= WIDTH - 2 else left
        top = 0 if top < 0 else HEIGHT - 2 if top >= HEIGHT - 2 else top
        pygame.draw.rect(window_surface, (0, 0, 0x64),
                         pygame.Rect((x + left * length, y + top * length),
                                     (2 * length - margin, 2 * length - margin)))
    elif selected_block_type == BlockType.TwoVertical:
        left = 0 if left < 0 else WIDTH - 1 if left >= WIDTH - 1 else left
        top = 0 if top < 0 else HEIGHT - 2 if top >= HEIGHT - 2 else top
        pygame.draw.rect(window_surface, (0, 0, 0x64),
                         pygame.Rect((x + left * length, y + top * length), (length - margin, 2 * length - margin)))
    elif selected_block_type == BlockType.TwoHorizontal:
        left = 0 if left < 0 else WIDTH - 2 if left >= WIDTH - 2 else left
        top = 0 if top < 0 else HEIGHT - 1 if top >= HEIGHT - 1 else top
        pygame.draw.rect(window_surface, (0, 0, 0x64),
                         pygame.Rect((x + left * length, y + top * length), (2 * length - margin, length - margin)))
    elif selected_block_type == BlockType.Single:
        left = 0 if left < 0 else WIDTH - 1 if left >= WIDTH - 1 else left
        top = 0 if top < 0 else HEIGHT - 1 if top >= HEIGHT - 1 else top
        pygame.draw.rect(window_surface, (0, 0, 0x64),
                         pygame.Rect((x + left * length, y + top * length), (length - margin, length - margin)))


def is_free(coor_x, coor_y):
    board = Board(placed_blocks, HEIGHT, WIDTH)
    return board.state[coor_x, coor_y] == 0


def has_four_square_block():
    for block in placed_blocks:
        if block.block_type == BlockType.FourSquare:
            return True
    return False


def add_block():
    global selected_block_type
    coor_x, coor_y = get_grid_coor()
    if selected_block_type == BlockType.FourSquare:
        if not has_four_square_block():
            coor_x = 0 if coor_x < 0 else WIDTH - 2 if coor_x >= WIDTH - 2 else coor_x
            coor_y = 0 if coor_y < 0 else HEIGHT - 2 if coor_y >= HEIGHT - 2 else coor_y
            if is_free(coor_x, coor_y) and is_free(coor_x + 1, coor_y) and \
                    is_free(coor_x, coor_y + 1) and is_free(coor_x + 1, coor_y + 1):
                placed_blocks.append(
                    Block([[coor_x, coor_y], [coor_x + 1, coor_y], [coor_x, coor_y + 1], [coor_x + 1, coor_y + 1]],
                          BlockType.FourSquare))
    elif selected_block_type == BlockType.TwoVertical:
        coor_x = 0 if coor_x < 0 else WIDTH - 1 if coor_x >= WIDTH - 1 else coor_x
        coor_y = 0 if coor_y < 0 else HEIGHT - 2 if coor_y >= HEIGHT - 2 else coor_y
        if is_free(coor_x, coor_y) and is_free(coor_x, coor_y + 1):
            placed_blocks.append(Block([[coor_x, coor_y], [coor_x, coor_y + 1]], BlockType.TwoVertical))
    elif selected_block_type == BlockType.TwoHorizontal:
        coor_x = 0 if coor_x < 0 else WIDTH - 2 if coor_x >= WIDTH - 2 else coor_x
        coor_y = 0 if coor_y < 0 else HEIGHT - 1 if coor_y >= HEIGHT - 1 else coor_y
        if is_free(coor_x, coor_y) and is_free(coor_x + 1, coor_y):
            placed_blocks.append(Block([[coor_x, coor_y], [coor_x + 1, coor_y]], BlockType.TwoHorizontal))
    elif selected_block_type == BlockType.Single:
        coor_x = 0 if coor_x < 0 else WIDTH - 1 if coor_x >= WIDTH - 1 else coor_x
        coor_y = 0 if coor_y < 0 else HEIGHT - 1 if coor_y >= HEIGHT - 1 else coor_y
        if is_free(coor_x, coor_y):
            placed_blocks.append(Block([[coor_x, coor_y]], BlockType.Single))
    selected_block_type = None


def calculate_solution():
    def worker():
        global solver
        global end_board_state
        global solution_current_state
        global solution_path
        solver.cancel_graph_generation()
        solver = Solver(Board(placed_blocks, HEIGHT, WIDTH), solver_end_condition)
        end_board_state = None
        solution_path = []
        solution_current_state = 0
        g, end_board_state = solver.generate_graph()
        solution_path = nx.shortest_path(g, solver.starting_layout, end_board_state)

    t = Thread(target=worker)
    t.start()


while is_running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if (event.type == pygame.MOUSEBUTTONUP and event.button == 3) or \
                (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
            selected_block_type = None
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            add_block()
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == four_square_button:
                    selected_block_type = BlockType.FourSquare
                elif event.ui_element == two_horizontal_button:
                    selected_block_type = BlockType.TwoHorizontal
                elif event.ui_element == two_vertical_button:
                    selected_block_type = BlockType.TwoVertical
                elif event.ui_element == single_button:
                    selected_block_type = BlockType.Single
                elif event.ui_element == clear_blocks_button:
                    placed_blocks = []
                elif event.ui_element == calculate_button:
                    calculate_solution()
                elif event.ui_element == prev_button:
                    solution_current_state = solution_current_state - 1 if solution_current_state > 0 else 0
                    placed_blocks = solution_path[solution_current_state].blocks
                elif event.ui_element == next_button:
                    solution_current_state = solution_current_state + 1 if solution_current_state < len(
                        solution_path) - 1 else len(solution_path) - 1
                    placed_blocks = solution_path[solution_current_state].blocks

        manager.process_events(event)

    manager.update(time_delta)

    label.set_text(
        f'{len(solver.g)} moves explored. Solution {"found" if end_board_state is not None else "not found"}')
    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    draw_grids()
    draw_temp_block()
    draw_placed_blocks()
    pygame.display.update()
