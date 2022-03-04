# < 0.005% 1/22176 chance to get 4 of the same color, before ~0.077% 1/1296
# ~0.1% 1/1056 chance to get 3 of the same color, before ~0.5 1/216

import turtle
import ctypes
import time
import random
import winsound
import json

import settings
settings.initialize()

# Variables
clicked = ""
click_delay = time.time()
color_selected = ""
row = 10
gamein_progress = False
bgliding = False
agliding = False
cgliding = False
location = None
popup = False
EXIT = False

# Screen Resolution
user32 = ctypes.windll.user32
monitor_size = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
monitor_ratio = [monitor_size[0] / 1920, monitor_size[1] / 1080]

if settings.get_settings()["resolution"] == "auto":
    if monitor_size[1] > 768 and monitor_size[0] > 1366:
        resolution = "1920x1080"
        monitor_ratio[0] = 1
        monitor_ratio[1] = 1

        board_resolution_distance = 80
        guess_info_resolution = 40
        color_panel_resolution = 100
    else:
        resolution = "1366x768"
        monitor_ratio[0] = 0.66
        monitor_ratio[1] = 0.66

        board_resolution_distance = 53
        guess_info_resolution = 26.4
        color_panel_resolution = 66
elif settings.get_settings()["resolution"] == "medium":
    resolution = "1920x1080"
    monitor_ratio[0] = 1
    monitor_ratio[1] = 1

    board_resolution_distance = 80
    guess_info_resolution = 40
    color_panel_resolution = 100
elif settings.get_settings()["resolution"] == "small":
    resolution = "1366x768"
    monitor_ratio[0] = 0.66
    monitor_ratio[1] = 0.66

    board_resolution_distance = 53
    guess_info_resolution = 26.4
    color_panel_resolution = 66

# Lists
buttons = list()
board = list()
color_pieces = list()
info_pieces = list()
colors = ["red", "blue", "green", "yellow", "white", "black"]
board_size = [4, 11]
code = list()
code_pieces = list()
unused = list()
arrow_list = list()
texts = list()
guess_accuracy = list()
guess_accuracy_average = list()
color_status = [1, 1, 1, 1, 1, 1]
color_status_pieces = list()
extra = list()

# The screen/canvas
screen = turtle.Screen()
screen.screensize()
screen.setup(width = 1.0, height = 1.0)
screen.title("Mastermind")
screen.tracer(0)
screen.bgcolor("white")
canvas = screen.getcanvas()

