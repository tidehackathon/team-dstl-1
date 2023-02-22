''' Train'''
import torch
from tqdm import tqdm
import os

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
            # act like pseudolabels

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
            torch.save(model.state_dict(), os.path.join(save_path, f'landcoversiamese_augmented{num_epochs}_{loss}.pt'))


    # save model 
    torch.save(model.state_dict(), os.path.join(save_path, f'landcoversiamese_augmented{num_epochs}_{loss}.pt'))
