import os
import platform

class TempFileArchiver:

    def __init__(self):
        self.archive_file = "archive.txt"

    # ---------- DETECT TEMP FILES ----------
    def detect_temp_files(self):
        system = platform.system()

        if system == "Windows":
            paths = [os.environ.get("TEMP"), os.environ.get("TMP")]
        else:
            paths = ["/tmp", "/var/tmp", os.path.expanduser("~/.cache")]

        files = []

        for p in paths:
            if p and os.path.exists(p):
                for root, _, f in os.walk(p):
                    for file in f:
                        if file.endswith((".txt", ".log", ".tmp")):
                            files.append(os.path.join(root, file))

        return files


    # ---------- READ FILE ----------
    def read_file(self, path):
        try:
            with open(path, "r", errors="ignore") as f:
                return f.read()
        except:
            return ""


    # ---------- LOAD ARCHIVE ----------
    def load_archive(self):
        if not os.path.exists(self.archive_file):
            return {}, []

        content_map = {}
        contents = []

        with open(self.archive_file, "r") as f:
            data = f.read().split("FILE:")

        for block in data[1:]:
            lines = block.strip().split("\n")
            name = lines[0].strip()
            text = "\n".join(lines[2:-1]) if "CONTENT:" in lines else ""

            if text:
                contents.append(text)
                content_map[text] = name

        return content_map, contents


    # ---------- ARCHIVE ----------
    def archive_files(self, files):
        content_map, contents = self.load_archive()
        a, d = 0, 0

        with open(self.archive_file, "a") as arch:
            for path in files:
                text = self.read_file(path)
                name = os.path.basename(path)

                if not text.strip():
                    continue

                if text in contents:
                    arch.write(f"FILE: {name}\nDUPLICATE OF: {content_map[text]}\nEND\n\n")
                    d += 1
                else:
                    arch.write(f"FILE: {name}\nCONTENT:\n{text}\nEND\n\n")
                    contents.append(text)
                    content_map[text] = name
                    a += 1

        print(f"\nArchived: {a} | Duplicates: {d}")


    # ---------- DELETE ----------
    def delete_files(self, files):
        if input("Delete original files? (y/n): ").lower() != "y":
            return

        for f in files:
            try:
                os.remove(f)
                print("Deleted:", f)
            except:
                print("Skipped:", f)


    # ---------- VIEW ----------
    def view_archive(self):
        if os.path.exists(self.archive_file):
            print(open(self.archive_file).read())
        else:
            print("No archive found.")


    # ---------- RESTORE ----------
    def restore_file(self, name):
        if not os.path.exists(self.archive_file):
            return print("No archive.")

        data = open(self.archive_file).read().split("FILE:")

        for block in data[1:]:
            block = block.strip() 

            if block.startswith(name):
                if "DUPLICATE" in block:
                    return print("Restore original first.")

                content = block.split("CONTENT:\n")[1].split("\nEND")[0]
                open(name, "w").write(content)
                return print(f"{name} restored.")

        print("Not found.")


# ---------- MAIN ----------
def main():
    archiver = TempFileArchiver()

    while True:
        print("\n1. Scan & Archive\n2. View\n3. Restore\n4. Exit")
        c = input("Choice: ")

        if c == "1":
            files = archiver.detect_temp_files()
            print("Found:", len(files))
            archiver.archive_files(files)
            archiver.delete_files(files)

        elif c == "2":
            archiver.view_archive()

        elif c == "3":
            archiver.restore_file(input("Filename: "))

        elif c == "4":
            break

        else:
            print("Invalid")


if __name__ == "__main__":
    main()