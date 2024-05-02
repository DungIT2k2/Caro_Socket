import pygame
from caro_game.settings import WINDOW_HEIGHT, WINDOW_WIDTH, TILE_SIZE, EDITOR_DATA, LINE_COLOR, TICK_SOUND_X, TICK_SOUND_O, DRAW_WIN, GAME_SOUNDS
from pygame.math import Vector2 as vector
from pygame.mouse import get_pressed as mouse_button
from pygame.mouse import get_pos as mouse_pos

class Game():
    def __init__(self, username, competitor_name, is_host):
        self.username = username
        self.competitor_name = competitor_name
        self.score_username = 0
        self.score_competitor_name = 0
        self.is_host = is_host

        self.display_surface = pygame.display.get_surface()
        self.origin = vector()
        self.pain_active = False
        self.pain_offset = vector()
        # support line
        self.support_line_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.canvas_data = {}
        self.last_selected_cell = None
        self.selection_index = 'x'

        self.playing = True
        self.flag_playing = True

        #check enter
        self.alert_displayed = False

    def get_current_cell(self):
        distance_to_origin = vector(mouse_pos()) - self.origin
        if distance_to_origin.x > 0:
            col = int(distance_to_origin.x / TILE_SIZE)
        else:
            col = int(distance_to_origin.x / TILE_SIZE) - 1

        if distance_to_origin.y > 0:
            row = int(distance_to_origin.y / TILE_SIZE)
        else:
            row = int(distance_to_origin.y / TILE_SIZE) - 1

        return col, row

    def pan_input(self, event):
        # kéo chuột phải
        if event.type == pygame.locals.MOUSEBUTTONDOWN and mouse_button()[2]:
            self.pain_active = True
            # self.pain_offset = vector(mouse_pos()) - self.origin

        if not mouse_button()[2]:
            self.pain_active = False
        # Lăn chuột
        # if event.type == pygame.MOUSEWHEEL:
        #     if pygame.key.get_pressed()[pygame.K_LCTRL]:
        #         self.origin.y -= event.y * 50
        #     else:
        #         self.origin.x -= event.y * 50
        # if self.pain_active:
        #     self.origin = vector(mouse_pos()) - self.pain_offset

    def play_again(self):
        # Xóa bảng chơi và bắt đầu trò chơi mới
        if self.alert_displayed:
            self.canvas_data.clear()
            self.playing = True
            self.flag_playing = True
            self.last_selected_cell = None
            self.alert_displayed = False

    def draw_board(self):
        cols = WINDOW_WIDTH // TILE_SIZE
        rows = WINDOW_HEIGHT // TILE_SIZE
        
        offset_vector = vector(
            x=self.origin.x - int(self.origin.x / TILE_SIZE) * TILE_SIZE,
            y=self.origin.y - int(self.origin.y / TILE_SIZE) * TILE_SIZE
        )
        self.support_line_surf.fill('white')
        # (Lặp vô hạn)
        # cols + 1 
        # rows + 1
        for col in range(cols + 1):
            x = offset_vector.x + col * TILE_SIZE
            pygame.draw.line(self.support_line_surf, LINE_COLOR,
                             (x, 0), (x, WINDOW_HEIGHT))

        for row in range(rows + 1):
            y = offset_vector.y + row * TILE_SIZE
            pygame.draw.line(self.support_line_surf, LINE_COLOR,
                             (0, y), (WINDOW_WIDTH, y))

        self.display_surface.blit(self.support_line_surf, (0, 0))

    def left_mouse_click(self, x, y):
        if (x, y) != self.last_selected_cell:
            if (x, y) not in self.canvas_data:
                self.canvas_data[(x, y)] = CanvasTile(self.selection_index)
                if self.selection_index == 'x':
                    GAME_SOUNDS.play(TICK_SOUND_X)
                else:
                    GAME_SOUNDS.play(TICK_SOUND_O)
            else:
                return False
            self.last_selected_cell = (x, y)
            self.selection_index = self.canvas_data[(x, y)].get_not_cell()
            if self.check_win((x, y)):
                self.playing = False
                self.alert_winning((x, y))
            return True
        return False

    def draw(self):
        for pos, item in self.canvas_data.items():
            if pos == self.last_selected_cell:
                border_color = (255, 0, 0)
                surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
                surface.fill((255, 255, 255))
                pygame.draw.rect(surface, border_color,
                                 (0, 0, TILE_SIZE, TILE_SIZE), 2)
                self.display_surface.blit(
                    surface, self.origin + vector(pos) * TILE_SIZE)
            current_pos = self.origin + \
                vector(pos) * TILE_SIZE + vector(TILE_SIZE/8, TILE_SIZE/8)
            if item.has_x:
                image = pygame.image.load(EDITOR_DATA[0]['image'])
                self.display_surface.blit(image, current_pos)
            if item.has_o:
                image = pygame.image.load(EDITOR_DATA[1]['image'])
                self.display_surface.blit(image, current_pos)

    def check_neighbors_cell(self, new_cell, current_index):
        if new_cell not in self.canvas_data:
            return False
        if self.canvas_data[new_cell].get_cell() != current_index:
            return False
        return True

    # theo hàng dọc
    def check_winning_vertical(self, current_cell):
        if current_cell not in self.canvas_data: return False
        current_index = self.canvas_data[current_cell].get_cell()
        # print(current_index)
        check_flag = 1

        # Check top
        neighbor_row_start = current_cell[1] - 1
        new_cell = (current_cell[0],neighbor_row_start)
        while neighbor_row_start >= current_cell[1] - 4 and check_flag != 5:
            if not self.check_neighbors_cell(new_cell, current_index):
                break
            neighbor_row_start -= 1
            check_flag += 1
            new_cell = (current_cell[0],neighbor_row_start)

        #check bottom
        neighbor_row_end = current_cell[1] + 1
        new_cell = (current_cell[0],neighbor_row_end)
        while neighbor_row_end <= current_cell[1] + 4 and check_flag != 5:
            if not self.check_neighbors_cell(new_cell, current_index):
                break
            neighbor_row_end += 1
            check_flag += 1
            new_cell = (current_cell[0],neighbor_row_end)

        if check_flag == 5:
            self.draw_player_winning_vertical(neighbor_row_start,neighbor_row_end -1)
            return True
        return False
    
    #check theo hàng ngàng  
    def check_winning_horizontal(self, current_cell):
        if current_cell not in self.canvas_data: return False
        current_index = self.canvas_data[current_cell].get_cell()
        # print(current_index)
        check_flag = 1

        # Check left
        neighbor_col_start = current_cell[0] - 1
        new_cell = (neighbor_col_start, current_cell[1])
        while neighbor_col_start >= current_cell[0] - 4 and check_flag != 5:
            if not self.check_neighbors_cell(new_cell, current_index):
                break
            neighbor_col_start -= 1
            check_flag += 1
            new_cell = (neighbor_col_start, current_cell[1])

        #check right
        neighbor_col_end = current_cell[0] + 1
        new_cell = (neighbor_col_end, current_cell[1])
        while neighbor_col_end <= current_cell[0] + 4 and check_flag != 5:
            if not self.check_neighbors_cell(new_cell, current_index):
                break
            neighbor_col_end += 1
            check_flag += 1
            new_cell = (neighbor_col_end, current_cell[1])

        if check_flag == 5:
            self.draw_player_winning_horizontal(neighbor_col_start,neighbor_col_end -1)
            return True
        return False

    #đường chéo chính
    def check_winning_main_diagonal(self, current_cell):
        if current_cell not in self.canvas_data: return False
        current_index = self.canvas_data[current_cell].get_cell()
        # print(current_index)
        check_flag = 1
        # Check top left
        neighbor_col = current_cell[0] - 1
        neighbor_row = current_cell[1] - 1
        new_cell = (neighbor_col, neighbor_row)
        while neighbor_col >= current_cell[0] - 4:
            if check_flag == 5 or not self.check_neighbors_cell(new_cell, current_index):
                break
            neighbor_col -= 1
            neighbor_row -= 1
            check_flag += 1
            new_cell = (neighbor_col, neighbor_row)

        new_cell_start = new_cell
        #check down right
        neighbor_col = current_cell[0] + 1
        neighbor_row = current_cell[1] + 1
        new_cell = (neighbor_col, neighbor_row)
        while neighbor_col <= current_cell[0] + 4:
            if check_flag == 5 or not self.check_neighbors_cell(new_cell, current_index):
                break
            neighbor_col += 1
            neighbor_row += 1
            check_flag += 1
            new_cell = (neighbor_col, neighbor_row)
        new_cell_end = new_cell

        if check_flag == 5:
            self.draw_player_winning_main_draw_player_winning_auxiliary_diagonal_diagonal(new_cell_start, new_cell_end - vector(1, 1))
            return True
        return False
    
    #đường chéo phụ
    def check_winning_auxiliary_diagonal(self, current_cell):
        if current_cell not in self.canvas_data: return False
        current_index = self.canvas_data[current_cell].get_cell()
        # print(current_index)
        check_flag = 1

        # Check top left
        neighbor_col = current_cell[0] - 1
        neighbor_row = current_cell[1] + 1
        new_cell = (neighbor_col, neighbor_row)
        while neighbor_col >= current_cell[0] - 4:
            if check_flag == 5 or not self.check_neighbors_cell(new_cell, current_index):
                break
            neighbor_col -= 1
            neighbor_row += 1
            check_flag += 1
            new_cell = (neighbor_col, neighbor_row)
        new_cell_start = new_cell
        #check down right
        neighbor_col = current_cell[0] + 1
        neighbor_row = current_cell[1] - 1
        new_cell = (neighbor_col, neighbor_row)
        while neighbor_col <= current_cell[0] + 4:
            if check_flag == 5 or not self.check_neighbors_cell(new_cell, current_index):
                break
            neighbor_col += 1
            neighbor_row -= 1
            check_flag += 1
            new_cell = (neighbor_col, neighbor_row)
        new_cell_end = new_cell
        if check_flag == 5:
            self.draw_player_winning_main_draw_player_winning_auxiliary_diagonal_diagonal(new_cell_start - vector(0, 1), new_cell_end - vector(1, 0))
            return True
        return False

    #vẽ hàng ngang
    def draw_player_winning_horizontal(self, start_point, end_point):
        start_pos = self.origin + vector(start_point, self.last_selected_cell[1]) * TILE_SIZE + vector(TILE_SIZE, TILE_SIZE/2)
        end_pos = self.origin + vector(end_point, self.last_selected_cell[1]) * TILE_SIZE + vector(TILE_SIZE, TILE_SIZE/2)
        pygame.draw.line(self.display_surface, (255, 0, 0), start_pos, end_pos, 3)
    
    #vẽ hàng dọc
    def draw_player_winning_vertical(self, start_point, end_point):
        start_pos = self.origin + vector(self.last_selected_cell[0], start_point) * TILE_SIZE + vector(TILE_SIZE/2, TILE_SIZE)
        end_pos = self.origin + vector(self.last_selected_cell[0], end_point) * TILE_SIZE + vector(TILE_SIZE/2, TILE_SIZE)
        pygame.draw.line(self.display_surface, (255, 0, 0), start_pos, end_pos, 3)
    
    # vẽ đường chéo chính , đường chéo phụ
    def draw_player_winning_main_draw_player_winning_auxiliary_diagonal_diagonal(self, start_point, end_point):
        start_pos = self.origin + vector(start_point[0], start_point[1]) * TILE_SIZE + vector(TILE_SIZE, TILE_SIZE)
        end_pos = self.origin + vector(end_point[0], end_point[1]) * TILE_SIZE + vector(TILE_SIZE, TILE_SIZE)
        pygame.draw.line(self.display_surface, (255, 0, 0), start_pos, end_pos, 3)

    def check_win(self, current_cell):
        if self.check_winning_horizontal(current_cell) or self.check_winning_vertical(current_cell) or self.check_winning_main_diagonal(current_cell) or self.check_winning_auxiliary_diagonal(current_cell):
            return True
        if current_cell is not None:
            self.alert_turn(current_cell)
        else:
            self.alert_turn(None)
        return False

    def alert_winning(self, current_cell):
        self.alert_displayed = True
        if self.canvas_data[current_cell].get_cell() == 'x':
            if self.is_host:
                _str = f'{str(self.username)} wins! Enter to Play again.'
            else:
                _str = f'{str(self.competitor_name)} wins! Enter to Play again.'
        else:
            if self.is_host:
                _str = f'{str(self.competitor_name)} wins! Enter to Play again.'
            else:
                _str = f'{str(self.username)} wins! Enter to Play again.'

        font = pygame.font.Font(None, 36)
        text = font.render(_str, 1, (255,255, 255))
        text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))

        # Draw border around text
        border_rect = text_rect.inflate(10, 10)
        pygame.draw.rect(self.display_surface, (0, 0, 0, 0.3), border_rect)

        # Draw text
        self.display_surface.blit(text, text_rect)
        
    def alert_turn(self, current_cell):
        if current_cell is not None:
            if self.canvas_data[current_cell].get_cell() == 'x':
                if self.is_host:
                    _str = f"{str(self.competitor_name)}'s Turn"
                else:
                    _str = f"{str(self.username)}'s Turn"
            else:
                if self.is_host:
                    _str = f"{str(self.username)}'s Turn"
                else:
                    _str = f"{str(self.competitor_name)}'s Turn"
        else:
            if self.selection_index == 'x':
                if self.is_host:
                    _str = f"{str(self.username)}'s Turn"
                else:
                    _str = f"{str(self.competitor_name)}'s Turn"
            else:
                if self.is_host:
                    _str = f"{str(self.competitor_name)}'s Turn"
                else:
                    _str = f"{str(self.username)}'s Turn"
                
                
        font = pygame.font.Font(None, 36)
        text = font.render(_str, 1, (255,255, 255))
        text_rect = text.get_rect(center=(WINDOW_WIDTH/2, 40))

        # Draw border around text
        border_rect = text_rect.inflate(10, 10)
        pygame.draw.rect(self.display_surface, (0, 0, 0, 0.3), border_rect)

        # Draw text
        self.display_surface.blit(text, text_rect)

    def draw_scoreboard(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"{self.username} {self.score_username} - {self.score_competitor_name} {self.competitor_name}", 1, (0, 0, 0))
        score_rect = score_text.get_rect(topright=(WINDOW_WIDTH - 10, 10))
        self.display_surface.blit(score_text, score_rect)

    def run(self):
        if self.flag_playing:
            self.draw_board()
            self.draw()
            self.draw_scoreboard()
            if self.check_win(self.last_selected_cell):
                self.playing = False
                #Cộng điểm cho người thắng
                if self.selection_index == 'x':
                    if self.is_host:
                        self.score_competitor_name += 1
                    else:
                        self.score_username += 1
                else:
                    if self.is_host:
                        self.score_username += 1
                    else:
                        self.score_competitor_name += 1
                self.alert_winning(self.last_selected_cell)
                GAME_SOUNDS.play(DRAW_WIN)
                
                
            if not self.playing:
                self.flag_playing = False
                
class CanvasTile:
    def __init__(self, id):
        self.has_x = False
        self.has_o = False
        self.add_id(id)

    def get_cell(self):
        if self.has_x:
            return 'x'
        else:
            return 'o'

    def get_not_cell(self):
        if self.has_o:
            return 'x'
        else:
            return 'o'

    def add_id(self, id):
        if id == EDITOR_DATA[0]['id']:
            self.has_x = True
        elif id == EDITOR_DATA[1]['id']:
            self.has_o = True
