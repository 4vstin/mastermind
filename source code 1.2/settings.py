import turtle
import time
import json

def initialize():
    reload_settings
        
def reload_settings():
    global settings
    global settings_objects
    global changes
    changes = False
    with open("settings.json") as file:
        settings = json.load(file)

class Settings_arrow(turtle.Turtle):
    def __init__(self, x, y, id, part_id, image, screen, res, monitor_r):
        turtle.Turtle.__init__(self)
        self.penup()
        self.goto(x * monitor_r, y * monitor_r)
        
        self.id = id
        self.part_id = part_id
        self.image = image
        
        screen.register_shape(f"assets/{res}/settings/arrow_right.gif")
        screen.register_shape(f"assets/{res}/settings/arrow_left.gif")
        
        self.shape(f"assets/{res}/settings/{self.image}.gif")
        
        self.area = {"left_bottom":[self.xcor() - 25 * monitor_r, self.ycor() - 25 * monitor_r], "right_top":[self.xcor() + 25 * monitor_r, self.ycor() + 25 * monitor_r]}
        
    def checkif_clicked(self, x, y, click_del, res, apply):
        click_delay = click_del
        global resolution_setting
        global guess_setting
        global animation_setting
        global changes
        if self.isvisible():
            if x >= self.area["left_bottom"][0] and x <= self.area["right_top"][0] and y >= self.area["left_bottom"][1] and y <= self.area["right_top"][1] and time.time() - click_delay > 0.5:
                if self.id == "resolution":
                    resolution_setting.change_selected(self.part_id, res)
                if self.id == "guesses":
                    guess_setting.change_selected(self.part_id, res)
                if self.id == "animations":
                    animation_setting.change_selected(self.part_id, res)
                
                #print(resolution_setting.selected, guess_setting.selected, )
                if resolution_setting.selected == settings["resolution"] and guess_setting.selected == settings["guesses"] and animation_setting.selected == settings["animations"]:
                    changes = False
                    apply.hideturtle()
                else:
                    changes = True
                    apply.showturtle()

                click_delay = time.time()

class Multi_option(turtle.Turtle):
    def __init__(self, x, y, settings_id, options, images, selected, screen, res, monitor_r):
        turtle.Turtle.__init__(self)
        self.penup()
        
        self.settings_id = settings_id
        self.options = options
        self.images = images
        self.selected = selected
        
        self.goto(x * monitor_r, y * monitor_r)
        
        for image in self.images:
            screen.register_shape(f"assets/{res}/settings/{image}.gif")
            
        self.shape(f"assets/{res}/settings/{self.selected}.gif")
        
    def change_selected(self, amount, res):
        if (self.options.index(self.selected) + amount) % (len(self.options)) < 0:
            index = 2
        else:
            index = (self.options.index(self.selected) + amount) % (len(self.options))
        
        self.selected = self.options[index]
        self.shape(f"assets/{res}/settings/{self.selected}.gif")
        
class Title(turtle.Turtle):
    def __init__(self, x, y, id, image, screen, res, monitor_r, mlol, foobar):
        turtle.Turtle.__init__(self)
        self.penup()
        
        self.id = id
        self.image = image
        self.goto(x * monitor_r, y * monitor_r)
        
        screen.register_shape(f"assets/{res}/settings/{image}.gif")
        self.shape(f"assets/{res}/settings/{image}.gif")
        
        if self.id == "lol":
            if resolution_setting.ycor() > mlol/2 + 25:
                foobar.showturtle()
                self.showturtle()
            else:
                foobar.hideturtle()
                self.hideturtle()
            
def settings_main(screen, monitor_r, res, mlol, foobar):
    reload_settings()
    global settings_objects
    global resolution_arrows
    global resolution_setting
    global guess_setting
    global guess_arrows
    global animation_setting
    global animation_arrows
    
    resolution_setting = Multi_option(200, 400, "resolution", ["auto", "medium", "small"], ["auto", "medium", "small"], settings["resolution"], screen, res, monitor_r[0])
    resolution_arrows = [Settings_arrow(50, 400, "resolution", -1, "arrow_left", screen, res, monitor_r[0]), Settings_arrow(350, 400, "resolution", 1, "arrow_right", screen, res, monitor_r[0])]
    resolution_title = Title(-150, 400, "resolution", "resolution", screen, res, monitor_r[0], mlol, foobar)
    
    guess_setting = Multi_option(200, 200, "guesses", [7, 8, 9, 10, 11], [7, 8, 9, 10, 11], settings["guesses"], screen, res, monitor_r[0])
    guess_arrows = [Settings_arrow(50, 200, "guesses", -1, "arrow_left", screen, res, monitor_r[0]), Settings_arrow(350, 200, "guesses", 1, "arrow_right", screen, res, monitor_r[0])]
    guess_title = Title(-150, 200, "guesses", "guesses", screen, res, monitor_r[0], mlol, foobar)
    
    animation_setting = Multi_option(200, 0, "animations", [True, False], [True, False], settings["animations"], screen, res, monitor_r[0])
    animation_arrows = [Settings_arrow(50, 0, "animations", -1, "arrow_left", screen, res, monitor_r[0]), Settings_arrow(350, 0, "animations", 1, "arrow_right", screen, res, monitor_r[0])]
    animation_title = Title(-175, 0, "animations", "animations", screen, res, monitor_r[0], mlol, foobar)
    
    lol = Title(0, -200, "lol", "lol", screen, res, monitor_r[0], mlol, foobar)
    
    settings_objects = [resolution_setting, resolution_arrows[0], resolution_arrows[1], resolution_title, guess_setting, guess_arrows[0], guess_arrows[1], guess_title, animation_setting, animation_arrows[0], animation_arrows[1], animation_title, lol]
    
def get_settings_objects():
    global settings_objects
    return settings_objects

def apply_changes():
    global require_restart
    global changes
    if not settings["resolution"] == resolution_setting.selected:
        require_restart = True
    else:
        require_restart = False
    
    settings["guesses"] = guess_setting.selected
    settings["animations"] = animation_setting.selected
    changes = False
    
    with open("settings.json", "w") as file:
        json.dump(settings, file, indent=2)
        
def get_settings():
    reload_settings()
    global settings
    return settings