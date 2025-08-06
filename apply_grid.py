
import os
import sys
from PIL import Image, ImageDraw

# Grid configurations based on breakpoints
GRID_CONFIG = {
    'SM': {'columns': 4, 'gutter': 16, 'margin': 16},
    'MD': {'columns': 8, 'gutter': 16, 'margin': 24},
    'LG': {'columns': 12, 'gutter': 24, 'margin': 24},
    'XL': {'columns': 12, 'gutter': 24, 'margin': 24},
}

# Grid color (light pink with transparency)
GRID_COLOR = (255, 182, 193, 100) # R, G, B, Alpha

def draw_grid(image_path, output_path):
    """
    Draws a grid on an image based on its breakpoint (inferred from path)
    and saves it to the output path.
    """
    try:
        # Infer breakpoint from the directory name
        breakpoint = None
        # Normalize path for consistency
        normalized_path = image_path.replace('\\', '/')
        parts = normalized_path.split('/')
        
        # The directory name is the second to last part
        if len(parts) >= 2:
            dir_name = parts[-2]
            if ' - SM' in dir_name:
                breakpoint = 'SM'
            elif ' - MD' in dir_name:
                breakpoint = 'MD'
            elif ' - LG' in dir_name:
                breakpoint = 'LG'
            elif ' - XL' in dir_name:
                breakpoint = 'XL'

        if not breakpoint:
            # print(f"Warning: Could not determine breakpoint for {image_path}. Skipping.")
            return

        config = GRID_CONFIG[breakpoint]
        margin = config['margin']
        columns = config['columns']
        gutter = config['gutter']

        with Image.open(image_path).convert("RGBA") as base_image:
            img_width, img_height = base_image.size

            # Create a transparent layer for the grid
            overlay = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)

            # --- INTEGER-BASED GRID CALCULATION ---
            # All calculations use integers to avoid floating point errors.

            if columns <= 0:
                return # Do not draw if there are no columns

            total_gutter_width = (columns - 1) * gutter
            total_margin_width = 2 * margin
            content_width = img_width - total_margin_width
            column_total_width = content_width - total_gutter_width

            # Calculate base width and distribute remaining pixels
            base_column_width = column_total_width // columns
            remainder = column_total_width % columns

            current_x = margin
            for i in range(columns):
                # Add 1px to the first 'remainder' columns
                col_width = base_column_width + (1 if i < remainder else 0)

                draw.rectangle(
                    [(current_x, 0), (current_x + col_width, img_height)],
                    fill=GRID_COLOR
                )
                # Move to the start of the next column
                current_x += col_width + gutter

            # Composite the overlay onto the base image
            combined = Image.alpha_composite(base_image, overlay)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save the result as PNG
            combined.convert("RGB").save(output_path, "PNG")

    except FileNotFoundError:
        # print(f"Error: Source file not found at {image_path}")
        pass
    except Exception as e:
        # print(f"Error processing {image_path}: {e}")
        pass


def process_screenshots(source_dir, output_dir_base):
    """
    Finds all screenshots in the source directory, applies grids,
    and saves them to the output directory.
    """
    print(f"Processing screenshots from: {source_dir}")
    for root, dirs, files in os.walk(source_dir):
        # Skip specific subdirectories
        if 'comparison_results' in root or 'screenshots_with_grid' in root:
            continue
            
        for file in files:
            if file.lower().endswith('.png'):
                source_path = os.path.join(root, file)
                
                # Create corresponding output path
                relative_path = os.path.relpath(source_path, source_dir)
                output_path = os.path.join(output_dir_base, relative_path)
                
                draw_grid(source_path, output_path)
    print(f"Output generated in: {output_dir_base}")


if __name__ == "__main__":
    try:
        project_root = os.path.dirname(os.path.abspath(__file__))

        # Default source directory
        source_dir_name = 'screenshots'

        # Check for command-line argument
        if len(sys.argv) > 1:
            source_dir_name = sys.argv[1]

        # These paths are relative to the project root
        SOURCE_SCREENSHOTS_DIR = os.path.join(project_root, source_dir_name)
        
        # The output directory is named based on the source, with a suffix
        output_dir_name = os.path.basename(os.path.normpath(source_dir_name)) + '_with_grid'
        OUTPUT_GRID_DIR = os.path.join(os.path.dirname(SOURCE_SCREENSHOTS_DIR), output_dir_name)


        if not os.path.isdir(SOURCE_SCREENSHOTS_DIR):
            print(f"Error: Source directory not found at '{SOURCE_SCREENSHOTS_DIR}'")
            print("Please provide a valid path to a screenshots directory as an argument.")
            print("Example: python apply_grid.py playwright_project/screenshots")
            sys.exit(1)

        print(f"Starting grid application...")
        
        process_screenshots(SOURCE_SCREENSHOTS_DIR, OUTPUT_GRID_DIR)
        
        print("Grid application complete.")
    except NameError:
        # Handle case where __file__ is not defined (e.g. in some interpreters)
        print("Could not determine project root. Please run from a standard Python environment.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
