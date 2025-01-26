# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 16:21:34 2025

@author: bart.bozon
"""

import tkinter as tk
from tkinter import filedialog


class TextEditor:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("SDF viewer - Bart Bozon")
        self.file=''

        self.text_area = tk.Text(self.window, wrap=tk.WORD)
        self.text_area.pack(expand=tk.YES, fill=tk.BOTH)
        self.indent_level=2
        self.value_label = tk.Label(self.window, text=f"Indent level: {self.indent_level-1}", anchor="w")
        self.value_label.pack(fill=tk.X, side=tk.BOTTOM)


        self.full_text = ""  # Store the full text when hiding lines
        
        self.create_menu()

        self.window.mainloop()
    def update_value_label(self):
        """Update the label at the bottom with the current value"""
        self.value_label.config(text=f"Indent level: {self.indent_level-1}")
    def create_menu(self):
        menu = tk.Menu(self.window)
        self.window.config(menu=menu)
        menu.add_command(label="Open", command=self.open_file)
        menu.add_command(label="Hide level", command=self.hide_level)
        menu.add_command(label="Show Level", command=self.show_level)
        menu.add_command(label="About", command=self.status)

    def status(self):
        """Display a popup showing the current value"""
        popup = tk.Toplevel(self.window)
        popup.title("About")
        label = tk.Label(popup, text="Written by : Bart Bozon")
        label.pack(padx=20, pady=20)
        close_button = tk.Button(popup, text="Close", command=popup.destroy)
        close_button.pack(padx=20, pady=10)
        popup.mainloop()
  
    def open_file(self):    
        file = filedialog.askopenfilename(
            defaultextension=".SDF",
            filetypes=[("Text Files", "*.SDF"), ("All Files", "*.*")],
        )
        line_no=0
        indentation=0
        if file:
            with open(file, "r") as source_file, open('temp_file', "w") as destination_file,open(file.rstrip('.sdf')+'.txt', "w") as reformated_file:
                for line in source_file:
                    prev_indentation=indentation
                    if ('<?xml' in line) or ('<!' in line):
                        pass
                    else:
                        if '<' in line:
                            if line[line.find('<')+1]=='/':
                                indentation-=1
                                prev_indentation=indentation                                
                            else:
                                if line.find('/')>-1:
                                    pass
                                else:
                                    indentation+=1
                    indent_str=str(prev_indentation)+'   '
                    line_no_str='     '+str(line_no)
                    line_dest=indent_str[:2]+'|'+line_no_str[-4:]+'|'+line
                    destination_file.write(line_dest)                   
                    line_no+=1    

                    line_refor=line.lstrip()
                    if prev_indentation>0:
                        for i in range (0,prev_indentation):
                            line_refor='  '+line_refor
                    reformated_file.write(line_refor)                   
                    
        if file:
            self.window.title(f"Python Text Editor - {file}")
            self.text_area.delete(1.0, tk.END)
            with open('temp_file', "r") as file_handler:
                self.text_area.insert(tk.INSERT, file_handler.read())
            self.file=file

    def hide_level(self):
        if self.file=='':
            pass
        else:
            self.full_text = self.text_area.get(1.0, tk.END).strip()
            lines = self.full_text.split("\n")
            cursor_position = self.text_area.index(tk.INSERT)
            bbox = self.text_area.bbox(cursor_position)
            if bbox:
                 x, y, _, _ = bbox
                 line_height=16
                 # Calculate the line number
                 line_number = int(y / line_height)  # Calculating the line numberumber
                 print(f"Cursor is in line {line_number}")
            else:
                 print("Cursor is out of view")
                 line_number=0
            line_pos, column_pos = map(int, cursor_position.split('.'))
            print (line_pos,lines[line_pos-1])
            if (line_pos>=len(lines)):
                line_pos=0             
            line_value=int(lines[line_pos-1][3:7].lstrip())-1 
            print ('line value ',line_value)
            self.text_area.delete(1.0, tk.END)
            with open('temp_file', "r") as file_handler:
                self.text_area.insert(tk.INSERT, file_handler.read())
            self.full_text = self.text_area.get(1.0, tk.END).strip()
            self.indent_level =self.indent_level-1
            if self.indent_level<2:
                self.indent_level=2
            # Restore the full text
            lines = self.full_text.split("\n")
            filtered_lines = lines            
            for i in range (self.indent_level,20) :
                filtered_lines = [line for line in filtered_lines if not (line.startswith(str(i)))]
            #lines = self.full_text.split("\n")
            #filtered_lines = [line for line in lines if not (line.startswith('2') or line.startswith('3'))]
    
            # Clear text widget and insert filtered lines
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, "\n".join(filtered_lines))
    
            # Restore scroll position
            for i in range (0,len(filtered_lines)-1):
                if line_value<=(int(filtered_lines[i][3:7].lstrip())-1):
                    self.text_area.yview_moveto((i-line_number)/len(filtered_lines))
                    print (str(line_number)+'.1')
                    self.text_area.mark_set(tk.INSERT,str(i+1)+'.'+str(column_pos))
                    self.text_area.see(tk.INSERT) 
                    break
            self.update_value_label()
            
    def show_level(self):
        if self.file=='':
            pass
        else:
            self.full_text = self.text_area.get(1.0, tk.END).strip()
            lines = self.full_text.split("\n")
            cursor_position = self.text_area.index(tk.INSERT)
            bbox = self.text_area.bbox(cursor_position)
            if bbox:
                 x, y, _, _ = bbox
                 line_height=16
                 # Calculate the line number
                 line_number = int(y / line_height)  # Calculating the line numberumber
                 print(f"Cursor is in line {line_number}")
            else:
                 print("Cursor is out of view")
                 line_number=0
            line_pos, column_pos = map(int, cursor_position.split('.'))
            print (line_pos,lines[line_pos-1])
            if (line_pos>=len(lines)):
                line_pos=0             
            line_value=int(lines[line_pos-1][3:7].lstrip())-1 
            print ('line value ',line_value)
            self.text_area.delete(1.0, tk.END)
            with open('temp_file', "r") as file_handler:
                self.text_area.insert(tk.INSERT, file_handler.read())
            self.full_text = self.text_area.get(1.0, tk.END).strip()
            self.indent_level =self.indent_level+1
            if self.indent_level>20:
                self.indent_level=20
            # Restore the full text
            lines = self.full_text.split("\n")
            filtered_lines = lines            
            for i in range (self.indent_level,20) :
                filtered_lines = [line for line in filtered_lines if not (line.startswith(str(i)))]
            #lines = self.full_text.split("\n")
            #filtered_lines = [line for line in lines if not (line.startswith('2') or line.startswith('3'))]
    
            # Clear text widget and insert filtered lines
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, "\n".join(filtered_lines))
    
            # Restore scroll position
            for i in range (0,len(filtered_lines)-1):
                if line_value<=(int(filtered_lines[i][3:7].lstrip())-1):
                    self.text_area.yview_moveto((i-line_number)/len(filtered_lines))
                    print (str(line_number)+'.1')
                    self.text_area.mark_set(tk.INSERT,str(i+1)+'.'+str(column_pos))
                    self.text_area.see(tk.INSERT) 
                    break
            self.update_value_label()
            
                

        


if __name__ == "__main__":
    TextEditor()
