from Tkinter import *
window = Tk()
window.wm_title("test")
window.wm_iconbitmap("")

def go():
	print("go",v.get())
	print(dir(v))
	window.destroy()

v = StringVar(value='TODO')
e = Entry(window, textvariable=v,show="*").pack(pady=10, padx = 10, side=LEFT)
b = Button(window,text="go", width=5, command=go).pack(side=RIGHT)
window.mainloop()
