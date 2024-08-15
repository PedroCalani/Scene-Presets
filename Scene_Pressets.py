import os
from PySide2 import QtWidgets

# Folder with pressets.
folder_path = hou.getenv("HOUDINI_USER_PREF_DIR") + "/scene_pressets"
if not os.path.exists(folder_path):
    os.mkdir(folder_path)


class Window_Scene_Pressets(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scene Presets")
        self.build_layout()

    def build_layout(self):
        # Vertical layout.
        lyt = QtWidgets.QVBoxLayout()
        self.setLayout(lyt)
        self.setFixedSize(400, 340)
        self.setStyleSheet("font-size: 14px;")

        # List with pressets.
        self.list_pressets = QtWidgets.QListWidget()
        self.list_pressets.setMinimumHeight(240)
        self.list_pressets.setMaximumHeight(240)

        self.list_pressets.itemClicked.connect(self.presset_clicked)
        lyt.addWidget(self.list_pressets)

        # Place to set presset name.
        self.presset_name = QtWidgets.QLineEdit()
        self.presset_name.textChanged.connect(self.name_changed)
        lyt.addWidget(self.presset_name)

        # Button to save a new presset or update an existing.
        self.save_button = QtWidgets.QPushButton("Save New Presset")
        self.save_button.clicked.connect(self.save_presset)
        self.save_button.setEnabled(False)
        lyt.addWidget(self.save_button)

        # Button to load presset.
        self.load_button = QtWidgets.QPushButton("Load Presset")
        self.load_button.clicked.connect(self.load_presset)
        self.load_button.setEnabled(False)
        lyt.addWidget(self.load_button)

        # Import saved pressets.
        cmd_files = self.get_pressets()
        self.add_to_list(cmd_files)


    def get_pressets(self):
        """Gets a list of all previously saved pressets."""

        cmd_files = []
        files = os.listdir(folder_path)

        for file in files:
            if file.endswith('.cmd'):
                name = os.path.splitext(file)[0]
                cmd_files.append(name)

        return cmd_files


    def add_to_list(self, cmd_files):
        """Adds all files to the list of pressets."""

        for file in cmd_files:
            self.list_pressets.addItem(file)


    def name_changed(self, text):
        """Check if there is a presset with the same name."""

        # If there is no text, return.
        if text == "":
            self.load_button.setEnabled(False)
            self.save_button.setEnabled(False)
            return

        # Check if this name is already used.
        total_items = self.list_pressets.count()
        for i in range(total_items):
            item = self.list_pressets.item(i)

            if text == item.text():
                self.save_button.setEnabled(True)
                self.save_button.setText("Update Presset")
                self.load_button.setEnabled(True)
                return

        # Correct name removing special characters.
        text = self.correct_text(text)
        self.presset_name.setText(text)

        self.save_button.setEnabled(True)
        self.save_button.setText("Save New Presset")
        self.load_button.setEnabled(False)


    def correct_text(self, text):
        """ Convert file name to valid name."""

        special_characters = [" ",".", "*", "!", "\\", ",", "/", 
                        "#", "(", ")", "$", "¡", "{", "}"]

        for c in special_characters:
            text = text.replace(c, "_")

        return text


    def presset_clicked(self, item):
        """Select that presset."""
        self.presset_name.setText(item.text())


    def save_presset(self):
        """Save presset."""

        name = self.presset_name.text()

        export_path = os.path.join(folder_path, f"{name}.cmd")

        # If this presset already exists, ask for confirmation.
        if os.path.exists(export_path):
            confirm_check = hou.ui.displayMessage(
                "Are you sure? This will remove the"
                "previous version of this presset.",
                buttons=("Confirm", "Cancel"),
                default_choice=0,
                close_choice=1)

            if not confirm_check == 0:
                # Reactivate principal window.
                self.activateWindow()
                return

        export_cmd = f'opscript -G -r / > "{export_path}"'
        hou.hscript(export_cmd)
        self.close()
        hou.ui.displayMessage("Saved.")


    def load_presset(self):
        """Create all nodes."""

        # Delete all existing nodes.
        for n in hou.node("/").children():
            for n_child in n.children():
                n_child.destroy()

        # Create nodes from selected presset.
        name = self.presset_name.text()

        hou.ui.setStatusMessage("Loading...")
        presset_path = os.path.join(folder_path, f"{name}.cmd")
        load_cmd = f'cmdread "{presset_path}"'
        hou.hscript(load_cmd)

        self.close()
        hou.ui.setStatusMessage("Ready.")


ui = Window_Scene_Pressets()
ui.show()


