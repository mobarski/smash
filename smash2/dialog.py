from Tkinter import *
window = Tk()
window.wm_title("test")
window.wm_iconbitmap("")

def go(event=None):
	print(e.get())
	window.destroy()

v = StringVar(value='')
e = Entry(window, textvariable=v,show="*")
e.pack(pady=10, padx = 10, side=LEFT)
e.focus_set()

b = Button(window,text="go", width=5, command=go).pack(side=RIGHT)

window.bind('<Return>', go)
window.bind('<Escape>', lambda e:window.destroy())
window.focus_force()
window.mainloop()
