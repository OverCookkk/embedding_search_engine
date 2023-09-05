from towhee import pipe, ops


class ImageModel:
    """
    """

    def __init__(self):
        self.image_embedding_pipi = (
            pipe.input('path')
            .map('path', 'img', ops.image_decode.cv2_rgb())
            .map('img', 'embedding', ops.image_embedding.timm(model_name='resnet50'))
            .map('embedding', 'embedding', ops.towhee.np_normalize())  # 归一化
            .output('embedding')
        )

    def extract_feat(self, img_path):
        feat = self.image_embedding_pipi(img_path)
        return feat.get()[0]


if __name__ == '__main__':
    MODEL = ImageModel()
    MODEL.extract_feat('https://raw.githubusercontent.com/towhee-io/towhee/main/towhee_logo.png')
