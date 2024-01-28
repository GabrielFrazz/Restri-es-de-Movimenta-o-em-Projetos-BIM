'''     
Trabalho_1 - Teoria dos Grafos

Alunos: 
* Carlos Gabriel de Oliveira Frazão - 22.1.8100
* Patrick Peres Nicolini - 22.1.8103

'''

import itertools
import os
import threading
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
from matplotlib import colors
from ttkthemes import ThemedTk
from bitmap import ImageGraph
import matplotlib.colors as mcolors

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
        self.image_paths = None
        self.start_pixel = None
        self.end_pixel = None
        self.scroll_bar = None
        self.buttons_canva_flag = None
        self.red_pixel = None
        self.green_pixel = None
        self.current_floor = 0
        self.scalling_factor = 1

    def load_bitmap(self):
        self.current_floor = 0
        file_path = filedialog.askopenfilenames(filetypes=[("Bitmap files", "*.bmp")])
        self.image_paths = list(file_path)
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

        if self.image_graph.width < 500 or self.image_graph.height < 500:
            hd_width = 800
            hd_height = 600
            width_scale = hd_width / self.image_graph.width
            height_scale = hd_height / self.image_graph.height
            self.scaling_factor = int(min(width_scale, height_scale)) 
        else:
            self.scaling_factor = 1

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
            
            if self.scaling_factor == 1:
                self.process_button = ttk.Button(self.button_frame, text="Process Pixels", command=self.process_pixels)
                self.process_button.grid(row=0, column=1, padx=5)  

            self.reset_button = ttk.Button(self.button_frame, text="Reset", command=self.reset_pixels)
            self.reset_button.grid(row=0, column=2, padx=5)  

            if self.scaling_factor == 1:
                self.show_graph_button = ttk.Button(self.button_frame, text="Show Graph", command=self.image_graph.plot_large_graph)
                self.show_graph_button.grid(row=0, column=4, padx=5)

            self.canvas = tk.Canvas(self.master, cursor="cross", bg='white', bd=2, relief='groove')
            self.canvas.pack(pady=10) 

            self.canvas.bind("<Button-1>", self.on_pixel_click)  # Bind left mouse click event
            self.buttons_canva_flag = True

        if self.image_graph.green_pixels is not None and self.image_graph.red_pixel is not None:
            self.process_green_red_button = ttk.Button(self.button_frame, text="Process G/R", command=self.process_green_red_pixels)
            self.process_green_red_button.grid(row=0, column=3, padx=5) 

        # Convert bitmap to Pillow Image
        self.original_images = [Image.open(image.filename) for image in self.image_graph.images]

        # Resize the images
        self.resized_images = [original_image.resize(
            (original_image.width * self.scaling_factor, original_image.height * self.scaling_factor),
            resample=Image.NEAREST
        ) for original_image in self.original_images]

        # Convert resized images to Tkinter-compatible format
        self.resized_images_tk = [ImageTk.PhotoImage(resized_image) for resized_image in self.resized_images]

        # Create a new Canvas for each image
        self.canvases = [tk.Canvas(self.master, cursor="cross", bg='white', bd=2, relief='groove') for _ in self.resized_images_tk]

        # Update canvas with the loaded and resized bitmap
        self.canvas.config(width=self.resized_images_tk[self.current_floor].width(), height=self.resized_images_tk[self.current_floor].height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.resized_images_tk[self.current_floor])
        self.canvas.image = self.resized_images_tk[self.current_floor]

        # Add navigation buttons if they don't exist yet and there is more than one floor
        if len(self.image_graph.images) > 1:
            if not hasattr(self, 'next_button'):
                self.next_button = ttk.Button(self.master, text="Next Floor", command=self.next_floor)
                self.next_button.place(relx=0.9, rely=0.5, anchor='e')  # Place the button on the right side

            if not hasattr(self, 'previous_button'):
                self.previous_button = ttk.Button(self.master, text="Previous Floor", command=self.previous_floor)
                self.previous_button.place(relx=0.1, rely=0.5, anchor='w')  # Place the button on the left side

        # Hide the "Previous Floor" button on the first floor
        if hasattr(self, 'previous_button'):
            if self.current_floor == 0:
                self.previous_button.place_forget()
            else:
                self.previous_button.place(relx=0.1, rely=0.5, anchor='w')

        # Hide the "Next Floor" button on the last floor
        if hasattr(self, 'next_button'):
            if self.current_floor == len(self.image_graph.images) - 1:
                self.next_button.place_forget()
            else:
                self.next_button.place(relx=0.9, rely=0.5, anchor='e')

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



    def next_floor(self):
        if self.current_floor < len(self.image_graph.images) - 1:
            self.current_floor += 1
            self.display_bitmap()

    def previous_floor(self):
        if self.current_floor > 0:
            self.current_floor -= 1
            self.display_bitmap()


    def update_scroll_region(self, event):
        # Configure canvas to scroll when the window is resized
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_pixel_click(self, event):
        # Get the original coordinates of the clicked pixel
        x_original, y_original = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))

        # Adjust coordinates for display in the interface
        x_resized, y_resized = int(x_original / self.scaling_factor), int(y_original / self.scaling_factor)

        # If two pixels have been processed, reset the selection
        if self.start_pixel is not None and self.end_pixel is not None:
            self.reset_pixels()

        # If the green and red pixels have been processed, reset the selection
        if self.image_graph.green_pixels is not None and self.image_graph.red_pixel is not None:
            if self.start_pixel is not None or self.end_pixel is None:
                self.reset_pixels()
                self.green_pixel = self.image_graph.green_pixels
                self.red_pixel = self.image_graph.red_pixel
                self.image_graph.green_pixels = None
                self.image_graph.red_pixel = None

        # Store the clicked pixel as the start or end pixel
        if self.start_pixel is None:
            self.start_pixel = (x_resized, y_resized)
            color = "salmon"
            rgb = tuple(round(i * 255) for i in mcolors.to_rgb(color))
        else:
            self.end_pixel = (x_resized, y_resized)
            color = "green"
            rgb = tuple(round(i * 255) for i in mcolors.to_rgb(color))
        
        if self.scaling_factor != 1:
            self.image_graph.image.putpixel((x_resized, y_resized), rgb)
        else:
            # Draw a marker at the clicked pixel
            self.canvas.create_oval(x_original - 2, y_original - 2, x_original + 2, y_original + 2, fill=color, outline=color, width=6)
        print("Clicked pixel: ({}, {})".format(x_resized, y_resized))
        print(f"color: {rgb}" )


    def reset_pixels(self):
        # Clear the canvas and reset the clicked pixels
        self.canvas.delete("all")
        self.start_pixel = None
        self.end_pixel = None

        self.image_graph.images = [Image.open(image_path) for image_path in self.image_paths]

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
                x1_original, y1_original = path[i]
                x2_original, y2_original = path[i + 1]

                x1_resized, y1_resized = x1_original * self.scaling_factor, y1_original * self.scaling_factor
                x2_resized, y2_resized = x2_original * self.scaling_factor, y2_original * self.scaling_factor

                self.canvas.create_line(x1_resized, y1_resized, x2_resized, y2_resized, fill="red", width=2, smooth=True)
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
            self.image_graph.green_pixels = self.green_pixel
            self.image_graph.red_pixel = self.red_pixel

        if self.image_graph.green_pixels is not None and self.image_graph.red_pixel is not None:
            dist, pred, first_green_pixel = self.image_graph.dijkstra(self.image_graph.red_pixel)

            if first_green_pixel is None:
                print("No green pixel found.")
                messagebox.showinfo("No Green Pixel", "No green pixel found in the image.")
                return

            # Reconstruct the path from red_pixel to first_green_pixel
            path = []
            current = first_green_pixel
            while current is not None:
                path.append(current)
                current = pred[current]
            path.reverse()

            if not path or path[0] != self.image_graph.red_pixel:
                print("No path found.")
                messagebox.showinfo("No Path", "No path found between the selected pixels.")
                return
            
            self.reset_pixels()
            

            saved_directory = None
            # Loop over all images
            print(f"\nIt is possible to move the equipment: \n", end="")
            for image_index, image in enumerate(self.image_graph.images):
                # Get the corresponding image path
                image_path = self.image_paths[image_index]

                # Create a copy of the image
                image_copy = image.copy()

                # Print the path with arrows indicating the direction
                for i in range(len(path) - 1):
                    # Only draw the path if the z coordinate of the path matches the z coordinate of the image
                    if path[i][2] == image_index:
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
                            if i != 0:
                                image_copy.putpixel((path[i][0], path[i][1]), (255, 100, 100))
                        except Exception as e:
                            print(f"Error putting pixel: {e}")

                if image_index != len(self.image_graph.images) - 1:
                    print("^ ", end="")

                # Extract the directory and filename from the original image path
                directory, filename = os.path.split(image_path)
                # Remove the extension from the filename
                filename_without_ext = os.path.splitext(filename)[0]
                # Create the new filename
                new_filename = f"{filename_without_ext}_path.bmp"
                # Create the full path for the new image
                path_image_name = os.path.join(directory, new_filename)

                saved_directory = directory

                # Save the image with the path in the same directory as the original image
                try:
                    image_copy.save(path_image_name, "BMP")
                    #converts the image to a Pillow Image
                    image_copy = Image.open(path_image_name)
                    #change the image to the one with the path
                    self.image_graph.images[image_index] = image_copy
                    #run display function again to update the image
                    self.display_bitmap()
                    # Show a message box with the path for the image
                    if len(self.image_graph.images) == 1:
                        messagebox.showinfo("Path Saved", f"A bitmap with the path between the pixels has been saved in the following directory: \n{path_image_name}")
 
                except Exception as e:
                    print(f"Error saving image: {e}")
                except Exception as e:
                    print(f"Unexpected error: {e}") 
            if len (self.image_graph.images) > 1:
                messagebox.showinfo("Path Saved", f"bitmaps with the path between the pixels has been saved in the following directory: \n{saved_directory}")

            print()
            # Print the number of pixels in the path
            print("\nNumber of pixels in the path: ", len(path))
        else:
            print("\nPlease select start and end pixels.")




# Create the main Tkinter window
root = tk.Tk()
app = BitmapProcessorApp(root)
root.mainloop()


