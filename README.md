# Jupyter to Markdown Action

This GitHub Action converts Jupyter notebooks (`.ipynb`) to markdown files (`.md`), preserving frontmatter. It's designed to be used in a GitHub Actions workflow to automate the process of publishing blog posts written in Jupyter notebooks.

## How it works

The action performs the following steps:

1.  Finds all `.ipynb` files in the `_notebook` directory of your repository.
2.  For each notebook, it reads the content and checks for a YAML frontmatter block in the first cell. The first cell must be a raw cell for the frontmatter to be recognized.
3.  It converts the notebook to a markdown file.
4.  If a frontmatter block was found, it prepends it to the markdown file.
5.  It saves the new `.md` file to the `_posts` directory. If a `categories` frontmatter is present, it will save the markdown file in a subdirectory of `_posts` named after the first category.
6.  It moves the original `.ipynb` file to the `_notebook_archived` directory.
7.  The action will create the `_posts` and `_notebook_archived` directories if they don't exist.

## Usage

To use this action, you need to create a workflow file (e.g., `.github/workflows/convert_notebooks.yml`) in your repository. Here's an example workflow:

```yaml
name: Convert Notebooks to Posts

on:
  push:
    branches:
      - main

jobs:
  convert:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v2

      - name: Convert Notebooks
        uses: techtana/ghaction_blogpost_from_ipynb@main

      - name: Commit changes
        uses: EndBug/add-and-commit@v7
        with:
          author_name: github-actions[bot]
          author_email: github-actions[bot]@users.noreply.github.com
          message: "Convert notebooks to markdown"
```

### Inputs

This action has no inputs.

### Outputs

This action has no outputs.

## License

The Dockerfile and scripts in this repository are released under the [MIT License](LICENSE).
