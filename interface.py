'''     
Trabalho_1 - Teoria dos Grafos

Alunos: 
* Carlos Gabriel de Oliveira Frazão - 22.1.8100
* Patrick Peres Nicolini - 22.1.8103

'''

import itertools
import threading
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
from ttkthemes import ThemedTk
from bitmap import ImageGraph


class BitmapProcessorApp:


    def __init__(self, master):
        self.master = master
        self.master.title("Bitmap Processor")
        self.master.geometry('500x500')  # Set the window size (width x height)
        self.master.configure(bg='lightgrey')  # Set the background color

        # Create a new window for the loading message (but don't show it yet)
        self.loading_window = tk.Toplevel(self.master)
        self.loading_window.withdraw()  # Hide the window
        self.loading_window.overrideredirect(True)  # Hide the title bar

        # Create a style
        style = ttk.Style()
        style.configure("TButton",
                        foreground="midnight blue",
                        background="lightgrey",
                        font=("Helvetica", 16),
                        padding=10)

        # Create a frame for the buttons
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)  

        # Create widgets
        self.load_button = ttk.Button(self.button_frame, text="Load Bitmap", command=self.load_bitmap)
        self.load_button.grid(row=0 , column=0, padx=5) 

        # Create a StringVar for the loading message
        self.loading_message = tk.StringVar()
        self.loading_label = tk.Label(self.loading_window, textvariable=self.loading_message, font=("Helvetica", 16), fg="green")
        self.loading_label.pack(padx=5, pady=5)  

        # Create an iterator for the loading animation
        self.loading_animation = itertools.cycle(['◢', '◣', '◤', '◥'])

        self.image_graph = None
        self.start_pixel = None
        self.end_pixel = None
        self.scroll_bar = None
        self.buttons_canva_flag = None
        self.red_pixel = None
        self.green_pixel = None


    def load_bitmap(self):
        file_path = filedialog.askopenfilename(filetypes=[("Bitmap files", "*.bmp")])
        if file_path:
            self.start_page_flag = True
            # Start the loading operation in a separate thread
            threading.Thread(target=self.load_bitmap_thread, args=(file_path,)).start()

            # Center the loading window
            self.center_window(self.loading_window)

    def center_window(self, window):
        # Update the window to make sure to get the correct sizes
        window.update()

        # Calculate the position to center the window
        x = self.master.winfo_x() + (self.master.winfo_width() / 2) - (window.winfo_width() / 2)
        y = self.master.winfo_y() + (self.master.winfo_height() / 2) - (window.winfo_height() / 2)

        # Set the position of the window
        window.geometry("+%d+%d" % (x, y))

        # Show the window
        window.deiconify()

    def load_bitmap_thread(self, file_path):
        # Start the loading animation
        self.start_loading_animation()

        self.image_graph = ImageGraph(file_path)
        self.image_graph.build_graph()

        print(">>>>>>> graph info <<<<<<<\n")
        #print the number of nodes and edges
        print("Number of nodes: ", self.image_graph.number_of_nodes)
        print("Number of edges: ", self.image_graph.number_of_edges)
        print("\n")

        # Update the window size and display the bitmap
        self.master.geometry('1280x720')
        self.display_bitmap()

        # Stop the loading animation
        self.stop_loading_animation()

    def start_loading_animation(self):
        self.loading = True
        threading.Thread(target=self.update_loading_animation).start()

        # Show the loading window
        self.loading_window.deiconify()

    def update_loading_animation(self):
        while self.loading:
            self.loading_message.set('Loading ' + next(self.loading_animation))
            time.sleep(0.01)  # Add a small delay to make the animation visible

    def stop_loading_animation(self):
        self.loading = False
        self.loading_message.set('')

        # Hide the loading window
        self.loading_window.withdraw()

    def display_bitmap(self):

        if self.buttons_canva_flag is None:

            self.process_button = ttk.Button(self.button_frame, text="Process Pixels", command=self.process_pixels)
            self.process_button.grid(row=0, column=1, padx=5)  

            self.reset_button = ttk.Button(self.button_frame, text="Reset", command=self.reset_pixels)
            self.reset_button.grid(row=0, column=2, padx=5)  

            self.canvas = tk.Canvas(self.master, cursor="cross", bg='white', bd=2, relief='groove')
            self.canvas.pack(pady=10) 

            self.canvas.bind("<Button-1>", self.on_pixel_click)  # Bind left mouse click event
            self.buttons_canva_flag = True

        if self.image_graph.green_pixel is not None and self.image_graph.red_pixel is not None:
            self.process_green_red_button = ttk.Button(self.button_frame, text="Process G/R", command=self.process_green_red_pixels)
            self.process_green_red_button.grid(row=0, column=3, padx=5) 

        # Convert bitmap to Tkinter-compatible format
        tk_bitmap = ImageTk.PhotoImage(self.image_graph.image)

        # Update canvas with the loaded bitmap
        self.canvas.config(width=self.image_graph.width, height=self.image_graph.height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_bitmap)
        self.canvas.image = tk_bitmap

        if self.scroll_bar is None:
            # Add horizontal scrollbar
            h_scrollbar = tk.Scrollbar(self.master, orient=tk.HORIZONTAL, command=self.canvas.xview, width=20, bg='blue')
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            self.canvas.config(xscrollcommand=h_scrollbar.set)
            # Configure canvas to scroll
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            # Make the scrollbar start in the middle
            self.canvas.xview_moveto(0.5/2)
            self.scroll_bar = True


        # Configure canvas to scroll
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        # Bind the scrollbar movement to the canvas (only after the image is loaded)
        self.canvas.bind("<Configure>", self.update_scroll_region)

    def update_scroll_region(self, event):
        # Configure canvas to scroll when the window is resized
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_pixel_click(self, event):
        # Get the original coordinates of the clicked pixel
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        # If two pixels have been processed, reset the selection
        if self.start_pixel is not None and self.end_pixel is not None:
            self.reset_pixels()

        # If the green and red pixels have been processed, reset the selection
        if self.image_graph.green_pixel is not None and self.image_graph.red_pixel is not None:
            if self.start_pixel is not None or self.end_pixel is None:
                self.reset_pixels()
                self.green_pixel = self.image_graph.green_pixel
                self.red_pixel = self.image_graph.red_pixel
                self.image_graph.green_pixel = None
                self.image_graph.red_pixel = None

        # Store the clicked pixel as the start or end pixel
        if self.start_pixel is None:
            self.start_pixel = (x, y)
            color = "salmon"
        else:
            self.end_pixel = (x, y)
            color = "pale green"

        # Draw a marker at the clicked pixel
        self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill=color,outline=color, width=6)
        print("Clicked pixel: ({}, {})".format(x, y))

    def reset_pixels(self):
        # Clear the canvas and reset the clicked pixels
        self.canvas.delete("all")
        self.start_pixel = None
        self.end_pixel = None

        # Redraw the bitmap
        self.display_bitmap()

    def reset(self):
        # Clear the canvas and reset the clicked pixels
        self.canvas.delete("all")

        # Redraw the bitmap
        self.display_bitmap()

    def process_pixels(self):
        if self.start_pixel is None or self.end_pixel is None:
            print("Please select start and end pixels.")
            messagebox.showinfo("No Pixels Selected", "Please select start and end pixels.")
            return
        if self.image_graph.image.getpixel(self.start_pixel) == (0, 0, 0) or self.image_graph.image.getpixel(self.end_pixel) == (0, 0, 0):
            print("Please select a valid start and end pixel.")
            messagebox.showinfo("Invalid Pixel", "Please select a valid start and end pixel.")
            return
        if self.start_pixel is not None and self.end_pixel is not None:
            path = self.image_graph.find_path(self.start_pixel, self.end_pixel)
            if path is None:
                print("No path found.")
                messagebox.showinfo("No Path", "No path found between the selected pixels.")
                return
            # Draw the path on the canvas
            for i in range(len(path) - 1):
                self.canvas.create_line(path[i][0], path[i][1], path[i + 1][0], path[i + 1][1], fill="red", width=2, smooth=True)
                self.canvas.update()

            #creates a copy of the image to be able to change the color of the pixels in the path
            image = self.image_graph.image.copy()
            #prints the path with arrows indicating the direction
            print("\nIt is possible to move the equipment: \n", end="")
            for i in range(len(path) - 1):
                if path[i][0] == path[i+1][0]:
                    if path[i][1] > path[i+1][1]:
                        print("↑ ", end="")
                    else:
                        print("↓ ", end="")
                else:
                    if path[i][0] > path[i+1][0]:
                        print("← ", end="")
                    else:
                        print("→ ", end="")
                try:
                    image.putpixel((path[i][0], path[i][1]), (255, 0, 0))
                except Exception as e:
                    print(f"Error putting pixel: {e}")

            path_image_name = f"{self.image_graph.image.filename.split('.')[0]}_{self.start_pixel}-{self.end_pixel}_path.bmp"
            #salves the image with the path in the same directory as the original image
            try:
                image.save(path_image_name, "BMP")
                #shows a message box with the path for the image
                messagebox.showinfo("Path Saved", f"A bitmap with the path between the pixels has been saved in the following directory: \n{path_image_name}")
                print("Image saved successfully.")
            except Exception as e:
                print(f"Error saving image: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}") 

            print()
            #prints the number of pixels in the path
            print("\nNumber of pixels in the path: ", len(path))
        else:
            print("\nPlease select start and end pixels.")

    def process_green_red_pixels(self):

        if self.green_pixel is not None or self.red_pixel is not None:
            self.image_graph.green_pixel = self.green_pixel
            self.image_graph.red_pixel = self.red_pixel

        if self.image_graph.green_pixel is not None and self.image_graph.red_pixel is not None:
            path = self.image_graph.find_path(self.image_graph.red_pixel, self.image_graph.green_pixel)
            if path is None:
                print("No path found.")
                messagebox.showinfo("No Path", "No path found between the selected pixels.")
                return
            self.reset_pixels()
            # Draw the path on the canvas
            for i in range(len(path) - 1):
                self.canvas.create_line(path[i][0], path[i][1], path[i + 1][0], path[i + 1][1], fill="red", width=2, smooth=True)
                self.canvas.update()

            #creates a copy of the image to be able to change the color of the pixels in the path
            image = self.image_graph.image.copy()
            
            #prints the path with arrows indicating the direction
            print("\nIt is possible to move the equipment: \n", end="")
            for i in range(len(path) - 1):
                if path[i][0] == path[i+1][0]:
                    if path[i][1] > path[i+1][1]:
                        print("↑ ", end="")
                    else:
                        print("↓ ", end="")
                else:
                    if path[i][0] > path[i+1][0]:
                        print("← ", end="")
                    else:
                        print("→ ", end="")
                try:
                    image.putpixel((path[i][0], path[i][1]), (255, 0, 0))
                except Exception as e:
                    print(f"Error putting pixel: {e}")

            path_image_name = f"{self.image_graph.image.filename.split('.')[0]}_{self.image_graph.red_pixel}-{self.image_graph.green_pixel}_path.bmp"
            #salves the image with the path in the same directory as the original image
            try:
                image.save(path_image_name, "BMP")
                #shows a message box with the path for the image
                messagebox.showinfo("Path Saved", f"A bitmap with the path between the pixels has been saved in the following directory: \n{path_image_name}")
                print("Image saved successfully.")
            except Exception as e:
                print(f"Error saving image: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}") 

            
            print()
            #prints the number of pixels in the path
            print("\nNumber of pixels in the path: ", len(path))
        else:
            print("\nPlease select start and end pixels.")


# Create the main Tkinter window
root = tk.Tk()
app = BitmapProcessorApp(root)
root.mainloop()


