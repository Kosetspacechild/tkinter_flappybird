from tkinter import *
import tkinter as tk
from threading import Timer
from random import randint
from PIL import Image

f = open("keymap", "r")
data = f.read().strip()
key = "<" + data + ">"
f.close()

f = open("leaderboard", "r")
_leaderboard = [int(i) for i in f.read().strip().split(",")]
f.close()


class MainMenu(tk.Canvas):
    def __init__(self):
        # call tk.Canvas constructor
        super().__init__(
            master=window,
            width=500,
            height=1000,
        )
        # we add self. so that it becomes an atribute of the class
        self.img = tk.PhotoImage(file='pixelbg.png', master=self)
        self.create_image(500, 500, anchor=tk.CENTER, image=self.img)

        label2 = Label(self, text="WELCOME", font=(
            "Garamond", 40), bg='#405fa9')
        label2.place(relx=0.5, rely=0.20, anchor=tk.CENTER)

        # Adding buttons:
        self.button1 = Button(self)
        self.button1["text"] = "start"
        self.button1["command"] = self.show_game
        self.button1.place(relx=0.5, rely=0.40, anchor=tk.CENTER)

        self.button2 = Button(self, text="Leaderboard",
                              command=lambda: Leaderboard())
        self.button2.place(relx=0.5, rely=0.50, anchor=tk.CENTER)

        self.button3 = Button(self, text="Set Jump Key",
                              command=lambda: self.bind(
                                  "<Key>", self.key_pressed))
        self.button3.place(relx=0.5, rely=0.60, anchor=tk.CENTER)
        self.keylabel = Label(self, text=key)
        self.keylabel.place(relx=0.7, rely=0.6, anchor=tk.CENTER)

        self.button4 = Button(self, text="Exit", command=window.destroy)
        self.button4.place(relx=0.5, rely=0.70, anchor=tk.CENTER)
        self.focus_set()

    def key_pressed(self, event=None):
        game_window.key = "<" + event.keysym + ">"
        self.keylabel.configure(text=game_window.key)
        self.unbind("<Key>")
        f = open("keymap", "w")
        f.write(event.keysym)
        f.close()

    def hide(self):  # unplaces the canvas
        self.place_forget()

    def show_game(self):  # hides menu and shows game canvas
        self.place_forget()
        game_window.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        game_window.paused = False
        game_window.focus_set()
        game_window.scroll_background()
        game_window.start_game()

    def continue_game(self):  # when game is paused it goes back to menu
        self.place_forget()  # and when unpaused it continues
        game_window.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        game_window.bind(game_window.key, game_window.player.jump)
        game_window.paused = False
        game_window.focus_set()
        game_window.scroll_background()
        game_window.player.check_collisions()
        Timer(0.25, game_window.player.handle_velocity).start()
        Timer(0.5, game_window.scroll_pipes).start()
        Timer(0.5, game_window.player.increment_score).start()


# class gamewindow opens canvas for game screen

