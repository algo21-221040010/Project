import numpy as np
from torch import nn
from torch.nn import functional as F
import torch
import pandas as pd
import downloadBackTestData


class Residual(nn.Module):
    def __init__(self, input_channels, num_channels, use_1x1conv=False, strides=1):
        super().__init__()
        self.conv1 = nn.Conv2d(input_channels, num_channels, kernel_size=3, padding=1, stride=strides)
        self.conv2 = nn.Conv2d(num_channels, num_channels, kernel_size=3, padding=1)
        if use_1x1conv:
            self.conv3 = nn.Conv2d(input_channels, num_channels, kernel_size=1, stride=strides)
        else:
            self.conv3 = None
        self.bn1 = nn.BatchNorm2d(num_channels)
        self.bn2 = nn.BatchNorm2d(num_channels)

    def forward(self, X):
        Y = F.relu(self.bn1(self.conv1(X)))
        Y = self.bn2(self.conv2(Y))
        if self.conv3:
            X = self.conv3(X)
        Y += X
        return F.relu(Y)


def resnet_block(input_channels, num_channels, num_residuals, first_block=False):
    blk = []
    for i in range(num_residuals):
        if i == 0 and not first_block:
            blk.append(Residual(input_channels, num_channels, use_1x1conv=True, strides=2))
        else:
            blk.append(Residual(num_channels, num_channels))
    return blk


b1 = nn.Sequential(nn.Conv2d(1, 64, kernel_size=2, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
                   nn.MaxPool2d(kernel_size=2, padding=1))
b2 = nn.Sequential(*resnet_block(64, 64, 2, first_block=True))
b3 = nn.Sequential(*resnet_block(64, 128, 2))
b4 = nn.Sequential(*resnet_block(128, 256, 2))
b5 = nn.Sequential(*resnet_block(256, 512, 2))

net = nn.Sequential(b1, b2, b3, b4, b5, nn.AdaptiveAvgPool2d((1, 1)), nn.Flatten(), nn.Linear(512, 3))


def train_ch6(net, train_iter, num_epochs, lr):
    def init_weights(m):
        if type(m) == nn.Linear or type(m) == nn.Conv2d:
            nn.init.xavier_uniform_(m.weight)

    net.apply(init_weights)
    optimizer = torch.optim.SGD(net.parameters(), lr=lr)
    loss = nn.CrossEntropyLoss()
    for epoch in range(num_epochs):
        # Sum of training loss, sum of training accuracy, no. of examples
        net.train()
        for i, (X, y) in enumerate(train_iter):
            optimizer.zero_grad()
            y_hat = net(X.float())
            l = loss(y_hat, y)
            l.backward()
            optimizer.step()
            print(f"Epoch {epoch+1} and iter {i+1}: Loss is {l}")


from torch.utils import data
def load_array(data_arrays, batch_size, is_train=True):
    dataset = data.TensorDataset(*data_arrays)
    return data.DataLoader(dataset, batch_size, shuffle=is_train)

def preprocess(df):
    features = df.iloc[:, :-1]
    features = (features - features.mean()) / features.std()
    features = torch.reshape(torch.tensor(features.values[:, np.newaxis][:, np.newaxis]), (-1, 1, 5, 5))
    labels = torch.tensor(df.iloc[:, -1].values) + 1
    return (features, labels)

lr, num_epochs, batch_size = 0.05, 5, 250
#df = pd.read_csv('data.csv').iloc[:4500,2:]
dfTemp = getDataForBackTestAnalysis()
df = dfTemp.iloc[:4500,1:]
df_test = dfTemp.iloc[4500:9000,1:]

train_iter = load_array(preprocess(df), batch_size=batch_size)
train_ch6(net, train_iter, num_epochs, lr)

#df_test=pd.read_csv('data_test.csv').iloc[:4500,2:]
x_test, y_test=preprocess(df_test)
y_test_hat=net(x_test.float()).argmax(axis=1)
torch.save(y_test_hat, 'result.pt')
accuracy=np.average(y_test_hat==y_test)
