"""UI component for loading files and folders."""

import logging
import os
import shutil
import tempfile
from pathlib import Path

from src.data.parsers import CSVParser
from src.data.document_loader import DocumentLoader

logger = logging.getLogger(__name__)


class FileLoader:
    """Handles file and folder loading UI interactions."""

    def __init__(self):
        self.upload_dir = tempfile.mkdtemp(prefix="construction_agent_")

    def cleanup(self) -> None:
        """Clean up temporary directory."""
        if os.path.exists(self.upload_dir):
            shutil.rmtree(self.upload_dir, ignore_errors=True)

    def validate_file_path(self, file_path: str) -> tuple[Path, str, float] | None:
        """
        Validate file path, extension, and size.
        Returns: (Path, extension, size_mb) or None if invalid
        """
        path = Path(file_path)

        if not path.exists():
            print(f"❌ File not found: {file_path}")
            return None

        ext = path.suffix.lower()
        if ext not in [".csv", ".pdf"]:
            print(f"❌ Invalid format: '.{ext[1:] if ext else 'no extension'}'")
            print(f"   Supported: .csv, .pdf")
            return None

        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 100:
            print(f"❌ File too large: {size_mb:.1f}MB (max 100MB)")
            return None

        return path, ext, size_mb

    def validate_folder_path(self) -> str:
        """
        Prompt user for folder path with validation.
        Returns path or empty string if cancelled.
        """
        print("\n📁 FOLDER LOADING")
        print("-" * 90)

        while True:
            folder_path = input("📂 Enter folder path (or 'cancel'): ").strip()

            if folder_path.lower() == "cancel":
                return ""

            path = Path(folder_path)

            if not path.exists():
                print(f"❌ Folder not found: {folder_path}")
                continue

            if not path.is_dir():
                print(f"❌ Not a folder: {folder_path}")
                continue

            return folder_path

    def copy_folder_files(self, file_paths: list[str]) -> list[str]:
        """Copy files from source to upload directory."""
        imported_files = []
        for file_path in file_paths:
            try:
                src = Path(file_path)
                dst = Path(self.upload_dir) / src.name
                shutil.copy(str(src), str(dst))
                imported_files.append(str(dst))
            except Exception as e:
                print(f"   ⚠️  Error copying {src.name}: {e}")
        return imported_files

    def parse_csv_files(self, file_paths: list[str]) -> list:
        """Parse CSV files and extract project data."""
        projects = []
        for file_path in file_paths:
            if file_path.lower().endswith('.csv'):
                try:
                    new_projects = CSVParser().parse(file_path)
                    projects.extend(new_projects)
                except Exception as e:
                    print(f"   ⚠️  Error parsing {Path(file_path).name}: {e}")
        return projects

    def upload_file(self) -> tuple[str, str]:
        """
        Prompt user to upload a file.
        Returns: (file_path, file_type) or ('', '') if cancelled
        """
        print("\n📁 FILE UPLOAD")
        print("-" * 90)
        print("Supported formats: CSV, PDF")
        print()

        while True:
            file_path = input("📂 Enter file path (or 'cancel'): ").strip()

            if file_path.lower() == "cancel":
                return "", ""

            # Validate file
            result = self.validate_file_path(file_path)
            if not result:
                continue

            path, ext, size_mb = result

            # Copy file to upload directory
            try:
                dest = Path(self.upload_dir) / path.name
                shutil.copy(str(path), str(dest))
                file_type = "csv" if ext == ".csv" else "pdf"
                print(f"✅ Uploaded: {path.name} ({size_mb:.1f}MB)")
                print(f"   Detected type: {file_type.upper()}")
                return str(dest), file_type
            except Exception as e:
                print(f"❌ Error: {e}")

    def load_folder(self) -> tuple[list[str], list]:
        """
        Load folder of documents.
        Returns: (file_paths, projects)
        """
        # Get and validate folder path
        folder_path = self.validate_folder_path()
        if not folder_path:
            return [], []

        try:
            # Discover files in folder
            file_paths, results = DocumentLoader.discover_files(folder_path)

            if not file_paths:
                print(f"❌ No CSV or PDF files found in {folder_path}")
                return [], []

            # Copy files to upload directory
            imported_files = self.copy_folder_files(file_paths)

            # Parse CSV files for project data
            projects = self.parse_csv_files(imported_files)

            print(f"\n✅ Loaded folder: {folder_path}")
            print(f"   • CSV files: {results['csv']}")
            print(f"   • PDF files: {results['pdf']}")
            print(f"   • Total files: {results['csv'] + results['pdf']}")
            print(f"   ℹ️  Files will be indexed in analysis phase")

            return imported_files, projects

        except Exception as e:
            print(f"❌ Error: {e}")
            return [], []

    def load_documents(self) -> tuple[list[str], list]:
        """
        Document loading menu: upload files, load folder, or start analysis.
        Returns: (uploaded_files, projects)
        """
        uploaded_files = []
        projects = []

        print("\n" + "=" * 90)
        print("  📄 DOCUMENT LOADING")
        print("=" * 90)

        while True:
            print("\nOptions:")
            print("  1. Upload a file (auto-detect CSV/PDF)")
            print("  2. Load folder")
            print("  3. Start analysis")

            choice = input("\n👉 Choose (1-3): ").strip()

            if choice == "1":
                file_path, file_type = self.upload_file()
                if file_path:
                    uploaded_files.append(file_path)

                    # Auto-process based on detected type
                    if file_type == "csv":
                        try:
                            new_projects = CSVParser().parse(file_path)
                            projects.extend(new_projects)
                            print(f"   ✅ CSV parsed: {len(new_projects)} projects")
                        except Exception as e:
                            print(f"   ⚠️  Error parsing CSV: {e}")
                    elif file_type == "pdf":
                        print(f"   ✅ PDF will be indexed during analysis")

            elif choice == "2":
                folder_files, folder_projects = self.load_folder()
                if folder_files:
                    uploaded_files.extend(folder_files)
                    projects.extend(folder_projects)
                    print(f"   ✅ Folder loaded: {len(folder_files)} files")

            elif choice == "3":
                break
            else:
                print("❌ Invalid option")

        if uploaded_files:
            print(f"\n✅ Documents ready for indexing: {len(uploaded_files)}")
        else:
            print("\n⚠️  No documents loaded. Using empty dataset.")

        return uploaded_files, projects
