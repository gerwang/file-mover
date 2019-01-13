import tkinter as tk
from tkinter import messagebox
import os
import shutil

src_dirs = [
	'C:\\path\\to\\desktop'
]
dest_dirs = [
	'D:\\path\\to\\warehouse'
]


def create_path_list(dirname, include_file=True, include_dir=False):
    res = []
    for name in os.listdir(dirname):
        abs_path = os.path.join(dirname, name)
        if os.path.isdir(abs_path):
            if include_dir:
                res.append(abs_path)
        elif os.path.isfile(abs_path):
            if include_file:
                res.append(abs_path)
    return res


class Application(tk.Frame):
    def __init__(self, master=None, src_dirs=[], dest_dirs=[]):
        super().__init__(master)
        self.master = master
        self.src_dirs = src_dirs
        self.dest_dirs = dest_dirs
        self.pack()
        self.create_widgets()

        self.todos = []
        for src in self.src_dirs:
            self.todos.extend(create_path_list(
                src, include_file=True, include_dir=True))
        self.dones = []
        self.load_new()

    def load_new(self):
        if not self.todos:
            self.current_name.set('done!!')
            messagebox.showinfo('Done', 'all done!')
        else:
            path = self.todos.pop()
            self.current_name.set(path)

    def push_todo_back(self, name):
        self.todos.append(self.current_name.get())
        self.current_name.set(name)

    def undo_new(self):
        try:
            if not self.dones:
                messagebox.showinfo('Nothing to undo',
                                    'nothing to undo, did nothing!')
            else:
                op = self.dones.pop()
                cmd = op['command']
                if cmd == 'move':
                    dest = op['dest']
                    src = op['src']
                    shutil.move(dest, src)
                    self.push_todo_back(src)
                elif cmd == 'rename':
                    dest = op['dest']
                    src = op['src']
                    shutil.move(dest, src)
                    self.current_name.set(src)
                elif cmd == 'skip':
                    src = op['src']
                    self.push_todo_back(src)
                elif cmd == 'add_directory':
                    button = op['button']
                    full_path = op['path']
                    os.rmdir(full_path)
                    button.destroy()
                else:
                    raise Exception('unknown command: '+cmd)

        except BaseException as e:
            messagebox.showerror('undo', str(e))

    def skip(self):
        try:
            self.dones.append({
                'command': 'skip',
                'src': self.current_name.get(),
            })
            self.load_new()
        except BaseException as e:
            messagebox.showerror('skip', str(e))

    def remove(self):
        try:
            path = self.current_name.get()
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            self.load_new()
        except BaseException as e:
            messagebox.showerror('remove', str(e))

    def open(self):
        try:
            os.startfile(self.current_name.get(), 'open')
        except BaseException as e:
            messagebox.showerror('open', str(e))

    def move(self, dest):
        try:
            src = self.current_name.get()
            basename = os.path.basename(src)
            dest = os.path.join(dest, basename)
            shutil.move(src, dest)
            self.dones.append({
                'command': 'move',
                'src': src,
                'dest': dest,
            })
            self.load_new()
        except BaseException as e:
            messagebox.showerror('move', str(e))

    def rename(self):
        try:
            src = self.current_name.get()
            dirname = os.path.dirname(src)

            dest = os.path.join(dirname, self.modify_name_entry.get())
            self.modify_name_entry.delete(0, tk.END)
            shutil.move(src, dest)
            self.current_name.set(dest)

            self.dones.append({
                'command': 'rename',
                'src': src,
                'dest': dest,
            })
        except BaseException as e:
            messagebox.showerror('rename', str(e))

    def add_button(self, res_frame, dirname):
        button = tk.Button(res_frame, text=os.path.basename(
            dirname), command=lambda: self.move(dirname))
        button.dirname = dirname
        button.pack()
        res_frame.button_list.append(button)
        return button

    def add_directory(self, res_frame):
        try:
            name = res_frame.add_dir_entry.get()
            res_frame.add_dir_entry.delete(0, tk.END)
            pathname = res_frame.pathname
            full_path = os.path.join(pathname, name)
            os.mkdir(full_path)
            self.dones.append({
                'command': 'add_directory',
                'button': self.add_button(res_frame, full_path),
                'path': full_path,
            })
        except BaseException as e:
            messagebox.showerror('add directory', str(e))

    def create_buttons_from_path(self, pathname, master):
        path_list = create_path_list(
            pathname, include_file=False, include_dir=True)
        res = tk.Frame(master)
        res.pack(side=tk.LEFT)
        res.pathname = pathname
        res.add_dir_entry = tk.Entry(res)
        res.add_dir_entry.pack()
        res.add_dir_button = tk.Button(
            res, text='add directory', command=lambda: self.add_directory(res))
        res.add_dir_button.pack()
        res.name_label = tk.Label(res, text=os.path.basename(pathname))
        res.name_label.pack()
        res.button_list = []
        for dirname in path_list:
            self.add_button(res, dirname)
        return res

    def create_widgets(self):
        self.current_name = tk.StringVar()
        self.current_name_label = tk.Label(
            self, textvariable=self.current_name)
        self.current_name_label.pack()

        self.modify_name_frame = tk.Frame(self)
        self.modify_name_frame.pack()
        self.modify_name_entry = tk.Entry(self.modify_name_frame)
        self.modify_name_entry.pack(side=tk.LEFT)
        self.modify_confirm_button = tk.Button(
            self.modify_name_frame, text='rename', command=self.rename)
        self.modify_confirm_button.pack(side=tk.LEFT)

        self.dest_dirs_frame = tk.Frame(self)
        self.dest_dirs_frame.pack()
        self.dir_frames_list = []
        for pathname in self.dest_dirs:
            self.dir_frames_list.append(
                self.create_buttons_from_path(pathname, self.dest_dirs_frame))

        self.control_frame = tk.Frame(self)
        self.control_frame.pack()
        self.undo_button = tk.Button(
            self.control_frame, text='undo', command=self.undo_new)
        self.undo_button.pack(side=tk.LEFT)
        self.skip_button = tk.Button(
            self.control_frame, text='skip', command=self.skip)
        self.skip_button.pack(side=tk.LEFT)
        self.remove_button = tk.Button(
            self.control_frame, text='remove', command=self.remove)
        self.remove_button.pack(side=tk.LEFT)
        self.open_button = tk.Button(
            self.control_frame, text='open', command=self.open)
        self.open_button.pack(side=tk.LEFT)


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root, src_dirs, dest_dirs)
    root.mainloop()
