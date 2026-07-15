import os
import json
import shutil
from PIL import Image

def main():
    # Determine directory paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    
    json_path = os.path.join(script_dir, "helper.json")
    collection_dir = os.path.join(script_dir, "collection")
    problem_screenshots_base = os.path.join(root_dir, "problem-screenshots")
    editorial_screenshots_base = os.path.join(root_dir, "editorial-screenshots")
    
    # Ensure collection directory exists
    os.makedirs(collection_dir, exist_ok=True)
    
    # Check if helper.json exists
    if not os.path.exists(json_path):
        print(f"Error: helper.json not found at {json_path}")
        return
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading helper.json: {e}")
        return
        
    problems = data.get("problems", [])
    if not problems:
        print("No problems found in helper.json.")
        return
        
    print(f"Processing {len(problems)} problems from helper.json...")
    
    def find_and_copy(base_dir, num, target_name):
        # Determine the subfolder
        if num < 1000:
            subfolder = "1-999"
        elif num < 2000:
            subfolder = "1000-1999"
        else:
            subfolder = "2000-2999"
            
        search_dir = os.path.join(base_dir, subfolder)
        if not os.path.exists(search_dir):
            print(f"  Directory not found: {search_dir}")
            return False
            
        prefix = f"{str(num).zfill(3)}."
        for filename in os.listdir(search_dir):
            if filename.startswith(prefix):
                src_path = os.path.join(search_dir, filename)
                _, ext = os.path.splitext(filename)
                dest_path = os.path.join(collection_dir, f"{num}-{target_name}{ext}")
                try:
                    shutil.copy2(src_path, dest_path)
                    print(f"  Copied: {filename} -> {num}-{target_name}{ext}")
                    return True
                except Exception as e:
                    print(f"  Error copying {filename}: {e}")
                    return False
                    
        print(f"  No file starting with '{prefix}' found in {subfolder}")
        return False

    for num in problems:
        print(f"\nProblem {num}:")
        # Grab and copy problem screenshot
        find_and_copy(problem_screenshots_base, num, "problem")
        # Grab and copy editorial screenshot
        find_and_copy(editorial_screenshots_base, num, "editorial")

    create_pdf = data.get("createPDF", False)
    if create_pdf:
        print("\nCompiling screenshots into PDF...")
        pdf_images = []
        opened_images = []
        
        # For each problem, look for its screenshots in helper/collection/
        for num in problems:
            prob_file = None
            edit_file = None
            
            # Find the copied files (supporting any extension like png, jpg, etc.)
            for filename in os.listdir(collection_dir):
                if filename.startswith(f"{num}-problem."):
                    prob_file = os.path.join(collection_dir, filename)
                elif filename.startswith(f"{num}-editorial."):
                    edit_file = os.path.join(collection_dir, filename)
            
            if prob_file:
                try:
                    img = Image.open(prob_file).convert('RGB')
                    pdf_images.append(img)
                    opened_images.append(img)
                    print(f"  Added problem page: {os.path.basename(prob_file)}")
                except Exception as e:
                    print(f"  Error loading {prob_file} for PDF: {e}")
            else:
                print(f"  Warning: No problem screenshot found in collection for problem {num}")
                
            if edit_file:
                try:
                    img = Image.open(edit_file).convert('RGB')
                    pdf_images.append(img)
                    opened_images.append(img)
                    print(f"  Added editorial page: {os.path.basename(edit_file)}")
                except Exception as e:
                    print(f"  Error loading {edit_file} for PDF: {e}")
            else:
                print(f"  Warning: No editorial screenshot found in collection for problem {num}")
                
        if pdf_images:
            pdf_path = os.path.join(collection_dir, "problems.pdf")
            try:
                pdf_images[0].save(pdf_path, save_all=True, append_images=pdf_images[1:])
                print(f"\nSuccessfully compiled PDF with {len(pdf_images)} pages at: {pdf_path}")
            except Exception as e:
                print(f"\nError saving PDF: {e}")
            finally:
                # Close all image instances to free locks
                for img in opened_images:
                    img.close()
        else:
            print("\nNo screenshots were successfully loaded. PDF not created.")

if __name__ == "__main__":
    main()
