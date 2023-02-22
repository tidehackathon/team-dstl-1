''' Train'''
import torch
import torchvision
from tqdm import tqdm
import os

from landcoversiamese import *

def train_triplet(model, dataloader, criterion, device, num_epochs=100, lr=1e-4, margin=1, save_path='models'):
    ''' '''
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.9)
    model = model.to(device)
    model.train()
    for epoch in range(num_epochs):
        optimizer.zero_grad()
        epoch_loss = 0
        # get data
        for map, pos, neg in tqdm(dataloader):
            # get embeddings
            map, pos, neg = model(map.to(device), pos.to(device), neg.to(device))
            # euclidean distance
            map_pos_dist = torch.cdist(map, pos)
            map_neg_dist = torch.cdist(map, neg)
            # act like pseudolabels, dont need as skipping mining
            # this is also why margin isnt used

            # skip mining, sort if time

            # loss
            loss = criterion(map, pos, neg)
            epoch_loss += loss.item()
            # backwards
            loss.backward()
            optimizer.step()
        scheduler.step()
        print(epoch_loss)

        if epoch%25==0:
            # this is a save rather than a checkpoint
            torch.save(model.state_dict(), os.path.join(save_path, f'landcoversiamese_augmented{num_epochs}_{loss}.pt'))


    # save model 
    torch.save(model.state_dict(), os.path.join(save_path, f'landcoversiamese_augmented{num_epochs}_{loss}.pt'))

def transforms(anchor, pos, neg):
    T = torch.nn.Sequential(torchvision.transforms.RandomPerspective(distortion_scale=0.6),
                    torchvision.transforms.RandomResizedCrop((512, 512)),
                    torchvision.transforms.RandomHorizontalFlip(),
                    torchvision.transforms.RandomRotation((-50, 50)),
                    torchvision.transforms.RandomAutocontrast(p=0.25),
                    torchvision.transforms.RandomEqualize(p=0.25),
                    torchvision.transforms.ColorJitter(brightness=0.5, contrast=0.2),
                    )
    anchor = T(anchor)
    pos = T(pos)
    neg = T(neg)
    return anchor, pos, neg

if __name__=='__main__':
    DATA_FOLDER = 'landcover.ai.v1'
    MARGIN = 1
    LR = 1e-4
    NUM_EPOCHS = 100
    SAVE_PATH = 'models'

    data = LandcoverAITriplet(DATA_FOLDER)
    dataloader = torch.utils.DataLoader(data, batch_size=32, shuffle=True)
    model = LandSiamese()
    criterion = torch.nn.TripletMarginLoss(margin=MARGIN)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(device)

    train_triplet(model, dataloader, criterion, device, num_epochs=NUM_EPOCHS, lr=LR, margin=1, save_path=SAVE_PATH)

