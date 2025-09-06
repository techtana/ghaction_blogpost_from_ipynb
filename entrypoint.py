
import os
import subprocess
import yaml
import nbformat
from nbconvert import MarkdownExporter

def main():
    # Get the repository path
    repo_path = os.environ.get("GITHUB_WORKSPACE")
    if not repo_path:
        print("Error: GITHUB_WORKSPACE environment variable not set.")
        return

    # Configure git
    subprocess.run(["git", "config", "--global", "--add", "safe.directory", repo_path], check=True)
    subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)

    # Define paths
    notebook_dir = os.path.join(repo_path, "_jupyter_notebook")
    posts_dir = os.path.join(repo_path, "_posts")

    # Ensure the posts directory exists
    os.makedirs(posts_dir, exist_ok=True)

    # Find all .ipynb files
    for filename in os.listdir(notebook_dir):
        if filename.endswith(".ipynb"):
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
                markdown_content += "---
"
                markdown_content += yaml.dump(frontmatter)
                markdown_content += "---
"
            markdown_content += body

            # Create new filename
            base_filename = os.path.splitext(filename)[0]
            markdown_filename = f"{base_filename}.md"
            markdown_path = os.path.join(posts_dir, markdown_filename)

            # Write the markdown file
            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            # Move the original notebook
            new_notebook_path = os.path.join(posts_dir, filename)
            os.rename(notebook_path, new_notebook_path)

            # Git add
            subprocess.run(["git", "add", markdown_path], check=True)
            subprocess.run(["git", "add", new_notebook_path], check=True)

    # Commit and push changes
    try:
        subprocess.run(["git", "commit", "-m", "Convert notebooks to markdown"], check=True)
        subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        # It's possible there were no changes to commit
        print(f"Git commit/push failed: {e}")

if __name__ == "__main__":
    main()
