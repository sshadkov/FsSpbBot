import os
import re
from PIL import Image
import pytesseract as tess
from functools import reduce
from fuzzywuzzy import fuzz

pink = [(188, 50, 124)]
back = [(11, 18, 36)]

dir_screens = 'TestScreens'
dir_result = 'TestResult'
image_ext = ['jpg', 'jpeg', 'png']
tessdata_dir_config = r' --tessdata-dir "C:\\Program Files\\tesseract-OCR\\tessdata\\" '
MODES = ["Explorer", "XM Collected", "Trekker", "Builder", "Connector", "Mind Controller", "Illuminator", "Recharger", "Liberator", "Pioneer", "Engineer", "Purifier", "Portal Destroy", "Links Destroy", "Fields Destroy", "SpecOps", "Hacker", "Translator"]



def doubled(img: Image):
    d = Image.new("RGB", (img.width * 2, img.height * 2))
    d.paste(img, (int(img.width / 2), int(img.height / 2)))
    return d


def color_diff(px: tuple, color: tuple):
    return abs(px[0]-color[0]) + abs(px[1]-color[1]) + abs(px[2]-color[2])


def find_lines(pixels: tuple, width: int, rect: tuple, colors: list, threshhold: int, min_width: int = 1,
               find_count: int = 0, average: bool = True, horizontal: bool = True):
    if horizontal:
        x_range = rect[2] - rect[0]
        y_start = rect[1]
        y_end = rect[3]
        px_diff = 1
    else:
        x_range = rect[3]-rect[1]
        y_start = rect[0]
        y_end = rect[2]
        px_diff = width

    results = []
    concurrent = 0
    already_saved = False
    for y in range(y_start, y_end):
        line_error = 0
        if horizontal:
            curr_px = y * width + rect[0]
        else:
            curr_px = y + rect[1] * width
        process = True
        for x in range(x_range):
            if process:
                diffs = tuple(color_diff(pixels[curr_px], color) for color in colors)
                curr_px += px_diff
                line_error += min(diffs)
                if not average:
                    if min(diffs) > threshhold:
                        process = False
        if process:
            line_error /= x_range
            if line_error < threshhold:
                concurrent += 1
                if concurrent >= min_width and not already_saved:
                    results.append(y)
                    already_saved = True
                    if find_count and (len(results) >= find_count):
                        return results
            else:
                concurrent = 0
                already_saved = False
        else:
            concurrent = 0
            already_saved = False
    return results


