import turtle, ctypes, threading
import time, random, winsound

# Variables
clicked = ""
click_delay = time.time()
color_selected = ""
row = 9
gamein_progress = False
EXIT = False

# Screen Resolution
user32 = ctypes.windll.user32
monitor_size = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
monitor_ratio = [monitor_size[0] / 1920, monitor_size[1] / 1080]

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

# Lists
buttons = list()
board = list()
color_pieces = list()
info_pieces = list()
colors = ["red", "blue", "green", "yellow", "white", "black"]
board_size = [4, 10]
code = list()
code_pieces = list()
unused = list()
arrow_list = list()
texts = list()
guess_accuracy = list()
guess_accuracy_average = list()
color_status = [1, 1, 1, 1, 1, 1]
color_status_pieces = list()

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
        global EXIT
        if self.isvisible():
            if x >= self.area["left_bottom"][0] and x <= self.area["right_top"][0] and y >= self.area["left_bottom"][1] and y <= self.area["right_top"][1] and time.time() - click_delay > 0.1:
                clicked = self.id
                # Play a sound
                winsound.PlaySound(f"assets/sounds/click.wav", winsound.SND_ASYNC)

                if clicked == "new":
                    for i in code_pieces:
                        unused.append(i)
                    for i in info_pieces:
                        unused.append(i)
                    for i in board:
                        if i.id[1] == -1:
                            unused.append(i)
                        else:
                            i.shape(f"assets/{resolution}/pieces/empty.gif")

                    row = 9

                    clicked = "play"

                # Run the specific thing for each id
                if self.id == "play":
                    new_scene()
                elif self.id == "back":
                    color_selected = ""
                    for button in color_pieces:
                            button.reset_color()
                    new_scene()
                elif self.id == "quit":
                    EXIT = True
                elif self.id == "guess":
                    if row_finished():

                        check_code()
                        if row > 0:
                            row -= 1
                        arrow_list[0].change_position(row)
                elif self.id == "random":
                    texts[1].var = False
                    code = []
                    for i in range(4):
                        code.append(colors[random.randint(0, 5)])
                    gamein_progress = True
                    arrow_list[0].change_position(row)
                    new_scene()
                elif self.id == "custom":
                    code = ["", "", "", ""]
                    create_code_pieces()
                    new_scene()
                elif self.id == "done":
                    texts[1].var = False
                    if not code.__contains__(""):
                        color_selected = ""
                        for button in color_pieces:
                            button.reset_color()
                        gamein_progress = True
                        arrow_list[0].change_position(row)
                        new_scene()
                elif self.id == "play2":
                    if texts[1].var:
                        texts[1].showturtle()
                    new_scene()
                elif self.id == "back2":
                    new_scene()
                elif self.id == "new":
                    color_status = [1, 1, 1, 1, 1, 1]
                    color_selected = ""
                    for button in color_pieces:
                            button.reset_color()
                    for slider in color_status_pieces:
                            slider.reset_image()
                    gamein_progress = False
                    new_scene()
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
        screen.register_shape(f"assets/{resolution}/pieces/{image}.gif")
        self.shape(f"assets/{resolution}/pieces/{image}.gif")
        
        self.id = id
        self.on_id = on_id
        self.off_id = off_id
        self.image = image

        self.left_top = [-160 * monitor_ratio[0], 370 * monitor_ratio[1]]
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
        self.shape(self.image)
        
    def change_ability(self, onoroff):
        global color_selected
        if onoroff:
            self.shape(self.image)
        else:
            if color_selected == self.id:
                color_selected = ""
            self.shape(self.image3)

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

    def check_visibility(self):
        if self.on_screen:
            self.showturtle()
        else:
            self.hideturtle()

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
        
        self.id = id
        self.on_id = on_id
        self.off_id = off_id
        self.distance = distance

        self.on_screen = on_screen
        if not on_screen:
            self.hideturtle()

        self.left_top = [-240 * monitor_ratio[0], 370 * monitor_ratio[1]]
        self.change_position(y)

    def change_position(self, newy):
        self.x = self.left_top[0] + self.distance/2
        self.y = (self.left_top[1] - (newy * self.distance)) - self.distance/2
        self.goto(self.x, self.y)

    def check_visibility(self):
        if self.on_screen:
            self.showturtle()
        else:
            self.hideturtle()

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

