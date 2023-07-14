from gooey import Gooey, GooeyParser
import os
import re

@Gooey(program_name="IIQ Mover", program_description='Checks PhaseOne output TIFs against RBG or RGB/NIR folders.')
def main():
    """
    Set up the user interface, get the user input, and call the appropriate functions.
    """
    # Set up the argument parser
    parser = GooeyParser()
    # Add arguments for the user to input the necessary directories and options
    parser.add_argument('TIFS', metavar='Processed TIFs', help="Path to the folder containing processed TIFs", widget='DirChooser')
    parser.add_argument('RGB', metavar='RGB Folder Path', help="Path to the folder containing RGB .IIQs", widget='DirChooser')
    parser.add_argument('-NIR', metavar='NIR Folder Path', help="Path to the folder containing NIR .IIQs", required=False, widget='DirChooser')
    parser.add_argument('--Autorun', help="If checked, the script will execute the .bat file.", action='store_true', default=False)

    # Parse
    args = parser.parse_args()

    # Define the pattern to match in the filenames
    pattern = r"_\d+_\d{2}-\d{2}-\d{2}.\d{3}"

    def get_files(folder, extensions):
        """
        Returns a dictionary with keys being matched patterns from the filenames and values being the full file paths.
        """
        return {re.search(pattern, f).group(): os.path.join(folder, f) for f in os.listdir(folder) if re.search(pattern, f) and f.endswith(extensions)}

    # Get the list of files from each directory
    input_files1 = get_files(args.RGB, ('.IIQ',))
    input_files2 = get_files(args.NIR, ('.IIQ',)) if args.NIR else {}
    output_files = get_files(args.TIFS, ('.tif',))

    # Find the files that are in the input directories but not in the output directory
    missing_files1 = set(input_files1.keys()) - set(output_files.keys())
    missing_files2 = set(input_files2.keys()) - set(output_files.keys()) if args.NIR else set()

    # Create the batch file
    bat_file_path = os.path.join(args.TIFS, 'rerun_files.bat')
    with open(bat_file_path, 'w') as bat_file:
        rerun_folder1 = os.path.join(args.RGB, 'rerun_files')
        bat_file.write(f'mkdir "{rerun_folder1}"\n')
        for file in missing_files1:
            bat_file.write(f'move "{input_files1[file]}" "{os.path.join(rerun_folder1, os.path.basename(input_files1[file]))}"\n')

        # If the NIR directory was provided, move the missing files from there as well
        if args.NIR:
            rerun_folder2 = os.path.join(args.NIR, 'rerun_files')
            bat_file.write(f'mkdir "{rerun_folder2}"\n')
            for file in missing_files2:
                bat_file.write(f'move "{input_files2[file]}" "{os.path.join(rerun_folder2, os.path.basename(input_files2[file]))}"\n')

    # If the Autorun option was selected, run the batch file
    if args.Autorun:
        os.system(bat_file_path)

    # Print the success messages
    print(f"Successfully created the batch file at:\n{bat_file_path}")
    print("🎉🎉🎉 Hooray! The program completed successfully! 🎉🎉🎉")

if __name__ == "__main__":
    main()  # Execute the main function