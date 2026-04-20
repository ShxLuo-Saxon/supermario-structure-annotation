
import os
import sys
import argparse
import zipfile
import subprocess
import tempfile
from pathlib import Path

XML2ABC_SCRIPT = Path(__file__).resolve().parent / "external" / "xml2abc.py"


def unzip_mxl(mxl_path, extract_dir):
    """
    Extracts the main .xml or .musicxml file found in the .mxl archive,
    skipping metadata files like container.xml.
    Returns the full path to the extracted file.
    """
    mxl_path = Path(mxl_path)
    extract_dir = Path(extract_dir)
    try:
        with zipfile.ZipFile(mxl_path, 'r') as z:
            # Find the first valid XML file that is NOT in META-INF
            for name in z.namelist():
                if (name.endswith('.xml') or name.endswith('.musicxml')) and not name.startswith('META-INF'):
                    # Prevent path traversal issues by using basename
                    filename = Path(name).name
                    target_path = extract_dir / filename
                    
                    with open(target_path, 'wb') as f:
                        f.write(z.read(name))
                    return target_path
                    
    except zipfile.BadZipFile:
        print(f"Error: {mxl_path} is not a valid zip file.")
    except Exception as e:
        print(f"Error extracting {mxl_path}: {e}")
    
    return None

def convert_to_abc(mxl_path, output_dir):
    """
    Converts a single .mxl file to .abc using xml2abc.
    """
    mxl_path = Path(mxl_path)
    output_dir = Path(output_dir)
    filename = mxl_path.name
    base_name = mxl_path.stem
    output_path = output_dir / f"{base_name}.abc"
    
    print(f"Processing: {filename}...")

    if not XML2ABC_SCRIPT.exists():
        print(f"Error: xml2abc script not found at {XML2ABC_SCRIPT}")
        return False

    # Create a temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        # Step 1: Extract .xml from .mxl
        xml_file = unzip_mxl(mxl_path, temp_dir)
        
        if not xml_file:
            # Fallback: Check if the input is actually a raw XML file
            if mxl_path.suffix.lower() in ('.xml', '.musicxml'):
                xml_file = mxl_path
            else:
                print(f"Failed: Could not extract music XML from {filename}")
                return False

        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        cmd = [sys.executable, str(XML2ABC_SCRIPT), str(xml_file)]
        print(f"Running conversion for {base_name}...")

        try:
            with open(output_path, 'w', encoding='utf-8') as outfile:
                result = subprocess.run(cmd, stdout=outfile, stderr=subprocess.PIPE,
                                     text=True, encoding='utf-8', errors='replace', env=env)
                
                if result.returncode != 0:
                    print(f"Error running xml2abc on {filename}:")
                    print(result.stderr)
                    return False
                    
                print(f"Success: Saved to {output_path}")
                return True

        except Exception as e:
            print(f"Exception during conversion: {e}")
            return False


def resolve_file_path(filename, input_dir, fixes_dir):
    """
    Check if a file exists in fixes_dir first, otherwise use input_dir.
    Returns the full path to the file to use.
    """
    input_dir = Path(input_dir)
    if fixes_dir:
        fixes_dir = Path(fixes_dir)
        if fixes_dir.is_dir():
            fixes_path = fixes_dir / filename
            if fixes_path.exists():
                print(f"  -> Using patched version from fixes folder")
                return fixes_path
    
    return input_dir / filename


def main():
    parser = argparse.ArgumentParser(description="Convert .mxl files to .abc using xml2abc.")
    parser.add_argument("input", help="Input .mxl file or directory")
    parser.add_argument("-o", "--output", required=True, help="Output directory")
    parser.add_argument("--fixes", default=None, help="Fixes/patches directory to check first (priority over input)")
    parser.add_argument("--only-fixes", action="store_true", help="Process only files that exist in fixes folder")

    args = parser.parse_args()

    output_dir = Path(args.output)

    # Process input
    files_to_process = []
    input_path = Path(args.input)
    if input_path.is_dir():
        input_base_dir = input_path
        for file_path in input_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ('.mxl', '.musicxml', '.xml'):
                files_to_process.append(file_path.name)
        if not files_to_process:
            print(f"No .mxl/.musicxml/.xml files found in {args.input}")
            return
    elif input_path.is_file():
        input_base_dir = input_path.parent
        files_to_process.append(input_path.name)
    else:
        print(f"Error: {args.input} is not a valid file or directory.")
        return
            
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Using output directory: {output_dir}")

    # Filter files if --only-fixes is enabled
    if args.only_fixes and args.fixes:
        fixes_dir = Path(args.fixes)
        if fixes_dir.is_dir():
            fixes_files = {
                f.name for f in fixes_dir.iterdir()
                if f.is_file() and f.suffix.lower() in ('.mxl', '.musicxml', '.xml')
            }
        else:
            fixes_files = set()

        original_count = len(files_to_process)
        files_to_process = [f for f in files_to_process if f in fixes_files]
        print(f"--only-fixes enabled: Processing {len(files_to_process)}/{original_count} files (only those with patches)")
        
        if not files_to_process:
            print("No files to process - no matching files in fixes folder.")
            return
    
    # Process all files
    success_count = 0
    for filename in files_to_process:
        # Resolve which version to use (fixes or original)
        file_path = resolve_file_path(filename, input_base_dir, args.fixes)
        
        if convert_to_abc(file_path, output_dir):
            success_count += 1

    print(f"\nBatch complete. Converted {success_count}/{len(files_to_process)} files.")

if __name__ == "__main__":
    main()
