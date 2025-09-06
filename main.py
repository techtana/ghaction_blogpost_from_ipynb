import os
import frontmatter
import openai
import config # Import the new config file

# --- Configuration ---
# Get environment variables
github_token = os.environ.get("GITHUB_TOKEN")
openai_api_key = os.environ.get("OPENAI_API_KEY")
repo_path = os.environ.get("GITHUB_WORKSPACE", ".") # Default to current directory for local testing

# --- Setup ---
if not openai_api_key:
    print("OPENAI_API_KEY is not set.")
    exit(1)
# Use the modern client initialization
client = openai.OpenAI(api_key=openai_api_key)

# Define directories
posts_dir = os.path.join(repo_path, "_posts_commit")
posts_out_dir = os.path.join(repo_path, "_posts")
enhance_policy_dir = os.path.join(repo_path, "_enhance_policy")
action_dir = os.path.dirname(__file__)
# Use the path from the config file
boilerplate_path = os.path.join(action_dir, config.INSTRUCTION_BOILERPLATE_PATH)

# Create output directory if it doesn't exist
if not os.path.isdir(posts_out_dir):
    os.makedirs(posts_out_dir)

# Read boilerplate
if os.path.isfile(boilerplate_path):
    with open(boilerplate_path, "r", encoding="utf-8") as f:
        instruction_boilerplate = f.read()
else:
    instruction_boilerplate = ""
    print("Warning: Boilerplate file not found.")

# --- Main Processing Loop ---
if not os.path.isdir(posts_dir):
    print(f"Directory not found: {posts_dir}")
    exit(0)

for filename in os.listdir(posts_dir):
    if not filename.endswith(".md"):
        continue

    filepath = os.path.join(posts_dir, filename)
    print(f"Processing {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    # Determine output directory based on category
    if 'categories' in post and post['categories']:
        category = post['categories']
        if isinstance(category, list):
            category = category[0]
        final_out_dir = os.path.join(posts_out_dir, category)
    else:
        final_out_dir = posts_out_dir

    if not os.path.isdir(final_out_dir):
        os.makedirs(final_out_dir)
    
    new_filepath = os.path.join(final_out_dir, filename)

    # Skip AI enhancement if already enhanced
    if "{% comment %}" in post.content:
        print(f"Skipping AI enhancement for {filename}, already enhanced.")
        with open(new_filepath, "wb") as f:
            frontmatter.dump(post, f)
        os.remove(filepath)
        print(f"Moved {filename} to {final_out_dir}")
        continue

    # Skip AI enhancement if policy is empty or null
    if "enhance_policy" not in post or not post["enhance_policy"]:
        print(f"Skipping AI enhancement for {filename}, no policy found.")
        with open(new_filepath, "wb") as f:
            frontmatter.dump(post, f)
        os.remove(filepath)
        print(f"Moved {filename} to {final_out_dir}")
        continue

    # --- AI Enhancement ---
    policy_name = post["enhance_policy"]
    policy_path = policy_name+'.prompt' if '.prompt' not in policy_name else policy_name
    policy_filepath = os.path.join(enhance_policy_dir, policy_name)

    if os.path.isfile(policy_filepath):
        with open(policy_filepath, "r", encoding="utf-8") as f:
            enhance_instruction = f.read()
        print(f"Using enhance policy from file: {policy_filepath}")
    else:
        enhance_instruction = policy_name
        print(f"Using enhance policy from front matter.")

    final_instruction = instruction_boilerplate + "\n\n------ \n\n Additional Instruction \n\n" + enhance_instruction
    content = post.content

    try:
        # Use the new client method
        response = client.responses.create(
            model="gpt-5",
            instructions=final_instruction,
            input=content
        )
        new_content = response.output_text
        post.content = new_content + "\n\n{% comment %}\n" + content + "\n{% endcomment %}"
        print(f"Successfully enhanced {filename}")

    except Exception as e:
        print(f"Error processing {filename} with OpenAI: {e}")
        # If there's an error, we still move the original file
        with open(new_filepath, "wb") as f:
            frontmatter.dump(post, f)
        os.remove(filepath)
        print(f"Moved original {filename} to {final_out_dir} due to error.")
        continue

    # --- Save and Move Enhanced File ---
    with open(new_filepath, "wb") as f:
        frontmatter.dump(post, f)
    
    os.remove(filepath) # remove original file from _posts_commit
    print(f"Moved enhanced {filename} to {final_out_dir}")