# Classes
class Button(turtle.Turtle):
    def __init__(self, image, id, x, y, image_size, on_screen, on_id, off_id):
        turtle.Turtle.__init__(self)
        self.penup()
        screen.register_shape(f"assets/{resolution}/buttons/{image}.gif")
        self.shape(f"assets/{resolution}/buttons/{image}.gif")

        self.x = x * monitor_ratio[0]
        self.y = y * monitor_ratio[1]
        self.image_size = [image_size[0] * monitor_ratio[0], image_size[1] * monitor_ratio[1]]
        self.goto(self.x, self.y)

        self.id = id
        self.on_id = on_id
        self.off_id = off_id
        self.left_bottom = [(self.x - (self.image_size[0] / 2)), (self.y - (self.image_size[1] / 2))]
        self.right_top = [(self.x + (self.image_size[0] / 2)), (self.y + (self.image_size[1] / 2))]

        self.on_screen = on_screen
        if not on_screen:
            self.hideturtle()

        self.area = {"left_bottom":[self.left_bottom[0], self.left_bottom[1]], "right_top":[self.right_top[0], self.right_top[1]]}

    def checkif_clicked(self, x, y):
        global clicked
        global click_delay
        global row
        global code
        global color_selected
        global gamein_progress
        global color_status
        global location
        global EXIT
        global popup_obj
        if self.isvisible():
            if x >= self.area["left_bottom"][0] and x <= self.area["right_top"][0] and y >= self.area["left_bottom"][1] and y <= self.area["right_top"][1] and time.time() - click_delay > 0.1:
                clicked = self.id
                # Play a sound
                winsound.PlaySound(f"assets/sounds/click.wav", winsound.SND_ASYNC)

                # Run the specific thing for each id
                if self.id == "play":
                    color_status = [1, 1, 1, 1, 1, 1]
                    color_selected = ""
                    for button in color_pieces:
                            button.reset_color()
                    for slider in color_status_pieces:
                            slider.reset_image()
                    gamein_progress = False
                    row = 10
                    new_scene()

                elif self.id == "back":
                    if location == "game":
                        popup_obj = Popup("leave", "back")
                    elif location == "settings" and settings.changes:
                        popup_obj = Popup("leave", "back")
                    else:
                        color_selected = ""
                        for button in color_pieces:
                                button.reset_color()
                        new_scene()
                        location = None
                        
                elif self.id == "quit":
                    EXIT = True
                elif self.id == "guess":
                    if row_finished():

                        check_code()
                        if row > board_size[1] - settings.get_settings()["guesses"]:
                            row -= 1
                        arrow_list[0].change_position(row)
                        
                elif self.id == "random":
                    texts[1].var = False
                    code = []
                    
                    random_colors = list()
                    for i in colors:
                        random_colors.append(i)
                    for i in range(board_size[0]):
                        random_number = random.randint(0, len(random_colors) - 1)
                        code.append(random_colors[random_number])
                        random_colors.remove(random_colors[random_number])
                        for j in colors:
                            random_colors.append(j)
                    for i in board:
                        i.shape(f"assets/{resolution}/pieces/empty.gif")
                        i.showturtle()
                        
                    gamein_progress = True
                    arrow_list[0].change_position(row)
                    new_scene()
                    
                    if settings.get_settings()["animations"]:
                        board_gliding()
                        color_gliding()
                    location = "game"
                    
                elif self.id == "custom":
                    code = ["", "", "", ""]
                    create_code_pieces()
                    new_scene()
                    location = "custom"
                elif self.id == "done":
                    texts[1].var = False
                    if not code.__contains__(""):
                        color_selected = ""
                        for button in color_pieces:
                            button.reset_color()
                        gamein_progress = True
                        arrow_list[0].change_position(row)
                        for i in board:
                            i.shape(f"assets/{resolution}/pieces/empty.gif")
                            i.showturtle()
                        if settings.get_settings()["animations"]:
                            board_gliding()
                            color_gliding()
                        new_scene()
                        location = "game"
                        
                elif self.id == "settings":
                    location = "settings"
                    new_scene()
                    
                elif self.id == "apply":
                    settings.apply_changes()
                    if settings.require_restart:
                        popup_obj = Popup("close_game", "close_game")
                    else:
                        new_scene()
                        
                elif self.id == "fix":
                    settings.get_settings()["resolution"] = "auto"
                    settings.apply_changes()
                    EXIT = True
                        
                click_delay = time.time()

    def check_visibility(self):
        if self.on_screen:
            self.showturtle()
        else:
            self.hideturtle()

class Board_Piece(turtle.Turtle):
    def __init__(self, image, id, x, y, distance, on_screen, on_id, off_id):
        turtle.Turtle.__init__(self)
        self.penup()
        self.setheading(90)
        screen.register_shape(f"assets/{resolution}/pieces/{image}.gif")
        self.shape(f"assets/{resolution}/pieces/{image}.gif")
        
        self.id = id
        self.on_id = on_id
        self.off_id = off_id
        self.image = image
        self.done_gliding = False

        self.left_top = [-160 * monitor_ratio[0], 410 * monitor_ratio[1]]
        self.x = ((x * distance) + self.left_top[0]) + distance/2
        self.y = (self.left_top[1] - (y * distance)) - distance/2
        self.goto(self.x, self.y)
        
        self.on_screen = on_screen
        if not on_screen:
            self.hideturtle()

        self.area = {"left_bottom":[(x * distance) + self.left_top[0], self.left_top[1] - (y * distance) - distance], "right_top":[(x * distance) + self.left_top[0] + distance, self.left_top[1] - (y * distance)]}

    def check_visibility(self):
        if self.on_screen:
            self.showturtle()
        else:
            self.hideturtle()

    def checkif_clicked(self, x, y):
        global click_delay
        global color_selected
        if self.isvisible():
            if x >= self.area["left_bottom"][0] and x <= self.area["right_top"][0] and y >= self.area["left_bottom"][1] and y <= self.area["right_top"][1] and time.time() - click_delay > 0.1:
                
                if not color_selected == "" and row == self.id[1]:
                    screen.register_shape(f"assets/{resolution}/pieces/{color_selected}.gif")
                    self.shape(f"assets/{resolution}/pieces/{color_selected}.gif")
                    self.image = color_selected

                click_delay = time.time()

    def checkif_filled(self):
        if row == self.id[1]:
            if self.shape() == f"assets/{resolution}/pieces/empty.gif":
                return 0
            else:
                return 1
        else:
            return 0
        
    def glide_tick(self):
        self.forward((self.y - self.ycor()) / 20)
        if self.y - self.ycor() <= 1:
            self.goto(self.xcor(), self.y)
            self.done_gliding = True

