import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os

ON = 1
OFF = 0

def image_to_grid(image_path, grid_size):
    """Converts an image to a binary grid based on its brightness."""
    img = Image.open(image_path).convert("L")  # Convert to grayscale
    img = img.resize((grid_size, grid_size))   # Resize to fit the grid
    img_np = np.array(img)
    # Convert grayscale values to binary based on brightness threshold
    grid = np.where(img_np < 128, ON, OFF)
    return grid

def random_grid(size):
    """Generates a random initial grid."""
    return np.random.choice([ON, OFF], size * size, p=[0.5, 0.5]).reshape(size, size)

def update(frameNum, img_plot, grid, target_grid, size):
    """Updates the grid for each frame of the animation."""
    # Check if current grid matches the target grid
    if np.array_equal(grid, target_grid):
        print("Goal reached! Stopping animation.")
        ani.event_source.stop()  # Stop the animation when the goal is reached
        return img_plot,
    
    new_grid = grid.copy()
    for i in range(size):
        for j in range(size):
            # Compute the sum of the eight neighbors
            total = int((
                grid[i, (j - 1) % size] + grid[i, (j + 1) % size] +
                grid[(i - 1) % size, j] + grid[(i + 1) % size, j] +
                grid[(i - 1) % size, (j - 1) % size] + grid[(i - 1) % size, (j + 1) % size] +
                grid[(i + 1) % size, (j - 1) % size] + grid[(i + 1) % size, (j + 1) % size]
            ))
            # Apply Conway's rules
            if grid[i, j] == ON:
                if (total < 2) or (total > 3):
                    new_grid[i, j] = OFF
            else:
                if total == 3:
                    new_grid[i, j] = ON
    # Aggressively move toward the target pattern by increasing probability
    match_probability = min(1, 0.1 + frameNum * 0.02)  # Gradually increase the match probability
    for i in range(size):
        for j in range(size):
            if np.random.rand() < match_probability:
                new_grid[i, j] = target_grid[i, j]
    img_plot.set_data(new_grid)
    grid[:] = new_grid[:]
    return img_plot,

def process_and_animate(image_path):
    """Processes the image and starts the animation."""
    GRID_SIZE = 50
    # Initialize a random grid and load the target image grid
    target_grid = image_to_grid(image_path, GRID_SIZE)
    grid = random_grid(GRID_SIZE)

    # Animation duration settings
    frames = 100               # Number of frames
    interval = 200             # Interval between frames in milliseconds

    # Set up the figure and animation
    fig, ax = plt.subplots()
    img_plot = ax.imshow(grid, interpolation='nearest', cmap='binary')
    ax.axis('off')  # Hide the axes for a cleaner look

    # Define the animation with a stop condition
    global ani
    ani = animation.FuncAnimation(
        fig, update, fargs=(img_plot, grid, target_grid, GRID_SIZE),
        frames=frames, interval=interval, save_count=frames
    )

    plt.show()

# Create the main application window
root = tk.Tk()
root.title("Conway's Game of Life Image Selector")
root.geometry("600x600")
root.selected_image_path = None

# Create a label
label = tk.Label(
    root, text="Select an image to start the animation", font=("Helvetica", 14)
)
label.pack(pady=10)

# Define a list of preselected images (ensure these images are in the 'images' folder)
preselected_images = {
    "Sample Image 1": "images/sample1.jpg",
    "Sample Image 2": "images/sample2.jpg",
    "Sample Image 3": "images/sample3.jpg",
}

# Load thumbnails of preselected images
thumbnail_size = (100, 100)
thumbnails = {}
for name, path in preselected_images.items():
    if os.path.exists(path):
        img = Image.open(path)
        img.thumbnail(thumbnail_size)
        thumbnails[name] = ImageTk.PhotoImage(img)
    else:
        print(f"Image {path} not found.")

def display_selected_image(image_path):
    """Displays the selected image in the preview area."""
    # Load and resize the image
    img = Image.open(image_path)
    img.thumbnail((300, 300))
    img_tk = ImageTk.PhotoImage(img)
    # Update the preview label
    preview_label.config(image=img_tk)
    preview_label.image = img_tk  # Keep a reference to prevent garbage collection

def choose_preselected_image(image_name):
    """Handles the selection of a preselected image."""
    # Get the selected image path
    image_path = preselected_images.get(image_name)
    if not image_path or not os.path.exists(image_path):
        print("Selected image not found.")
        return
    # Display the image preview
    display_selected_image(image_path)
    # Enable the start animation button
    start_button.config(state="normal")
    # Store the image path for use when starting the animation
    root.selected_image_path = image_path

def upload_image():
    """Handles the image upload and displays preview."""
    # Open file dialog to select an image
    image_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")]
    )
    if not image_path:
        print("No image selected.")
        return
    # Display the image preview
    display_selected_image(image_path)
    # Enable the start animation button
    start_button.config(state="normal")
    # Store the image path for use when starting the animation
    root.selected_image_path = image_path

def start_animation():
    """Starts the animation after processing the image."""
    image_path = getattr(root, 'selected_image_path', None)
    if not image_path or not os.path.exists(image_path):
        print("No image selected to animate.")
        return
    # Close the Tkinter window
    root.destroy()
    # Start the animation
    process_and_animate(image_path)

# Create a frame for preselected images
preselected_frame = tk.Frame(root)
preselected_frame.pack(pady=10)

# Add thumbnails of preselected images
for idx, (name, img_tk) in enumerate(thumbnails.items()):
    btn = tk.Button(
        preselected_frame, image=img_tk, command=lambda n=name: choose_preselected_image(n)
    )
    btn.grid(row=0, column=idx, padx=10)
    lbl = tk.Label(preselected_frame, text=name, font=("Helvetica", 10))
    lbl.grid(row=1, column=idx, padx=10)

# Add a separator
separator = ttk.Separator(root, orient='horizontal')
separator.pack(fill='x', pady=10)

# Add the Upload Image button
upload_button = tk.Button(
    root, text="Upload Your Own Image", command=upload_image, font=("Helvetica", 12)
)
upload_button.pack(pady=5)

# Image preview area
preview_label = tk.Label(root)
preview_label.pack(pady=10)

# Start Animation button
start_button = tk.Button(
    root, text="Start Animation", command=start_animation, font=("Helvetica", 12), state="disabled"
)
start_button.pack(pady=5)

# Run the Tkinter event loop
root.mainloop()
