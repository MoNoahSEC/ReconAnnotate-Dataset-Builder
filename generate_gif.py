import os
from PIL import Image, ImageDraw, ImageFont


def create_animated_preview():
    width, height = 800, 450
    frames = []
    num_frames = 30

    # Ensure assets directory exists
    os.makedirs("./assets", exist_ok=True)

    for i in range(num_frames):
        # Create a new white canvas
        img = Image.new("RGB", (width, height), "#ffffff")
        draw = ImageDraw.Draw(img)

        # 1. Top Titlebar
        draw.rectangle([0, 0, width, 40], fill="#fafafa")
        draw.line([0, 40, width, 40], fill="#e2e8f0", width=1)
        # Titlebar circles
        draw.ellipse([20, 14, 32, 26], fill="#ff5f56")
        draw.ellipse([40, 14, 52, 26], fill="#ffbd2e")
        draw.ellipse([60, 14, 72, 26], fill="#27c93f")

        # Title text
        title_text = "Noah ReconAnnotate Pro — Premium Workspace Preview"
        draw.text((100, 14), title_text, fill="#1e293b")

        # 2. Left Sidebar (Cream/Peach theme)
        draw.rectangle([10, 50, 200, 440], fill="#fffaf6", outline="#ffe0cc", width=1)
        draw.text((25, 70), "ReconAnnotate Pro", fill="#ff6b00")
        draw.text((25, 88), "DESIGNED BY NOAH", fill="#64748b")

        draw.text((25, 120), "CLASSES (Dataset)", fill="#1e293b")

        # Active Class item (orange pill)
        draw.rectangle([20, 140, 190, 170], fill="#ffe0cc", outline="#ff6b00", width=1)
        draw.text((35, 148), "0: Defect", fill="#ff6b00")

        # Inactive class items
        draw.text((35, 185), "1: Good", fill="#64748b")
        draw.text((35, 215), "2: Object", fill="#64748b")

        # 3. Main Image Canvas (Cool Slate gray grid)
        canvas_coords = [210, 50, 790, 440]
        draw.rectangle(canvas_coords, fill="#f8fafc", outline="#ffe0cc", width=1)

        # Draw grid lines on canvas
        for x in range(210, 790, 50):
            draw.line([x, 50, x, 440], fill="#f1f5f9", width=1)
        for y in range(50, 440, 50):
            draw.line([210, y, 790, y], fill="#f1f5f9", width=1)

        # Bounding box 1 (Static Good item)
        draw.rectangle([250, 100, 450, 220], outline="#2ecc71", width=2)
        draw.rectangle([250, 80, 350, 100], fill="#2ecc71")
        draw.text((255, 85), "1: Good [98%]", fill="#ffffff")

        # Active elements based on frame index
        cursor_x, cursor_y = 650, 350
        box_start_x, box_start_y = 500, 180
        box_end_x, box_end_y = 700, 320

        # Phase 1: Cursor moves towards drawing start (Frames 0 to 9)
        if i < 10:
            ratio = i / 9.0
            cursor_x = int(650 - ratio * (650 - box_start_x))
            cursor_y = int(350 - ratio * (350 - box_start_y))

        # Phase 2: Bounding box is being drawn (Frames 10 to 19)
        elif i < 20:
            ratio = (i - 10) / 9.0
            cursor_x = int(box_start_x + ratio * (box_end_x - box_start_x))
            cursor_y = int(box_start_y + ratio * (box_end_y - box_start_y))
            # Draw dashed/orange preview box
            draw.rectangle(
                [box_start_x, box_start_y, cursor_x, cursor_y], outline="#ff6b00", width=1
            )

        # Phase 3: Box completed, laser sweeps (Frames 20 to 29)
        else:
            # Draw solid completed orange box
            draw.rectangle([box_start_x, box_start_y, box_end_x, box_end_y], outline="#ff6b00", width=2)
            draw.rectangle([box_start_x, box_start_y - 20, box_start_x + 120, box_start_y], fill="#ff6b00")
            draw.text((box_start_x + 5, box_start_y - 15), "0: Defect [99%]", fill="#ffffff")

            # Draw sweeping orange laser line
            laser_ratio = (i - 20) / 9.0
            laser_y = int(50 + laser_ratio * 390)
            draw.line([210, laser_y, 790, laser_y], fill="#ff6b00", width=2)

        # Draw Crosshair cursor (+)
        draw.line([cursor_x - 10, cursor_y, cursor_x + 10, cursor_y], fill="#ff6b00", width=2)
        draw.line([cursor_x, cursor_y - 10, cursor_x, cursor_y + 10], fill="#ff6b00", width=2)
        draw.ellipse([cursor_x - 3, cursor_y - 3, cursor_x + 3, cursor_y + 3], outline="#ff6b00", width=1)

        # Stats Overlay (Top-Right of canvas)
        draw.rectangle([660, 60, 780, 115], fill="#ffffff", outline="#ffe0cc", width=1)
        draw.text((670, 68), "● NOAH ENGINE", fill="#ff6b00")
        draw.text((670, 83), "FPS: 144.0 (GPU)", fill="#64748b")
        draw.text((670, 98), "ZOOM: FIT", fill="#64748b")

        frames.append(img)

    # Save as animated GIF
    frames[0].save(
        "./assets/preview.gif",
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
    )
    print("✅ Animated GIF successfully created at assets/preview.gif")


if __name__ == "__main__":
    create_animated_preview()