class Color(turtle.Turtle):
    def __init__(self, image, id, x, y, distance, on_screen, on_id, off_id):
        turtle.Turtle.__init__(self)
        self.penup()

        self.image = f"assets/{resolution}/colors/{image}.gif"
        self.image2 = f"assets/{resolution}/colors/{image}_selected.gif"
        self.image3 = f"assets/{resolution}/colors/{image}_disabled.gif"
        screen.register_shape(self.image)
        screen.register_shape(self.image2)
        screen.register_shape(self.image3)
        self.shape(self.image)

        self.id = id
        self.on_id = on_id
        self.off_id = off_id

        self.left_top = [-500 * monitor_ratio[0], 300 * monitor_ratio[1]]
        self.x = ((x * distance) + self.left_top[0]) + distance/2
        self.y = (self.left_top[1] - (y * distance)) - distance/2
        self.goto(self.x, self.y)
        self.done_gliding = False

        self.on_screen = on_screen
        if not on_screen:
            self.hideturtle()

        self.area = {"left_bottom":[(x * distance) + self.left_top[0], self.left_top[1] - (y * distance) - distance], "right_top":[(x * distance) + self.left_top[0] + distance, self.left_top[1] - (y * distance)]}

    def check_visibility(self):
        if self.on_screen:
            self.showturtle()
        else:
            self.hideturtle()

    def checkif_clicked(self, x, y):
            global click_delay
            global color_selected
            global row
            if self.isvisible():
                if x >= self.area["left_bottom"][0] and x <= self.area["right_top"][0] and y >= self.area["left_bottom"][1] and y <= self.area["right_top"][1] and time.time() - click_delay > 0.1 and row >= 0:
                    
                    if color_status[colors.index(self.id)] == 1:
                        if not color_selected == "":
                            for button in color_pieces:
                                button.reset_color()

                        color_selected = self.id
                        self.shape(self.image2)

                    click_delay = time.time()

    def reset_color(self):
        if color_status[colors.index(self.id)] == 1:
            self.shape(self.image)
        else:
            self.shape(self.image3)
        
    def change_ability(self, onoroff):
        global color_selected
        if onoroff:
            self.shape(self.image)
        else:
            if color_selected == self.id:
                color_selected = ""
            self.shape(self.image3)
            
    def glide_tick(self):
        self.forward((self.x - self.xcor()) / 20)
        if self.x - self.xcor() <= 1:
            self.goto(self.x, self.ycor())
            self.done_gliding = True

class Guess_Info(turtle.Turtle):
    def __init__(self, x, y, image, on_id, off_id):
        turtle.Turtle.__init__(self)
        self.penup()
        screen.register_shape(f"assets/{resolution}/piece data/{image}.gif")
        self.shape(f"assets/{resolution}/piece data/{image}.gif")
        self.goto(x, y)
        
        self.off_id = off_id
        self.on_id = on_id
        self.id = None

class Custom_Code(turtle.Turtle):
    def __init__(self, x, y, id, image, distance, on_screen, on_id, off_id):
        turtle.Turtle.__init__(self)
        self.penup()
        screen.register_shape(f"assets/{resolution}/code/{image}.gif")
        self.shape(f"assets/{resolution}/code/{image}.gif")
        
        self.on_id = on_id
        self.off_id = off_id
        self.image = image
        self.id = id

        self.left_top = [-200 * monitor_ratio[0], 100 * monitor_ratio[1]]
        self.x = ((x * distance) + self.left_top[0]) + distance/2
        self.y = (self.left_top[1] - (y * distance)) - distance/2
        self.goto(self.x, self.y)

        self.on_screen = on_screen
        if not on_screen:
            self.hideturtle()

        self.area = {"left_bottom":[(x * distance) + self.left_top[0], self.left_top[1] - (y * distance) - distance], "right_top":[(x * distance) + self.left_top[0] + distance, self.left_top[1] - (y * distance)]}

    def checkif_clicked(self, x, y):
        global click_delay
        global color_selected
        global code
        if self.isvisible():
            if x >= self.area["left_bottom"][0] and x <= self.area["right_top"][0] and y >= self.area["left_bottom"][1] and y <= self.area["right_top"][1] and time.time() - click_delay > 0.1:
                if not color_selected == "":
                    screen.register_shape(f"assets/{resolution}/code/{color_selected}.gif")
                    self.shape(f"assets/{resolution}/code/{color_selected}.gif")
                    self.image = color_selected
                    code[self.id] = self.image

                click_delay = time.time()

    def check_visibility(self):
        if self.on_screen:
            self.showturtle()
        else:
            self.hideturtle()

