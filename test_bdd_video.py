# System libs
import os,math
import argparse
from distutils.version import LooseVersion
# Numerical libs
import numpy as np
import torch
import torch.nn as nn
from scipy.io import loadmat
# Our libs
from dataset import TestDataset
from models import ModelBuilder, SegmentationModule
from utils import colorEncode
from lib.nn import user_scattered_collate, async_copy_to
from lib.utils import as_numpy
import lib.utils.data as torchdata
import cv2
from tqdm import tqdm
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
colors = loadmat('data/color_bdd.mat')['colors']

def visualize_result(data, pred, args):
	(img, info) = data

	# prediction
	#pred = pred + 1
	pred_color = colorEncode(pred, colors,mode="BGR")
	

#     cv2.imwrite("gray.png",pred)
#     pred = cv2.cvtColor(pred, cv2.COLOR_GRAY2RGB)

	# aggregate images and save
	im_vis = np.concatenate((img, pred_color),
							axis=1).astype(np.uint8) #pred_color
	
	img_name = info.split('/')[-1]
	cv2.imwrite(os.path.join(args.result,
				img_name.replace('.jpg', '.png')), im_vis)


def test(segmentation_module, loader, args):
	segmentation_module.eval()
	#print("loader",loader)
	pbar = tqdm(total=len(loader))
	for batch_data in loader:
		# process data
		batch_data = batch_data[0]
		segSize = (batch_data['img_ori'].shape[0],
				   batch_data['img_ori'].shape[1])
		img_resized_list = batch_data['img_data']

		with torch.no_grad():
			scores = torch.zeros(1, args.num_class, segSize[0], segSize[1])
			scores = async_copy_to(scores, args.gpu)

			for img in img_resized_list:
				feed_dict = batch_data.copy()
				feed_dict['img_data'] = img
				del feed_dict['img_ori']
				del feed_dict['info']
				feed_dict = async_copy_to(feed_dict, args.gpu)

				# forward pass
				pred_tmp = segmentation_module(feed_dict, segSize=segSize)
				scores = scores + pred_tmp / len(args.imgSize)

			_, pred = torch.max(scores, dim=1)
			pred = as_numpy(pred.squeeze(0).cpu())
#             np.save("output_1.npy",pred)
#         break
		# visualization
		visualize_result(
			(batch_data['img_ori'], batch_data['info']),
			pred, args)

		pbar.update(1)
import time

def main(args):
	torch.cuda.set_device(args.gpu)

	# Network Builders
	builder = ModelBuilder()
	net_encoder = builder.build_encoder(
		arch=args.arch_encoder,
		fc_dim=args.fc_dim,
		weights=args.weights_encoder)
	net_decoder = builder.build_decoder(
		arch=args.arch_decoder,
		fc_dim=args.fc_dim,
		num_class=args.num_class,
		weights=args.weights_decoder,
		use_softmax=True)

	crit = nn.NLLLoss(ignore_index=-1)

	segmentation_module = SegmentationModule(net_encoder, net_decoder, crit)

	# Dataset and Loader
	# list_test = [{'fpath_img': args.test_img}]
#     test_chk = []
#     testing = os.listdir("/home/teai/externalhd2/BDD100K/segmentation_v2/test/")
#     for i in testing:
#         if(i.endswith(".jpg")):
#             test_chk.append("/home/teai/externalhd2/BDD100K/segmentation_v2/test/"+i)
	video_path = "./test_video_input/test_1.mp4"
	vidcap = cv2.VideoCapture(video_path)
	video_fps=math.ceil(vidcap.get(cv2.CAP_PROP_FPS))
	length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
	frame_array = []
	
	for i in tqdm(range(length-1)):
		ret,frame = vidcap.read()
		cv2.imwrite("./test_video_input/frame.png",frame)
		test_chk = ['./test_video_input/frame.png']
	#     print(type(args.test_imgs))
		list_test = [{'fpath_img': x} for x in test_chk]
		#list_test=[{'fpath_img': 'frame_143.png'},{'fpath_img': 'frame_100.png'},{'fpath_img': 'frame_1.png'}]
		#print("list_test",list_test)
		dataset_test = TestDataset(
			list_test, args, max_sample=args.num_val)
		loader_test = torchdata.DataLoader(
			dataset_test,
			batch_size=args.batch_size,
			shuffle=False,
			collate_fn=user_scattered_collate,
			num_workers=5,
			drop_last=True)

		segmentation_module.cuda()

		# Main loop
