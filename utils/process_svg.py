from bs4 import BeautifulSoup

def process_svg(svg_path: str) -> BeautifulSoup:
    """Process an SVG file by removing stroke numbers and adding gray background strokes."""
    with open(svg_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "xml")

    # Remove all <text> elements (stroke numbers)
    for text in soup.find_all("text"):
        text.decompose()

    # Find the group containing the strokes
    stroke_group = soup.find('g', transform=lambda x: x and 'scale(1, -1)' in x)

    if stroke_group:
        # Create a new group for the gray background strokes
        gray_group = soup.new_tag('g')
        gray_group['transform'] = stroke_group['transform']
        
        # Copy each path and make it gray
        original_paths = stroke_group.find_all("path")
        num_strokes = len(original_paths)
        
        # Create gray background strokes
        for path in original_paths:
            gray_path = soup.new_tag('path')
            for attr, value in path.attrs.items():
                gray_path[attr] = value
            gray_path['fill'] = '#CCCCCC'
            gray_path['style'] = 'fill:#CCCCCC'
            gray_group.append(gray_path)
        
        # Insert the gray background before the colored strokes
        stroke_group.insert_before(gray_group)
        
        # Helper function to extract coordinates from path data
        def get_path_coords(d):
            parts = d.strip().split()
            if parts[0] == 'M':
                return float(parts[1]), float(parts[2])
            return None
            
        # Group connected paths and make them black
        current_stroke = 0
        last_end = None
        
        for i, path in enumerate(original_paths):
            d = path.get('d', '')
            coords = get_path_coords(d)
            
            # Start a new stroke if:
            # 1. This is the first path
            # 2. This path starts with 'M' AND is far from the last endpoint
            if i == 0 or (coords and (not last_end or 
                abs(coords[0] - last_end[0]) > 50 or 
                abs(coords[1] - last_end[1]) > 50)):
                current_stroke += 1
                print(f"New stroke {current_stroke} at path {i} at ({coords[0]}, {coords[1]})")
            
            # Update last endpoint if this path has coordinates
            if coords:
                last_end = coords
                
            path['fill'] = '#000000'
            path['style'] = 'fill:#000000'
            path['class'] = f'stroke-{current_stroke}'  # Mark as part of a stroke
    else:
        print(f"Warning: No stroke group found in {svg_path}")

    return soup
