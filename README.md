# Selenium UI Test Automation Tool

## 🚀 Project Overview

This project is a GUI-based automation tool that leverages Selenium to automatically test web application UIs and capture screenshots at various screen sizes (Breakpoints). It provides a flexible testing environment by allowing users to directly specify login information, a list of URLs to test, screenshot save paths, and Breakpoint settings.

## ✨ Key Features

*   **Automatic Login**: Automatically logs in to a specified login URL using the user ID and password.
*   **Screenshot Capture at Various Breakpoints**:
    *   XL (1280px and above)
    *   LG (1024px ~ 1279px)
    *   MD (768px ~ 1023px)
    *   SM (360px ~ 767px)
    *   Users can directly set the width for each Breakpoint, and input validation ensures the width is within the valid range.
*   **URL List-Based Screenshots**: Iterates through URLs listed in `url.txt` or another user-specified `.txt` file to capture screenshots.
*   **Configurable Save Path**: Users can specify the folder where captured screenshots will be saved.
*   **Chrome and Edge Browser Support**: Supports testing on both Chrome and Edge browsers.
*   **GUI-Based**: Provides an intuitive user interface using Tkinter.

## 🛠️ Installation and Execution

### 1. Python Installation

Python 3.8 or higher is required.
Download and install from the [official Python website](https://www.python.org/downloads/).

### 2. Dependency Installation

Navigate to the project directory and run the following command to install the necessary libraries:

```bash
pip install selenium webdriver-manager
```

### 3. Application Execution

Once installed, run the `main.py` file to start the GUI application:

```bash
python main.py
```

## 🖥️ How to Use

Upon running the application, you will see the following UI:

1.  **Login Information**:
    *   **ID**: Enter the user ID for login.
    *   **Password**: Enter the user password for login.
2.  **Login URL**:
    *   Enter the URL of the login page for the website to perform automatic login. A default value is provided.
3.  **Breakpoint Settings**:
    *   The currently set Breakpoint list is displayed.
    *   Click the `Edit` button to modify the width for each Breakpoint (XL, LG, MD, SM).
    *   Each Breakpoint's width can only be set within its specified valid range.
4.  **Save Path**:
    *   Displays the folder path where captured screenshots will be saved.
    *   Click the `Select Folder` button to specify a different save path.
5.  **URL File**:
    *   Displays the path to the `.txt` file containing the list of URLs for screenshot capture. The default is `url.txt`.
    *   Click the `Select File` button to specify a different `.txt` file. Each line should contain one complete URL.
6.  **Chrome / Edge**:
    *   **Login**: Attempts to log in using the respective browser.
    *   **Screenshot**: After successful login, iterates through the pages specified in the URL file, captures screenshots, and saves them to the designated save path.

## ⚙️ Configuration Files

*   `config.py`: Defines the default login URL, default Breakpoint settings, and valid ranges for each Breakpoint.
*   `url.txt`: A text file containing a list of web page URLs for screenshot capture. Each line should contain one complete URL.

## 📦 Packaging (Optional)

You can package this application into a single executable file using PyInstaller.

1.  **Install PyInstaller**:
    ```bash
pip install pyinstaller
    ```
2.  **Package the Application**:
    From the project root directory, run the following command:
    ```bash
pyinstaller --noconsole --onefile --add-data "config.py;." --add-data "autologin.py;." --add-data "screenshot.py;." --add-data "url.txt;." main.py
    ```
    Once packaged, the executable file will be generated in the `dist` folder.

## ⬇️ Download Executable

You can download the latest packaged executable from the [GitHub Releases page](https://github.com/kx2471/AutoScreenshot_UI_Test/releases).
*(Note: You will need to create a new release on your GitHub repository and upload the `main.exe` file from the `dist` folder to that release for the link to work.)*

## 🤝 Contributing

This project can be continuously improved to enhance user convenience. Contributions are welcome!

---