import torch
from transformers import CLIPImageProcessor, CLIPModel
from PIL import Image

def is_valid_image(base_image, comment_images, file_path):
    similarityScore = get_similarity_score(base_image, file_path)

    if similarityScore < 0.6:
        print("Calculating Second ")
        totalSimilarityScore = 0
        for comment_image in comment_images:
            totalSimilarityScore += get_similarity_score(comment_image, file_path)
        averageSimilarityScore = totalSimilarityScore / len(comment_images)
        print("Avarage Similarity Score:", averageSimilarityScore)
        if averageSimilarityScore < 0.6:
            return False
    return True

def get_similarity_score(base_image, comment_image):
    # Load the CLIP model
    model_ID = "openai/clip-vit-base-patch32"
    model = CLIPModel.from_pretrained(model_ID)

    preprocess = CLIPImageProcessor.from_pretrained(model_ID)

    def load_and_preprocess_image(image_path):
        image = Image.open(image_path)
        image = preprocess(image, return_tensors="pt")
        return image

    def preprocess_image(image):
        image = preprocess(image, return_tensors="pt")
        return image

    image_a = load_and_preprocess_image(base_image)["pixel_values"]
    image_b = preprocess_image(comment_image)["pixel_values"]

    with torch.no_grad():
        embedding_a = model.get_image_features(image_a)
        embedding_b = model.get_image_features(image_b)

    similarity_score = torch.nn.functional.cosine_similarity(embedding_a, embedding_b)
    print('Similarity score:', similarity_score.item())
    return similarity_score.item()