class GameWindow(tk.Canvas):
    def __init__(self):
        super().__init__(
            master=window,
            width=360,
            height=640,
            highlightthickness=0
        )
        self.key = key
        self.scorebox = tk.Label(master=self)
        self.scorebox.configure(text="0")
        self.scorebox.place(relx=0.5, rely=0, anchor=tk.N)

        self.offset = 0

        self.paused = False

        self.bgimg = tk.PhotoImage(file="bg.png")  # background image
        # duplicated so that we can use it as a moving bg
        self.bgimgarea = self.create_image(
            0, 0, anchor=tk.NW, image=self.bgimg)
        self.bgimgarea2 = self.create_image(
            360, 0, anchor=tk.NW, image=self.bgimg)
        # holds a reference to the leftmost image so that the
        self.leftmost = self.bgimgarea
        # images can be switched around so the background scrolls

        # bind keys:
        self.bind("<Escape>", self.pause)
        self.bind("<Tab>", self.boss)

        self.focus_set()  # sets focus on the canvas so that keybinds work
        self.pipeimg = tk.PhotoImage(file="pipe.png")
        self.pipeimg2 = tk.PhotoImage(file="pipe2.png")

        self.pb1 = self.create_image(
            299, 360, anchor=tk.NW, image=self.pipeimg)
        self.pb2 = self.create_image(
            501, 360, anchor=tk.NW, image=self.pipeimg),
        self.pb3 = self.create_image(
            703, 360, anchor=tk.NW, image=self.pipeimg)

        self.pt1 = self.create_image(
            299, 240, anchor=tk.SW, image=self.pipeimg2)
        self.pt2 = self.create_image(
            501, 240, anchor=tk.SW, image=self.pipeimg2),
        self.pt3 = self.create_image(
            703, 240, anchor=tk.SW, image=self.pipeimg2)

        self.bottompipes = [self.pb1, self.pb2, self.pb3]
        self.toppipes = [self.pt1, self.pt2, self.pt3]
        print(self.bottompipes)
        print(self.bbox(self.toppipes[0]))
        self.leftmostpipe = 0
        self.rightmostpipe = 2
        self.handle_pipes()

    def boss(self, event):
        if not self.paused:
            self.paused = True
            self.bossimg = tk.PhotoImage(file="bosskeyimg.png")
            self.bossimgarea = self.create_image(
                0, 0, anchor=tk.NW, image=self.bossimg)
        else:
            self.paused = False
            self.itemconfigure(self.bossimgarea, state="hidden")

    def scroll_pipes(self):
        if self.paused:
            return
        self.move(self.pb1, -1, 0)
        self.move(self.pt1, -1, 0)
        self.move(self.pb2, -1, 0)
        self.move(self.pt2, -1, 0)
        self.move(self.pb3, -1, 0)
        self.move(self.pt3, -1, 0)
        if (self.coords(self.bottompipes[self.leftmostpipe])[0] <= -51):
            self.move(self.bottompipes[self.leftmostpipe], 606, 0)
            self.move(self.toppipes[self.leftmostpipe], 606, 0)
            self.leftmostpipe = (self.leftmostpipe + 1) % 3
            self.rightmostpipe = (self.rightmostpipe + 1) % 3
        self.after(10, self.scroll_pipes)  # frequency it reruns the funtion

    def handle_pipes(self):
        offset = randint(10, 100)
        while True:
            upordown = randint(0, 1)
            if upordown == 1:
                if (self.coords(self.toppipes[self.rightmostpipe]
                                )[1] - self.offset) > 30:
                    self.move(self.toppipes[self.rightmostpipe], 0, -offset)
                    self.move(self.bottompipes[self.rightmostpipe], 0, -offset)
                    break
                else:
                    self.move(self.toppipes[self.rightmostpipe], 0, offset)
                    self.move(self.bottompipes[self.rightmostpipe], 0, offset)
                    break
            if upordown == 0:
                if (self.coords(self.toppipes[self.rightmostpipe]
                                )[1] + self.offset) < 600:
                    self.move(self.toppipes[self.rightmostpipe], 0, offset)
                    self.move(self.bottompipes[self.rightmostpipe], 0, offset)
                    break
                else:
                    self.move(self.toppipes[self.rightmostpipe], 0, -offset)
                    self.move(self.bottompipes[self.rightmostpipe], 0, -offset)
                    break
        self.after(1000, self.handle_pipes)

    def game_over(self):
        self.unbind("<Escape>")
        self.gowindow = GameOverWindow(self.player.score)
        pass

    # defining pause as an event is needed bc of the binding
    def pause(self, event):
        self.paused = True
        menu.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        menu.focus_set()
        menu.button1["text"] = "continue"  # changes text "start" to "continue"
        menu.button1["command"] = menu.continuegame  # when tapped resumes game

    # this part is what makes the scrolling background work
    def scroll_background(self):
        if self.paused:
            return  # calls back
        self.move(self.bgimgarea, -1, 0)  # amount it moves
        self.move(self.bgimgarea2, -1, 0)
        # checking for coordinates
        # if the image to the left (since there's two) touches -360
        if (self.coords(self.leftmost)[0] == -360):
            # if it is image1 it moves to the right and continues scrolling
            if self.leftmost == self.bgimgarea:
                self.moveto(self.leftmost, 360, 0)
                self.leftmost = self.bgimgarea2
            else:
                # if it is image 2 it does the same
                self.moveto(self.leftmost, 360, 0)
                self.leftmost = self.bgimgarea
        # frequency it reruns the function
        self.after(20, self.scroll_background)

    def start_game(self):
        self.handle_pipes()
        self.player = Player(self)

        self.bind(self.key, self.player.jump)

        self.player.check_collisions()
        Timer(1, self.player.handle_velocity).start()
        Timer(1, self.scroll_pipes).start()
        Timer(4, game_window.player.increment_score).start()