# Functions
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
    used = list()
    guess = list()
    data = list()
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
        info_pieces.append(Guess_Info((180 * monitor_ratio[0]) + (index * guess_info_resolution), ((370 * monitor_ratio[1]) - (row * board_resolution_distance)) - (board_resolution_distance / 2), "correct", ["random", "done", "play2"], ["back2"]))
        index += 1

    for i in range(location):
        info_pieces.append(Guess_Info((180 * monitor_ratio[0]) + (index * guess_info_resolution), ((370 * monitor_ratio[1]) - (row * board_resolution_distance)) - (board_resolution_distance / 2), "place", ["random", "done", "play2"], ["back2"]))
        index += 1

    #for i in range(4 - (correct + location)):
        #info_pieces.append(Guess_Info((180 * monitor_ratio[0]) + (index * guess_info_resolution), ((370 * monitor_ratio[1]) - (row * board_resolution_distance)) - (board_resolution_distance / 2), "x", ["random", "done", "play2"], ["back2"]))
        #index += 1

    # Check to see if you won or lost
    if correct == 4:
        row = -9
        for i in range(4):
            board.append(Board_Piece(code[i], [i, -1], i, -1, board_resolution_distance, True, ["random", "done", "play2"], ["back2"]))

        color_selected = ""
        for button in color_pieces:
            button.reset_color()

        texts[1].showturtle()
        texts[1].var = True

        winsound.PlaySound(f"assets/sounds/yes.wav", winsound.SND_ASYNC)

    if row == 0:
        row = -9
        for i in range(4):
            board.append(Board_Piece(code[i], [i, -1], i, -1, board_resolution_distance, True, ["random", "done", "play2"], ["back2"]))

        color_selected = ""
        for button in color_pieces:
                button.reset_color()

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

def list_checking(list):
    for object in list:
        if object.on_id.__contains__(clicked):
            object.on_screen = True
            object.check_visibility()
        elif object.off_id.__contains__(clicked):
            object.on_screen = False
            object.check_visibility()

        # Stupid stuff
        if object.id == "play2" and (clicked == "back2"):
            object.on_screen = True
            object.check_visibility()

        if object.id == "back2" and (clicked == "random" or clicked == "done"):
            object.on_screen = True
            object.check_visibility()

def new_scene():
    global clicked
    list_checking(buttons)

    list_checking(board)
   
    list_checking(color_pieces)

    list_checking(info_pieces)

    list_checking(code_pieces)

    list_checking(arrow_list)

    list_checking(texts)
    
    list_checking(color_status_pieces)

    clicked = ""

# Objects
buttons.append(Button("play", "play", 0, 0, [300, 150], True, ["back"], ["play"]))
buttons.append(Button("back", "back", -500, 350, [150, 75], False, ["custom", "play"], ["back", "done", "random"]))
buttons.append(Button("play2", "play2", 0, 0, [300, 150], False, [], ["play2", "play"]))
buttons.append(Button("back2", "back2", -500, 350, [150, 75], False, ["play2"], ["back2"]))

buttons.append(Button("quit", "quit", 0, -300, [300, 150], True, ["back", "back2"], ["play", "play2"]))

buttons.append(Button("guess", "guess", 500, 400, [150, 75], False, ["random", "done", "play2"], ["back2"]))

buttons.append(Button("random", "random", 0, 50, [300, 150], False, ["play"], ["random", "custom", "back"]))
buttons.append(Button("custom", "custom", 0, -250, [300, 150], False, ["play"], ["random", "custom", "back"]))
buttons.append(Button("done", "done", 0, -300, [150, 75], False, ["custom"], ["back", "done"]))

buttons.append(Button("new_game", "new", 0, 300, [300, 150], False, ["back2"], ["play2", "play", "new"]))

# Board
for x in range(board_size[0]):
    for y in range(board_size[1]):
        board.append(Board_Piece("empty", [x, y], x, y, board_resolution_distance, False, ["random", "done", "play2"], ["back2"]))

# Color panel
for color in colors:
    color_pieces.append(Color(color, color, 0, colors.index(color), color_panel_resolution, False, ["random", "custom", "play2"], ["back", "back2"]))
    color_status_pieces.append(Color_Status(4, 0, colors.index(color), colors.index(color), 100, ["random", "done", "play2"], ["back2"], False, 50))

# The single arrow
arrow_list.append(Arrow(row, "arrow", board_resolution_distance, False, ["done", "random", "play2"], ["back2"]))

# Text
texts.append(Text("code", 0, 0 * monitor_ratio[0], 312 * monitor_ratio[1], False, ["play", "new"], ["random", "back", "custom"], None))
texts.append(Text("line", 1, 0 * monitor_ratio[0], 371 * monitor_ratio[1], False, [], ["back2"], False))

# Main loop
screen.onscreenclick(click, btn=1, add=None)
while True:
    if EXIT:
        break
    else:
        screen.update()

    for i in unused:
        i.hideturtle()