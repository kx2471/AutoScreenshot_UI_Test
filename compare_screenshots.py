import os
import logging
import numpy as np
from PIL import Image, ImageChops

# --- Configuration ---
# 1. 픽셀 값 차이 임계값 (0-255)
# 각 픽셀의 R, G, B 값 차이가 이 값보다 커야 '다른 픽셀'로 간주합니다.
PIXEL_DIFF_THRESHOLD = 25

# 2. 다른 픽셀 개수 임계값
# '다른 픽셀'의 수가 이 값보다 커야 최종적으로 '다른 이미지'로 판단합니다.
# 이 값을 조절하여 민감도를 설정할 수 있습니다. (예: 100 -> 100개 이상 다를 때만 감지)
SIGNIFICANT_PIXEL_COUNT_THRESHOLD = 100

# 3. 차이점 표시 색상
DIFF_COLOR = (255, 0, 0) # 밝은 빨강

# --- Core Functions ---

def compare_images(file1, file2, diff_output_path):
    """
    두 이미지를 비교하여 '의미 있는' 차이가 있을 경우, 
    차이점을 빨간색으로 칠한 diff 이미지를 저장합니다.
    """
    try:
        img1 = Image.open(file1).convert('RGB')
        img2 = Image.open(file2).convert('RGB')

        if img1.size != img2.size:
            logging.warning(f"이미지 크기 다름: {os.path.basename(file1)} {img1.size} vs {os.path.basename(file2)} {img2.size}. 작은 크기로 잘라내어 비교합니다.")
            w = min(img1.width, img2.width)
            h = min(img1.height, img2.height)
            img1 = img1.crop((0, 0, w, h))
            img2 = img2.crop((0, 0, w, h))

        # 1. 두 이미지의 절대적인 차이를 계산
        diff = ImageChops.difference(img1, img2)

        # 2. '의미 있는' 차이만 남기는 마스크 생성
        fn = lambda x: 255 if x > PIXEL_DIFF_THRESHOLD else 0
        mask = diff.convert('L').point(fn, mode='1')

        # 3. '의미 있는' 차이를 가진 픽셀의 개수 계산
        num_significant_diffs = np.sum(np.array(mask)) / 255 # 마스크는 0 또는 255 값을 가지므로 255로 나눔

        # 4. 다른 픽셀의 개수가 임계값을 초과하는 경우에만 '다르다'고 판단
        if num_significant_diffs > SIGNIFICANT_PIXEL_COUNT_THRESHOLD:
            logging.info(f"차이점 발견 (다른 픽셀 수: {int(num_significant_diffs)} > {SIGNIFICANT_PIXEL_COUNT_THRESHOLD}): {os.path.basename(file1)}")

            # 5. 차이점을 빨간색으로 칠하기
            diff_highlight = img2.copy()
            red_img = Image.new('RGB', img2.size, DIFF_COLOR)
            diff_highlight.paste(red_img, mask=mask)

            diff_highlight.save(diff_output_path)
            logging.info(f"Diff 이미지 저장: {diff_output_path}")
            return True

        return False

    except FileNotFoundError as e:
        logging.error(f"이미지 파일을 여는 중 오류 발생: {e}")
        return True
    except Exception as e:
        logging.error(f"이미지 비교 중 오류 발생: {e}")
        return True

def run_comparison(base_path, output_dir_name="comparison_results"):
    """
    base_path에서 Chrome과 Edge의 스크린샷을 찾아 비교합니다.
    """
    logging.info(f"스크린샷 비교 시작: {base_path}")

    output_path = os.path.join(base_path, output_dir_name)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        logging.info(f"결과 폴더 생성: {output_path}")

    all_dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]

    grouped_dirs = {}
    for d in all_dirs:
        if d.startswith("chrome_") or d.startswith("edge_"):
            try:
                browser, breakpoint_key = d.split('_', 1)
                if breakpoint_key not in grouped_dirs:
                    grouped_dirs[breakpoint_key] = {}
                grouped_dirs[breakpoint_key][browser] = os.path.join(base_path, d)
            except ValueError:
                logging.warning(f"폴더 이름 형식이 올바르지 않아 건너뜁니다: {d}")


    diff_count = 0
    for breakpoint_key, browsers in grouped_dirs.items():
        if 'chrome' in browsers and 'edge' in browsers:
            chrome_dir = browsers['chrome']
            edge_dir = browsers['edge']

            logging.info(f"Breakpoint 비교 중: {breakpoint_key}")

            breakpoint_output_path = os.path.join(output_path, breakpoint_key)
            if not os.path.exists(breakpoint_output_path):
                os.makedirs(breakpoint_output_path)

            for img_name in os.listdir(chrome_dir):
                if img_name.lower().endswith('.png'):
                    chrome_img_path = os.path.join(chrome_dir, img_name)
                    edge_img_path = os.path.join(edge_dir, img_name)

                    if os.path.exists(edge_img_path):
                        diff_img_name = f"{os.path.splitext(img_name)[0]}_diff.png"
                        diff_output_path = os.path.join(breakpoint_output_path, diff_img_name)

                        if compare_images(chrome_img_path, edge_img_path, diff_output_path):
                            diff_count += 1
                    else:
                        logging.warning(f"Edge 폴더에 해당 이미지가 없습니다: {img_name}")
        else:
            logging.warning(f"'{breakpoint_key}' Breakpoint에 비교할 브라우저 쌍이 없습니다.")

    logging.info(f"비교 완료. 총 {diff_count}개의 차이점을 발견했습니다.")
    return diff_count, output_path
