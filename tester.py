from utils import SimpleJsonYmlReader

def main():
    fm = SimpleJsonYmlReader("requirements.txt")
    fm.read_file()

if __name__ == "__main__":
    main()