# 		start=time.time()
		test(segmentation_module, loader_test, args)
# 		end=time.time()
# 		print("Time taken",(end-start))
		#print('Inference done!')
		img = cv2.imread("./test_video_output/frame.png")
		height, width, layers = img.shape
		size = (width,height)
		frame_array.append(img)
		
	out = cv2.VideoWriter("./test_video_output/test_1_sgd_100.mp4",cv2.VideoWriter_fourcc(*'DIVX'), video_fps, size)

	for i in range(len(frame_array)):
		# writing to a image array
		out.write(frame_array[i])
	out.release()


if __name__ == '__main__':
	assert LooseVersion(torch.__version__) >= LooseVersion('0.4.0'), \
		'PyTorch>=0.4.0 is required'

	parser = argparse.ArgumentParser()
	# Path related arguments
	parser.add_argument('--test_imgs', required=False, nargs='+', type=str,
						help='a list of image paths that needs to be tested')
	parser.add_argument('--model_path', default="./ckpt/baseline-resnet50dilated-ppm_deepsup-ngpus1-batchSize2-imgMaxSize1000-paddingConst8-segmDownsampleRate8-LR_encoder0.02-LR_decoder0.02-epoch100",required=False,
						help='folder to model path')
	parser.add_argument('--suffix', default='_epoch_100.pth',
						help="which snapshot to load")

	# Model related arguments
	parser.add_argument('--arch_encoder', default='resnet50dilated',
						help="architecture of net_encoder")
	parser.add_argument('--arch_decoder', default='ppm_deepsup',
						help="architecture of net_decoder")
	parser.add_argument('--fc_dim', default=2048, type=int,
						help='number of features between encoder and decoder')

	# Data related arguments
	parser.add_argument('--num_val', default=-1, type=int,
						help='number of images to evalutate')
	parser.add_argument('--num_class', default=38, type=int,
						help='number of classes')
	parser.add_argument('--batch_size', default=1, type=int,
						help='batchsize. current only supports 1')
	parser.add_argument('--imgSize', default=[300, 400, 500, 600],
						nargs='+', type=int,
						help='list of input image sizes.'
							 'for multiscale testing, e.g. 300 400 500') #[300, 400, 500, 600]
	parser.add_argument('--imgMaxSize', default=1000, type=int,
						help='maximum input image size of long edge') #1280
	parser.add_argument('--padding_constant', default=8, type=int,
						help='maxmimum downsampling rate of the network')
	parser.add_argument('--segm_downsampling_rate', default=8, type=int,
						help='downsampling rate of the segmentation label')

	# Misc arguments
	parser.add_argument('--result', default='./test_video_output/',
						help='folder to output visualization results')
	parser.add_argument('--gpu', default=0, type=int,
						help='gpu id for evaluation')

	args = parser.parse_args()
	args.arch_encoder = args.arch_encoder.lower()
	args.arch_decoder = args.arch_decoder.lower()
	#print("Input arguments:")
#     for key, val in vars(args).items():
#         print("{:16} {}".format(key, val))

	# absolute paths of model weights
	args.weights_encoder = os.path.join(args.model_path,
										'encoder' + args.suffix)
	args.weights_decoder = os.path.join(args.model_path,
										'decoder' + args.suffix)

	assert os.path.exists(args.weights_encoder) and \
		os.path.exists(args.weights_encoder), 'checkpoint does not exitst!'

	if not os.path.isdir(args.result):
		os.makedirs(args.result)

	main(args)
