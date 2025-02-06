"""Group Name: [HIT137 group 14] 
Group Members: 
[MUSKANPREET KAUR] - [S384001] 
[ARASHDEEP KAUR] - [S384121]
[ABISHEK KANDEL] - [S387576] 
[DAKSH JULKA] - [S384122] """


import cv2
import tkinter as tk
from tkinter import filedialog, Toplevel, Button, Scale, Frame
root=tk.Tk()
from PIL import Image, ImageTk


# Creating a app name Image editor app which can do different function like croping and rotating.

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x600")
        self.root.title("Image Editor")
        
        self.photo_label = None
        self.image = None
        self.original_image = None
        self.edit_window = None
        self.cropping_enabled = False
        self.cropping = False
        self.start_x = self.start_y = self.end_x = self.end_y = 0
        self.cropped_area = None
        self.resized_cropped = None
        self.resize_factor = 1.0
        self.history = []
        self.redo_stack = []

        self.create_widgets()
        
# Creating the buttons Load image and Edit image

    def create_widgets(self):
        
        self.button_1 = Button(self.root, text="Load Image", command=self.image_loader)
        self.button_1.pack(pady=10)

        self.edit_button = Button(self.root, text="Edit Image", command=self.open_edit_window, state="disabled")
        self.edit_button.pack(pady=10)
  
# Function to load image and display it.
    def image_loader(self):
    
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif"))])
        if not file_path:
            return

        try:
            self.image = Image.open(file_path).convert("RGBA")
            self.original_image = self.image.copy()
            self.history = [self.original_image.copy()]
            self.redo_stack.clear()
            self.update_image()
            self.edit_button.config(state="normal")
        except Exception as e:
            print(f"Error loading image: {e}")
            
