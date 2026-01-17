import os
import sys
import subprocess

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QFileDialog, QGroupBox,
    QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon


from config import load_config, save_config
from appveyor import download_latest_artifact, parse_project_url, get_last_successful_build
from git_ops import git_pull, git_status, git_push, git_commit
from miz_ops import extract_miz


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        def resource_path(relative):
            if hasattr(sys, "_MEIPASS"):
                return os.path.join(sys._MEIPASS, relative)
            return relative

        icon_path = resource_path("assets/icon.ico")

        self.cfg = load_config()

        self.setWindowTitle("132nd vWing Mission Tool")
        self.setFixedSize(500, 700)

        tabs = QTabWidget()
        tabs.addTab(self.build_actions_tab(), "Actions")
        tabs.addTab(self.build_config_tab(), "Config")
        tabs.addTab(self.build_about_tab(), "About")
       
        self.setCentralWidget(tabs)

        # runtime icon
        self.setWindowIcon(QIcon(icon_path))


    # ---------------------------------------------------------
    # TAB 1: ACTIONS
    # ---------------------------------------------------------
    def build_actions_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # ---------------- Frame 1: .miz File ----------------
        miz_group = QGroupBox("Step 1 Get Latest .miz File")
        miz_layout = QVBoxLayout()

        # Row 1: Local version
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Local Version:"))
        self.local_version_label = QLabel("unknown")
        row1.addWidget(self.local_version_label)
        row1.addStretch()
        miz_layout.addLayout(row1)

        # Row 2: Remote version
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Remote Version:"))
        self.remote_version_label = QLabel("unknown")
        row2.addWidget(self.remote_version_label)
        row2.addStretch()
        miz_layout.addLayout(row2)

        # Row 3: Buttons
        row3 = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.update_versions)
        download_btn = QPushButton("Download")
        download_btn.clicked.connect(self.download_action)
        row3.addWidget(refresh_btn)
        row3.addWidget(download_btn)
        miz_layout.addLayout(row3)

        miz_group.setLayout(miz_layout)
        layout.addWidget(miz_group)

        # ---------------- Frame 2: Git Repo ----------------
        git_group = QGroupBox("Step 2 Sync Git Repository")
        git_layout = QVBoxLayout()

        # Row 1: Pull + Status
        row4 = QHBoxLayout()
        pull_btn = QPushButton("Git Pull")
        pull_btn.clicked.connect(self.git_pull_action)
        status_btn = QPushButton("Git Status")
        status_btn.clicked.connect(self.git_status_action)
        row4.addWidget(pull_btn)
        row4.addWidget(status_btn)
        git_layout.addLayout(row4)

        git_group.setLayout(git_layout)
        layout.addWidget(git_group)

        # -------------------Frame 2b: Edit-------------------
        edit_group = QGroupBox("Step 3 Edit .miz file in DCS. (Save as same name)")
        edit_layout = QVBoxLayout()

        edit_group.setLayout(edit_layout)
        layout.addWidget(edit_group)


        # ---------------- Frame 3: Re-order MIZ ----------------
        reorder_group = QGroupBox("Step 4 Re-order MIZ")
        reorder_layout = QVBoxLayout()

        # Override miz. 
        row_override = QHBoxLayout()
        row_override.addWidget(QLabel("Use different .miz file (optional):"))

        self.override_miz_edit = QLineEdit()
        self.override_miz_edit.setPlaceholderText("Use Step 1 capture")

        # Default browse directory = settings miz folder
        default_dir = os.path.dirname(self.cfg["miz"]["miz_path"])

        browse_override = QPushButton("Browse")
        browse_override.clicked.connect(
            lambda: self.pick_file(self.override_miz_edit, start_dir=default_dir)
        )

        row_override.addWidget(self.override_miz_edit)
        row_override.addWidget(browse_override)
        reorder_layout.addLayout(row_override)


        # Extract button
        extract_btn = QPushButton("Re-Order (Extract MIZ into Repo)")
        extract_btn.clicked.connect(self.extract_action)
        reorder_layout.addWidget(extract_btn)

        reorder_group.setLayout(reorder_layout)
        layout.addWidget(reorder_group)


        # ---------------- Frame 4: Open Repo ----------------
        openrepo_group = QGroupBox("Step 5 Modify local repo script or asset files")
        openrepo_layout = QVBoxLayout()

        open_repo_btn = QPushButton("Open Repo Folder")
        open_repo_btn.clicked.connect(self.open_repo_folder)
        openrepo_layout.addWidget(open_repo_btn)

        openrepo_group.setLayout(openrepo_layout)
        layout.addWidget(openrepo_group)

        # ---------------- Frame 4: Commit & Push ----------------
        commit_group = QGroupBox("Step 6 Commit Updates and Push")
        commit_layout = QVBoxLayout()

        # Commit message input
        self.commit_message_edit = QLineEdit()
        self.commit_message_edit.setPlaceholderText("Commit message (required)")
        commit_layout.addWidget(self.commit_message_edit)

        row5 = QHBoxLayout()
        commit_btn = QPushButton("Commit")
        commit_btn.clicked.connect(self.git_commit_action)
        push_btn = QPushButton("Push")
        push_btn.clicked.connect(self.git_push_action)

        row5.addWidget(commit_btn)
        row5.addWidget(push_btn)
        commit_layout.addLayout(row5)

        commit_group.setLayout(commit_layout)
        layout.addWidget(commit_group)

        # ---------------- Shared Output Window ----------------
        self.output_window = QTextEdit()
        self.output_window.setReadOnly(True)
        layout.addWidget(self.output_window)

        # ---------------- Exit button bottom-right ------------
        exit_row = QHBoxLayout()
        exit_row.addStretch()
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.close)
        exit_row.addWidget(exit_btn)
        layout.addLayout(exit_row)

        self.update_versions()

        return tab

    # ---------------------------------------------------------
    # TAB 2: CONFIG
    # ---------------------------------------------------------
    def build_config_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # ---------------- Frame 1: .miz File ----------------
        miz_group = QGroupBox(".miz File")
        miz_layout = QVBoxLayout()

        # Row 1: Local .miz path
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Local .miz File Path:"))
        self.miz_path_edit = QLineEdit(self.cfg["miz"]["miz_path"])
        browse1 = QPushButton("Browse")
        browse1.clicked.connect(lambda: self.pick_folder(self.miz_path_edit))
        row1.addWidget(self.miz_path_edit)
        row1.addWidget(browse1)
        miz_layout.addLayout(row1)

        hint1 = QLabel("e.g. C:/dcs/trma-miz")
        hint1.setStyleSheet("color: gray; font-style: italic; font-size: 11px;")
        hint1.setContentsMargins(100, 0, 0, 0)   # indent without affecting layout stretch
        miz_layout.addWidget(hint1)


        # Row 2: Appveyor URL
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Appveyor URL:"))
        self.appveyor_url_edit = QLineEdit(self.cfg["miz"].get("miz_url", ""))
        row2.addWidget(self.appveyor_url_edit)
        miz_layout.addLayout(row2)
        miz_group.setLayout(miz_layout)
        layout.addWidget(miz_group)

        hint2 = QLabel("e.g. https://ci.appveyor.com/project/132nd-VirtualWing/trma")
        hint2.setStyleSheet("color: gray; font-style: italic; font-size: 11px;")
        hint2.setContentsMargins(100, 0, 0, 0)   # indent without affecting layout stretch
        miz_layout.addWidget(hint2)



        # ---------------- Frame 2: Git Repo ----------------
        git_group = QGroupBox("Git Repository")
        git_layout = QVBoxLayout()

        # Row 1: Local repo path
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Local Repo Path:"))
        self.repo_path_edit = QLineEdit(self.cfg["git"]["repo_path"])
        browse2 = QPushButton("Browse")
        browse2.clicked.connect(lambda: self.pick_folder(self.repo_path_edit))
        row3.addWidget(self.repo_path_edit)
        row3.addWidget(browse2)
        git_layout.addLayout(row3)

        hint3 = QLabel("e.g. C:/dcs/trma-git")
        hint3.setStyleSheet("color: gray; font-style: italic; font-size: 11px;")
        hint3.setContentsMargins(100, 0, 0, 0)   # indent without affecting layout stretch
        git_layout.addWidget(hint3)


        # Row 2: Git Repo URL
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Git Repo URL:"))
        self.repo_url_edit = QLineEdit(self.cfg["git"]["repo_url"])
        row4.addWidget(self.repo_url_edit)
        git_layout.addLayout(row4)

        git_group.setLayout(git_layout)
        layout.addWidget(git_group)

        hint4 = QLabel("e.g. https://github.com/132nd-vWing/TRMA")
        hint4.setStyleSheet("color: gray; font-style: italic; font-size: 11px;")
        hint4.setContentsMargins(100, 0, 0, 0)   # indent without affecting layout stretch
        git_layout.addWidget(hint4)

        layout.addWidget(miz_group)
        layout.addWidget(git_group)
        layout.addStretch()

        # Save + Exit
        row5 = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        row5.addWidget(save_btn)
        row5.addStretch()
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.close)
        row5.addWidget(exit_btn)
        layout.addLayout(row5)



        return tab

    # ---------------------------------------------------------
    # TAB 3: ABOUT
    # ---------------------------------------------------------
    def build_about_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        about_group = QGroupBox("About This Tool")
        about_layout = QVBoxLayout()

        about_text = QLabel(
            "132nd vWing Mission Tool\n\n"
            "Manages .miz files, Appveyor builds, and Git repositories.\n"
            "Rev 1.0.\n\n"
            "Contact 132nd.Jonde for help"
        )
        about_text.setWordWrap(True)
        about_layout.addWidget(about_text)

        about_group.setLayout(about_layout)
        layout.addWidget(about_group)

        # Exit button bottom-right
        exit_row = QHBoxLayout()
        exit_row.addStretch()
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.close)
        exit_row.addWidget(exit_btn)
        layout.addLayout(exit_row)

        return tab

    # ---------------------------------------------------------
    # LOGIC METHODS (converted from Tkinter version)
    # ---------------------------------------------------------

    def open_repo_folder(self):
        path = self.cfg["git"]["repo_path"]

        # Windows
        if sys.platform.startswith("win"):
            # If it's a WSL UNC path, convert it
            if path.startswith("\\\\wsl.localhost"):
                try:
                    win_path = subprocess.check_output(
                        ["wsl", "wslpath", "-w", path],
                        text=True
                    ).strip()
                    os.startfile(win_path)
                    return
                except Exception as e:
                    self.output_window.append(f"[Open Repo] WSL path conversion failed: {e}")
                    return

            # Normal Windows path
            try:
                os.startfile(path)
            except Exception as e:
                self.output_window.append(f"[Open Repo] Failed to open folder: {e}")
            return

        # Linux / WSL
        try:
            subprocess.Popen(["xdg-open", path])
        except Exception as e:
            self.output_window.append(f"[Open Repo] xdg-open failed: {e}")

    def find_latest_miz(self):
        files = [f for f in os.listdir(self.cfg["miz"]["miz_path"]) if f.endswith(".miz")]

        def extract_version(f):
            import re
            m = re.search(r"\.(\d+)\.miz$", f)
            return int(m.group(1)) if m else -1

        if not files:
            return None

        return sorted(files, key=extract_version)[-1]

    def update_versions(self):
        # Local version
        try:
            files = [f for f in os.listdir(self.cfg["miz"]["miz_path"]) if f.endswith(".miz")]
            if files:
                def extract_version(f):
                    import re
                    m = re.search(r"\.(\d+)\.miz$", f)
                    return int(m.group(1)) if m else -1

                files.sort(key=extract_version)
                self.local_version_label.setText(files[-1])
            else:
                self.local_version_label.setText("none")
        except Exception as e:
            self.local_version_label.setText(f"error ({e})")

        # Remote version
        try:
            account, project = parse_project_url(self.cfg["miz"]["miz_url"])
            job_id, version = get_last_successful_build(account, project)
            self.remote_version_label.setText(version)
        except Exception:
            self.remote_version_label.setText("no file")

    def download_action(self):
        try:
            # Notify user immediately
            self.output_window.append("[Download] Downloading...")
            QApplication.processEvents()   # force UI update

            result = download_latest_artifact(
                self.cfg["miz"]["miz_url"],
                self.cfg["miz"]["miz_path"]
            )

            self.output_window.append(
                "[Download] Completed\n"
                f"  Version   : {result['version']}\n"
                f"  Artifact  : {result['artifact']}\n"
                f"  Job ID    : {result['job_id']}\n"
                f"  Size      : {result['bytes']} bytes\n"
                f"  Saved to  : {result['path']}\n"
            )

            self.update_versions()

        except Exception as e:
            self.output_window.append(f"[Download Error] {e}\n")

    def extract_action(self):
        try:
            latest = self.find_latest_miz()
            if not latest:
                self.output_window.append("[MIZ Extract] No .miz file found.\n")
                return

            override = self.override_miz_edit.text().strip()
            miz_path = override if override else os.path.join(self.cfg["miz"]["miz_path"], latest)

            extracted, overwritten = extract_miz(
                miz_path,
                self.cfg["git"]["repo_path"]
            )

            self.output_window.append(
                "[MIZ Extract]\n"
                f"  Source: {miz_path}\n"
                f"  New files: {len(extracted)}\n"
                f"  Overwritten: {len(overwritten)}\n"
            )

            for f in overwritten:
                self.output_window.append(f"  OVERWRITE: {f}")
            for f in extracted:
                self.output_window.append(f"  ADD:       {f}")

            self.output_window.append("")

        except Exception as e:
            self.output_window.append(f"[MIZ Extract Error] {e}\n")


    def git_pull_action(self):
        repo_path = self.cfg["git"]["repo_path"]
        remote_url = self.cfg["git"]["repo_url"]  # ensure this exists in config

        git_dir = os.path.join(repo_path, ".git")

        # ---------------------------------------------------------
        # CASE 1: Repo does NOT exist → perform first-time clone
        # ---------------------------------------------------------
        if not os.path.isdir(git_dir):
            self.output_window.append(f"[Git Pull]\nNo local repo found at:\n{repo_path}\n")
            self.output_window.append(f"Cloning from:\n{remote_url}\n")

            try:
                result = subprocess.run(
                    ["git", "clone", remote_url, repo_path],
                    capture_output=True,
                    text=True,
                    shell=False
                )

                output = result.stdout + result.stderr
                self.output_window.append(output)

                if result.returncode == 0:
                    self.output_window.append("[Git Pull] Clone completed successfully.\n")
                else:
                    self.output_window.append(f"[Git Pull Error] Clone failed with code {result.returncode}\n")

            except Exception as e:
                self.output_window.append(f"[Git Pull Error] {e}\n")
            return

        # ---------------------------------------------------------
        # CASE 2: Repo exists → normal pull
        # ---------------------------------------------------------
        try:
            output = git_pull(repo_path)
            self.output_window.append(f"[Git Pull]\n{output}\n")
        except Exception as e:
            self.output_window.append(
                f"[Git Pull Error] {e}\n"
                "You probably need to first do a git clone\n"
                "to create your local repo.\n"
            )

    def git_status_action(self):
        try:
            output = git_status(self.cfg["git"]["repo_path"])
            self.output_window.append(f"[Git Status]\n{output}\n")
        except Exception as e:
            self.output_window.append(f"[Git Status Error] {e}\n")

    def git_commit_action(self):
        message = self.commit_message_edit.text().strip()

        if not message:
            self.output_window.append(
                "[Git Commit Error] Commit message is required.\n"
            )
            return

        try:
            output = git_commit(
                self.cfg["git"]["repo_path"],
                message
            )
            self.output_window.append(f"[Git Commit]\n{output}\n")
            self.commit_message_edit.clear()
        except Exception as e:
            self.output_window.append(f"[Git Commit Error] {e}\n")


    def git_push_action(self):
        try:
            output = git_push(self.cfg["git"]["repo_path"])
            self.output_window.append(f"[Git Push]\n{output}\n")
        except Exception as e:
            self.output_window.append(f"[Git Push Error] {e}\n")


    # ---------------------------------------------------------
    # CONFIG SAVE + PATH PICKER
    # ---------------------------------------------------------
    def save_settings(self):
        self.cfg["miz"]["miz_path"] = self.miz_path_edit.text()
        self.cfg["miz"]["miz_url"] = self.appveyor_url_edit.text()
        self.cfg["git"]["repo_path"] = self.repo_path_edit.text()
        self.cfg["git"]["repo_url"] = self.repo_url_edit.text()

        save_config(self.cfg)
        QMessageBox.information(self, "Saved", "Settings saved")

    def pick_folder(self, line_edit, start_dir=None):
        initial = start_dir or line_edit.text() or ""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", initial)
        if folder:
            line_edit.setText(folder)


    def pick_file(self, line_edit, start_dir=None):
        initial = start_dir or os.path.dirname(line_edit.text()) or ""
        path, _ = QFileDialog.getOpenFileName(self, "Select .miz File", initial, "MIZ Files (*.miz)")
        if path:
            line_edit.setText(path)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