class Arrow(turtle.Turtle):
    def __init__(self, y, id, distance, on_screen, on_id, off_id):
        turtle.Turtle.__init__(self)
        self.penup()
        screen.register_shape(f"assets/{resolution}/arrow.gif")
        self.shape(f"assets/{resolution}/arrow.gif")
        self.setheading(90)
        
        self.id = id
        self.on_id = on_id
        self.off_id = off_id
        self.distance = distance
        self.done_gliding = False

        self.on_screen = on_screen
        if not on_screen:
            self.hideturtle()

        self.left_top = [-240 * monitor_ratio[0], 410 * monitor_ratio[1]]
        self.change_position(y)

    def change_position(self, newy):
        self.x = self.left_top[0] + self.distance/2
        self.y = (self.left_top[1] - (newy * self.distance)) - self.distance/2
        
        if settings.get_settings()["animations"]:
            self.goto(self.x, self.ycor())
            arrow_gliding()
        else:
            self.goto(self.x, self.y)

    def check_visibility(self):
        if self.on_screen:
            self.showturtle()
        else:
            self.hideturtle()
            
    def glide_tick(self):
        self.setheading(90)
        self.forward((self.y - self.ycor()) / 10)
        if self.y - self.ycor() <= 1:
            self.goto(self.xcor(), self.y)
            self.done_gliding = True
            
    def _glide_tick(self):
        self.setheading(0)
        self.forward((self.x - self.xcor()) / 22)
        if self.x - self.xcor() <= 1:
            self.goto(self.x, self.ycor())
            self.done_gliding = True

class Text(turtle.Turtle):
    def __init__(self, image, id, x, y, on_screen, on_id, off_id, var):
        turtle.Turtle.__init__(self)
        self.penup()
        screen.register_shape(f"assets/{resolution}/text/{image}.gif")
        self.shape(f"assets/{resolution}/text/{image}.gif")
        
        self.image = image
        self.on_id = on_id
        self.off_id = off_id
        self.id = id
        self.var = var
        self.goto(x, y)

        self.on_screen = on_screen
        if not on_screen:
            self.hideturtle()

    def check_visibility(self):
        if self.on_screen:
            self.showturtle()
        else:
            self.hideturtle()

class Color_Status(turtle.Turtle):
    def __init__(self, image, x, y, id, distance, on_id, off_id, on_screen, image_size):
        turtle.Turtle.__init__(self)
        self.penup()
        for i in range(5):
            screen.register_shape(f"assets/{resolution}/color status/{i}.gif")
        
        self.shape(f"assets/{resolution}/color status/{image}.gif")

        self.image = image
        self.on_id = on_id
        self.off_id = off_id
        self.id = id
        self.distance = distance * monitor_ratio[0]
        self.done_gliding = False

        self.image_size = image_size * monitor_ratio[0]
        self.left_top = [-575 * monitor_ratio[0], 275 * monitor_ratio[1]]
        self.x = ((x * self.distance) + self.left_top[0]) + self.image_size/2
        self.y = (self.left_top[1] - (y * self.distance)) - self.image_size/2
        self.goto(self.x, self.y)
        
        self.on_screen = on_screen
        if not on_screen:
            self.hideturtle()

        self.area = {"left_bottom":[(x * self.image_size) + self.left_top[0], self.left_top[1] - (y * self.distance) - self.image_size], "right_top":[(x * self.image_size) + self.left_top[0] + self.image_size, self.left_top[1] - (y * self.distance)]}
        
    def check_visibility(self):
        if self.on_screen:
            self.showturtle()
        else:
            self.hideturtle()

    def checkif_clicked(self, x, y):
            global click_delay
            global color_selected
            global row
            if self.isvisible():
                if x >= self.area["left_bottom"][0] and x <= self.area["right_top"][0] and y >= self.area["left_bottom"][1] and y <= self.area["right_top"][1] and time.time() - click_delay > 0.1 and row >= 0:
                    
                    if color_status[self.id] == 1:
                        color_pieces[self.id].change_ability(False)
                        color_status[self.id] = 0
                        
                        for i in range(3, -1, -1):
                            self.shape(f"assets/{resolution}/color status/{i}.gif")
                            screen.update()
                            time.sleep(0.01)
                    else:
                        color_pieces[self.id].change_ability(True)
                        color_status[self.id] = 1
                        
                        for i in range(1, 5):
                            self.shape(f"assets/{resolution}/color status/{i}.gif")
                            screen.update()
                            time.sleep(0.01)
                    
                    click_delay = time.time()
                    
    def reset_image(self):
        self.shape(f"assets/{resolution}/color status/4.gif")
        
    def glide_tick(self):
        self.forward((self.x - self.xcor()) / 20)
        if self.x - self.xcor() <= 1:
            self.goto(self.x, self.ycor())
            self.done_gliding = True