class Player():  # player image and control
    def __init__(self, master):
        self.master = master
        self.score = 0
        self.velocity = 0
        self.targetheight = 0
        self.img = tk.PhotoImage(file="bird.png")
        self.imgarea = self.master.create_image(
            150, 300, anchor=tk.CENTER, image=self.img, tag="player")
        print("bg1 " + str(self.master.bgimgarea))
        print("bg2 " + str(self.master.bgimgarea2))
        print("birb " + str(self.imgarea))
        self.collcheck = [self.imgarea,
                          self.master.bgimgarea, self.master.bgimgarea2]
        print(self.collcheck)

    def increment_score(self):
        if self.master.paused:
            return
        self.score += 1
        self.master.scorebox.configure(text=str(self.score))
        self.master.after(3100, self.increment_score)

    def jump(self, event=None):
        self.velocity = 2.5

    def handle_velocity(self):
        if self.master.paused:
            return
        self.master.move(self.imgarea, 0, -self.velocity)
        self.velocity -= 0.1
        self.master.after(10, self.handle_velocity)

    def check_collisions(self):  # collision box for the player
        # gets coordinates of the image tagged player
        if self.master.paused:
            return
        p = self.master.coords("player")
        if (p[1] > 640):
            print("below screen")
            self.master.game_over()
            return
        x1, y1, x2, y2 = self.master.bbox(self.imgarea)
        coll = self.master.find_overlapping(x1-2, y1-2, x2-2, y2-2)
        coll = list(coll)
        coll.remove(self.imgarea)
        try:
            coll.remove(self.master.bgimgarea)
        except ValueError:
            pass

        try:
            coll.remove(self.master.bgimgarea2)
        except ValueError:
            pass

        if (len(coll)):
            print("hit")
            print(coll)
            self.master.game_over()
        self.master.after(50, self.check_collisions)


class GameOverWindow(tk.Canvas):
    def __init__(self, score):
        super().__init__(
            master=window,
            width=360,
            height=640,
            highlightthickness=0,
            bg="black"
        )
        game_window.place_forget()
        f = open("leaderboard", "r")
        data = f.read().strip()
        print(data)
        f.close()
        leaderboard = [int(i) for i in data.split(",")]
        print(leaderboard)
        self.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        game_window.paused = True
        leaderboard.append(score)
        leaderboard.sort()
        leaderboard = [str(i) for i in leaderboard][::-1]
        leaderboard.pop(len(leaderboard) - 1)
        print(leaderboard)
        f = open("leaderboard", "w")
        f.write(",".join(leaderboard))
        f.close()

        Label(self, text="GAME OVER", font=("Arial", 30)).place(
            relx=0.5, rely=0.3, anchor=tk.CENTER)
        Button(self, text="Main Menu", command=self.show_menu).place(
            relx=0.5, rely=0.5, anchor=tk.CENTER)

    def show_menu(self):
        menu.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.place_forget()


class Leaderboard(tk.Canvas):
    def __init__(self):
        super().__init__(
            master=window,
            width=360,
            height=640,
            highlightthickness=0,
            bg="black"
        )

        menu.place_forget()
        f = open("leaderboard", "r")
        data = f.read().strip()
        print(data)
        f.close()
        leaderboard = [int(i) for i in data.split(",")]
        self.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        Label(self, width=15, text="LEADERBOARD").grid(row=1, column=1)
        Label(self, width=15, text=str(leaderboard[0])).grid(row=2, column=1)
        Label(self, width=15, text=str(leaderboard[1])).grid(row=3, column=1)
        Label(self, width=15, text=str(leaderboard[2])).grid(row=4, column=1)
        Label(self, width=15, text=str(leaderboard[3])).grid(row=5, column=1)
        Label(self, width=15, text=str(leaderboard[4])).grid(row=6, column=1)

        Button(self, text="Main Menu", command=self.show_menu).grid(
            row=10, column=1)

    def show_menu(self):
        menu.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.place_forget()


window = Tk()
window.title("Flappy bird game")
window.geometry("1920x1080")
window.attributes("-fullscreen", True)
window.resizable(width=False, height=False)
window.configure(bg="black")

game_window = GameWindow()


menu = MainMenu()
menu.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


window.mainloop()
