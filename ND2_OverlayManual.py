import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from nd2reader import ND2Reader
import cv2
import numpy as np
import matplotlib as mpl


class ImageTransformApp:
    """Class representing the main image transformation application."""
    def __init__(self, root):
        """Initialize the ImageTransformApp.

        Args:
            root (tk.Tk): The main tkinter window.
        """
        self.root = root
        self.root.geometry("500x600")
        self.root.title("Image Transformer")

        self.image_label = tk.Label(root)
        self.image_label.grid(row=0, column=0, columnspan=3, pady=10)

        self.load_button = tk.Button(root, text="Load Images", command=self.loadImage)
        self.load_button.grid(row=1, column=0, pady=10)

        self.save_button = tk.Button(root, text="Save Rotated Image", command=self.saveImageMask)
        self.save_button.grid(row=1, column=1, pady=10)

        self.save_button = tk.Button(root, text="Save Composite Image", command=self.saveCompositeImages)
        self.save_button.grid(row=1, column=2, pady=10)

        self.rotation_slider = tk.Scale(root, from_=-180, to=180, orient="horizontal", label="Rotation Angle",
                                        command=self.applyImageTransform)
        self.rotation_slider.set(0)
        self.rotation_slider.grid(row=2, column=0, pady=10)

        self.translation_slider_x = tk.Scale(root, from_=-100, to=100, orient="horizontal", label="Translation X",
                                             command=self.applyImageTransform)
        self.translation_slider_x.grid(row=2, column=1, pady=10)

        self.translation_slider_y = tk.Scale(root, from_=-100, to=100, orient="horizontal", label="Translation Y",
                                             command=self.applyImageTransform)
        self.translation_slider_y.grid(row=2, column=2, pady=10)

        # Initialize transformed_image as None
        self.image = None
        self.full_image = None
        self.second_image = None
        self.full_second_image = None
        self.composite_image = None
        self.image2save = None
        self.scaleConstant = 0.05

    def loadImage(self):
        """Load images from file or ND2 format.

        - Handles loading images from different formats (file or ND2).
        - Normalizes and processes ND2 images for display.
        - Configures UI elements and updates the displayed image.
        """
        file_path_1 = filedialog.askopenfilename()
        file_path_2 = filedialog.askopenfilename()
        # handling of ND2 format, literally a garbage image format that needs to be replaced with something more usable
        if file_path_1[-3:] == 'nd2':
            ND2_image1 = ND2Reader(file_path_1)[0][:, :][:]
            ND2_image2 = ND2Reader(file_path_2)[0][:, :][:]

            normalND2_image1 = cv2.normalize(ND2_image1, None, 0, 255, cv2.NORM_MINMAX)
            normalND2_image2 = cv2.normalize(ND2_image2, None, 0, 255, cv2.NORM_MINMAX)

            cm_hot = mpl.colormaps.get('hot')

            normalND2_image1 = cm_hot(normalND2_image1)
            normalND2_image2 = cm_hot(normalND2_image2)

            normalND2_image1 = np.uint8(normalND2_image1 * 255)
            normalND2_image2 = np.uint8(normalND2_image2 * 255)

            normalND2_image1 = Image.fromarray(normalND2_image1)
            normalND2_image2 = Image.fromarray(normalND2_image2)

            width, height = normalND2_image1.size

            normalND2_image2 = normalND2_image2.resize((width, height))

            # saves a copy of the full size images, ND2 files are so large that they are annoying to visualize
            self.full_image = normalND2_image1
            self.full_second_image = normalND2_image2

            # resize to self.scaleConstant (0.05) in both directions to preserve aspect ratio, use these to visualize
            self.image = normalND2_image1.resize(
                size=(
                    int(
                        width * self.scaleConstant
                    ), 
                    int(
                        height * self.scaleConstant
                    )
                )
            )
            
            self.second_image = normalND2_image2.resize(
                size=(
                    int(
                        width * self.scaleConstant
                    ), 
                    int(
                        height * self.scaleConstant
                    )
                )
            )
        # other image file handling, isn't this so much better
        else:
            self.image = Image.open(file_path_1)
            self.second_image = Image.open(file_path_2)

        # sets some variables, converts the image to be RGBA so we can mess with the opacity
        self.image_label.config(width=self.image.size[0] + 150, height=self.image.size[1] + 150)
        self.second_image = self.second_image.convert("RGBA")
        self.image = self.image.convert("RGBA")
        self.second_image.putalpha(128)
        self.displayImage()
        self.configureTranslationSliders()
        self.root.geometry("500x600")

    def saveImageMask(self):
        """Save the full size translated/rotated image.

        - Allows the user to save the translated/rotated top mask image.
        - Displays a success message upon successful save.
        """
        if self.image2save:
            # recreate the rotated image with the full size images
            rotated_image = self.full_image.rotate(self.rotation_slider.get(), expand=True)
            saveImage = rotated_image.transform(rotated_image.size,
                                                Image.AFFINE,
                                                (
                                                    1, 0, self.translation_slider_x.get()/self.scaleConstant,
                                                    0, 1, self.translation_slider_y.get()/self.scaleConstant
                                                )
                                                )
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"),
                                                                                         ("All files", "*.*")])
            if save_path:
                saveImage.save(save_path)
                messagebox.showinfo("Save", "Image saved successfully.")
        else:
            messagebox.showinfo("Save", "No image to save.")

    def saveCompositeImages(self):
        """Saves both of the images at full size with the top mask being translated/rotated and set to 50% visibility

        - Saves the composite image after applying rotation and translation.
        - Handles proper overlaying of two images.
        """
        if self.composite_image:
            # Rotate the full image based on the rotation slider value
            rotated_image = self.full_image.rotate(self.rotation_slider.get(), expand=True)

            # Apply translation to the rotated image using the transform method
            saveImage = rotated_image.transform(rotated_image.size,
                                                Image.AFFINE,
                                                (
                                                    1, 0, self.translation_slider_x.get() / self.scaleConstant,
                                                    0, 1, self.translation_slider_y.get() / self.scaleConstant
                                                )
                                                )

            # Prompt user to choose a file path for saving the image
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"),
                                                                                         ("All files", "*.*")])

            # Get sizes of the secondary image and the rotated image
            second_image_size = self.full_second_image.size
            rotated_image_size = rotated_image.size

            # Calculate the differences in width and height between the two images
            width_dif = rotated_image_size[0] - second_image_size[0]
            height_dif = rotated_image_size[1] - second_image_size[1]

            # Calculate the new width and height for the secondary image
            new_width = second_image_size[0] + width_dif
            new_height = second_image_size[1] + height_dif

            # Create a new blank image with the calculated width and height
            resized_second_image = Image.new(
                self.full_second_image.mode,
                (new_width, new_height),
                (255, 255, 255, 0)
            )

            # Paste the secondary image onto the blank image at the calculated position
            resized_second_image.paste(
                self.full_second_image,
                (int(width_dif / 2),
                 int(height_dif / 2)
                 )
            )

            # Convert images to RGBA format
            saveImage.convert("RGBA")
            resized_second_image.convert("RGBA")

            # Set alpha channel for transparency
            resized_second_image.putalpha(128)

            # Create a composite image by overlaying the rotated and translated image with the resized secondary image
            composite_image = Image.alpha_composite(saveImage, resized_second_image)

            if save_path:
                # Save the composite image to the specified path
                composite_image.save(save_path)
                messagebox.showinfo("Save", "Images saved successfully.")
        else:
            # Display a message if there is no composite image to save
            messagebox.showinfo("Save", "No overlayed image to save.")

    def displayImage(self):
        """Display the composite image.

        - Updates the displayed image label with the current composite image.
        """
        self.composite_image = Image.alpha_composite(self.image, self.second_image)

        img = ImageTk.PhotoImage(self.composite_image)
        self.image_label.config(image=img)
        self.image_label.image = img

    def configureTranslationSliders(self):
        """Configure translation sliders based on image size.

        - Adjusts translation sliders based on the size of the loaded image.
        - Ensures sliders cover the entire image for translation.
        """
        # gets the small image size
        imageSize = self.image.size

        # adjust the image sliders to make it so we can edit them
        windowSize = str(imageSize[0] + 200) + 'x' + str(imageSize[1] + 200)
        self.translation_slider_x.config(from_=-imageSize[0], to=imageSize[0])
        self.translation_slider_y.config(from_=-imageSize[1], to=imageSize[1])
        self.root.geometry(windowSize)

    def applyImageTransform(self, _):
        """Apply rotation and translation to the image.

        - Applies rotation and translation to the loaded image.
        - Handles exceptions related to image processing.
        - Updates the displayed image after transformation.
        """
        # Retrieve rotation and translation values from sliders
        degrees = self.rotation_slider.get()
        translation_x = self.translation_slider_x.get()
        translation_y = self.translation_slider_y.get()

        # Rotate the primary image using the specified angle (degrees)
        rotated_image = self.image.rotate(degrees, expand=True)

        # Perform translation on the rotated image using the transform method
        translated_image = rotated_image.transform(rotated_image.size, Image.AFFINE,
                                                   (1, 0, translation_x, 0, 1, translation_y))

        # Get sizes of the secondary image and the rotated image
        second_image_size = self.second_image.size
        rotated_image_size = rotated_image.size

        # Calculate the differences in width and height between the two images
        width_dif = rotated_image_size[0] - second_image_size[0]
        height_dif = rotated_image_size[1] - second_image_size[1]

        # Calculate the new width and height for the secondary image
        new_width = second_image_size[0] + width_dif
        new_height = second_image_size[1] + height_dif

        # Create a new blank image with the calculated width and height
        resized_second_image = Image.new(
            self.second_image.mode,
            (new_width, new_height),
            (255, 255, 255, 0)
        )

        # Paste the secondary image onto the blank image at the calculated position
        resized_second_image.paste(
            self.second_image,
            (int(width_dif / 2),
             int(height_dif / 2)
             )
        )

        # Store the translated image for potential saving
        self.image2save = translated_image

        # Create a composite image by overlaying the translated image and the resized secondary image
        self.composite_image = Image.alpha_composite(translated_image, resized_second_image)

        # Convert the composite image to a PhotoImage for display in the tkinter label
        img = ImageTk.PhotoImage(self.composite_image)

        # Update the label with the new image
        self.image_label.config(image=img)
        self.image_label.image = img


if __name__ == "__main__":
    """Run the main application."""
    root = tk.Tk()
    app = ImageTransformApp(root)
    root.mainloop()