class Popup(turtle.Turtle):
    def __init__(self, image, id):
        global popup
        turtle.Turtle.__init__(self)
        self.penup()
        
        popup = True
        screen.register_shape(f"assets/{resolution}/popup/{image}.gif")
        self.shape(f"assets/{resolution}/popup/{image}.gif")
        self.id = id
        
        self.yes_area = {"left_bottom":[-120 * monitor_ratio[0], -111 * monitor_ratio[1]], "right_top":[-10 * monitor_ratio[0], -38 * monitor_ratio[1]]}
        self.no_area = {"left_bottom":[10 * monitor_ratio[0], -111 * monitor_ratio[1]], "right_top":[120 * monitor_ratio[0], -38 * monitor_ratio[1]]}
        
    def checkif_clicked(self, x, y):
        global clicked
        global color_selected
        global location
        global click_delay
        global popup
        global EXIT
        if x >= self.yes_area["left_bottom"][0] and x <= self.yes_area["right_top"][0] and y >= self.yes_area["left_bottom"][1] and y <= self.yes_area["right_top"][1] and time.time() - click_delay > 0.1:
            winsound.PlaySound(f"assets/sounds/click.wav", winsound.SND_ASYNC)
            if self.id == "back":
                clicked = "back"
                color_selected = ""
                for button in color_pieces:
                        button.reset_color()
                new_scene()
                location = None
                
            if self.id == "close_game":
                settings.settings["resolution"] = settings.resolution_setting.selected
                with open("settings.json", "w") as file:
                    json.dump(settings.settings, file, indent=2)
                EXIT = True
            
            popup = False
            self.id = None
            self.hideturtle()
                 
            click_delay = time.time()
        elif x >= self.no_area["left_bottom"][0] and x <= self.no_area["right_top"][0] and y >= self.no_area["left_bottom"][1] and y <= self.no_area["right_top"][1] and time.time() - click_delay > 0.1:
            winsound.PlaySound(f"assets/sounds/click.wav", winsound.SND_ASYNC)
            popup = False
            self.id = None
            self.hideturtle()
            
            click_delay = time.time()

# Functions
def board_gliding():
    for piece in board:
        piece.goto(piece.xcor(), -(monitor_size[1] / 2) - board_resolution_distance)
        piece.done_gliding = False
    
    global bgliding_ticks
    global bgliding
    bgliding_ticks = 0
    bgliding = True
    
def color_gliding():
    for color in color_pieces:
        color.goto(-(monitor_size[0] / 2) - color_panel_resolution, color.ycor())
        color.done_gliding = False
    
    for color in color_status_pieces:
        color.goto(-(monitor_size[0] / 2) - color_panel_resolution - (75 * monitor_ratio[0]), color.ycor())
        color.done_gliding = False
    
    for i in arrow_list:
        i.goto(-(monitor_size[0] / 2) - 80 * monitor_ratio[0], i.ycor())
        i.done_gliding = False
    
    global cgliding_ticks
    global cgliding
    cgliding_ticks = 0
    cgliding = True

def arrow_gliding():
    for i in arrow_list:
        i.done_gliding = False

    global agliding
    agliding = True

def enter_hotkey():
    global row
    global color_selected
    global gamein_progress
    global location
    global clicked
    winsound.PlaySound(f"assets/sounds/click.wav", winsound.SND_ASYNC)
    
    if location == "game":
        if row_finished():
            check_code()
            if row > board_size[1] - settings.get_settings()["guesses"]:
                row -= 1
                arrow_list[0].change_position(row)
    elif location == "custom":
        texts[1].var = False
        if not code.__contains__(""):
            color_selected = ""
            for button in color_pieces:
                button.reset_color()
            gamein_progress = True
            arrow_list[0].change_position(row)
            clicked = "done"
            new_scene()
            location = "game"
        
