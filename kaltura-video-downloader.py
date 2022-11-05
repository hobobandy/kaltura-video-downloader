import os
import shutil
import argparse
import requests

temp_dir = "temp_dl"

def main(url_mp4, url_query, output_file):
    # Download all the available segments from the url.
    # Append /seg-x-v1-a1.ts, check for successful response, and save the file

    response = requests.get(url_mp4 + "/seg-1-v1-a1.ts" + url_query)

    if response.status_code != 200:
        print("Invalid URL or video does not exist.")
        exit()

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    count = 1
    fileList = []
    print("Downloading pieces...")
    while response.status_code == 200:
        curr_seg = "/seg-{}-v1-a1.ts".format(count)
        response = requests.get(url_mp4 + curr_seg + url_query)
        with open(temp_dir + curr_seg, 'wb') as f:
            f.write(response.content)
        fileList.append(temp_dir + curr_seg)
        count += 1

    # Edge case: Last piece seems to not contain any video or audio stream
    # If the file less less than 1KB, ignore and delete it
    if os.path.getsize(fileList[-1]) < 1000:
        os.remove(fileList[-1])
        fileList = fileList[:-1]

    print("Stitching pieces...")
    with open(output_file, 'wb') as stitched:
        for filename in fileList:
            with open(os.path.join("", filename), 'rb') as part:
                shutil.copyfileobj(part, stitched)

    # Cleanup downloaded files
    for filename in fileList:
        os.remove(filename)
    if len(os.listdir(temp_dir)) == 0:
        os.removedirs(temp_dir)

    print("Done")

if __name__ == "__main__":
    # Expected input URL format:
    # https://streaming.video.ubc.ca/ ........  a6rb/name/a.mp4
    # https://kaltura.com/.../name/a.mp4/seg-12-v1-a1.ts?Policy=...&Key-Pair-Id=...
    parser = argparse.ArgumentParser(description='Download and stitch Kaltura videos')
    parser.add_argument('-url', action='store', dest='url', default=None, help='Wrap in double-quotes - URL ending in .../a.mp4/seg-1-v1-a1.ts - include all parts such as ?Policy=...&Signature=...&Key-Pair-Id=...')
    parser.add_argument('-output', action='store', dest='output', default="kaltura_vid.mp4", help='Output file name (default: kaltura_vid.mp4)')

    args = parser.parse_args()
    # Retain the url upto ".mp4"
    url_mp4 = args.url[:args.url.index(".mp4") + 4]
    url_query = args.url[args.url.index("?"):]
    main(url_mp4, url_query, args.output)