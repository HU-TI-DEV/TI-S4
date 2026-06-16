from pathlib import Path
import argparse

import cv2
import torch


ROOT = Path(__file__).resolve().parents[3]


def resize_to_fit(image, max_width: int = 1920, max_height: int = 1080):
	height, width = image.shape[:2]
	scale = min(max_width / width, max_height / height, 1.0)
	if scale == 1.0:
		return image
	new_size = (int(width * scale), int(height * scale))
	return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="YOLOv5 model check")
	parser.add_argument(
		"--weights",
		type=Path,
		default=ROOT / "runs" / "train" / "exp3" / "weights" / "best.pt",
		help="pad naar weights van getraind model (best.pt of last.pt)",
	)
	parser.add_argument(
		"--image",
		type=Path,
		default=ROOT / "workspace" / "gazebo" / "dataset" / "images" / "test" / "img_0175.png",
		help="pad naar testafbeelding",
	)
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	weights_path = args.weights
	image_path = args.image

	if not weights_path.exists():
		raise FileNotFoundError(f"Weights not found: {weights_path}")
	if not image_path.exists():
		raise FileNotFoundError(f"Image not found: {image_path}")

	model = torch.hub.load("ultralytics/yolov5", "custom", path=str(weights_path))

	img = cv2.imread(str(image_path))
	if img is None:
		raise RuntimeError(f"OpenCV could not read image: {image_path}")

	results = model(img)
	boxes = results.xyxy[0]
	print(boxes)

	display_image = resize_to_fit(results.render()[0])
	cv2.namedWindow("Detections", cv2.WINDOW_NORMAL)
	cv2.imshow("Detections", display_image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()


if __name__ == "__main__":
	main()
