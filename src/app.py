import requests
from PIL import Image, ImageTk
import io
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class PokedexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokédex")
        self.current_image = None
        self.current_gif = None
        self.current_pokemon_name = None
        self.showing_gif = False
        
        # Create and configure main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=0, column=0, pady=5)
        
        # Create entry and buttons
        ttk.Label(input_frame, text="Enter Pokémon number (1-1025):").grid(row=0, column=0, padx=5)
        self.number_entry = ttk.Entry(input_frame, width=10)
        self.number_entry.grid(row=0, column=1, padx=5)
        ttk.Button(input_frame, text="Search", command=self.search_pokemon).grid(row=0, column=2, padx=5)
        
        # Create a frame for the name entry and copy button
        name_frame = ttk.Frame(main_frame)
        name_frame.grid(row=1, column=0, pady=5)
        
        # Add Pokemon name entry (readonly)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(name_frame, 
                                  textvariable=self.name_var,
                                  justify='center',
                                  font=('Arial', 14, 'bold'),
                                  width=20)
        self.name_entry.pack(side='left', padx=(0, 5))
        self.name_entry.configure(state='readonly')
        
        # Add copy button
        copy_button = ttk.Button(name_frame, text="Copy Name", command=self.copy_pokemon_name)
        copy_button.pack(side='left')
        
        # Navigation buttons frame
        nav_frame = ttk.Frame(main_frame)
        nav_frame.grid(row=2, column=0, pady=5)
        
        ttk.Button(nav_frame, text="◀ Previous", command=self.previous_pokemon).grid(row=0, column=0, padx=5)
        ttk.Button(nav_frame, text="Next ▶", command=self.next_pokemon).grid(row=0, column=1, padx=5)
        
        # Add toggle button for GIF/static image
        self.toggle_text = tk.StringVar(value="Show GIF")
        toggle_button = ttk.Button(nav_frame, textvariable=self.toggle_text, command=self.toggle_image)
        toggle_button.grid(row=0, column=2, padx=5)
        
        # Create a frame to contain the image label with fixed size
        self.image_size = (800, 800)  # Increased from 600x600 to 800x800 to better match static image size
        image_frame = ttk.Frame(main_frame, width=self.image_size[0], height=self.image_size[1])
        image_frame.grid(row=3, column=0, pady=10)
        image_frame.grid_propagate(False)  # Prevent the frame from resizing
        
        # Create image label inside the fixed-size frame
        self.image_label = ttk.Label(image_frame)
        self.image_label.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Variables for GIF animation
        self.gif_frames = []
        self.current_frame = 0
        self.is_animating = False
        
        # Create button frame for download
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, pady=(0, 5))
        
        # Add download button
        download_button = ttk.Button(button_frame, text="Download Image", command=self.save_image)
        download_button.pack()
        
        # Bind events
        self.number_entry.bind('<Return>', lambda e: self.search_pokemon())

    def get_pokemon_data(self, number):
        try:
            # Get Pokemon details from PokeAPI
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{number}", timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                'name': data['name'].title(),
                'gif_url': data['sprites']['other']['showdown']['front_default']
            }
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch Pokémon data: {e}")
            return None

    def get_pokemon_image(self, number):
        # Format number to 3 digits with leading zeros
        formatted_num = str(number).zfill(3)
        url = f"https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/{formatted_num}.png"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))
            return image
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to download image: {e}")
            return None
        except Image.UnidentifiedImageError:
            messagebox.showerror("Error", "Downloaded data is not a valid image")
            return None

    def animate_gif(self):
        """Handles GIF animation by cycling through frames"""
        if self.showing_gif and self.gif_frames and self.is_animating:
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.image_label.configure(image=self.gif_frames[self.current_frame])
            self.root.after(100, self.animate_gif)  # Update every 100ms

    def get_pokemon_gif(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            gif = Image.open(io.BytesIO(response.content))
            
            # Clear previous frames
            self.gif_frames = []
            
            try:
                # Extract all frames from the GIF
                frame_count = 0
                while True:
                    # Resize frame to maintain consistent size
                    gif.thumbnail(self.image_size, Image.Resampling.LANCZOS)
                    # Convert to PhotoImage and store
                    self.gif_frames.append(ImageTk.PhotoImage(gif.copy()))
                    frame_count += 1
                    gif.seek(frame_count)
            except EOFError:
                pass  # We've reached the end of the frames
                
            return gif if self.gif_frames else None
            
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to download GIF: {e}")
            return None
        except Image.UnidentifiedImageError:
            messagebox.showerror("Error", "Downloaded data is not a valid image")
            return None

    def toggle_image(self):
        if not self.current_image and not self.current_gif:
            return
            
        self.showing_gif = not self.showing_gif
        self.toggle_text.set("Show Static" if self.showing_gif else "Show GIF")
        
        if self.showing_gif and self.gif_frames:
            self.is_animating = True
            self.current_frame = 0
            self.image_label.configure(image=self.gif_frames[0])
            self.animate_gif()
        elif not self.showing_gif and self.current_image:
            self.is_animating = False
            # Resize static image
            display_image = self.current_image.copy()
            display_image.thumbnail(self.image_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(display_image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo  # Keep a reference

    def search_pokemon(self):
        try:
            number = int(self.number_entry.get())
            if not 1 <= number <= 1025:
                messagebox.showwarning("Invalid Input", "Number must be between 1 and 1025")
                return
            
            self.display_pokemon(number)
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid number")

    def copy_pokemon_name(self):
        if self.current_pokemon_name:
            formatted_name = f"justin/{self.current_pokemon_name.lower()}"
            self.root.clipboard_clear()
            self.root.clipboard_append(formatted_name)
            self.root.update()  # Required to make clipboard changes stick
            messagebox.showinfo("Copied", f"Copied: {formatted_name}")

    def display_pokemon(self, number):
        # Get Pokemon data first
        pokemon_data = self.get_pokemon_data(number)
        if pokemon_data:
            self.current_pokemon_name = pokemon_data['name']
            # Update the name entry
            self.name_entry.configure(state='normal')
            self.name_var.set(pokemon_data['name'])
            self.name_entry.configure(state='readonly')
            
            # Get both static image and GIF
            self.current_image = self.get_pokemon_image(number)
            if pokemon_data['gif_url']:
                self.current_gif = self.get_pokemon_gif(pokemon_data['gif_url'])
            else:
                self.current_gif = None
                self.gif_frames = []
            
            # Display the appropriate image based on current toggle state
            if self.showing_gif and self.gif_frames:
                self.is_animating = True
                self.current_frame = 0
                self.image_label.configure(image=self.gif_frames[0])
                self.animate_gif()
            else:
                self.is_animating = False
                self.showing_gif = False
                self.toggle_text.set("Show GIF")
                if self.current_image:
                    # Resize image to maintain consistent size
                    display_image = self.current_image.copy()
                    display_image.thumbnail(self.image_size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(display_image)
                    self.image_label.configure(image=photo)
                    self.image_label.image = photo
            
            # Update the entry field
            self.number_entry.delete(0, tk.END)
            self.number_entry.insert(0, str(number))

    def next_pokemon(self):
        try:
            current = int(self.number_entry.get())
            next_num = min(current + 1, 1025)
            self.display_pokemon(next_num)
        except ValueError:
            self.display_pokemon(1)

    def previous_pokemon(self):
        try:
            current = int(self.number_entry.get())
            prev_num = max(current - 1, 1)
            self.display_pokemon(prev_num)
        except ValueError:
            self.display_pokemon(1)

    def save_image(self):
        """Separate method for saving the image (formerly copy_image)"""
        if self.current_image and self.current_pokemon_name:
            try:
                # Get current pokemon number and name for the filename
                pokemon_number = self.number_entry.get().zfill(3)
                default_filename = f"{pokemon_number}-{self.current_pokemon_name}.png"
                
                # Ask user where to save the file
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                    title="Save Pokémon Image",
                    initialfile=default_filename
                )
                
                if file_path:  # If user didn't cancel the dialog
                    # Save the image
                    self.current_image.save(file_path, 'PNG')
                    messagebox.showinfo("Success", f"Image saved to {file_path}!")
            except (OSError, IOError) as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")

def main():
    root = tk.Tk()
    PokedexApp(root)  # No need to store the instance
    root.mainloop()

if __name__ == "__main__":
    main()
