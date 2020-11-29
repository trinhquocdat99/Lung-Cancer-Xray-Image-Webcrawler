import torch
from torchvision import transforms
import torch.nn.functional as F
from PIL import Image
import torchvision
import onnxruntime as ort

"""
    0 - not xray
    1 - xray
    accuracy(tested on 166 images) - 0.9940
"""

model = ort.InferenceSession('model/xray_image_classification.onnx')


def isImageXray(image_path, return_bool=True):
    im = Image.open(image_path)
    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,)),
        torchvision.transforms.Resize([84, 84])
    ])

    im = transform(im)

    logps = model.run(None, {'input': im.view(1, 1, 84, 84).cpu().numpy()})
    logps = torch.from_numpy(logps[0])

    ps = torch.exp(logps)
    probab = list(ps.cpu()[0])
    pred_label = probab.index(max(probab))

    probs = F.softmax(logps, dim=1)
    if return_bool:
        return pred_label
    else:
        return {'prediction': pred_label, 'probability': torch.max(probs).item()}


def getModelStats():
    return {'model_name': 'xray_image_classification.onnx', "accuracy": "99.40%", 'inference_time': '0.1s'}