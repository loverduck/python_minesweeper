import tkinter as tk
from tkinter import messagebox
import numpy as np
import random

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
    	return self.canvas.coords(self.item)

    def move(self, x, y):
    	self.canvas.move(self.item, x, y)

    def delete(self):
    	self.canvas.delete(self.item)



class Square(GameObject):
	def __init__(self, canvas, x, y):
		self.width = 40
		self.height = 40
		self.x = x
		self.y = y
		item = canvas.create_rectangle(x - self.width / 2,
										y - self.height / 2,
										x + self.width / 2,
										y + self.height / 2,
										fill = '#6B66FF', tags = 'square')
		font = ('Helvetica', 20)
		self.hud = canvas.create_text(x, y, text = ' ', font = font, fill = 'black')
		super(Square, self).__init__(canvas, item)

	def text_update(self, color, text):
		self.canvas.itemconfig(self.hud, text = text, fill = color)

	def click_update(self, color):
		self.canvas.itemconfig(self.item, fill = color)


class Game(tk.Frame):
	def __init__(self, master):
		super(Game, self).__init__(master)
		
		self.mines = 10
		self.column = 9
		self.row = 9

		self.width = self.column * 40
		self.height = self.row * 40
		self.canvas = tk.Canvas(self, bg = '#aaaaff',
								width = self.width,
								height = self.height)
		self.canvas.pack()
		self.pack()
		
		self.set_menu(master)
		self.init_game(1)
		

		self.canvas.focus_set()

	def set_menu(self, master):
		menubar = tk.Menu(master)
		filemenu = tk.Menu(menubar, tearoff = 0)
		filemenu.add_command(label = "9 * 9", command = lambda:self.init_game(1))
		filemenu.add_command(label = "16 * 16", command = lambda:self.init_game(2))
		filemenu.add_command(label = "16 * 30", command = lambda:self.init_game(3))
		filemenu.add_separator()
		filemenu.add_command(label = "Exit", command = master.destroy)
		menubar.add_cascade(label = "File", menu = filemenu)
		master.config(menu = menubar)


	def init_game(self, level):
		
		self.deinit_game()

		if level == 1:
			self.mines = 10
			self.column = 9
			self.row = 9
		elif level == 2:
			self.mines = 40
			self.column = 16
			self.row = 16
		elif level == 3:
			self.mines = 99
			self.column = 30
			self.row = 16

		self.width = self.column * 40
		self.height = self.row * 40
		self.canvas = tk.Canvas(self, bg = '#aaaaff',
								width = self.width,
								height = self.height)

		self.canvas.pack()
		self.pack()

		self.canvas.bind('<Button-1>', self.left_button)
		self.canvas.bind('<Button-3>', self.right_button)

		self.items = [[0 for x in range(self.column)] for y in range(self.row)]#[[None]*self.column]*self.row
		#self.items = np.arange(self.row*self.column).reshape(self.row,self.column)
		self.pattern = np.arange(self.column*self.row*3).reshape(self.row,self.column,3)
		
		for y in range(0, self.row):
			for x in range(0, self.column):
				self.add_square(x, y)

		for y in range(0, self.row):
			for x in range(0, self.column):
				self.pattern[y][x][0] = 0
				self.pattern[y][x][1] = 0

		cnt = 0

		while cnt < self.mines :
			x = random.randint(0, self.column-1)
			y = random.randint(0, self.row - 1)

			if self.pattern[y][x][0] == 0 :
				self.pattern[y][x][0] = 1
				cnt = cnt + 1

		for y in range(0, self.row):
			for x in range(0, self.column):
				cnt = 0
				for yy in range(-1, 2):
					for xx in range(-1, 2):
						if x+xx < 0:
							continue
						if y+yy < 0:
							continue
						if x+xx >= self.column :
							continue
						if y+yy >= self.row : 
							continue

						if self.pattern[y+yy][x+xx][0] == 1:
							cnt += 1

				self.pattern[y][x][2] = cnt


	def add_square(self, x, y):
		#square = Square(self.canvas, x * 40 + 20, y * 40 + 20)
		self.items[y][x] = Square(self.canvas, x * 40 + 20, y * 40 + 20)


	def deinit_game(self):
		self.canvas.destroy()

	def update(self):
		cnt = 0

		for y in range(0, self.row):
			for x in range(0, self.column):
				if self.pattern[y][x][1] == 0:
					text = ' '
				elif self.pattern[y][x][1] == 2:
					text = 'X'
				else :
					text = '%d' % self.pattern[y][x][2]
					self.items[y][x].click_update('#4641D9')
					cnt += 1
				
				if self.pattern[y][x][1] == 2:
					self.items[y][x].text_update('red', text)
				else :
					self.items[y][x].text_update('black', text)

		if cnt == (self.column*self.row) - self.mines:
			tk.messagebox.showinfo('Game', 'You Win!')
			self.deinit_game()
			self.init_game(1)



	def left_button(self, event):
		x = event.x//40
		y = event.y//40

		if self.pattern[y][x][0] == 1:
			tk.messagebox.showinfo('Game', 'Game Over')
			self.deinit_game()
			self.init_game(1)
		else :
			self.pattern[y][x][1] = 1
			if self.pattern[y][x][2] == 0:
				self.detect_region(x, y)

		self.update()

	def right_button(self, event):
		x = event.x//40
		y = event.y//40

		if self.pattern[y][x][1] == 0:
			self.pattern[y][x][1] = 2
		elif self.pattern[y][x][1] == 2:
			self.pattern[y][x][1] = 0

		self.update()

	def detect_region(self, x, y):
		for yy in range(-1, 2):
			for xx in range(-1, 2):
				if x+xx < 0 :
					continue
				if y+yy < 0 :
					continue
				if x+xx >= self.column :
					continue
				if y+yy >= self.row :
					continue
				
				if self.pattern[y+yy][x+xx][0] == 1:
					continue
				if self.pattern[y+yy][x+xx][1] == 1:
					continue

				self.pattern[y+yy][x+xx][1] = 1

				if self.pattern[y+yy][x+xx][2] != 0 :
					continue
				self.detect_region(x+xx, y+yy)


if __name__ == '__main__':
	root = tk.Tk()
	root.title('Minesweeper')
	game = Game(root)
	game.mainloop()