import os
import cv2
from distutils import dir_util
import argparse
from os import path
from bs4 import BeautifulSoup
import re
import os
from shutil import copy2


def Resize_Images(src: str, folder: str, dst: str, size: tuple = ()):
    """Auto crops images from the source directory to destination directory.
    src: source directory path name which contain images to be cropped
    folder: patient folder name
    dst: destination directory path name  to put resized images
    size: the size to resize the images in pixes, as a 2-tuple:
        (width, height)
    """

    # create the destination directory for resized Images
    if not dst:
        dest_directory = os.path.join(
            # specify destination folder for resized images here if not parsed as argument while running script
            "E:\\Work\\Deep Learning\\Cervical Cancer\\new data 512by512 oldform2",
            folder,
        )
        dir_util.mkpath(dest_directory)
    else:
        dest_directory = dst
    # file names in the directory
    file_names = os.listdir(path.join(src, folder))
    resized_images = 0
    for filename in file_names:
        # read the image from the disk
        img = cv2.imread(path.join(src, folder, filename), cv2.IMREAD_UNCHANGED)
        if img is not None:
            print(f"Resizing: {filename}")
            resized = cv2.resize(img, size)
            cv2.imwrite(
                path.join(dest_directory, filename.split(".")[0] + ".png"), resized
            )
            resized_images += 1
        else:
            print(f"Cant read this file, probably not an Image: {filename}")
    print(f"Resized {resized_images} Image(s)")


def extractor(source_path, dst: str, size: tuple = ()):
    for folder in os.listdir(source_path):
        try:
            print(folder)
            if os.path.exists(os.path.join(source_path, folder, "submission.xml")):
                soup = BeautifulSoup(
                    open(os.path.join(source_path, folder, "submission.xml")), "xml"
                )
                dir_util.mkpath(os.path.join(dst, "Positive"))
                dir_util.mkpath(os.path.join(dst, "Negative"))
                study_id = soup.StudyID.text
                print(study_id)
                result = soup.VIAResult.text
                print(result)
                dir_util.mkpath(os.path.join(dst, result, study_id))
                for image_tag in soup.find_all(re.compile(r"Picture\d+")):
                    image_name = image_tag.text
                    if image_name:
                        print(image_name)
                        copy2(
                            os.path.join(source_path, folder, image_name),
                            os.path.join(dst, result, study_id, image_name),
                        )
        except FileNotFoundError:
            print("File not found")
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto crop Images")
    parser.add_argument(
        "src",
        metavar="source directory",
        help="The source directory that contains images to be "
        "extracted, cropped and resized",
    )
    parser.add_argument(
        "-dst",
        metavar="extract destination directory",
        help="destination folder to store extracted image folders",
        default="",
    )
    parser.add_argument(
        "-dst_resized",
        metavar="resize destination directory",
        help="destination folder to store resized image folders",
        default="",
    )
    parser.add_argument(
        "-size",
        type=int,
        help="Size for resizing cropped images in form of  width, height",
        default=(764, 764),
        nargs=2,
    )
    args = parser.parse_args()
    if not path.isdir(args.src):
        parser.error("Please Enter Valid source directory")
    if args.dst and not path.isdir(args.dst):
        parser.error("Please Enter valid destination directory")
    if args.dst_resized and not path.isdir(args.dst_resized):
        parser.error("Please enter valid resize destination directory")

    extractor(args.src, args.dst, tuple(args.size))
    source_path = args.dst
    for x in [
        os.path.join(source_path, "Positive"),
        os.path.join(source_path, "Negative"),
    ]:
        for y in os.listdir(x):
            Resize_Images(x, y, args.dst_resized, size=(512, 512))