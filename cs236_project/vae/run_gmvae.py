# Copyright (c) 2021 Rui Shu
import argparse
import numpy as np
import torch
import tqdm
from codebase import utils as ut
from codebase.models.gmvae import GMVAE
from codebase.train import train
from pprint import pprint
from torchvision import datasets, transforms

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--z',         type=int, default=128,    help="Number of latent dimensions")
parser.add_argument('--k',         type=int, default=2,   help="Number mixture components in MoG prior")
parser.add_argument('--iter_max',  type=int, default=40000, help="Number of training iterations")
parser.add_argument('--iter_save', type=int, default=10000, help="Save model every n iterations")
parser.add_argument('--run',       type=int, default=0,     help="Run ID. In case you want to run replicates")
parser.add_argument('--train',     type=int, default=1,     help="Flag for training")
parser.add_argument('--overwrite', type=int, default=0,     help="Flag for overwriting")
args = parser.parse_args()
layout = [
    ('model={:s}',  'gmvae'),
    ('z={:02d}',  args.z),
    ('k={:03d}',  args.k),
    ('run={:04d}', args.run)
]
model_name = '_'.join([t.format(v) for (t, v) in layout])
pprint(vars(args))
print('Model name:', model_name)
character = "_Kirby"
model_name += character

if torch.cuda.is_available():
    print("GPU is available.")
    # Set the device to GPU
    device = torch.device('cuda')
else:
    print("GPU is not available. Using CPU.")
    # Set the device to CPU
    device = torch.device('cpu')

gmvae = GMVAE(z_dim=args.z, k=args.k, name=model_name).to(device)
pixels = gmvae.get_num_pixels()
#train_loader, labeled_subset = ut.load_custom_dataset("D:\\CS236_project_data_landscapes", device,pixels)
dataset = ut.convert_dataset_toTensor("D:\CS236_project_data_kirby")
train_loader, labeled_subset = ut.load_custom_dataset(dataset, device,pixels)


if args.train:
    writer = ut.prepare_writer(model_name, overwrite_existing=args.overwrite)
    train(model=gmvae,
          train_loader=train_loader,
          labeled_subset=labeled_subset,
          device=device,
          tqdm=tqdm.tqdm,
          writer=writer,
          iter_max=args.iter_max,
          iter_save=args.iter_save)
    #ut.evaluate_lower_bound(gmvae, labeled_subset, run_iwae=args.train == 2)

else:
    ut.load_model_by_name(gmvae, global_step=args.iter_max, device=device)
    #ut.evaluate_lower_bound(gmvae, labeled_subset, run_iwae=True)

