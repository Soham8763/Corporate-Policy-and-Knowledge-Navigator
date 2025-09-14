import os

def save_uploaded_file(uploaded_file, directory="data/documents"):
    """
    Saves an uploaded Streamlit file to a specified directory.
    Returns the full path of the saved file.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path