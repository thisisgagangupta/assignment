import argparse
from medmitra import load_model


def download_models():
    parser = argparse.ArgumentParser(description="Download models")

    parser.add_argument("--documents", action="store_true", help="Load document models")
    args = parser.parse_args()

    load_model(args.documents)


if __name__ == "__main__":
    download_models()