def number_key_1():
    global row
    global location
    key = 1
    if location == "game":
        if not color_selected == "":
            for piece in board:
                if piece.id[1] == row and piece.id[0] == key - 1:
                    screen.register_shape(f"assets/{resolution}/pieces/{color_selected}.gif")
                    piece.shape(f"assets/{resolution}/pieces/{color_selected}.gif")
                    piece.image = color_selected
    elif location == "custom":
        if not color_selected == "":
            screen.register_shape(f"assets/{resolution}/code/{color_selected}.gif")
            code_pieces[key - 1].shape(f"assets/{resolution}/code/{color_selected}.gif")
            code_pieces[key - 1].image = color_selected
            code[code_pieces[key - 1].id] = code_pieces[key - 1].image
                
def number_key_2():
    global row
    global location
    key = 2
    if location == "game":
        if not color_selected == "":
            for piece in board:
                if piece.id[1] == row and piece.id[0] == key - 1:
                    screen.register_shape(f"assets/{resolution}/pieces/{color_selected}.gif")
                    piece.shape(f"assets/{resolution}/pieces/{color_selected}.gif")
                    piece.image = color_selected
    elif location == "custom":
        if not color_selected == "":
            screen.register_shape(f"assets/{resolution}/code/{color_selected}.gif")
            code_pieces[key - 1].shape(f"assets/{resolution}/code/{color_selected}.gif")
            code_pieces[key - 1].image = color_selected
            code[code_pieces[key - 1].id] = code_pieces[key - 1].image
                
def number_key_3():
    global row
    global location
    key = 3
    if location == "game":
        if not color_selected == "":
            for piece in board:
                if piece.id[1] == row and piece.id[0] == key - 1:
                    screen.register_shape(f"assets/{resolution}/pieces/{color_selected}.gif")
                    piece.shape(f"assets/{resolution}/pieces/{color_selected}.gif")
                    piece.image = color_selected
    elif location == "custom":
        if not color_selected == "":
            screen.register_shape(f"assets/{resolution}/code/{color_selected}.gif")
            code_pieces[key - 1].shape(f"assets/{resolution}/code/{color_selected}.gif")
            code_pieces[key - 1].image = color_selected
            code[code_pieces[key - 1].id] = code_pieces[key - 1].image
                
def number_key_4():
    global row
    global location
    key = 4
    if location == "game":
        if not color_selected == "":
            for piece in board:
                if piece.id[1] == row and piece.id[0] == key - 1:
                    screen.register_shape(f"assets/{resolution}/pieces/{color_selected}.gif")
                    piece.shape(f"assets/{resolution}/pieces/{color_selected}.gif")
                    piece.image = color_selected
    elif location == "custom":
        if not color_selected == "":
            screen.register_shape(f"assets/{resolution}/code/{color_selected}.gif")
            code_pieces[key - 1].shape(f"assets/{resolution}/code/{color_selected}.gif")
            code_pieces[key - 1].image = color_selected
            code[code_pieces[key - 1].id] = code_pieces[key - 1].image
            
def create_code_pieces():
    for i in range(4):
        code_pieces.append(Custom_Code(i, 0, i, "empty", 200 * monitor_ratio[0], True, [], ["done", "back"]))

def row_finished():
    filled = 0
    for piece in board:
        filled += piece.checkif_filled()
    
    if filled == 4:
        return True

