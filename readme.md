# Image Transformation Application
This Python application provides a user interface for loading, transforming, and saving images. It uses the tkinter library for the graphical user interface, Pillow (PIL) for image processing, and other libraries for additional functionalities.

## Features
Load Images:

The application allows users to load images from either regular file formats or the ND2 format.
For ND2 format, the application processes and normalizes the images for visualization.

## Image Transformation:

Users can rotate and translate the loaded images interactively using sliders.
The transformation is applied to the primary image, and the secondary image is overlaid on top.
Save Options:

### Save Rotated Image: 

Save the translated and rotated top mask image.

### Save Composite Image: 

Save both images at full size with the top mask being translated/rotated and set to 50% visibility.

# Usage:

## Load Images:

Click the "Load Images" button to choose two images for processing.
Supports common image formats and ND2 format.

### Image Transformation:

Adjust the rotation and translation sliders to transform the images.
Real-time display updates as transformations are applied.
Save Images:

Click "Save Rotated Image" to save the translated/rotated top mask image.
Click "Save Composite Image" to save both images at full size with overlay.

# Requirements
```bash
tkinter
Pillow (PIL)
nd2reader
OpenCV (cv2)
NumPy
Matplotlib
```
# Installation
```bash
pip install -r requirements.txt
```

# Run the Application
```bash
cd /filePath/ofInstalled/script/
python ND2_OverlayManual.py
```

License
This application is open-source and released under the MIT License. Feel free to modify and distribute.
