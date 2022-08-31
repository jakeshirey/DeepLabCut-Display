# DeepLabCut-Display
A GUI for displaying landmark data from DeepLabCut Models for animal locomotion.

This tool is meant to compliment the output of a DeepLabCut inference and allow a video with landmark annotations to be displayed with a plot of the coordinates of the landmark points. 

DeepLabCut is a package for markerless pose estimation of animals using deep learning models. The Github repository for this package can be found here: https://github.com/DeepLabCut/DeepLabCut

This complimentary tool was originally developed for the University of Florida Department of Animal Sciences to display locomotion data from livestock ranging from beef heifers to sport horses.

![display example](https://user-images.githubusercontent.com/94328784/184924777-e04cf534-029f-4e1f-8d42-3d661727edef.JPG)

# Download and Installation
Begin by downloading the codebase from this GitHub page either from the "download zip" option off the green "Code" button or by running this command:

    git clone https://github.com/jakeshirey/DeepLabCut-Display.git

Switch to the OpenCV-based branch by using:

    git checkout opencv

After cloning the repository or downloading and extracting the zip folder, the required python libraries need to be downloaded. ***It is recommended to use a python virtual environment to manage the libraries.*** A reference for creating virtual environments can be found here: (https://docs.python.org/3/tutorial/venv.html)

- ***From the root directory of the repository*** create the environment:

    ```python -m venv virt```
    
- Activate the environment:
  - For Windows command line interface:
   
    ```virt\Scripts\activate.bat```
    
  - For Unix/Mac command line interface:
   
    ```source virt/bin/activate```
    
- Install the external libraries
    
        pip install -r requirements.txt
    
Building the application is the next step. The application can simply be compiled everytime using the command:

        python mainGUI.py
        
or the application can be compiled once into an executable file (.exe) using the pyinstaller library. If the external libraries have been installed from requirements.txt then pyinstaller is already ready to go. Simply run the command:

        pyinstaller --onefile mainGUI.py

and wait for the process to finish executing. This should create a 'dist' folder in the same directory that holds the executable file with the same name. This executable is now available to be used!