def check_code():
    global row
    global color_selected
    global extra
    used = list()
    guess = list()
    data = list()
    extra = list()
    for piece in board:
        if piece.id[1] == row:
            guess.append(piece.image)

    icounter = 0
    for i in guess:
        if i == code[icounter]:
            data.append("correct")
            used.append(icounter)
        icounter += 1

    icounter = 0
    for i in guess:
        if i == code[icounter]:
            icounter += 1
            continue
        
        jcounter = 0
        for j in code:
            if used.__contains__(jcounter):
                jcounter += 1
                continue

            if j == i:
                data.append("place")
                used.append(jcounter)
                break

            jcounter += 1
        icounter += 1

    # Make the visual stuff idk
    correct = data.count("correct")
    location = data.count("place")
    guess_accuracy.append(round((correct * 25) + (location * 12.5)))
    guess_accuracy_average.append(sum(guess_accuracy) / len(guess_accuracy))

    index = 0
    for i in range(correct):
        info_pieces.append(Guess_Info((180 * monitor_ratio[0]) + (index * guess_info_resolution), ((410 * monitor_ratio[1]) - (row * board_resolution_distance)) - (board_resolution_distance / 2), "correct", [], ["back"]))
        index += 1

    for i in range(location):
        info_pieces.append(Guess_Info((180 * monitor_ratio[0]) + (index * guess_info_resolution), ((410 * monitor_ratio[1]) - (row * board_resolution_distance)) - (board_resolution_distance / 2), "place", [], ["back"]))
        index += 1

    #for i in range(4 - (correct + location)):
        #info_pieces.append(Guess_Info((180 * monitor_ratio[0]) + (index * guess_info_resolution), ((370 * monitor_ratio[1]) - (row * board_resolution_distance)) - (board_resolution_distance / 2), "x", ["random", "done"], ["back"]))
        #index += 1

    # Check to see if you won or lost
    if correct == 4:
        row = -9
        arrow_list[0].hideturtle()
        for i in range(4):
            extra.append(Board_Piece(code[i], [i, (board_size[1] - settings.get_settings()["guesses"]) - 1], i, (board_size[1] - settings.get_settings()["guesses"]) - 1, board_resolution_distance, True, [], ["back"]))

        color_selected = ""
        for button in color_pieces:
            button.reset_color()

        texts[1].goto(texts[1].xcor(), (411 * monitor_ratio[1]) - ((board_size[1] - settings.get_settings()["guesses"]) * board_resolution_distance))
        texts[1].showturtle()
        texts[1].var = True

        winsound.PlaySound(f"assets/sounds/yes.wav", winsound.SND_ASYNC)

    if row == board_size[1] - settings.get_settings()["guesses"]:
        row = -9
        arrow_list[0].hideturtle()
        for i in range(4):
            extra.append(Board_Piece(code[i], [i, (board_size[1] - settings.get_settings()["guesses"]) - 1], i, (board_size[1] - settings.get_settings()["guesses"]) - 1, board_resolution_distance, True, [], ["back"]))

        color_selected = ""
        for button in color_pieces:
                button.reset_color()

        texts[1].goto(texts[1].xcor(), (411 * monitor_ratio[1]) - ((board_size[1] - settings.get_settings()["guesses"]) * board_resolution_distance))
        texts[1].showturtle()
        texts[1].var = True

        winsound.PlaySound(f"assets/sounds/fail.wav", winsound.SND_ASYNC)

    # Sounds
    if row > 0:
        if correct == 0 and location == 0:
            winsound.PlaySound(f"assets/sounds/none.wav", winsound.SND_ASYNC)
        elif not correct == 4:
            winsound.PlaySound(f"assets/sounds/good.wav", winsound.SND_ASYNC)

def click(x, y):
    global click_delay
    if not popup:
        for button in buttons:
            button.checkif_clicked(x, y)

        for piece in board:
            piece.checkif_clicked(x, y)

        for color in color_pieces:
            color.checkif_clicked(x, y)

        for thing in code_pieces:
            thing.checkif_clicked(x, y)
            
        for color_status in color_status_pieces:
            color_status.checkif_clicked(x, y)
        
        try:
            for button in buttons:
                if button.id == "apply":
                    _apply = button
            
            for settings_arrow in settings.resolution_arrows:
                settings_arrow.checkif_clicked(x, y, click_delay, resolution, _apply)
                
            for settings_arrow in settings.guess_arrows:
                settings_arrow.checkif_clicked(x, y, click_delay, resolution, _apply)
                
            for settings_arrow in settings.animation_arrows:
                settings_arrow.checkif_clicked(x, y, click_delay, resolution, _apply)
        except:
            pass
    else:
        popup_obj.checkif_clicked(x, y)

def list_checking(list):
    global board_size
    for object in list:
        if object.on_id.__contains__(clicked):
            object.on_screen = True
            object.check_visibility()
        elif object.off_id.__contains__(clicked):
            object.on_screen = False
            object.check_visibility()
            
        if list == board:
            if (board_size[1] - settings.get_settings()["guesses"]) * board_size[0] > board.index(object):
                object.hideturtle()