def check_screen(img: Image, file: str):
    pxls = tuple(img.getdata())

    # Find pink lines (1 - above AP, 2 - in medal)
    pink_zone = (int(img.width * 0.28), 0, int(img.width * 0.6), int(img.height * 0.7))

    pink_lines = []
    pink_lines = find_lines(pxls, img.width,
                            pink_zone,
                            pink, 140, 1, 2)

    pink_zone_img = img.crop(pink_zone)
    # print("pink:" + str(len(pink_lines)))

    # Search for empty line after AP pink_lines[0] + 50

    if len(pink_lines) == 2:  # Found
        backs_zone = (
            int(img.width * 0.25),
            pink_lines[0] + 60,
            int(img.width * 0.98),
            pink_lines[1])

        prime_backs = find_lines(pxls, img.width, backs_zone, back, 50,
                                 1, 1, False)

        backs_zone_img = img.crop(backs_zone)
        backs_zone_img.save(dir_result + os.path.sep + 'black_zone_' + file + '.png')

        if len(prime_backs) == 1:
            # Main height parameter
            prime_height = prime_backs[0] - pink_lines[0]
            # print(prime_height)
            # Extract AP to IMG
            ap_zone = (int(img.width * 0.1), prime_backs[0] - int(prime_height * 1.7),
                       img.width, prime_backs[0])

            nick_zone = (int(img.width * 0.28), pink_lines[0] + 10,
                         int(img.width * 0.8) + 10, prime_backs[0])

            prime_ap_img = img.crop(ap_zone)
            nick_img = img.crop(nick_zone)

            pxls = tuple(prime_ap_img.getdata())
            backs = find_lines(pxls, prime_ap_img.width,
                               (0, 0, prime_ap_img.width, prime_ap_img.height),
                               [(0, 0, 0)], 30, 5, 0)

            ap_zone_img = img.crop(ap_zone)

            if len(backs) == 2:
                ap_img = ap_zone_img.crop((0, backs[0], img.width, backs[1] + 10))

                medal_zone = (int(img.width / 4), pink_lines[1] - int(prime_height / 2) - 10,
                              int(img.width * 3 / 4), pink_lines[1] + int(prime_height * 2 / 3) + 10)

                medal_img = img.crop(medal_zone)
                medal_name = medal_img.crop((0, int(medal_img.height / 2), medal_img.width, medal_img.height))
                medal_val = medal_img.crop((0, 0, medal_img.width, int(medal_img.height * 0.42)))

                pink_zone_img.save(dir_result + os.path.sep + 'pink_zone_' + file + '.png')
                ap_zone_img.save(dir_result + os.path.sep + 'ap_zone_' + file + '.png')
                ap_img.save(dir_result + os.path.sep + 'ap_' + file + '.png')
                nick_img.save(dir_result + os.path.sep + 'nick_' + file + '.png')
                medal_img.save(dir_result + os.path.sep + 'medal_' + file + '.png')
                medal_name.save(dir_result + os.path.sep + 'medal_name_' + file + '.png')
                medal_val.save(dir_result + os.path.sep + 'medal_value_' + file + '.png')

                pxls = tuple(ap_img.getdata())
                ap_img.putdata([px if px[0] + px[1] + px[2] > 100 else (0, 0, 0) for px in pxls])
                pxls = tuple(ap_img.getdata())
                colors = reduce(
                    lambda prev, new: (prev[0] + new[0], prev[1] + new[1], prev[2] + new[2]), pxls)
                faction = "Enlightened" if colors[1] > colors[2] else "Resistance"
                ap = tess.image_to_string(doubled(ap_img), lang='exo',
                                          config=tessdata_dir_config + ' -c tessedit_char_whitelist="0123456789AP.,/"') \
                    .replace(".", "") \
                    .replace(",", "").replace(" ", "")
                # print(ap)
                # config='-psm 7 -c tessedit_char_whitelist="0123456789AP.,/"').replace(

                level = 1
                try:
                    slash = ap.index("/")
                    (curr, lvlreq) = (ap[:slash], ap[slash + 1:len(ap) - 2])
                    lvldiffs = {
                        1: (2500, 2600),
                        2: (17500, 17600),
                        3: (50000, 60000),
                        4: (80000, 30000),
                        5: (150000, 160000),
                        6: (300000, 800000),
                        7: (600000, 500000),
                        8: (1200000, 1200000),
                        9: (1600000, 1500000),
                        10: (2000000, 2000000),
                        11: (2400000, 2100000),
                        12: (3600000, 3500000),
                        13: (5000000, 6000000),
                        14: (7000000, 1000000),
                        15: (16000000, 15000000),
                    }
                    currap = int(curr)
                    t = 0
                    for i in range(1, 16):
                        if int(lvlreq) in lvldiffs[i]:
                            break
                        t += lvldiffs[i][0]
                        level += 1
                    if level < 16:
                        ap = t + currap
                except ValueError:
                    if len(ap) in (10, 11, 12):
                        ap = ap[:-2]
                        level = 16

                name = tess.image_to_string(medal_name, lang='exo', config=tessdata_dir_config)
                mod_name = 'Unknown'
                mod_rate = 0
                for mod in MODES:
                    rate = fuzz.ratio(name, mod)
                    if rate > mod_rate:
                        mod_name = mod
                        mod_rate = rate

                name = mod_name

                value = tess.image_to_string(medal_val, lang='exo',
                                             # config='-psm 7 -c tessedit_char_whitelist="0123456789.,"').replace(
                                             config=tessdata_dir_config + ' -c tessedit_char_whitelist="0123456789.,"').replace(
                    " ", "").replace(".", "").replace(",", "")
                print('{} :: ap:{} faction:{} medal:{} value:{}'
                      .format(file, ap, faction, name, value))


def test():
    pass
    print('RUN TEST')
    if os.path.isdir(dir_screens):
        for screen in os.listdir(dir_screens):
            screen_path = dir_screens+os.path.sep+screen
            if os.path.isfile(screen_path):
                if re.search('\.({ext})$'.format(ext="|".join(image_ext)), screen.lower()):
                    img = Image.open(screen_path)
                    check_screen(img, screen)

    else:
        print('no screensdir')


if __name__ == '__main__':
    if os.environ.get('OS', '') == 'Windows_NT':
        tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    print(tess.get_tesseract_version())
    test()
