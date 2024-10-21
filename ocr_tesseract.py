import cv2
import pytesseract

def invert_image(image_path):
    # Grayscaling
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Invertinhg
    inverted_image = cv2.bitwise_not(image)

    cv2.imwrite('inverted_image.png', inverted_image)
    
    return inverted_image

def rescale_image(image, scale_percent=200):
    # Rescaling
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    
    # Resizing
    rescaled_image = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)
    
    cv2.imwrite('rescaled_image.png', rescaled_image)
    
    return rescaled_image

def ocr_on_processed_image(image_path):
    inverted_image = invert_image(image_path)
    rescaled_image = rescale_image(inverted_image, scale_percent=200)  # Scaling by 200% for better OCR
    
    # ocr
    text = pytesseract.image_to_string(rescaled_image)
    
    return text

image_path = 'report1.jpg' 
extracted_text = ocr_on_processed_image(image_path)
print("Extracted Text:")
print(extracted_text)