def new_scene():
    global clicked
    global info_pieces
    global extra
    global unused
    global monitor_size
    list_checking(buttons)

    list_checking(board)
   
    list_checking(color_pieces)

    list_checking(code_pieces)

    list_checking(arrow_list)

    list_checking(texts)
    
    list_checking(color_status_pieces)
    
    for i in buttons:
        if i.id == "fix":
            foobar = i
            break
    
    if clicked == "settings":
        settings.settings_main(screen, [monitor_ratio[0], monitor_ratio[1]], resolution, monitor_size[1], foobar)
        
    if clicked == "back":
        for i in info_pieces:
            if not unused.__contains__(i):
                unused.append(i)
        for i in extra:
            if not unused.__contains__(i):
                unused.append(i)
        try:
            for i in settings.get_settings_objects():
                i.hideturtle()
        except:
            pass
            
    if clicked == "apply":
        for i in settings.get_settings_objects():
            i.hideturtle()

    clicked = ""

# Objects
buttons.append(Button("play", "play", 0, 0, [300, 150], True, ["back", "apply"], ["play", "settings"]))
buttons.append(Button("back", "back", -500, 350, [150, 75], False, ["play", "settings"], ["back", "apply"]))

buttons.append(Button("quit", "quit", 160, -300, [300, 150], True, ["back", "apply"], ["play", "settings"]))
buttons.append(Button("settings", "settings", -160, -300, [300, 150], True, ["back", "apply"], ["play", "settings"]))
buttons.append(Button("apply", "apply", -500, 250, [150, 75], False, [], ["back", "apply"]))
buttons.append(Button("fix", "fix", 350, -200, [150, 75], False, [], ["back"]))

buttons.append(Button("guess", "guess", 500, 400, [150, 75], False, ["random", "done"], ["back"]))

buttons.append(Button("random", "random", 0, 50, [300, 150], False, ["play"], ["random", "custom", "back"]))
buttons.append(Button("custom", "custom", 0, -250, [300, 150], False, ["play"], ["random", "custom", "back"]))
buttons.append(Button("done", "done", 0, -300, [150, 75], False, ["custom"], ["back", "done"]))

#buttons.append(Button("new_game", "new", 0, 300, [300, 150], False, ["back2"], ["play2", "play", "new"]))

# Board
for y in range(board_size[1]):
    for x in range(board_size[0]):
        board.append(Board_Piece("empty", [x, y], x, y, board_resolution_distance, False, ["random", "done"], ["back"]))
        
#for piece in board:
#    piece.goto(x=piece.xcor(),y=-500)
#    piece.glide(300)

# Color panel
for color in colors:
    color_pieces.append(Color(color, color, 0, colors.index(color), color_panel_resolution, False, ["random", "custom"], ["back"]))
    color_status_pieces.append(Color_Status(4, 0, colors.index(color), colors.index(color), 100, ["random", "done"], ["back"], False, 50))

# The single arrow
arrow_list.append(Arrow(row, "arrow", board_resolution_distance, False, ["done", "random"], ["back"]))

# Text
texts.append(Text("code", 0, 0 * monitor_ratio[0], 312 * monitor_ratio[1], False, ["play", "new"], ["random", "back", "custom"], None))
texts.append(Text("line", 1, 0 * monitor_ratio[0], 411 * monitor_ratio[1], False, [], ["back"], False))

# Hotkeys
screen.listen()
screen.onkeypress(enter_hotkey, "Return")
screen.onkeypress(number_key_1, "1")
screen.onkeypress(number_key_2, "2")
screen.onkeypress(number_key_3, "3")
screen.onkeypress(number_key_4, "4")

# Main loop
screen.onscreenclick(click, btn=1, add=None)
while True:
    if EXIT:
        break
    else:
        try:
            screen.update()
        except:
            break

    if bgliding:
        for piece in board:
            if bgliding_ticks >= board.index(piece):
                piece.glide_tick()
        bgliding_ticks += 1
        
        for piece in board:
            if not piece.done_gliding:
                break
            bgliding = False
    
    if agliding:
        for piece in arrow_list:
            piece.glide_tick()
        
        for piece in arrow_list:
            if not piece.done_gliding:
                break
            agliding = False
    
    if cgliding:
        for piece in color_pieces:
            if cgliding_ticks / 4 >= color_pieces.index(piece):
                piece.glide_tick()
                
        for piece in color_status_pieces:
            if cgliding_ticks / 4 >= color_status_pieces.index(piece):
                piece.glide_tick()   
                
        for piece in arrow_list:
            if (cgliding_ticks - 20) / 4 >= arrow_list.index(piece):
                piece._glide_tick()      
        cgliding_ticks += 1
        
        for piece in color_pieces:
            if not piece.done_gliding:
                break
            cgliding = False
                
    for i in unused:
        i.hideturtle()