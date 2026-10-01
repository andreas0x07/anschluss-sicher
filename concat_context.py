import os

def append_file_to_output(file_path, outfile, root_dir):
    """
    Reads a file and appends it to outfile with a distinct markdown-style header.
    """
    rel_path = os.path.relpath(file_path, start=root_dir).replace("\\", "/")
    header = f"\n// ==========================================\n// FILE: {rel_path}\n// ==========================================\n\n"

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as infile:
            content = infile.read()
            outfile.write(header)
            outfile.write(content)
            outfile.write("\n\n")
            print(f"  [+] Included: {rel_path}")
            return 1
    except Exception as e:
        print(f"  [!] Error reading '{rel_path}': {e}")
        return 0

def generate_context(project_root, output_path):
    # Extensions that represent relevant source code, configuration, or documentation
    INCLUDED_EXTENSIONS = {
        ".java", ".yaml", ".yml", ".properties",
        ".sql", ".xml", ".md", ".json"
    }

    # Explicit standalone files that might not have standard extensions or are in root
    EXPLICIT_ROOT_FILES = [
        "pom.xml",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        ".gitignore",
        ".dockerignore",
        "README.md",
        "SPECIFICATION.md",
        "HELP.md",
        ".mvn/wrapper/maven-wrapper.properties"
    ]

    # Directories that should NEVER be scanned (build artifacts, IDE caches, VCS)
    EXCLUDED_DIRS = {
        ".git",
        ".idea",
        "target",
        "classes",
        "generated-sources",
        ".mvn"  # wrapper configs handled explicitly if present
    }

    # Specific files to ignore even if their extension matches
    EXCLUDED_FILES = {
        "compiler.xml",
        "encodings.xml",
        "jarRepositories.xml",
        "misc.xml",
        "workspace.xml",
        "code_context.txt",
        "concat_context.py"
    }

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created output directory: {output_dir}")
        except Exception as e:
            print(f"Error creating directory '{output_dir}': {e}")
            return

    file_count = 0
    collected_paths = set()

    try:
        with open(output_path, "w", encoding="utf-8") as outfile:
            print(f"\n--- Scanning Java source code and resources under 'src' ---")
            src_dir = os.path.join(project_root, "src")

            if os.path.exists(src_dir):
                for root, dirs, files in os.walk(src_dir):
                    # Prune excluded directories in-place
                    dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

                    for file in files:
                        if file in EXCLUDED_FILES:
                            continue

                        _, ext = os.path.splitext(file)
                        if ext.lower() in INCLUDED_EXTENSIONS:
                            full_path = os.path.join(root, file)
                            collected_paths.add(os.path.abspath(full_path))
                            file_count += append_file_to_output(full_path, outfile, project_root)
            else:
                print(f"  [!] Warning: 'src' folder not found in {project_root}")

            print(f"\n--- Checking root build configs and project manifests ---")
            for rel_file in EXPLICIT_ROOT_FILES:
                full_path = os.path.join(project_root, rel_file)
                abs_path = os.path.abspath(full_path)

                if os.path.exists(full_path) and os.path.isfile(full_path):
                    if abs_path not in collected_paths and os.path.basename(full_path) not in EXCLUDED_FILES:
                        collected_paths.add(abs_path)
                        file_count += append_file_to_output(full_path, outfile, project_root)

            print(f"\n[DONE] Successfully merged {file_count} context files into:\n-> '{output_path}'\n")

    except Exception as e:
        print(f"Fatal error generating context file: {e}")

if __name__ == "__main__":
    # Resolve the project root dynamically from wherever this script is executed
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

    # Target output directory for AnschlussSicher:
    OUTPUT_DIRECTORY = r"D:\Sync\Dev\anschluss-sicher"
    OUTPUT_FILE_NAME = "code_context.txt"
    OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIRECTORY, OUTPUT_FILE_NAME)

    generate_context(project_root=CURRENT_DIR, output_path=OUTPUT_FILE_PATH)