#Updating the display of the image as of the window.
    def update_image(self):
        
        if self.image is not None:
            new_width = self.root.winfo_width()
            new_height = self.root.winfo_height() - 60
            resized_image = self.image.resize((new_width, new_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)

            if self.photo_label is None:
                self.photo_label = tk.Label(self.root, image=photo)
                self.photo_label.photo = photo
                self.photo_label.pack(fill="both", expand=True, pady=(40, 0))
            else:
                self.photo_label.config(image=photo)
                self.photo_label.photo = photo
                
# Opening the window for editing the image .
    def open_edit_window(self):
        
        if self.edit_window and self.edit_window.winfo_exists():
            return

        self.edit_window = Toplevel(self.root)
        self.edit_window.title("Edit Image")
        self.edit_window.geometry("900x600")

        frame = tk.Frame(self.edit_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
# Creating 2 screens inside windows to show orginal image and modified image
        left_frame = Frame(frame, bd=2, relief="solid")
        left_frame.pack(side="left", padx=10, pady=10)
        canvas_original = tk.Canvas(left_frame, width=600, height=600, bg="white")
        canvas_original.pack()

        right_frame = Frame(frame, bd=2, relief="solid")
        right_frame.pack(side="right", padx=10, pady=10)
        canvas_cropped = tk.Canvas(right_frame, width=600, height=600, bg="white")
        canvas_cropped.pack()

        img_tk = ImageTk.PhotoImage(self.original_image)
        canvas_original.image = img_tk
        canvas_original.create_image(0, 0, anchor="nw", image=img_tk)

        self.canvas_original = canvas_original
        self.canvas_cropped = canvas_cropped
        
#  Enabling use of mouse to crop image
        self.bind_mouse_actions()

        self.create_edit_buttons()

    def bind_mouse_actions(self):
        self.canvas_original.bind("<ButtonPress-1>", self.start_crop)
        self.canvas_original.bind("<B1-Motion>", self.draw_crop)
        self.canvas_original.bind("<ButtonRelease-1>", self.end_crop)
        
# Create different buttons for editing image.

    def create_edit_buttons(self):
        button_frame = Frame(self.edit_window)
        button_frame.pack(pady=10)

        crop_button = Button(button_frame, text="Crop", command=self.enable_crop_mode)
        crop_button.grid(row=0, column=0, padx=10)

        undo_button = Button(button_frame, text="Undo", command=self.undo)
        undo_button.grid(row=0, column=1, padx=10)

        redo_button = Button(button_frame, text="Redo", command=self.redo)
        redo_button.grid(row=0, column=2, padx=10)

        rotate_button = Button(button_frame, text="Rotate Image", command=self.rotate_image)
        rotate_button.grid(row=0, column=3, padx=10)

        save_button = Button(button_frame, text="Save Image", command=self.save_image)
        save_button.grid(row=0, column=4, padx=10)

        self.resize_slider = Scale(self.edit_window, from_=50, to=200, orient="horizontal", label="Resize %", command=self.update_resized)
        self.resize_slider.set(100)
        self.resize_slider.pack(pady=5)

        close_button = Button(button_frame, text="Close", command=self.close_edit_window)
        close_button.grid(row=0, column=5, padx=10)
        
    
#Enabling crope once mouse is clicked.
    def start_crop(self, event):
        if self.cropping_enabled:
            self.cropping = True
            self.start_x, self.start_y = event.x, event.y
  
# Drawing rectangle for croping
    def draw_crop(self, event):
        if self.cropping and self.cropping_enabled:
            self.canvas_original.delete("crop_rect")
            self.canvas_original.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red", tags="crop_rect")
   
# Compliting crop and displaying it in second screen
    def end_crop(self, event):
        if not self.cropping_enabled:
            return
        self.cropping = False
        self.end_x, self.end_y = event.x, event.y
        self.cropping_enabled = False  

        x1, x2 = sorted([self.start_x, self.end_x])
        y1, y2 = sorted([self.start_y, self.end_y])

        if x2 - x1 < 5 or y2 - y1 < 5:
            return
        self.cropped_area = self.original_image.crop((x1, y1, x2, y2))
        self.resized_cropped = self.cropped_area.copy()

        self.history.append(self.original_image.copy())
        self.redo_stack.clear()

        new_image = Image.new("RGBA", (600, 600), (255, 255, 255, 255))
        new_image.paste(self.resized_cropped, (int((600 - new_image.width) / 2), int((600 - new_image.height) / 2)))

        self.update_canvas_image(self.canvas_cropped, new_image)

# Updating Canvas with new image
    def update_canvas_image(self, canvas, image):
        img_tk = ImageTk.PhotoImage(image)
        canvas.image = img_tk
        canvas.create_image(0, 0, anchor="nw", image=img_tk)
 
# Resizing  cropped image
    def update_resized(self, event):
        self.resize_factor = self.resize_slider.get() / 100.0
        if self.cropped_area:
            new_size = (
                int(self.cropped_area.width * self.resize_factor),
                int(self.cropped_area.height * self.resize_factor),
            )
            self.resized_cropped = self.cropped_area.resize(new_size, Image.LANCZOS)

            new_image = Image.new("RGBA", (600, 600), (255, 255, 255, 255))
            new_image.paste(self.resized_cropped, (int((600 - new_image.width) / 2), int((600 - new_image.height) / 2)))

            self.update_canvas_image(self.canvas_cropped, new_image)

# Function to save  the modified image
    def save_image(self):
        if self.resized_cropped:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All Files", "*.*")],
            )
            if save_path:
                self.resized_cropped.save(save_path)
                print(f"Image saved at {save_path}")

# Enabling croping
    def enable_crop_mode(self):
        self.cropping_enabled = True

# Undo the last update
    def undo(self):
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            self.original_image = self.history[-1].copy()
            self.cropped_area = None
            self.resized_cropped = None
            self.update_image()
            self.update_canvas_image(self.canvas_cropped, self.original_image)


# Redo last undo
    def redo(self):
        if self.redo_stack:
            self.history.append(self.redo_stack.pop())
            self.original_image = self.history[-1].copy()
            self.update_image()
            self.update_canvas_image(self.canvas_cropped, self.original_image)
            
# Roatating image everytime by 90 degree.
    def rotate_image(self):
        if self.image:
            self.image = self.image.rotate(90, expand=True)
            self.history.append(self.image.copy())
            self.redo_stack.clear()
            self.update_image()
            self.update_canvas_image(self.canvas_cropped, self.image)

# Closing the editing window without closing image editior window so that user can load another image
    def close_edit_window(self):
        self.edit_window.destroy()

#Runing the main program
app = ImageEditorApp(root)
root.mainloop()