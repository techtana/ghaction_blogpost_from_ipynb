import os
import re
import yaml
import nbformat
from nbconvert import MarkdownExporter

def main():
    # Get the repository path
    repo_path = os.environ.get("GITHUB_WORKSPACE")
    if not repo_path:
        print("Error: GITHUB_WORKSPACE environment variable not set.")
        return

    # Define paths
    notebook_dir = os.path.join(repo_path, "_notebook")
    posts_dir = os.path.join(repo_path, "_posts")
    notebook_archive_dir = os.path.join(repo_path, "_notebook_archived")

    # Check if notebook directory exists
    if not os.path.isdir(notebook_dir):
        print("'_jupyter_notebook' directory not found. Exiting.")
        return
    
    # Ensure the directories exist
    os.makedirs(posts_dir, exist_ok=True)
    os.makedirs(notebook_archive_dir, exist_ok=True)

    # Find all .ipynb files
    for filename in os.listdir(notebook_dir):
        if filename.endswith(".ipynb") and re.match(r"^\d{4}-\d{2}-\d{2}-", filename):
            notebook_path = os.path.join(notebook_dir, filename)
            
            # Read the notebook
            with open(notebook_path, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)

            # Check for frontmatter in the first cell
            frontmatter = None
            if nb.cells and nb.cells[0].cell_type == "raw":
                try:
                    frontmatter = yaml.safe_load(nb.cells[0].source)
                    # Remove the frontmatter cell
                    nb.cells.pop(0)
                except yaml.YAMLError:
                    pass # Not a valid YAML frontmatter

            # Convert to markdown
            exporter = MarkdownExporter()
            (body, resources) = exporter.from_notebook_node(nb)

            # Create markdown content
            markdown_content = ""
            if frontmatter:
                markdown_content += "---\n"
                markdown_content += yaml.dump(frontmatter)
                markdown_content += "---\n"
            markdown_content += body

            # Determine output directory based on frontmatter
            output_dir = posts_dir
            if frontmatter and "categories" in frontmatter:
                categories = frontmatter["categories"]
                if isinstance(categories, list) and categories:
                    category = categories[0]
                    if category:
                        output_dir = os.path.join(posts_dir, category)
                elif isinstance(categories, str) and categories:
                    category = categories
                    output_dir = os.path.join(posts_dir, category)

            # Ensure the output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Create new filename
            base_filename = os.path.splitext(filename)[0]
            markdown_filename = f"{base_filename}.md"
            markdown_path = os.path.join(output_dir, markdown_filename)

            # Write the markdown file
            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            # Move the original notebook
            new_notebook_path = os.path.join(notebook_archive_dir, filename)
            os.rename(notebook_path, new_notebook_path)

if __name__ == "__main__":
    main()