       print("← ", end="")
                            else:

                                print("→ ", end="")
                        try:
                            image.putpixel((path[i][0], path[i][1]), (255, 0, 0))
                        except Exception as e:
                            print(f"Error putting pixel: {e}")

                path_image_name = f"path_{image_index}.bmp"
                # Save the image with the path in the same directory as the original image
                try:
                    image.save(path_image_name, "BMP")
                    # Show a message box with the path for the image
                    messagebox.showinfo("Path Saved", f"A bitmap with the path between the pixels has been saved in the following directory: \n{path_image_name}")
                    print("Image saved successfully.")
                except Exception as e:
                    print(f"Error saving image: {e}")
                except Exception as e:
                    print(f"Unexpected error: {e}") 

                print()
                # Print the number of pixels in the path
                print("\nNumber of pixels in the path: ", len(path))
            else:
                print("\nPlease select start and end pixels.")