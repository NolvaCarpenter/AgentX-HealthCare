import os


def validate_medication_image(filename=None):
    """
    Validates medication image filename and returns a valid path.

    Args:
        filename (str, optional): The user-provided filename. If None, uses default.

    Returns:
        tuple: (valid_filename, message) where message describes any changes made
    """
    default_path = "upload/drug_labels/"
    default_file = "prescription label example.png"
    default_full_path = os.path.join(default_path, default_file)
    message = ""

    # Use default if empty
    if not filename:
        message = "Using default medication label image."
        return default_full_path, message

    # If just a filename without path, assume it's in the default path
    if not os.path.dirname(filename):
        original_filename = filename
        filename = os.path.join(default_path, filename)
        message = f"Looking for '{original_filename}' in {default_path}"

    # Check if file exists
    if not os.path.exists(filename):
        message = f"Error: File '{filename}' not found. Using default instead."
        return default_full_path, message

    message = f"Using medication label: {filename}"
    return filename, message


def get_available_samples():
    """
    Returns a list of available sample medication label images.

    Returns:
        list: List of filenames in the default samples directory
    """
    default_path = "data/drug_labels/"
    if os.path.exists(default_path):
        return os.listdir(default_path)
    return []


if __name__ == "__main__":
    # Test the function
    samples = get_available_samples()
    print(f"Available samples: {samples}")

    test_cases = [
        None,
        "",
        "prescription label example.png",
        "nonexistent.png",
        "data/drug_labels/DAYTIME_COLD_AND_FLU_NON_DROWSY.jpeg",
    ]

    for test in test_cases:
        valid_path, msg = validate_medication_image(test)
        print(f"\nInput: {test}\nResult: {valid_path}\nMessage: {msg}")
